"""Docstring for file."""
from django_tenants.utils import get_tenant_domain_model
from django.db import connection


def set_tenant(request):
    """Docstring for set_tenant."""
    domain_model = get_tenant_domain_model()
    hostname = None
    try:
        hostname = request.user.restaurant.schema_name
        domain = domain_model.objects.select_related(
            'tenant').get(domain=hostname)

        tenant = domain.tenant
        tenant.domain_url = hostname

        # request.tenant = tenant
        connection.set_tenant(tenant)
    except domain_model.DoesNotExist:
        print('No tenant for hostname "%s"' % hostname)
    except Exception as e:
        print("message from tenant => "+str(e))

    return True


def set_tenant_from_user(user):
    """Docstring for set_tenant_from_user."""
    domain_model = get_tenant_domain_model()
    hostname = None
    try:
        hostname = user.restaurant.schema_name
        domain = domain_model.objects.select_related(
            'tenant').get(domain=hostname)

        tenant = domain.tenant
        tenant.domain_url = hostname

        # request.tenant = tenant
        connection.set_tenant(tenant)
    except domain_model.DoesNotExist:
        print('No tenant for hostname "%s"' % hostname)
    except Exception as e:
        print("message from tenant => "+str(e))

    return True


def set_tenant_from_restaurant(restaurant):
    """Docstring for set_tenant_from_restaurant."""
    domain_model = get_tenant_domain_model()
    hostname = None
    try:
        hostname = restaurant.schema_name
        domain = domain_model.objects.select_related(
            'tenant').get(domain=hostname)

        tenant = domain.tenant
        tenant.domain_url = hostname

        connection.set_tenant(tenant)
    except domain_model.DoesNotExist:
        print('No tenant for hostname "%s"' % hostname)
    except Exception as e:
        print("message from tenant => "+str(e))

    return True
