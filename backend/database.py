# backend/database.py
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

# =====================================================================
#                        CONFIGURAÇÃO DE AMBIENTE
# =====================================================================

# Carrega as variáveis de ambiente a partir do arquivo .env local
load_dotenv()

# Obtém a string de conexão (protegendo credenciais sensíveis)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Validação Fail-Fast: Impede que o servidor inicie sem a configuração do banco
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "CRÍTICO: A variável de ambiente DATABASE_URL não foi encontrada. "
        "Verifique se o arquivo .env existe e está configurado corretamente."
    )


# =====================================================================
#                        MOTOR DO BANCO DE DADOS
# =====================================================================

# Cria o motor (engine) principal de comunicação com o PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Fábrica de Sessões:
# autocommit=False e autoflush=False garantem controle manual e seguro das transações.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe Base Declarativa: Todos os modelos do SQLAlchemy herdarão desta classe.
Base = declarative_base()


# =====================================================================
#                        INJEÇÃO DE DEPENDÊNCIA
# =====================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Gera uma sessão independente do banco de dados por requisição HTTP.

    A utilização do 'yield' permite que a rota consuma a sessão.
    O bloco 'finally' garante que a conexão seja devolvida ao pool
    mesmo que ocorram exceções durante o processamento da rota, prevenindo vazamento de memória.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
