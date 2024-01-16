from pydantic import BaseModel


class DomainMapBase(BaseModel):
    domain: str


class DomainMapCreate(DomainMapBase):
    pass


class DomainMap(DomainMapBase):
    id: int
    host_id: int

    class Config:
        orm_mode = True


class HostBase(BaseModel):
    hostname: str


class HostCreate(HostBase):
    token: str


class Host(HostBase):
    id: int
    domains: list[DomainMap] = []

    class Config:
        orm_mode = True
