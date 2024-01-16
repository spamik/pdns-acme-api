from http import HTTPStatus
from fastapi import FastAPI, Request, Response, APIRouter
import requests
import json

from . import models
from .database import SessionLocal, engine
from sqlalchemy import Session

models.Base.metadata.create_all(bind=engine)

router = APIRouter()
PDNS_URL = 'http://172.16.14.28:8082'
PDNS_ZONE_URL = '/api/v1/servers/localhost/zones'
HEADERS = {
    'X-API-Key': '0123456789ABCDEF'
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(PDNS_ZONE_URL)
async def get_zones():
    response = requests.get(PDNS_URL + PDNS_ZONE_URL, headers=HEADERS)
    return json.loads(response.content)


@router.api_route(PDNS_ZONE_URL + '/{zone}', methods=['GET', 'PATCH'])
async def patch_zone(request: Request, api_response: Response, zone: str):
    request_f = requests.get
    data = None
    if request.method == 'PATCH':
        request_f = requests.patch
        data = await request.json()
    response = request_f(PDNS_URL + PDNS_ZONE_URL + '/' + zone, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 204:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    return json.loads(response.content)


@router.put(PDNS_ZONE_URL + '/{zone}/notify')
async def notify_zone(zone: str):
    response = requests.get(PDNS_URL + PDNS_ZONE_URL + '/' + zone + '/.notify', headers=HEADERS)
    return response.content


@router.get('/acme-api/hosts')
async def list_hosts(db: Session):
    return db.query(models.Host).all()
