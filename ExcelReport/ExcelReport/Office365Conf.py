import urllib.parse

ms_site_login_url = "https://login.microsoftonline.com"
Office365_auth_url = "{}/common/oauth2/v2.0/authorize?".format(ms_site_login_url)
Relative_token_url = "/common/oauth2/v2.0/token"
Office365_token_url = "{}{}".format(ms_site_login_url, Relative_token_url)
CLIENT_ID = "ecba77e2-0392-46b1-827d-67c78567511f"

redirect_url = "https://localhost:5050/auth/"
REDIRECT_URI = urllib.parse.urlencode({"url":redirect_url})[4:]

RAW_SCOPE = ["Files.Read", "Files.Read.All", "Files.ReadWrite", "Files.ReadWrite.All",
         "offline_access", "openid", "profile"]
SCOPE = "%20".join(RAW_SCOPE)

CLIENT_SECRET = "ilgbeaETBDS42[vBI328|=%"

