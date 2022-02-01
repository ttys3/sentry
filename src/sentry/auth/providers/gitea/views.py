from __future__ import absolute_import, print_function

import logging
import os

from sentry.auth.view import AuthView, ConfigureView
from sentry.utils import json
from sentry import http
from sentry import options

from .constants import (
    ERR_INVALID_RESPONSE,
    ERR_INVALID_ORGANIZATION,
)

logger = logging.getLogger('sentry.auth.gitea')


class FetchUser(AuthView):
    def __init__(self, userinfo_url, version, allowed_organizations, *args, **kwargs):
        self.http = http.build_session()
        self.userinfo_url = userinfo_url
        self.version = version
        self.allowed_organizations = allowed_organizations
        super(FetchUser, self).__init__(*args, **kwargs)

    def dispatch(self, request, helper):
        logger.debug('gitea FetchUser.dispatch userinfo_url: %s' % self.userinfo_url)
        logger.debug('gitea FetchUser.dispatch allowed_organizations: %s' % self.allowed_organizations)

        data = helper.fetch_state('data')
        headers = {"Authorization": u'token %s' % data['access_token']}

        verify_ssl = True
        if os.environ.get('SENTRY_FORCE_DISABLE_SSL_VERIFY'):
            logger.warn('force disable ssl verify due to env var SENTRY_FORCE_DISABLE_SSL_VERIFY exists, url=%r',
                        self.userinfo_url)
            verify_ssl = False

        try:
            req = self.http.get(
                self.userinfo_url,
                headers=headers,
                verify=verify_ssl,
            )
        except Exception as exc:
            logger.error(u'Unable to get user info: %s' % exc, exc_info=True)
            return helper.error(ERR_INVALID_RESPONSE)
        if req.status_code < 200 or req.status_code >= 300:
            logger.error(u'Unable to get user info, invalid status code: %d' % req.status_code)
            return helper.error(ERR_INVALID_RESPONSE)

        try:
            payload = json.loads(req.content)
            logger.debug('gitea FetchUser.dispatch get user info response payload: %s' % payload)
        except Exception as exc:
            logger.error(u'Unable to decode payload: %s' % exc, exc_info=True)
            return helper.error(ERR_INVALID_RESPONSE)

        if not payload.get('sub'):
            logger.error('Missing sub in userinfo payload: %s' % payload)
            return helper.error(ERR_INVALID_RESPONSE)

        if not payload.get('email'):
            logger.error('Missing email in userinfo payload: %s' % payload)
            return helper.error(ERR_INVALID_RESPONSE)

        if not payload.get('preferred_username'):
            logger.error('Missing preferred_username in userinfo payload: %s' % payload)
            return helper.error(ERR_INVALID_RESPONSE)

        allowed = False
        if len(self.allowed_organizations) == 0:
            allowed = True
        else:
            # groups is null, payload.get('groups') will be None
            if payload.get('groups') and len(self.allowed_organizations) > 0:
                for group in payload.get('groups'):
                    if group in self.allowed_organizations:
                        allowed = True
                        break

        if not allowed:
            logger.error('Invalid organization, userinfo payload: %s' % payload)
            return helper.error(ERR_INVALID_ORGANIZATION % (payload.get('groups'),))

        helper.bind_state('user', payload)

        return helper.next_step()


class GiteaConfigureView(ConfigureView):
    def dispatch(self, request, organization, auth_provider):
        # config = auth_provider.config
        return self.render('sentry_auth_gitea/configure.html', {
            'base_url': options.get('auth-gitea.base-url') or 'warning: empty auth-gitea.base-url !!!',
            'allowed_organizations': options.get('auth-gitea.allowed-organizations') or 'allow any organizations',
            'sentry_url_prefix': options.get('system.url-prefix'),
        })


def extract_domain(email):
    return email.rsplit('@', 1)[-1]
