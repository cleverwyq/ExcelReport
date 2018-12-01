from .Office365Conf import *


class RedirectConf:

    @staticmethod
    def get_redirect_url():
        formatter = "{}client_id={}&response_type=code&redirect_uri={}" \
                 "&response_mode=query&scope={}&state=12345"
        _redirect_url = formatter.format(Office365_auth_url,
                                        CLIENT_ID,
                                        REDIRECT_URI,
                                        SCOPE)

        return _redirect_url
