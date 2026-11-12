# Heurísticas de análise de projeto

## Stack

- Python: `pyproject.toml`, `requirements*.txt`, imports de Flask/FastAPI/Django e arquivos `.py`.
- Node.js: `package.json`, `package-lock.json`, imports de Express e entry point declarado em `main`/scripts.
- Banco: `sqlite3`, `SQLAlchemy`, `Prisma`, migrations, `CREATE TABLE`, URLs de conexão e arquivos `.db`.

## Arquitetura

Mapeie entry point, rotas, handlers, controllers, services, models, repositories, configuração e integrações. Marque mistura de camadas quando uma função de rota também executa SQL, valida entrada, aplica regra de negócio e serializa resposta.

## Evidência

Use busca textual e leitura de contexto. Registre linhas exatas e uma evidência sanitizada. Não copie valores de senha, token, chave, cartão ou cookie. Diferencie fato observado de inferência.

## Validação

Antes da refatoração, capture boot e contratos básicos. Depois, repita os mesmos checks: import/compile, processo iniciado, health/root, GETs principais, uma operação de escrita com dados de teste e encerramento limpo.

## APIs obsoletas

Procure padrões conhecidos da stack e consulte documentação oficial quando houver dúvida. Registre a API encontrada, versão/contexto, equivalente moderno e se a substituição foi validada. Não marque como deprecated apenas por estilo.
