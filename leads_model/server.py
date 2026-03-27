import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import uvicorn

# Importar lógica local
from pipeline import load_and_prepare
import modelo_a
import modelo_b

app = FastAPI(title="Prestes Lead Predictor API")

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")

# Cache global simples
data_cache = {
    "df": None,
    "model_a": None,
    "model_b": None
}

def get_resources():
    if data_cache["df"] is None:
        data_cache["df"] = load_and_prepare(DATA_PATH)
    if data_cache["model_a"] is None:
        data_cache["model_a"] = modelo_a.load_model(MODEL_A_PATH)
    if data_cache["model_b"] is None:
        data_cache["model_b"] = modelo_b.load_model(MODEL_B_PATH)
    return data_cache["df"], data_cache["model_a"], data_cache["model_b"]

class PredictionRequest(BaseModel):
    praca: str
    empreendimento: str
    investimento: float
    mes_calendario: int
    taxa_manual: Optional[float] = None

@app.get("/api/metadata")
async def get_metadata():
    df, _, _ = get_resources()
    pracas = sorted(df["praca"].unique().tolist())
    
    # Criar mapeamento de praça -> empreendimentos
    mapping = {}
    for praca in pracas:
        mapping[praca] = sorted(df[df["praca"] == praca]["empreendimento"].unique().tolist())
    
    # Taxas históricas para a tabela
    df_taxas = (
        df.groupby("praca")
        .agg(
            cpl_medio=("cpl", "mean"),
            taxa_qualif=("taxa_qualificacao", "mean"),
            taxa_visita=("taxa_visita", "mean"),
            taxa_reserva=("taxa_reserva", "mean"),
            meses=("mes", "count"),
        )
        .round(4)
        .reset_index()
    )
    
    return {
        "pracas": pracas,
        "mapping": mapping,
        "historico": df_taxas.to_dict(orient="records"),
        "summary": {
            "total_registros": len(df),
            "empreendimentos": df["empreendimento"].nunique(),
            "periodo": f"{df['mes'].min().strftime('%b/%Y')} -> {df['mes'].max().strftime('%b/%Y')}"
        }
    }

@app.post("/api/predict")
async def predict(req: PredictionRequest):
    df, m_a, m_b_model = get_resources()
    
    # 1. Determinar mes_ciclo automaticamente (último conhecido para aquele empreendimento)
    mes_ciclo = int(df[df["empreendimento"] == req.empreendimento]["mes_ciclo"].max())
    
    # 2. Predição Modelo A
    leads_res = modelo_a.predict_leads(
        m_a, req.investimento, req.praca, mes_ciclo, req.mes_calendario
    )
    leads_est = leads_res["estimativa"]
    
    # 3. Predição Modelo B
    pred_b = modelo_b.predict_qualificados(
        model_dict=m_b_model,
        leads=leads_est,
        praca=req.praca,
        mes_ciclo=mes_ciclo,
        mes_calendario=req.mes_calendario,
        taxa_manual=req.taxa_manual,
        df_historico=df,
    )
    
    cpl = req.investimento / leads_est if leads_est > 0 else 0
    
    return {
        "leads_estimados": int(leads_est),
        "leads_qualificados_modelo": int(pred_b["pred_modelo"]),
        "leads_qualificados_taxa": int(pred_b["pred_taxa"]),
        "cpl": round(cpl, 2),
        "taxa_usada": pred_b["taxa_usada"],
        "origem_taxa": pred_b["origem_taxa"]
    }

# Servir frontend estático
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
