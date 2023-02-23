import json
import logging
import os
# import smtplib
import time
import urllib
# from email.mime.text import MIMEText
import requests


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# logging_file_name = os.path.join(ROOT_DIR, f'{time.strftime("%Y-%m-%d-%H-%M-%S")}debug.log')
#
# logging.basicConfig(
#     filename=logging_file_name,
#     level=print,
#     format="%(asctime)s:%(levelname)s:%(message)s", filemode='w'
# )


def get_all_coupons(store_id, access_token):
    headers = {
        'authority': 'www.vons.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'x-swy_version': '1.1',
        'dnt': '1',
        'x-swy_banner': 'vons',
        'x-swy-application-type': 'web',
        'sec-ch-ua-mobile': '?0',
        'authorization': f'Bearer {access_token}',
        'content-type': 'application/vnd.safeway.v2+json',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'x-swy_api_key': 'emjou',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.vons.com/justforu/coupons-deals.html',
        'accept-language': 'en-US,en;q=0.9,es-419;q=0.8,es;q=0.7',
    }

    params = (
        ('storeId', '2090'),
        ('rand', '482754'),
    )

    response = requests.get('https://www.vons.com/abs/pub/xapi/offers/companiongalleryoffer', headers=headers,
                            params=params)
    print(f'[Request]: get coupons status code: {response.status_code}')
    return response.json()['companionGalleryOffer']


def add_coupon_by_id(offer_id, store_id, offer_type, access_token):
    headers = {
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'x-swy_banner': 'vons',
        'swy_sso_token': f'{access_token}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'referer': 'https://www.vons.com/justforu/coupons-deals.html?r=https%3A%2F%2Fwww.vons.com%2Fjustforu%2Fcoupons-deals.html',
        'accept-language': 'en-US,en;q=0.9,es-419;q=0.8,es;q=0.7',
    }

    params = (
        ('storeId', store_id),
    )

    json_data = {
        'items': [
            {
                'clipType': 'C',
                'itemId': f'{offer_id}',
                'itemType': offer_type,
            },
            {
                'clipType': 'L',
                'itemId': f'{offer_id}',
                'itemType': f'{offer_type}',
            },
        ],
    }

    response = requests.post('https://www.vons.com/abs/pub/web/j4u/api/offers/clip', headers=headers, params=params,
                             json=json_data)

    print(f'[Request]: Add coupon status code: {response.status_code}')

    return response.json()


"""
AUTHENTICATION: 
Get the sessionToken by submitting username and password. SessionToken is a short token that 
represents the user has been authenticated via okta's sign-in API as opposed to Okta's sign-in UI page. 
"""


def get_session_token(username, password):
    headers = {
        'authority': 'albertsons.okta.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'x-okta-user-agent-extended': 'okta-auth-js-1.15.0',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'dnt': '1',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://www.safeway.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.safeway.com/',
        'accept-language': 'en-US,en;q=0.9,es-419;q=0.8,es;q=0.7',
        'cookie': 'DT=DI053aFLGcdTNKzIDnCydfhHw',
    }

    json_data = {
        'username': f'{username}',
        'password': f'{password}',
    }

    response = requests.post('https://albertsons.okta.com/api/v1/authn', headers=headers, json=json_data)
    response.raise_for_status()

    print(f'[Request]: Login status code: {response.status_code}')
    return response.json()['sessionToken']


"""AUTHORIZATION: First to get an auth code, submit the sessionToken and Safeway's SSO url as the 
redirect_uri to Okta's authorization url. Okta will respond with the redirection_uri containing the auth code. As a 
note, we disable redirects in the request call because we'll get an HTML page instead of a location. Second, 
make a get request with the redirection url containing the auth code. On their server, Safeway will exchange this 
code for an access token using a secret key. The response will have the access token in cookies. Third, the access 
token in the cookies is Json object that is Url encoded. We have to decode this to get the access token. """


def get_access_token(session_token):
    headers = {
        'authority': 'albertsons.okta.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.safeway.com/',
        'accept-language': 'en-US,en;q=0.9,es-419;q=0.8,es;q=0.7',
        'cookie': '_okta_original_attribution={%22utm_page%22:%22/%22%2C%22utm_date%22:%2203/09/2022%22}; DT=DI053aFLGcdTNKzIDnCydfhHw; t=default; JSESSIONID=F0A3F8D245BD10C284BCF4F0FFB8DE61',
    }

    params = (
        ('client_id', '0oap6ku01XJqIRdl42p6'),
        ('redirect_uri', 'https://www.safeway.com/bin/safeway/unified/sso/authorize'),
        ('response_type', 'code'),
        ('response_mode', 'query'),
        ('state', 'mucho-religion-hermon-girish'),
        ('nonce', 'UXjlnZSbw9JhbLc5uy3A9KieH8USBOL58UlJzaAKIMQjyx48nWrK7TOnRl1C2q8e'),
        ('prompt', 'none'),
        ('sessionToken', f'{session_token}'),
        ('scope', 'openid profile email offline_access used_credentials'),
    )

    auth_code_response = requests.get('https://albertsons.okta.com/oauth2/ausp6soxrIyPrm8rS2p6/v1/authorize',
                                      headers=headers,
                                      params=params, allow_redirects=False)
    location = auth_code_response.headers['Location']

    access_token_response = requests.get(location, allow_redirects=False)
    print(f'[Request]: Get access token status code: {access_token_response.status_code}')

    encoded_json_token_cookie = access_token_response.cookies.get_dict()['SWY_SHARED_SESSION']
    json_token_cookie = parse_url_encoded_json(encoded_json_token_cookie)
    return json_token_cookie['accessToken']


def parse_url_encoded_json(encoded):
    unencoded = urllib.parse.unquote(encoded)
    return json.loads(unencoded)


def get_json_from_file(file_name):
    abs_file_name = os.path.join(ROOT_DIR, file_name)
    f = open(abs_file_name, encoding='utf-8')
    return json.load(f)


def get_login_data_from_config_json(config_json):
    return config_json['loginData']


def get_email_login_data_from_config_json(config_json):
    return config_json['emailLoginData']


def get_email_recipient(config_json):
    return config_json['emailRecipient']


def check_coupon_clipped(coupon):
    return coupon['status'] == 'C'


def get_coupon_id(coupon):
    return coupon['offerId']


def get_coupon_type(coupon):
    return coupon['offerPgm']


def return_vons_names(username, password):
    STORE_ID = 2090
    try:
        session_token = get_session_token(username, password)
        access_token = get_access_token(session_token)
        coupons = get_all_coupons(store_id=STORE_ID, access_token=access_token)
        coupons_names = []
        for key, coupon in coupons.items():
            coupons_names.append(coupon['name'])
        return coupons_names
    except:
        print("Error occurred in main block.")


def clip_vons(username, password):
    STORE_ID = 2090
    try:
        session_token = get_session_token(username, password)
        access_token = get_access_token(session_token)
        coupons = get_all_coupons(store_id=STORE_ID, access_token=access_token)
        for key, coupon in coupons.items():
            if not check_coupon_clipped(coupon):
                coupon_id = get_coupon_id(coupon)
                coupon_type = get_coupon_type(coupon)
                add_coupon_by_id(offer_id=coupon_id, store_id=STORE_ID, offer_type=coupon_type,
                                 access_token=access_token)
                print(f'Coupon with id of {coupon_id} added!')
                time.sleep(0.6)
        print('Completed')
    except:
        print("Error occurred in main block.")
