from fastapi import FastAPI, Request
import requests
import json

app = FastAPI()
PDNS_URL = 'http://172.16.14.28:8082'
PDNS_ZONE_URL = '/api/v1/servers/localhost/zones'
HEADERS = {
    'X-API-Key': '0123456789ABCDEF'
}


@app.get(PDNS_ZONE_URL)
async def get_zones():
    response = requests.get(PDNS_URL + PDNS_ZONE_URL, headers=HEADERS)
    return json.loads(response.content)


@app.patch(PDNS_ZONE_URL + '/{zone}')
async def patch_zone(request: Request, zone: str):
    response = requests.patch(PDNS_ZONE_URL + '/{zone}', headers=HEADERS, data=request.json())
    return json.loads(response.content)
