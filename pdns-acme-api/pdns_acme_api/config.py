import os

PDNS_URL = os.environ.get('PDNS_ADDRESS')
PDNS_ZONE_URL = os.environ.get('PDNS_URL', '/api/v1/servers/localhost/zones')
HEADERS = {
    'X-API-Key': os.environ.get('PDNS_TOKEN')
}
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'changemenow')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////var/lib/pdns-acme-api/pdns-acme-api.db')
