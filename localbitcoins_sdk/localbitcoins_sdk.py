import hmac
import json
import hashlib
from urllib import parse
from datetime import datetime

import requests


class LBClient:
    lb_url = 'https://localbitcoins.com'

    def __init__(self, hmac_auth_key, hmac_auth_secret, debug=False):
        self.hmac_auth_key = hmac_auth_key
        self.hmac_auth_secret = hmac_auth_secret
        self.debug = debug

    def get_account_info(self, username: str) -> dict:
        """
        :param username: Localbitcoins user's username.
        :return: Localbitcoins public user information.
        """
        endpoint = f'/api/account_info/{username}/'
        return self.send_request(endpoint)

    def get_notifications(self) -> dict:
        """
        :return: User's notifications.
        """
        return self.send_request('/api/notifications/')

    def get_myself(self) -> dict:
        """
        :return: Information of the currently logged in user
        """
        return self.send_request('/api/myself/')

    def check_pin_code(self, code: str) -> dict:
        """
        Checks the given PIN code against the token owners currently active PIN code.
        You can use this method to ensure the person using the session is the legitimate user.
        :param code: PIN code.
        :return:
        """
        params = {'code': code}
        return self.send_request('/api/pincode/', method='post', params=params)

    def get_dashboard(self) -> dict:
        """
        :return: Open and active trades.
        """
        return self.send_request('/api/dashboard/')

    def get_dashboard_released(self) -> dict:
        """
        :return: released trades.
        """
        return self.send_request('/api/dashboard/released/')

    def get_dashboard_canceled(self) -> dict:
        """
        :return: canceled trades.
        """
        return self.send_request('/api/dashboard/canceled/')

    def get_dashboard_closed(self) -> dict:
        """
        :return: closed trades (both released and canceled).
        """
        return self.send_request('/api/dashboard/closed/')

    def contact_release(self, contact_id: str) -> dict:
        """
        Releases Bitcoin trades specified by ID {contact_id}.
        If the release was successful a message is returned on the data key.
        :param contact_id:
        :return:
        """
        endpoint = f'/api/contact_release/{contact_id}/'
        return self.send_request(endpoint, method='post')

    def contact_release_pin(self, contact_id: str, pincode: str) -> dict:
        """
        Releases Bitcoin trades specified by ID {contact_id}.
        If the current pincode is provided. If the release was successful a message is returned on the data key.
        :param contact_id:
        :param pincode:
        :return:
        """
        endpoint = f'/api/contact_release_pin/{contact_id}/'
        params = {'pincode': pincode}
        return self.send_request(endpoint, method='post', params=params)

    def get_contact_messages(self, contact_id: str) -> dict:
        """
        Returns all chat messages from the trade. Messages are on the message_list key
        :param contact_id:
        :return: all chat messages from the trade.
        """
        endpoint = f'/api/contact_messages/{contact_id}/'
        return self.send_request(endpoint)

    def mark_contact_as_paid(self, contact_id: str) -> dict:
        """
        Marks a trade as paid.
        """
        endpoint = f'/api/contact_mark_as_paid/{contact_id}/'
        return self.send_request(endpoint)

    def post_message_to_contact(self, contact_id: str, message: str) -> dict:
        """
        Post a message to contact.
        """
        endpoint = f'/api/contact_message_post/{contact_id}/'
        return self.send_request(endpoint, 'post', {'msg': message})

    def start_dispute(self, contact_id: str, topic: str = None) -> dict:
        """
        Starts a dispute on the specified trade ID if the requirements for starting the dispute has been fulfilled.
        You can provide a short (optional) description using topic.
        This helps customer support to deal with the problem.
        """
        if topic:
            topic = {'topic': topic}
        endpoint = f'/api/contact_dispute/{contact_id}/'
        return self.send_request(endpoint, 'post', topic)

    def cancel_contact(self, contact_id: str) -> dict:
        """
        Cancels the trade if the token owner is the Bitcoin buyer.
        Bitcoin sellers cannot cancel trades.
        """
        endpoint = f'/api/contact_cancel/{contact_id}/'
        return self.send_request(endpoint, 'post')

    def create_contact(self, contact_id: str, ammount: str, message: str = None) -> dict:
        """
        Attempts to start a Bitcoin trade from the specified advertisement ID.
        :param contact_id: Contact ID.
        :param ammount: A number in the advertisement's fiat currency.
        :param message: Message text.
        :return: The API URL to the newly created contact at actions.contact_url.
        """
        if message:
            params = {'ammount': ammount, 'message': message}
        else:
            params = {'ammount': ammount}

        endpoint = f'/api/contact_create/{contact_id}/'
        return self.send_request(endpoint, 'post', params)

    def get_contact_info(self, contact_id: str) -> dict:
        """
        :param contact_id: Contact ID.
        :return: Information about a single trade that the token owner is part in.
        """
        endpoint = f'/api/contact_info/{contact_id}/'
        return self.send_request(endpoint)

    def get_contacts_info(self, contacts) -> dict:
        """
        A maximum of 50 contacts can be requested at a time.
        The contacts are not returned in any particular order.
        :param contacts: comma-separated list of contact IDs that you want to access in bulk.
        """
        return self.send_request('/api/contact_info/', params={'contacts': contacts})

    def get_recent_messages(self) -> dict:
        """
        Messages are ordered by sending time, and the newest one is first.
        The list has same format as /api/contact_messages/, but each message has also contact_id field.
        :return: Maximum of 50 newest trade messages.
        """
        return self.send_request('/api/recent_messages/')

    def post_feedback_to_user(self, username: str, feedback: str, message: str = None) -> dict:
        """
        Gives feedback to user. Possible feedback values are: trust, positive, neutral, block, block_without_feedback.
        This is only possible to set if there is a trade between the token owner and the user specified in {username}
        that is canceled or released.
        You may also set feedback message using msg field with few exceptions.
        Feedback block_without_feedback clears the message and with block the message is mandatory.
        """
        if message:
            params = {'feedback': feedback, 'msg': message}
        else:
            params = {'feedback': feedback}
        endpoint = f'/api/feedback/{username}/'
        return self.send_request(endpoint, 'post', params)

    def get_wallet(self) -> dict:
        """
        Gets information about the token owner's wallet balance.
        """
        return self.send_request('/api/wallet/')

    def get_wallet_ballance(self) -> dict:
        """
        Same as /api/wallet/ above, but only returns the receiving_address and total fields.
        Use this instead if you don't care about transactions at the moment.
        """
        return self.send_request('/api/wallet-balance/')

    def wallet_send(self, ammount: str, address: str) -> dict:
        """
        Sends amount of bitcoins from the token owner's wallet to address.
        On success, the response returns a message indicating success.
        It is highly recommended to minimize the lifetime of access tokens with the money permission.
        Request /api/logout/ to make the current token expire instantly.
        """
        return self.send_request('/api/wallet-send/', 'post', {'ammount': ammount, 'address': address})

    def wallet_send_with_pin(self, ammount, address, pincode) -> dict:
        """
        As /api/wallet-send/, but needs the token owner's active PIN code to succeed.
        You can check if a PIN code is valid with the API request /api/pincode/.
        Security concern: To improve security, do not save the PIN code longer than the users session,
        a few minutes at most. If you are planning to save the PIN code please use the money permission instead.
        """
        params = {'ammount': ammount, 'address': address, 'pincode': pincode}
        return self.send_request('/api/wallet-send-pin/', 'post', params=params)

    def get_wallet_address(self) -> dict:
        """
        Returns an unused receiving address from the token owner's wallet.
        The address is returned in the address key of the response.
        Note that this API may keep returning the same (unused) address if requested repeatedly.
        """
        return self.send_request('/api/wallet-addr/', 'post')

    def logout(self):
        """
        Expires the current access token immediately.
        To get a new token afterwards, public apps will need to re-authenticate,
        confidential apps can turn in a refresh token.
        """
        return self.send_request('/api/logout/', 'post')

    def get_own_ads(self) -> dict:
        """
        Returns the token owner's all advertisements in the data key ad_list.
        If there are a lot of ads, the response will be paginated.
        You can filter the response using the optional arguments.
        """
        return self.send_request('/api/ads/', 'post')

    def edit_ad(self, ad_id: str, price_equation: str, lat: int, lon: int, bank_name: str,
                countrycode: str, opening_hours: list, msg: str, max_amount: int,
                track_max_amount: bool, visible: bool) -> dict:
        """
        This endpoint lets you edit an ad given the ad id and all the required fiends as designated by the API.
        If you just want to update the equation there is a better endpoint for that,
        this one takes a lot of LBC resources.
        """
        endpoint = f'/api/ad/{ad_id}/'
        params = {
            'lat': lat,
            'lon': lon,
            'bank_name': bank_name,
            'price_equation': price_equation,
            'countrycode': countrycode,
            'opening_hours': opening_hours,
            'msg': msg,
            'max_amount': max_amount,
            'track_max_amount': track_max_amount,
            'visible': visible
        }
        return self.send_request(endpoint, method='post', params=params)

    def mark_identity_verified(self, contact_id: str) -> dict:
        """
        Marks the identity of trade partner as verified.
        You must be the advertiser in this trade.
        """
        endpoint = f'/api/contact_mark_identified/{contact_id}/'
        return self.send_request(endpoint, 'post')

    def get_ad(self, ad_id: str) -> dict:
        """
        Returns information of single advertisement based on the ad ID, it returns the same fields as /api/ads/.
        If a valid advertisement ID is provided the API response returns the ad within a list structure.
        If the advertisement is not viewable an error is returned.
        """
        endpoint = f'/api/ad-get/{ad_id}/'
        return self.send_request(endpoint)

    def change_equation(self, ad_id: str, equation: str) -> dict:
        """
        Update price equation of an advertisement.
        If there are problems with new equation,
        the price and equation are not updated and advertisement remains visible.
        """
        endpoint = f'/api/ad-equation/{ad_id}/'
        return self.send_request(endpoint, 'post', {'price_equation': equation})

    def send_request(self, endpoint: str, method: str = 'get', params: dict = None) -> dict:
        """
        Sends request to endpoint with params.
        :param endpoint: Localbitcoins endpoint path.
        :param method: Request method.
        :param params: Request params.
        :return: Response from localbitcoins.net in JSON format.
        """
        params_encoded = ''
        if params:
            params_encoded = parse.urlencode(params)

            if method == 'get':
                params_encoded = '?' + params_encoded

        now = datetime.utcnow()
        epoch = datetime.utcfromtimestamp(0)
        delta = now - epoch
        nonce = int(delta.total_seconds() * 1000)

        message = str(nonce) + self.hmac_auth_key + endpoint + params_encoded
        signature = hmac.new(bytes(self.hmac_auth_secret, 'latin-1'), msg=bytes(message, 'latin-1'),
                             digestmod=hashlib.sha256).hexdigest().upper()

        headers = dict()
        headers['Apiauth-key'] = self.hmac_auth_key
        headers['Apiauth-Nonce'] = str(nonce)
        headers['Apiauth-Signature'] = signature
        if method == 'get':
            response = requests.get(self.lb_url + endpoint, headers=headers, params=params)
        else:
            response = requests.post(self.lb_url + endpoint, headers=headers, data=params)

        if self.debug:
            print('REQUEST: ' + self.lb_url + endpoint)
            print('PARAMS: ' + str(params))
            print('METHOD: ' + method)
            print('RESPONSE: ' + response.text)

        return json.loads(response.text)['data']
