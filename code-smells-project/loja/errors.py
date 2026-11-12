"""Exceções de domínio e handlers centralizados de erro."""

import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

LOGGER = logging.getLogger(__name__)

MENSAGEM_ERRO_INTERNO = "Erro interno do servidor"


class DomainError(Exception):
    """Erro esperado de negócio, traduzível em resposta HTTP."""

    status_code = 400

    def __init__(self, mensagem, status_code=None, incluir_sucesso=False):
        super().__init__(mensagem)
        self.mensagem = mensagem
        if status_code is not None:
            self.status_code = status_code
        self.incluir_sucesso = incluir_sucesso

    def to_payload(self):
        payload = {"erro": self.mensagem}
        if self.incluir_sucesso:
            payload["sucesso"] = False
        return payload


class ValidationError(DomainError):
    status_code = 400


class NotFoundError(DomainError):
    status_code = 404


class UnauthorizedError(DomainError):
    status_code = 401


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def _handle_domain_error(error):
        return jsonify(error.to_payload()), error.status_code

    @app.errorhandler(HTTPException)
    def _handle_http_exception(error):
        return jsonify({"erro": error.description}), error.code

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        # O detalhe fica no log do servidor; o cliente recebe mensagem genérica.
        LOGGER.error("Erro não tratado; tipo=%s", type(error).__name__)
        return jsonify({"erro": MENSAGEM_ERRO_INTERNO}), 500
