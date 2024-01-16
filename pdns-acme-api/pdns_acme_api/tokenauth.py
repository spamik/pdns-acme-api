from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from . import crud
from .database import get_db


async def validate_token(x_api_key: str = Header(), db: Session = Depends(get_db)):
    if not crud.get_host_by_token(db, crud.sha512(x_api_key)):
        raise HTTPException(status_code=401, detail='Unauthorized')
