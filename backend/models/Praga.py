from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Pragas(Base):
    __tablename__ = "pragas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    nome_cientifico = Column(String(150))
    descricao = Column(Text)
    nivel = Column(Integer)
    deteccoes = relationship("Deteccao", back_populates="praga")