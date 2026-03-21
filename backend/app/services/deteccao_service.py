from app.models.Deteccao import Deteccao
from app.database import SessionLocal

def salvar_deteccao(imagem_id: int, planta_id: int, doenca_id: int, porcentagem_confianca: float):
    db = SessionLocal()
    nova_deteccao = Deteccao(
        imagem_id=imagem_id,
        planta_id=planta_id,
        doenca_id=doenca_id,
        porcentagem_confianca=porcentagem_confianca
    )
    db.add(nova_deteccao)
    db.commit()
    db.refresh(nova_deteccao)
    db.close()
    return nova_deteccao

def buscar_deteccao_por_id(deteccao_id: int):
    db = SessionLocal()
    deteccao = db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
    db.close()
    return deteccao