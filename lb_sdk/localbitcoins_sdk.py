import hmac
import json
import hashlib
from urllib import parse
from datetime import datetime

import requests


class Client:
    lb_url = 'https://localbitcoins.com'

    def __init__(self, hmac_auth_key, hmac_auth_secret, debug=False):
        self.hmac_auth_key = hmac_auth_key
        self.hmac_auth_secret = hmac_auth_secret
        self.debug = debug

    def send_request(self, endpoint: str, method: str = 'get', params: dict = None) -> dict:
        """
        Sends request to endpoint with params.
        :param str endpoint: Localbitcoins endpoint path.
        :param str method: Request method ('get' or 'post').
        :param dict params: Request params.
        :return dict: Response from localbitcoins.net in JSON format.
        """
        params_encoded = self._encode_params(params, method)
        nonce = self._make_nonce()
        message = self._make_message(nonce, endpoint, params_encoded)
        signature = self._make_signature(message)
        headers = _make_headers(nonce, signature)

        response_data = self._get_response_data(method, endpoint, headers, params)

        return response_data

    @staticmethod
    def _encode_params(params, method):
        params_encoded = ''
        if params:
            params_encoded = parse.urlencode(params)
            if method == 'get':
                params_encoded = '?' + params_encoded

        return params_encoded

    @staticmethod
    def _make_nonce():
        now = datetime.utcnow()
        epoch = datetime.utcfromtimestamp(0)
        delta = now - epoch
        nonce = int(delta.total_seconds() * 1000)

        return nonce

    def _make_message(self, nonce, endpoint, params_encoded):
        return str(nonce) + self.hmac_auth_key + endpoint + params_encoded

    def _make_signature(self, message):
        return hmac.new(bytes(self.hmac_auth_secret, 'latin-1'), msg=bytes(message, 'latin-1'),
                        digestmod=hashlib.sha256).hexdigest().upper()

    def _make_headers(self, nonce, signature):
        return {
            'Apiauth-key': self.hmac_auth_key,
            'Apiauth-Nonce': str(nonce),
            'Apiauth-Signature': signature
        }

    def _get_response_data(self, method, endpoint, headers, params):
        if method == 'get':
            response = requests.get(self.lb_url + endpoint, headers=headers, params=params)
        else:
            response = requests.post(self.lb_url + endpoint, headers=headers, data=params)

        return json.loads(response.text)['data']
