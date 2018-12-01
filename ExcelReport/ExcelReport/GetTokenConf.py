from .Office365Conf import *


class GetTokenConf:
    @staticmethod
    def get_token_body(code):
        formatter = "client_id={}&scope={}" \
                    "&code={}&redirect_uri={}" \
                    "&grant_type=authorization_code" \
                    "&client_secret={}"
        body = formatter.format(CLIENT_ID, " ".join(RAW_SCOPE),
                               code, REDIRECT_URI, CLIENT_SECRET)
        # url = dict()
        # url['client_id'] = CLIENT_ID
        # url['scope'] = " ".join(RAW_SCOPE)
        # url['code'] = code
        # url['redirect_uri'] = REDIRECT_URI
        # url['grant_type'] = "authorization_code"
        # url['client_secret'] = CLIENT_SECRET
        return body

    @staticmethod
    def get_token_url():
        return Relative_token_url
