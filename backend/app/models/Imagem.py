from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Imagem(Base):
    __tablename__ = "imagens"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    url_imagem = Column(Text, nullable=False)
    data_upload = Column(TIMESTAMP, server_default=func.now())
    deteccoes = relationship("Deteccao", back_populates="imagem")