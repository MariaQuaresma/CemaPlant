from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from backend.app.database import Base

class Usuarios(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120))
    email = Column(String(120), unique=True)
    senha = Column(String)
    data_criacao = Column(TIMESTAMP, server_default=func.now())