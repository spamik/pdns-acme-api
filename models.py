from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    hostname = Column(String, unique=True)
    token = Column(String, unique=True, index=True)

    domains = relationship('DomainMap', back_populates='host')


class DomainMap(Base):
    __tablename__ = 'domain_map'

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'))
    domain = Column(String)

    host = relationship('Host', back_populates='domains')
