from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Planta(Base):
    __tablename__ = "plantas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    nome_cientifico = Column(String(150))
    descricao = Column(Text)