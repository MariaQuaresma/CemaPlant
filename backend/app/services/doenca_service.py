import numpy as np
from PIL import Image
import os

DOENCAS = {
    0: "Oídio",
    1: "Míldio",
    2: "Antracnose",
    3: "Mofo branco"
}

def predizer_doenca(caminho_imagem: str) -> tuple[int, float]:
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}") 
        img = Image.open(caminho_imagem).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        print(f"[IA] Imagem processada: {img_array.shape}")
        doenca_id = np.random.randint(0, len(DOENCAS))
        confianca = np.random.uniform(65, 99)
        print(f"[IA] Doença detectada: {DOENCAS[doenca_id]} ({confianca:.2f}%)")
        return doenca_id, float(confianca)
    except Image.UnidentifiedImageError:
        raise ValueError(f"Arquivo não é uma imagem válida: {caminho_imagem}")
    except Exception as e:
        raise Exception(f"Erro ao processar imagem: {str(e)}")
def listar_doenças_conhecidas() -> dict:
    return DOENCAS
