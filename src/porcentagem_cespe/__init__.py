"""
Porcentagem CESPE - Análise Estatística de Questões de Concursos

Este pacote fornece ferramentas para análise de dados hierárquicos
de questões de concursos organizadas por tópicos.
"""

__version__ = "1.0.0"
__author__ = "Gabriel Ramos"

from .analisador import AnalisadorDados
from .models import Inconsistencia, Topico
from .validador import ValidadorHierarquia

__all__ = [
    "Topico",
    "Inconsistencia",
    "ValidadorHierarquia",
    "AnalisadorDados",
]
