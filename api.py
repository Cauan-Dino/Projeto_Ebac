from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')
from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base,Session,sessionmaker
from sqlalchemy import Column,String,Float,Integer,create_engine
import secrets
import os
from typing import Optional


# Criacao do banco de dados

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL,connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base = declarative_base()


# Criação das colunas da tabela 'Jogos' do banco de dados
class DBJogos(Base):
    __tablename__ = 'jogos'
    id = Column(Integer,primary_key=True,index=True)
    nome_do_criador = Column(String,index=True)
    nome_do_jogo = Column(String,index=True)
    data_lancamento = Column(String,index=True)

# BODYMODELS

class BODYJogos(BaseModel):
    nome_do_criador: str
    nome_do_jogo: str
    data_lancamento: str

# Body model para alterar informações de um jogo cadastrado
class BODYPUTJogos(BaseModel):
    nome_do_criador: Optional[str] = None
    nome_do_jogo: Optional[str] = None
    data_lancamento: Optional[str] = None

Base.metadata.create_all(bind=engine)


# Declaracao das classes 
app = FastAPI()
security = HTTPBasic()

# Função que autoriza ou não o usuario a entrar em um endpoint
def autorizacao(credenciais: HTTPBasicCredentials = Depends(security)):
    SENHA = os.getenv('SENHA')
    USUARIO = os.getenv('USUARIO')

    verificacao_senha = secrets.compare_digest(SENHA,credenciais.password)
    verificacao_usuario = secrets.compare_digest(USUARIO,credenciais.username)

    if not (verificacao_senha and verificacao_usuario):
        raise HTTPException(
            status_code=401,
            detail='Senha ou usuario incorretos',
            headers={'WWW-Authenticate':'Basic'}
        )

# Função para criar e gerenciar o banco de dados 
def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============
# | ENDPOINTS  |
# ==============

# Endpoint para adicionar um jogo
@app.post('/jogos')
def cadastrar_jogo(body: BODYJogos,db: Session = Depends(sessao_db),_: None = Depends(autorizacao)):
    # Verifica se o jogo ja existe
    verificacao = db.query(DBJogos).filter(DBJogos.nome_do_jogo == body.nome_do_jogo, DBJogos.nome_do_criador == body.nome_do_criador, DBJogos.data_lancamento == body.data_lancamento).first()
    if verificacao:
        raise HTTPException(
            status_code=400,
            detail='Esse jogo já está cadastrado'
        )
    
    # Adiciona o jogo no banco de dados
    adicionar_jogo = DBJogos(**body.model_dump())
    db.add(adicionar_jogo)
    db.commit()
    db.refresh(adicionar_jogo)
    
    return {'message':f'Jogo {body.nome_do_jogo} adicionado com sucesso'}

# Endpoint Para listar todos os jogos cadastrados
@app.get('/jogos')
def listar_jogos(db: Session = Depends(sessao_db),page: int = 1, limit: int = 10):
    # Verifica se o usuario digitou corretamento a pagina e o limit
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail='Por favor, selecione um limite e uma pagina validas'
        )
    
    # Define o que sera retornado no get
    lista_de_jogos = db.query(DBJogos).offset((page-1)*limit).limit(limit).all()

    # Verifica a quantidade jogos cadastrados
    quantidade = db.query(DBJogos).count()
    if quantidade == 0:
        raise HTTPException(
            status_code=400,
            detail='Ainda não há nada cadastrado'
        )

    paginacao = [
        {
            'id': valor.id,
            'nome_do_jogo': valor.nome_do_jogo,
            'nome_do_criador': valor.nome_do_criador,
            'data_de_lançamento': valor.data_lancamento
        }
        for valor in lista_de_jogos
    ]
    return {
        'pagina':page,
        'limite':limit,
        'quantidade_de_jogos_cadastrados': quantidade,
        'paginacao': paginacao
            }

# Endpoint para atualizar as informações de um jogo
@app.put('/jogos/{id}')
def mudar_jogos(id: int,body: BODYPUTJogos,db: Session = Depends(sessao_db),_: None = Depends(autorizacao)):
    # Verifica se o jogo existe
    verificacao_existe_jogo = db.query(DBJogos).filter(DBJogos.id == id).first()
    if not verificacao_existe_jogo:
        raise HTTPException(
            status_code=404,
            detail='Esse jogo nao existe'
        )
    
    # Verifica se o usuario colocou alguma coisa no atributo nome_do_criador
    if body.nome_do_criador is not None:
        verificacao_existe_jogo.nome_do_criador = body.nome_do_criador
    
    # Verifica se o usuario colocou alguma coisa no atributo nome_do_jogo
    if body.nome_do_jogo is not None:
        verificacao_existe_jogo.nome_do_jogo = body.nome_do_jogo
    
    # Verifica se o usuario colocou alguma coisa no atributo data_lancamento
    if body.data_lancamento is not None:
        verificacao_existe_jogo.data_lancamento = body.data_lancamento
    
    db.commit()
    db.refresh(verificacao_existe_jogo)
    return {'message':f'Descrições do jogo mudado com sucesso'}


# Endpoint para deletar um jogo
@app.delete('/jogos/{id}')
def deletar_jogo(id: int, db: Session = Depends(sessao_db),_: None = Depends(autorizacao)):
    # Verifica se o jogo existe dentro do banco de dados
    verificacao_existe_jogo = db.query(DBJogos).filter(DBJogos.id == id).first()
    if not verificacao_existe_jogo:
        raise HTTPException(
            status_code=404,
            detail='Esse jogo não existe'
        )
    
    # Apagando o jogo dentro do banco de dados
    db.delete(verificacao_existe_jogo)
    db.commit()
    
    return {'message':f'Jogo {DBJogos.nome_do_jogo} deletado com sucesso'}
        