from __future__ import absolute_import, print_function

from sentry import options
from sentry.auth.provider import MigratingIdentityId
from sentry.auth.providers.oauth2 import (
    OAuth2Callback, OAuth2Provider, OAuth2Login
)

from .constants import (
    AUTHORIZE_ENDPOINT, ACCESS_TOKEN_ENDPOINT, USERINFO_ENDPOINT, DATA_VERSION, SCOPE
)
from .views import FetchUser, GiteaConfigureView

import logging

logger = logging.getLogger('sentry.auth.gitea')


class GiteaOAuth2Login(OAuth2Login):
    scope = SCOPE

    def __init__(self, client_id, authorize_url):
        logger.info('GiteaOAuth2Login init, client_id=%s authorize_url=%s' % (client_id, authorize_url))
        super(GiteaOAuth2Login, self).__init__(client_id=client_id, authorize_url=authorize_url)

    def get_authorize_params(self, state, redirect_uri):
        params = super(GiteaOAuth2Login, self).get_authorize_params(
            state, redirect_uri
        )
        # TODO(dcramer): ideally we could look at the current resulting state
        # when an existing auth happens, and if they're missing a refresh_token
        # we should re-prompt them a second time with ``approval_prompt=force``
        params['approval_prompt'] = 'force'
        params['access_type'] = 'offline'
        return params


class GiteaOAuth2Provider(OAuth2Provider):
    name = 'Gitea'

    def __init__(self, version=None, **config):
        self.version = version
        super(GiteaOAuth2Provider, self).__init__(**config)

    @staticmethod
    def get_base_url():
        return options.get('auth-gitea.base-url')

    def get_authorize_url(self):
        return '%s%s' % (self.get_base_url(), AUTHORIZE_ENDPOINT)

    def get_access_token_url(self):
        return '%s%s' % (self.get_base_url(), ACCESS_TOKEN_ENDPOINT)

    def get_userinfo_url(self):
        return '%s%s' % (self.get_base_url(), USERINFO_ENDPOINT)

    @staticmethod
    def get_allowed_organizations():
        orgs = options.get('auth-gitea.allowed-organizations')
        if not orgs:
            return []
        else:
            return orgs.split(',')

    def get_client_id(self):
        return options.get('auth-gitea.client-id')

    def get_client_secret(self):
        return options.get('auth-gitea.client-secret')

    def get_configure_view(self):
        return GiteaConfigureView.as_view()

    def get_auth_pipeline(self):
        return [
            GiteaOAuth2Login(client_id=self.get_client_id(), authorize_url=self.get_authorize_url()),
            OAuth2Callback(
                access_token_url=self.get_access_token_url(),
                client_id=self.get_client_id(),
                client_secret=self.get_client_secret(),
            ),
            FetchUser(
                userinfo_url=self.get_userinfo_url(),
                version=self.version,
                allowed_organizations=self.get_allowed_organizations(),
            ),
        ]

    def get_refresh_token_url(self):
        return self.get_access_token_url()

    def build_config(self, state):
        logger.info('gitea build_config called: base_url=%s', self.get_base_url())
        return {
            'base_url': self.get_base_url(),
            'allowed_organizations': self.get_allowed_organizations(),
            'version': DATA_VERSION,
        }

    def build_identity(self, state):
        """
        Return a mapping containing the identity information.
        """

        # https://github.com/go-gitea/gitea/blob/7f2530e004c9908f9ee18b4060c8d4837a72f93b/routers/web/auth/oauth.go#L259
        # see type userInfoResponse struct
        # if user not in any organizations, groups will be null
        #
        # data.user =>
        # {
        #     "sub": "1",
        #     "name": "MyDisplayName",
        #     "preferred_username": "ttys3",
        #     "email": "admin@example.com",
        #     "picture": "https://git.nomad.lan/avatar/e64c7d89f26bd1972efa854d13d7dd61",
        #     "groups": [
        #         "devops",
        #         "devops:owners"
        #     ]
        # }

        data = state['data']
        user_data = state['user']

        logger.info(u'gitea build_identity got state.data: %s' % data)
        logger.info(u'gitea build_identity got state.user: %s' % user_data)

        # nickname
        nickname = user_data['name']
        if not nickname:
            nickname = user_data['preferred_username']
        if not nickname:
            nickname = user_data['email']

        # see src/sentry/auth/provider.py build_identity()
        # The ``email`` and ``id`` keys are required, ``name`` is optional.
        user_id = MigratingIdentityId(id=user_data['sub'], legacy_id=user_data['email'])
        return {
            'id': user_id,
            'email': user_data['email'],
            'name': nickname,
            'data': self.get_oauth_data(data),
            'email_verified': False,
        }
