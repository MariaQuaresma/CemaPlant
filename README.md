# 🌱 CemaPlant – Identifica Doenças nas plantas

O **CemaPlant** é um aplicativo que utiliza **Inteligência Artificial, Visão Computacional e Machine Learning** para auxiliar agricultores familiares na identificação de doenças em plantações. A partir do envio de imagens, o sistema analisa a planta, identifica possíveis doenças e fornece recomendações de **remédios caseiros e tratamentos naturais** para ajudar no controle da infestação.

---

# 🧠 Tecnologias Utilizadas
* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic

Inteligência Artificial:
* Visão Computacional
* Machine Learning


# ⚙️ Como iniciar o projeto
1️⃣ Clonar o repositório
```
git clone <url-do-repositorio>
```


2️⃣ Entrar na pasta do backend
```
cd backend
```

3️⃣ Criar ambiente virtual
```
py -3.11 -m venv venv
```


4️⃣ Ativar ambiente virtual
Windows:
```
venv\Scripts\activate
```

5️⃣ Instalar dependências
```
pip install -r requirements.txt
```


6️⃣ Configurar variáveis de ambiente

Criar arquivo `.env` na pasta **backend**:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/cemaplant
```


7️⃣ Executar as migrations do banco
```
python -m alembic upgrade head
```

8️⃣ Iniciar a API
```
uvicorn app.main:app --reload
```
---

# 🌐 Acessar a API
Servidor local:
```
http://127.0.0.1:8000
```
Documentação automática:

```
http://127.0.0.1:8000/docs
```
