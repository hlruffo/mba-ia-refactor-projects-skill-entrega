# Catálogo de anti-patterns

| ID | Anti-pattern | Severidade padrão | Sinais de detecção |
|---|---|---|---|
| AP-001 | Segredo hardcoded | CRITICAL | senha, token, SECRET_KEY ou chave literal em código |
| AP-002 | SQL injection | CRITICAL | SQL concatenado/interpolado com entrada externa |
| AP-003 | God module/class | HIGH | arquivo/método mistura rota, persistência, regra e serialização |
| AP-004 | Endpoint administrativo inseguro | CRITICAL | reset, query ou debug sem autenticação/allow-list |
| AP-005 | Criptografia caseira ou hash fraco | CRITICAL | MD5/SHA1, base64 como hash, sem salt/KDF |
| AP-006 | Vazamento de dado sensível | CRITICAL | senha, cartão, chave ou stack trace em resposta/log |
| AP-007 | Acoplamento global | HIGH | singleton mutável, dependência criada dentro do handler |
| AP-008 | N+1 / consultas em loop | MEDIUM | query por item dentro de loop ou múltiplos cursores correlatos |
| AP-009 | Validação duplicada/inconsistente | MEDIUM | mesmas regras repetidas em rotas/modelos |
| AP-010 | Tratamento de exceção amplo | MEDIUM | `except:` ou catch que oculta erro sem logging seguro |
| AP-011 | Magic numbers/strings | LOW | limites, status e configurações espalhados como literais |
| AP-012 | Nomenclatura e código morto | LOW | imports não usados, nomes genéricos, funções sem uso |
| AP-013 | API deprecated | MEDIUM | método/runtime explicitamente obsoleto na documentação da versão |
| AP-014 | Responsabilidade de configuração no entry point | HIGH | segredos, defaults e infraestrutura misturados ao boot |

A severidade pode ser elevada ou reduzida somente com justificativa baseada no impacto e no contexto. Findings devem ser ordenados por severidade. Para cada API deprecated, registre a fonte/versionamento e o equivalente moderno; não faça substituição especulativa.
