# code-smells-project

API de e-commerce em Python/Flask, organizada em rotas, serviços, persistência SQLite, configuração e tratamento centralizado de erros.

## Rodar

```bash
python -m pip install -r requirements.txt
# configure as variáveis documentadas em .env.example no ambiente
python app.py
```

A aplicação escuta em `127.0.0.1:5000` por padrão. O SQLite usa `DATABASE_PATH` (padrão `loja.db`); o schema e os dados de demonstração são inicializados quando o banco está vazio. Senhas de demonstração usam `SEED_PASSWORD_ADMIN`, `SEED_PASSWORD_JOAO` e `SEED_PASSWORD_MARIA`; se ausentes, são geradas aleatoriamente e não são registradas.

O endpoint legado `POST /admin/query` retorna `410 Gone` e não executa SQL. `POST /admin/reset-db` retorna `404` por padrão; para habilitá-lo, configure `ADMIN_API_ENABLED=true` e `ADMIN_API_TOKEN`, e envie `Authorization: Bearer <token>`.

## Testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_api.py
```
