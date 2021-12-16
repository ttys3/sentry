from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.bases.organization import OrganizationEndpoint
from sentry.models import Organization
from sentry.plugins.base import bindings


class OrganizationConfigRepositoriesEndpoint(OrganizationEndpoint):
    def get(self, request: Request, organization: Organization) -> Response:
        provider_bindings = bindings.get("repository.provider")
        providers = []
        for provider_id in provider_bindings:
            provider = provider_bindings.get(provider_id)(id=provider_id)
            # TODO(jess): figure out better way to exclude this
            if provider_id == "github_apps":
                continue
            providers.append(
                {"id": provider_id, "name": provider.name, "config": provider.get_config()}
            )

        return Response({"providers": providers})
