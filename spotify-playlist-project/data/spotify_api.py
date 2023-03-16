import base64
import datetime
import requests
from urllib.parse import urlencode


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None and client_secret == None:
            raise Exception("You must set client_id and client_secret")
        client_credentials = f'{client_id}:{client_secret}'
        client_credentials_b64 = base64.b64encode(client_credentials.encode())
        return client_credentials_b64.decode()
    
    def get_token_headers(self):
        client_credentials_b64 = self.get_client_credentials()
        return {
            'Authorization': f'Basic {client_credentials_b64}'
        }
    
    def get_token_data(self):
        return {
            'grant_type': 'client_credentials'
        }
    
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception('Authentication failed')
        data = r.json()
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=data['expires_in'])    # seconds
        
        self.access_token = data['access_token']
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now or token == None:
            self.perform_auth()
            return self.get_access_token()
        return token
    
    def get_resource_headers(self):
        access_token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        return headers
    
    def get_resource(self, _id, resource_type='albums', version='v1'):
        endpoint = f'https://api.spotify.com/{version}/{resource_type}/{_id}'
        headers = self.get_resource_headers()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    
    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')
    
    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')
    
    def get_playlist(self, _id):
        return self.get_resource(_id, resource_type='playlists')
    
    def get_my_playlists(self, user_id='12130028192', limit=50, offset=0, version='v1'):
        endpoint = f'https://api.spotify.com/{version}/users/{user_id}/playlists?limit={limit}&offset={offset}'
        headers = self.get_resource_headers()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    
    def base_search(self, query_params):
        headers = self.get_resource_headers()
        endpoint = 'https://api.spotify.com/v1/search'
        lookup_url = f'{endpoint}?{query_params}'
        r = requests.get(lookup_url, headers=headers)
        if r.status_code  not in range(200, 299):
            return {}
        return r.json()
    
    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        if query == None:
            raise Exception('A query is required')
        if isinstance(query, dict):
            query = ' '.join([f'{k}:{v}' for k,v in query.items()]) # Dict into list
        if operator != None and operator_query != None:
            if operator.lower() == 'or' or operator.lower() == 'not':
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f'{query} {operator} {operator_query}'
        query_params = urlencode({'q': query, 'type': search_type.lower()})
        return self.base_search(query_params)