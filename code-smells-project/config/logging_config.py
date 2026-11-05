"""Configuração central de logging e utilitário de mascaramento."""
import logging


def configurar_logging(nivel="INFO"):
    logging.basicConfig(
        level=getattr(logging, nivel, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def mascarar(valor, manter=4):
    """Mostra só os primeiros caracteres de um dado sensível (ex.: e-mail)."""
    if not valor:
        return valor
    return str(valor)[:manter] + "***"
