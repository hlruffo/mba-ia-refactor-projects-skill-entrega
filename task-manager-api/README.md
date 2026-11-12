# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env
# Defina SECRET_KEY e SEED_DEFAULT_PASSWORD em .env antes de popular o banco
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco configurado em `DATABASE_URL` com usuários, categorias e tasks de exemplo. Configure `SEED_DEFAULT_PASSWORD` antes de executá-lo; os três usuários de demonstração recebem essa senha. Para os usuários existentes no banco antigo, redefina as senhas: os hashes MD5 não são aceitos após a migração para Werkzeug.
