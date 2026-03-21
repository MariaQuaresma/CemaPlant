from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Doenca(Base):
    __tablename__ = "doencas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    nome_cientifico = Column(String(150))
    descricao = Column(Text)
    nivel = Column(Integer)
    deteccoes = relationship("Deteccao", back_populates="doenca")