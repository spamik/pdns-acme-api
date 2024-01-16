from http import HTTPStatus
from fastapi import FastAPI, Request, Response, APIRouter, Depends, HTTPException, Header
import requests
import json

from . import models, schemas, crud
from .database import SessionLocal, engine, get_db
from .tokenauth import validate_token, filter_rrsets, authorize_change_request
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

router = APIRouter()
PDNS_URL = 'http://172.16.14.28:8082'
PDNS_ZONE_URL = '/api/v1/servers/localhost/zones'
HEADERS = {
    'X-API-Key': '0123456789ABCDEF'
}


@router.get(PDNS_ZONE_URL, dependencies=[Depends(validate_token)])
async def get_zones():
    response = requests.get(PDNS_URL + PDNS_ZONE_URL, headers=HEADERS)
    return json.loads(response.content)


@router.api_route(PDNS_ZONE_URL + '/{zone}', methods=['GET', 'PATCH'], dependencies=[Depends(validate_token)])
async def patch_zone(request: Request, zone: str, x_api_key: str = Header(), db: Session = Depends(get_db)):
    request_f = requests.get
    host_domains = crud.get_host_by_token(db, crud.sha512(x_api_key)).domains
    data = None

    if request.method == 'PATCH':
        request_f = requests.patch
        data = await request.json()
        if not authorize_change_request(data, host_domains):
            raise HTTPException(status_code=401, detail='Unauthorized')

    response = request_f(PDNS_URL + PDNS_ZONE_URL + '/' + zone, headers=HEADERS, data=json.dumps(data))

    if response.status_code == 204:
        return Response(status_code=HTTPStatus.NO_CONTENT)

    return filter_rrsets(json.loads(response.content), host_domains)


@router.put(PDNS_ZONE_URL + '/{zone}/notify', dependencies=[Depends(validate_token)])
async def notify_zone(zone: str):
    response = requests.put(PDNS_URL + PDNS_ZONE_URL + '/' + zone + '/notify', headers=HEADERS)
    return response.content


@router.get('/acme-api/hosts/', response_model=list[schemas.Host])
async def list_hosts(db: Session = Depends(get_db)):
    return crud.get_hosts(db)


@router.post('/acme-api/hosts/')
async def create_host(host: schemas.HostCreate, db: Session = Depends(get_db)):
    db_host = crud.get_host_by_token(db, token_hash=crud.sha512(host.token))
    if db_host:
        raise HTTPException(status_code=400, detail='Host token already exists')
    return crud.create_host(db=db, host=host)


@router.post('/acme-api/hosts/{host_id}/domain_maps/', response_model=schemas.DomainMap)
async def create_domain_map(host_id: int, domain_map: schemas.DomainMapCreate, db: Session = Depends(get_db)):
    return crud.create_domain_map(db=db, domain_map=domain_map, host_id=host_id)
