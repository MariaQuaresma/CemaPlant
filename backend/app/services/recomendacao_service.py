from app.models.Recomendacao import Recomendacao
from app.models.Deteccao import Deteccao
from app.models.Doenca import Doenca
from app.database import SessionLocal
from fastapi import HTTPException
import os


def criar_recomendacao(deteccao_id: int, texto: str):
    db = SessionLocal()
    try:
        deteccao = db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
        if not deteccao:
            raise HTTPException(status_code=404, detail="Detecção não encontrada")
        recomendacao = Recomendacao(
            deteccao_id=deteccao_id,
            texto_recomendacao=texto
        )
        db.add(recomendacao)
        db.commit()
        db.refresh(recomendacao)
        return recomendacao
    finally:
        db.close()


def buscar_recomendacoes_por_deteccao(deteccao_id: int):
    db = SessionLocal()
    try:
        return db.query(Recomendacao).filter(
            Recomendacao.deteccao_id == deteccao_id
        ).all()
    finally:
        db.close()


def gerar_recomendacao_por_deteccao(deteccao_id: int) -> str:
    db = SessionLocal()
    try:
        deteccao = db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
        if not deteccao:
            raise HTTPException(status_code=404, detail="Detecção não encontrada")
        doenca = db.query(Doenca).filter(Doenca.id == deteccao.doenca_id).first()
        nome_doenca = doenca.nome if doenca else "desconhecida"
        return gerar_recomendacao_openrouter(nome_doenca)

    finally:
        db.close()


def gerar_recomendacao_openrouter(doenca_nome: str) -> str:
    doenca_nome = doenca_nome.lower().strip()

    remedios = {
        "oídio": "Aplique enxofre ou solução de leite (1:10) nas folhas afetadas.",
        "míldio": "Evite molhar as folhas e utilize fungicidas naturais como calda bordalesa.",
        "antracnose": "Remova partes infectadas e aplique fungicida à base de cobre.",
        "mofo branco": "Melhore a ventilação e reduza a umidade ao redor da planta.",
        "default": "Mantenha a planta saudável com boa irrigação, iluminação e use soluções naturais preventivas."
    }

    return remedios.get(doenca_nome, remedios["default"])