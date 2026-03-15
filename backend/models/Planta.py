from sqlalchemy import Column, Integer, String, Text
from backend.app.database import Base

class Plantas(Base):
    __tablename__ = "plantas"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    nome_cientifico = Column(String)
    descricao = Column(Text)