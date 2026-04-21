import numpy as np
from PIL import Image, UnidentifiedImageError
import json
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PLANTA_PATH = os.path.join(BASE_DIR, "modelo_plantas.keras")
MODEL_DOENCA_PATH = os.path.join(BASE_DIR, "modelo_doencas.keras")

CLASS_PLANTA_PATH = os.path.join(BASE_DIR, "class_names_plantas.json")
CLASS_DOENCA_PATH = os.path.join(BASE_DIR, "class_names_doencas.json")

model_planta = tf.keras.models.load_model(MODEL_PLANTA_PATH)
model_doenca = tf.keras.models.load_model(MODEL_DOENCA_PATH)

with open(CLASS_PLANTA_PATH, "r") as f:
    classes_plantas = json.load(f)

with open(CLASS_DOENCA_PATH, "r") as f:
    classes_doencas = json.load(f)

IMG_SIZE = 224

ALIASES_PREFIXO_DOENCA = {
    "Cherry": "Cherry_(including_sour)",
    "Corn": "Corn_(maize)",
    "Pepper": "Pepper,_bell",
}

ALIASES_NOME_DOENCA = {
    "Leaf_Molde": "Leaf_Mold",
}

INDICES_DOENCA_POR_PLANTA = {}
for idx, classe_doenca in enumerate(classes_doencas):
    prefixo = classe_doenca.split("___", 1)[0]
    planta = ALIASES_PREFIXO_DOENCA.get(prefixo, prefixo)
    INDICES_DOENCA_POR_PLANTA.setdefault(planta, []).append(idx)

def preprocess(img: Image.Image):
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img).astype(np.float32)
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def _obter_prefixo_doenca_para_planta(planta_nome: str) -> str:
    return ALIASES_PREFIXO_DOENCA.get(planta_nome, planta_nome)

def _obter_prefixo_classe_doenca(classe_doenca: str) -> str:
    return classe_doenca.split("___", 1)[0]

def _normalizar_nome_doenca(doenca_nome: str) -> str:
    return ALIASES_NOME_DOENCA.get(doenca_nome, doenca_nome)

def _extrair_top_doenca_por_planta(pred_doenca: np.ndarray, planta_nome: str):
    indices = INDICES_DOENCA_POR_PLANTA.get(planta_nome, [])
    if not indices:
        idx = int(np.argmax(pred_doenca[0]))
        return classes_doencas[idx], float(pred_doenca[0][idx]), None, 0.0
    logits = pred_doenca[0][indices]
    ordem = np.argsort(logits)[::-1]
    idx_top = indices[int(ordem[0])]
    nome_top = classes_doencas[idx_top]
    conf_top = float(pred_doenca[0][idx_top])
    if len(ordem) > 1:
        idx_segundo = indices[int(ordem[1])]
        nome_segundo = classes_doencas[idx_segundo]
        conf_segundo = float(pred_doenca[0][idx_segundo])
    else:
        nome_segundo = None
        conf_segundo = 0.0
    return nome_top, conf_top, nome_segundo, conf_segundo

def _ajustar_tomato_por_indicio(
    pred_planta: np.ndarray,
    pred_doenca: np.ndarray,
    planta_nome: str,
    conf_planta: float,
    doenca_completa: str,
    conf_doenca: float,
):
    if "Tomato" not in classes_plantas:
        return planta_nome, conf_planta, doenca_completa, conf_doenca

    idx_tomato_planta = classes_plantas.index("Tomato")
    conf_tomato_planta = float(pred_planta[0][idx_tomato_planta])

    top5_ids = np.argsort(pred_doenca[0])[-5:][::-1]
    top5_nomes = [classes_doencas[i] for i in top5_ids]
    qtde_tomato_top5 = sum(1 for nome in top5_nomes if nome.startswith("Tomato___"))

    ha_indicio_tomato = (
        planta_nome == "Tomato"
        or doenca_completa.startswith("Tomato___")
        or conf_tomato_planta >= 0.35
        or qtde_tomato_top5 >= 2
    )
    if not ha_indicio_tomato:
        return planta_nome, conf_planta, doenca_completa, conf_doenca

    melhor_tomato, conf_melhor_tomato, segundo_tomato, conf_segundo_tomato = _extrair_top_doenca_por_planta(
        pred_doenca,
        "Tomato",
    )

    if (
        melhor_tomato == "Tomato___healthy"
        and segundo_tomato is not None
        and conf_segundo_tomato >= 0.12
        and (conf_melhor_tomato - conf_segundo_tomato) <= 0.65
    ):
        melhor_tomato = segundo_tomato
        conf_melhor_tomato = conf_segundo_tomato
    return "Tomato", max(conf_planta, conf_tomato_planta), melhor_tomato, conf_melhor_tomato

def _ajustar_tomato_falso_healthy(pred_doenca: np.ndarray, doenca_completa: str, conf_doenca: float):
    if doenca_completa != "Tomato___healthy":
        return doenca_completa, conf_doenca

    foco_tomato = {
        "Tomato___Leaf_Mold",
        "Tomato___Target_Spot",
        "Tomato___Septoria_leaf_spot",
    }

    top_ids = np.argsort(pred_doenca[0])[-8:][::-1]
    melhor_foco = None
    melhor_conf_foco = 0.0

    for idx in top_ids:
        nome = classes_doencas[idx]
        if nome in foco_tomato:
            conf = float(pred_doenca[0][idx])
            if conf > melhor_conf_foco:
                melhor_conf_foco = conf
                melhor_foco = nome
    if melhor_foco and melhor_conf_foco >= 0.20 and (conf_doenca - melhor_conf_foco) <= 0.18:
        return melhor_foco, melhor_conf_foco
    return doenca_completa, conf_doenca


def _selecionar_par_por_doenca(pred_planta: np.ndarray, pred_doenca: np.ndarray):
    top_doencas_ids = np.argsort(pred_doenca[0])[-5:][::-1]
    top_plantas_ids = np.argsort(pred_planta[0])[-5:][::-1]
    
    planta_top1 = classes_plantas[top_plantas_ids[0]]
    conf_planta_top1 = float(pred_planta[0][top_plantas_ids[0]])
    
    melhor_par = None
    melhor_score = -1
    
    for doenca_id in top_doencas_ids:
        doenca_completa = classes_doencas[doenca_id]
        conf_doenca = float(pred_doenca[0][doenca_id])
        
        prefixo_planta_doenca = _obter_prefixo_classe_doenca(doenca_completa)
        planta_doenca = _obter_prefixo_doenca_para_planta(prefixo_planta_doenca)
        
        if planta_doenca == planta_top1:
            planta_id = classes_plantas.index(planta_doenca)
            conf_planta = float(pred_planta[0][planta_id])
            score_consistencia = (conf_doenca + conf_planta) / 2
            
            if score_consistencia > melhor_score:
                melhor_score = score_consistencia
                melhor_par = (planta_doenca, conf_planta, doenca_completa, conf_doenca)
    
    if melhor_par is None:
        doenca_id = int(np.argmax(pred_doenca))
        doenca_completa = classes_doencas[doenca_id]
        conf_doenca = float(pred_doenca[0][doenca_id])
        prefixo_planta = _obter_prefixo_classe_doenca(doenca_completa)
        planta_nome = _obter_prefixo_doenca_para_planta(prefixo_planta)
        
        planta_id = classes_plantas.index(planta_nome) if planta_nome in classes_plantas else int(np.argmax(pred_planta))
        conf_planta = float(pred_planta[0][planta_id]) if planta_nome in classes_plantas else float(np.max(pred_planta))
        
        melhor_par = (planta_nome, conf_planta, doenca_completa, conf_doenca)
    
    return melhor_par

def prever_imagem(caminho_imagem: str):
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

        img = Image.open(caminho_imagem).convert("RGB")
        img_array = preprocess(img)

        pred_planta = model_planta.predict(img_array, verbose=0)
        pred_doenca = model_doenca.predict(img_array, verbose=0)
        planta_nome, conf_planta, doenca_completa, conf_doenca = _selecionar_par_por_doenca(
            pred_planta,
            pred_doenca,
        )
        planta_nome, conf_planta, doenca_completa, conf_doenca = _ajustar_tomato_por_indicio(
            pred_planta,
            pred_doenca,
            planta_nome,
            conf_planta,
            doenca_completa,
            conf_doenca,
        )
        doenca_completa, conf_doenca = _ajustar_tomato_falso_healthy(
            pred_doenca,
            doenca_completa,
            conf_doenca,
        )

        partes_doenca = doenca_completa.split("___", 1)
        if len(partes_doenca) == 2:
            doenca_nome = _normalizar_nome_doenca(partes_doenca[1])
        else:
            doenca_nome = _normalizar_nome_doenca(doenca_completa)
        resultado = f"{planta_nome}___{doenca_nome}"
        plantas_com_poucos_dados = {"Blueberry", "Raspberry", "Soybean", "Orange"}
        if planta_nome in plantas_com_poucos_dados:
            confianca_final = conf_doenca
        else:
            confianca_final = max(conf_doenca, (conf_planta + conf_doenca) / 2)
        print(f"[IA] Planta: {planta_nome} ({conf_planta:.4f})")
        print(f"[IA] Doença: {doenca_nome} ({conf_doenca:.4f})")
        print(f"[IA] Confiança Final: {confianca_final:.4f}")
        return resultado, confianca_final
    except UnidentifiedImageError:
        raise Exception("Arquivo enviado não é uma imagem válida")
    except Exception as e:
        raise Exception(f"Erro na predição: {str(e)}")