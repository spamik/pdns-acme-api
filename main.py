from fastapi import FastAPI, Request
import requests

app = FastAPI()
PDNS_URL = 'http://172.16.14.28:8081'
PDNS_ZONE_URL = '/api/v1/servers/localhost/zones'
HEADERS = {
    'X-API-Key': '0123456789ABCDEF'
}


@app.get(PDNS_ZONE_URL)
async def get_zones():
    response = requests.get(PDNS_URL + PDNS_ZONE_URL, headers=HEADERS)
    return response.content


@app.patch(PDNS_ZONE_URL + '/{zone}')
async def patch_zone(request: Request, zone: str):
    response = requests.patch(PDNS_ZONE_URL + '/{zone}', headers=HEADERS, data=request.json())
    return response.content
