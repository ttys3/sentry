from __future__ import absolute_import, print_function

from django.conf import settings


AUTHORIZE_URL = 'https://git.nomad.lan/login/oauth/authorize'

ACCESS_TOKEN_URL = 'https://git.nomad.lan/login/oauth/access_token'

USERINFO_URL = 'https://git.nomad.lan/login/oauth/userinfo'

ERR_INVALID_DOMAIN = 'The domain for your Gitea account (%s) is not allowed to authenticate with this provider.'

ERR_INVALID_RESPONSE = 'Unable to fetch user information from Gitea.  Please check the log.'

SCOPE = 'email'

DOMAIN_BLOCKLIST = frozenset(getattr(settings, 'GOOGLE_DOMAIN_BLOCKLIST', ['gmail.com']) or [])

DATA_VERSION = '1'
