from sqlalchemy.orm import Session
from . import models, schemas
import hashlib


def sha512(txt):
    return hashlib.sha512(txt.encode('utf-8')).hexdigest()


def get_host_by_token(db: Session, token_hash: str):
    return db.query(models.Host).filter(models.Host.token == token_hash).first()


def create_host(db: Session, host: schemas.HostCreate):
    token_hash = sha512(host.token)
    db_host = models.Host(hostname=host.hostname, token=token_hash)
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host
