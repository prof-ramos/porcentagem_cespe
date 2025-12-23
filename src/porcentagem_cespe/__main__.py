"""
Permite executar o pacote como módulo: python -m porcentagem_cespe
"""

import sys

from porcentagem_cespe.cli import main

if __name__ == "__main__":
    sys.exit(main())
