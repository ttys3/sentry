from __future__ import absolute_import, print_function

import logging


from .constants import (
    USERINFO_URL
)
from sentry.auth.view import AuthView, ConfigureView
from sentry.utils import json
from sentry import http

from .constants import (
    DOMAIN_BLOCKLIST, ERR_INVALID_DOMAIN, ERR_INVALID_RESPONSE,
)
from .utils import urlsafe_b64decode

logger = logging.getLogger('sentry.auth.gitea')


class FetchUser(AuthView):
    def __init__(self, domains, version, *args, **kwargs):
        self.http = http.build_session()
        self.domains = domains
        self.version = version
        super(FetchUser, self).__init__(*args, **kwargs)

    def dispatch(self, request, helper):
        data = helper.fetch_state('data')

        headers = {"Authorization": u'token %s' % data['access_token']}

        try:
            req = self.http.get(
                USERINFO_URL,
                headers=headers,
                verify=False,
            )
        except Exception as exc:
            logger.error(u'Unable to get user info: %s' % exc, exc_info=True)
            return helper.error(ERR_INVALID_RESPONSE)
        if req.status_code < 200 or req.status_code >= 300:
            logger.error(u'Unable to get user info, invalid status code: %d' % req.status_code)
            return helper.error(ERR_INVALID_RESPONSE)

        try:
            payload = json.loads(req.content)
        except Exception as exc:
            logger.error(u'Unable to decode payload: %s' % exc, exc_info=True)
            return helper.error(ERR_INVALID_RESPONSE)

        if not payload.get('email'):
            logger.error('Missing email in userinfo payload: %s' % payload)
            return helper.error(ERR_INVALID_RESPONSE)

        helper.bind_state('id', payload.get('sub'))
        helper.bind_state('email', payload.get('email'))
        helper.bind_state('name', payload.get('name'))
        helper.bind_state('user', payload)

        return helper.next_step()


class GiteaConfigureView(ConfigureView):
    def dispatch(self, request, organization, auth_provider):
        config = auth_provider.config
        if config.get('domain'):
            domains = [config['domain']]
        else:
            domains = config.get('domains')
        return self.render('sentry_auth_gitea/configure.html', {
            'domains': domains or [],
        })


def extract_domain(email):
    return email.rsplit('@', 1)[-1]
