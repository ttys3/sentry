from __future__ import absolute_import, print_function

# see https://docs.gitea.io/en-us/oauth2-provider/#endpoints

AUTHORIZE_ENDPOINT = '/login/oauth/authorize'

ACCESS_TOKEN_ENDPOINT = '/login/oauth/access_token'

USERINFO_ENDPOINT = '/login/oauth/userinfo'

ERR_INVALID_RESPONSE = 'Unable to fetch user information from Gitea.  Please check the log.'

ERR_INVALID_ORGANIZATION = 'The organization for your Gitea account (%s) is not allowed to authenticate with this provider.'

SCOPE = 'email'

DATA_VERSION = '1'
