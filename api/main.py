from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Dict, Any, cast
from datetime import date
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set. Configure a URL válida para o banco.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FeedbackDB(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    data_feedback = Column(Date)
    id_curso = Column(String)
    qualidade_conteudo = Column(Numeric(2, 1))
    qualidade_instrutor = Column(Numeric(2, 1))
    recomendacao = Column(String)
    comentario = Column(String)

class Feedback(BaseModel):
    id: int
    data_feedback: date
    id_curso: str
    qualidade_conteudo: float
    qualidade_instrutor: float
    recomendacao: str
    comentario: str

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    data_feedback: date
    id_curso: str
    qualidade_conteudo: float
    qualidade_instrutor: float
    recomendacao: str
    comentario: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="API de Análise de Feedback - Cursos Livres")

@app.get("/feedbacks", response_model=List[Feedback])
def listar_feedbacks(db: Session = Depends(get_db)):
    feedbacks = db.query(FeedbackDB).all()
    return feedbacks

@app.get("/feedbacks/analise")
def analise_feedbacks(db: Session = Depends(get_db)):
    resultado = (
        db.query(
            FeedbackDB.id_curso.label("curso"),
            func.count(FeedbackDB.id).label("total_avaliacoes"),
            func.avg(FeedbackDB.qualidade_conteudo).label("media_conteudo"),
            func.avg(FeedbackDB.qualidade_instrutor).label("media_instrutor"),
            func.sum(func.cast(FeedbackDB.recomendacao == "Sim", Integer)).label("total_sim"),
        )
        .group_by(FeedbackDB.id_curso)
        .all()
    )

    return [
        {
            "curso": r.curso,
            "total_avaliacoes": r.total_avaliacoes,
            "media_conteudo": float(r.media_conteudo or 0.0),
            "media_instrutor": float(r.media_instrutor or 0.0),
            "percentual_sim": float((r.total_sim / r.total_avaliacoes) * 100) if r.total_avaliacoes > 0 else 0.0,
        }
        for r in resultado
    ]

@app.post("/feedbacks", response_model=Feedback)
def criar_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    payload = feedback.model_dump()
    
    novo_feedback = FeedbackDB(**payload)
    db.add(novo_feedback)
    db.commit()
    db.refresh(novo_feedback)

    return novo_feedback

Base.metadata.create_all(bind=engine)