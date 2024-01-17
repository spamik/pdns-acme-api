from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from . import crud
from .database import get_db
from .config import ADMIN_TOKEN


async def validate_admin(x_api_key: str = Header()):
    """
    Authorization validation for admin API endpoints. Raise HTTP unauthorized if token specified in X-API-Key header
    is not equal with ADMIN_TOKEN in config.py
    :param x_api_key:
    """
    if x_api_key != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail='Unauthorized')


async def validate_token(x_api_key: str = Header(), db: Session = Depends(get_db)):
    if not crud.get_host_by_token(db, crud.sha512(x_api_key)):
        raise HTTPException(status_code=401, detail='Unauthorized')


def filter_dns_name(dns_name):
    """
    Remove trailing dot in dns record name and _acme-challenge prefix for dns record name comparison with allowed
    domains
    :param dns_name: DNS record name
    :return: str
    """
    if dns_name.startswith('_acme-challenge.'):
        # if DNS records starts with _acme-challenge, ignore it for allowed domain comparison
        dns_name = dns_name[len('_acme-challenge.'):]
    if dns_name[-1] == '.':
        # remove trailing dot in dns zone name, if presents
        dns_name = dns_name[:-1]
    return dns_name


def filter_rrsets(pdns_reply, domains):
    allowed_domains = tuple(i.domain for i in domains)
    pdns_reply['rrsets'] = [i for i in pdns_reply['rrsets'] if filter_dns_name(i['name']) in allowed_domains]
    return pdns_reply


def authorize_change_request(request_body, domains):
    """
    Returns True if this request wants changes only in specified domains
    :param request_body: body of request to pDNS API
    :param domains: allowed domains to change
    :return: bool
    """
    request_count = len(request_body['rrsets'])
    if request_count != len(filter_rrsets(request_body, domains)['rrsets']):
        # if filter_rrsets filtered some domains it means that in request is some record for which host is not
        # authorized
        return False
    return True
