import os

#PDNS_URL = 'http://172.16.14.28:8082'
PDNS_URL = os.environ.get('PDNS_ADDRESS')
PDNS_ZONE_URL = os.environ.get('PDNS_URL', '/api/v1/servers/localhost/zones')
HEADERS = {
    'X-API-Key': os.environ.get('PDNS_TOKEN')
}
