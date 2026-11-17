# Playbook de refatoração

Cada transformação deve ser aplicada somente após o gate humano e validada por testes.

## PB-01 — Segredos

Antes: `SECRET_KEY = "literal"`.
Depois: `SECRET_KEY = os.environ["SECRET_KEY"]`, com `.env.example` sem valor real.

## PB-02 — SQL seguro

Antes: `"... WHERE id = " + str(value)`.
Depois: `cursor.execute("... WHERE id = ?", (value,))`.

## PB-03 — Separação de camadas

Antes: rota executa SQL, valida, calcula e serializa.
Depois: route → controller/service → repository/model → DTO.

## PB-04 — Administração segura

Antes: endpoint `/admin/query` executa SQL arbitrário.
Depois: remover ou restringir a operações allow-listed, autenticação e ambiente explicitamente habilitado.

## PB-05 — Senhas

Antes: MD5, base64 ou senha em claro.
Depois: KDF com salt e custo configurável, como `generate_password_hash`/`check_password_hash` ou `scrypt`/`argon2`.

## PB-06 — Dados sensíveis

Antes: senha/cartão/chave em response ou log.
Depois: DTO público, mascaramento e logging estruturado sem segredo.

## PB-07 — Dependências globais

Antes: conexão/cache mutável global criado no import.
Depois: factory de aplicação e dependência injetada por request/service.

## PB-08 — N+1

Antes: uma query por item em loop.
Depois: join/eager loading ou consulta em lote, mantendo o mesmo contrato.

## PB-09 — Validação centralizada

Antes: limites e status repetidos em várias rotas.
Depois: schema/validator e constantes compartilhadas, com mensagens compatíveis.

## PB-10 — Erros e APIs deprecated

Antes: `except:` amplo ou API documentada como obsoleta.
Depois: exceções específicas, handler centralizado e equivalente moderno confirmado pela documentação da versão.

## PB-11 — Token de autenticação real

Antes: `return {"token": "fake-jwt-token-" + str(user.id)}`.
Depois: emita um JWT assinado com algoritmo explícito e chave carregada de configuração/ambiente, contendo somente claims mínimas (`sub`, `iat`, `exp` e, quando necessário, `role`). Defina expiração curta e valide o token com a mesma chave/algoritmo nos recursos protegidos; nunca use ID, email ou timestamp como segredo. Atualize dependências, `.env.example`, testes de login/decodificação, documentação e o relatório. Se a auditoria encontrar um placeholder previsível, esta transformação é obrigatória na Fase 3 e não deve ser adiada por compatibilidade de contrato.
