from pydantic import BaseModel


class HostBase(BaseModel):
    hostname: str


class HostCreate(HostBase):
    token: str


class Host(HostBase):
    id: int

    class Config:
        orm_mode = True
