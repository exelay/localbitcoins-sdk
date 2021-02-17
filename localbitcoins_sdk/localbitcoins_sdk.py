import hmac
import json
import hashlib
from urllib import parse
from datetime import datetime

import requests


class LocalBitcoins:
    baseurl = 'https://localbitcoins.com'

    def __init__(self, hmac_auth_key, hmac_auth_secret, debug=False):
        self.hmac_auth_key = hmac_auth_key
        self.hmac_auth_secret = hmac_auth_secret
        self.debug = debug

    def get_account_info(self, username):
        """
        Returns public user profile information
        """
        return self.send_request('/api/account_info/' + username + '/', '', 'get')

    def get_notifications(self):
        """
        Returns recent notifications.
        """
        return self.send_request('/api/notifications/', '', 'get')

    def get_myself(self):
        """
        Return the information of the currently logged in user (the owner of authentication token).
        """
        return self.send_request('/api/myself/', '', 'get')

    def check_pin_code(self, code):
        """
        Checks the given PIN code against the user's currently active PIN code.
        You can use this method to ensure the person using the session is the legitimate user.
        """
        return self.send_request('/api/pincode/', {'code': code}, 'post')

    def get_dashboard(self):
        """
        Return open and active contacts
        """
        return self.send_request('/api/dashboard/', '', 'get')

    def get_dashboard_released(self):
        """
        Return released (successful) contacts
        """
        return self.send_request('/api/dashboard/released/', '', 'get')

    def get_dashboard_canceled(self):
        """
        Return canceled contacts
        """
        return self.send_request('/api/dashboard/canceled/', '', 'get')

    def get_dashboard_closed(self):
        """
        Return closed contacts, both released and canceled
        """
        return self.send_request('/api/dashboard/closed/', '', 'get')

    def contact_release(self, contact_id):
        """
        Releases the escrow of contact specified by ID {contact_id}.
        On success there's a complimentary message on the data key.
        """
        return self.send_request('/api/contact_release/' + contact_id + '/', '', 'post')

    def contact_release_pin(self, contact_id, pincode):
        """
        Releases the escrow of contact specified by ID {contact_id}.
        On success there's a complimentary message on the data key.
        """
        return self.send_request('/api/contact_release_pin/' + contact_id + '/', {'pincode': pincode}, 'post')

    def get_contact_messages(self, contact_id):
        """
        Reads all messaging from the contact. Messages are on the message_list key.
        On success there's a complimentary message on the data key.
        attachment_* fields exist only if there is an attachment.
        """
        return self.send_request('/api/contact_messages/' + contact_id + '/', '', 'get')

    def mark_contact_as_paid(self, contact_id):
        """
        Marks a contact as paid.
        It is recommended to access this API through /api/online_buy_contacts/ entries' action key.
        """
        return self.send_request('/api/contact_mark_as_paid/' + contact_id + '/', '', 'get')

    def post_message_to_contact(self, contact_id, message, document=None):
        """
        Post a message to contact
        """
        return self.send_request('/api/contact_message_post/' + contact_id + '/', {'msg': message}, 'post')

    def start_dispute(self, contact_id, topic=None):
        """
        Starts a dispute with the contact, if possible.
        You can provide a short description using topic. This helps support to deal with the problem.
        """
        topic = ''
        if topic != None:
            topic = {'topic': topic}
        return self.send_request('/api/contact_dispute/' + contact_id + '/', topic, 'post')

    def cancel_contact(self, contact_id):
        """
        Cancels the contact, if possible
        """
        return self.send_request('/api/contact_cancel/' + contact_id + '/', '', 'post')

    def fund_contact(self, contact_id):
        """
        Attempts to fund an unfunded local contact from the seller's wallet.
        """
        return self.send_request('/api/contact_fund/' + contact_id + '/', '', 'post')

    def create_contact(self, contact_id, ammount, message=None):
        """
        Attempts to create a contact to trade bitcoins.
        Amount is a number in the advertisement's fiat currency.
        Returns the API URL to the newly created contact at actions.contact_url.
        Whether the contact was able to be funded automatically is indicated at data.funded.
        Only non-floating LOCAL_SELL may return unfunded, all other trade types either fund or fail.
        """
        post = ''
        if message == None:
            post = {'ammount': ammount}
        else:
            post = {'ammount': ammount, 'message': message}
        return self.send_request('/api/contact_create/' + contact_id + '/', post, 'post')

    def get_contact_info(self, contact_id):
        """
        Gets information about a single contact you are involved in. Same fields as in /api/contacts/.
        """
        return self.send_request('/api/contact_info/' + contact_id + '/', '', 'get')

    def get_contacts_info(self, contacts):
        """
        contacts is a comma-separated list of contact IDs that you want to access in bulk.
        The token owner needs to be either a buyer or seller in the contacts,
        contacts that do not pass this check are simply not returned.
        A maximum of 50 contacts can be requested at a time.
        The contacts are not returned in any particular order.
        """
        return self.send_request('/api/contact_info/', {'contacts': contacts}, 'get')

    def get_recent_messages(self):
        """
        Returns maximum of 50 newest trade messages.
        Messages are ordered by sending time, and the newest one is first.
        The list has same format as /api/contact_messages/, but each message has also contact_id field.
        """
        return self.send_request('/api/recent_messages/', '', 'get')

    def post_feedback_to_user(self, username, feedback, message=None):
        """
        Gives feedback to user.
        Possible feedback values are: trust, positive, neutral, block, block_without_feedback as strings.
        You may also set feedback message field with few exceptions.
        Feedback block_without_feedback clears the message and with block the message is mandatory.
        """
        post = {'feedback': feedback}
        if message != None:
            post = {'feedback': feedback, 'msg': message}
        return self.send_request('/api/feedback/' + username + '/', post, 'post')

    def get_wallet(self):
        """
        Gets information about the token owner's wallet balance.
        """
        return self.send_request('/api/wallet/', '', 'get')

    def get_wallet_ballance(self):
        """
        Same as /api/wallet/ above, but only returns the message, receiving_address_list and total fields.
        (There's also a receiving_address_count but it is always 1:
        only the latest receiving address is ever returned by this call.)
        Use this instead if you don't care about transactions at the moment.
        """
        return self.send_request('/api/wallet-balance/', '', 'get')

    def wallet_send(self, ammount, address):
        """
        Sends amount bitcoins from the token owner's wallet to address.
        Note that this API requires its own API permission called Money.
        On success, this API returns just a message indicating success.
        It is highly recommended to minimize the lifetime of access tokens with the money permission.
        Call /api/logout/ to make the current token expire instantly.
        """
        return self.send_request('/api/wallet-send/', {'ammount': ammount, 'address': address}, 'post')

    def wallet_send_with_pin(self, ammount, address, pincode):
        """
        As above, but needs the token owner's active PIN code to succeed.
        Look before you leap. You can check if a PIN code is valid without attempting a send with /api/pincode/.
        Security concern: To get any security beyond the above API,
        do not retain the PIN code beyond a reasonable user session, a few minutes at most.
        If you are planning to save the PIN code anyway,
        please save some headache and get the real no-pin-required money permission instead.
        """
        return self.send_request('/api/wallet-send-pin/', {'ammount': ammount, 'address': address, 'pincode': pincode},
                                'post')

    def get_wallet_address(self):
        """
        Gets an unused receiving address for the token owner's wallet,
        its address given in the address key of the response.
        Note that this API may keep returning the same (unused) address if called repeatedly.
        """
        return self.send_request('/api/wallet-addr/', '', 'post')

    def logout(self):
        """
        Expires the current access token immediately.
        To get a new token afterwards, public apps will need to reauthenticate,
        confidential apps can turn in a refresh token.
        """
        return self.send_request('/api/logout/', '', 'post')

    def get_own_ads(self):
        """
        Lists the token owner's all ads on the data key ad_list, optionally filtered. If there's a lot of ads,
        the listing will be paginated.
        Refer to the ad editing pages for the field meanings. List item structure is like so:
        """
        return self.send_request('/api/ads/', '', 'post')

    def edit_ad(self, ad_id, lat, bank_name, price_equation, lon, countrycode, opening_hours, msg, max_amount,
               track_max_amount, visible):
        """
        This endpoint lets you edit an ad given the ad id and all the required fiends as designated by the API.
        If you just want to update the equation there is a better endpoint for that,
        this one takes a lot of LBC resources.
        """
        return self.send_request('/api/ad/' + ad_id + '/',
                                 {'lat': lat, 'bank_name': bank_name, 'price_equation': price_equation, 'lon': lon,
                                 'countrycode': countrycode, 'opening_hours': opening_hours, 'msg': msg,
                                 'max_amount': max_amount, 'track_max_amount': track_max_amount, 'visible': visible},
                                'post')

    def new_invoice(self, currency, amount, description):
        """
        Creates a new invoice under the LBC merchant services page.
        """
        return self.send_request('/api/merchant/new_invoice/',
                                 {'currency': currency, 'amount': amount, 'description': description, }, 'post')

    def mark_identity_verified(self, contact_id):
        """
        Marks a users id as verified based on an open contact id.
        """
        return self.send_request('/api/contact_mark_identified/' + contact_id + '/', '', 'post')

    def get_ad(self, ad_id):
        """
        Get all the details of an ad based on its ID, can be any ad.
        """
        return self.send_request('/api/ad-get/' + ad_id + '/', '', 'get')

    def change_equation(self, ad_id, equation):
        """
        Change an ad's pricing equation to something else.
        """
        return self.send_request('/api/ad-equation/{ad_id}/'.format(ad_id=ad_id), {'price_equation': equation}, 'post')

    def send_request(self, endpoint, params, method):
        """
        Main driver.
        """
        params_encoded = ''
        if params != '':
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

        headers = {}
        headers['Apiauth-key'] = self.hmac_auth_key
        headers['Apiauth-Nonce'] = str(nonce)
        headers['Apiauth-Signature'] = signature
        if method == 'get':
            response = requests.get(self.baseurl + endpoint, headers=headers, params=params)
        else:
            response = requests.post(self.baseurl + endpoint, headers=headers, data=params)

        if self.debug == True:
            print('REQUEST: ' + self.baseurl + endpoint)
            print('PARAMS: ' + str(params))
            print('METHOD: ' + method)
            print('RESPONSE: ' + response.text)

        return json.loads(response.text)['data']
