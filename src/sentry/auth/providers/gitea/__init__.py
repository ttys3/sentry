from __future__ import absolute_import

from sentry import auth, options

from .provider import GiteaOAuth2Provider

auth.register('gitea', GiteaOAuth2Provider)

options.register(
    'auth-gitea.base-url',
    flags=options.FLAG_ALLOW_EMPTY | options.FLAG_PRIORITIZE_DISK,
)
options.register(
    'auth-gitea.client-id',
    flags=options.FLAG_ALLOW_EMPTY | options.FLAG_PRIORITIZE_DISK,
)
options.register(
    'auth-gitea.client-secret',
    flags=options.FLAG_ALLOW_EMPTY | options.FLAG_PRIORITIZE_DISK,
)
options.register(
    'auth-gitea.allowed-organizations',
    flags=options.FLAG_ALLOW_EMPTY | options.FLAG_PRIORITIZE_DISK,
)
