from sqlalchemy import Column, Integer, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class Deteccao(Base):
    __tablename__ = "deteccoes"
    id = Column(Integer, primary_key=True, index=True)
    imagem_id = Column(Integer, ForeignKey("imagens.id"))
    planta_id = Column(Integer, ForeignKey("plantas.id"))
    praga_id = Column(Integer, ForeignKey("pragas.id"))
    porcentagem_confianca = Column(Float)
    data_deteccao = Column(TIMESTAMP, server_default=func.now())
    imagem = relationship("Imagem", back_populates="deteccoes")
    praga = relationship("Praga", back_populates="deteccoes")
    recomendacoes = relationship("Recomendacao", back_populates="deteccao")