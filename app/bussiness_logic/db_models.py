from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NombreDelModelo(Base):
    __tablename__ = 'Nombre de la tabla'
    __table_args__ = {'schema': 'Schema de la tabla'}

    columna_1 = Column(Integer, primary_key=True)
    columna_2 = Column(String)
    columna_3 = Column(Integer)
    columna_4 = Column(Integer, ForeignKey('Modelo2.columna_1')) # Llave foranea



class Modelo2(Base):
    __tablename__ = 'Nombre de la tabla'
    __table_args__ = {'schema': 'Schema de la tabla'}

    columna_1 = Column(Integer, primary_key=True)
    columna_2 = Column(String)

