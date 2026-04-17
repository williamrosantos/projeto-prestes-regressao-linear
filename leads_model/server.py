import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import uvicorn

# Importar lógica local
from pipeline import load_and_prepare
import modelo_a
import modelo_b

app = FastAPI(title="Prestes Lifecycle Simulator API")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")

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

class LifecycleRequest(BaseModel):
    praca: str
    produto: str
    investimento_mensal: float
    mes_calendario_inicio: int  # 1 a 12
    meses_projecao: int = 12

@app.get("/api/health")
async def health():
    return {"status": "ok", "resources_loaded": data_cache["df"] is not None}

@app.get("/api/metadata")
async def get_metadata():
    try:
        df, _, _ = get_resources()
        pracas = sorted(df["praca"].unique().tolist())
        produtos = sorted(df["produto"].unique().tolist()) if "produto" in df.columns else ["Produto 1"]
        
        # Taxas históricas por praça
        df_taxas = (
            df.groupby("praca")
            .agg(
                cpl_medio=("cpl", "mean"),
                taxa_qualif=("taxa_qualificacao", "mean"),
                taxa_visita=("taxa_visita", "mean"),
                taxa_reserva=("taxa_reserva", "mean"),
                meses=("mes", "count"),
            )
            .fillna(0)
            .round(4)
            .reset_index()
        )
        
        # Taxa Geral
        geral = {
            "praca": "Geral (Média)",
            "cpl_medio": round(df["cpl"].mean(), 2),
            "taxa_qualif": round(df["taxa_qualificacao"].mean(), 4),
            "taxa_visita": round(df["taxa_visita"].mean(), 4),
            "taxa_reserva": round(df["taxa_reserva"].mean(), 4),
            "meses": len(df)
        }
        
        historico = [geral] + df_taxas.to_dict(orient="records")
        
        return {
            "pracas": pracas,
            "produtos": produtos,
            "historico": historico
        }
    except Exception as e:
        print(f"ERRO NO METADATA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate-lifecycle")
async def simulate_lifecycle(req: LifecycleRequest):
    try:
        df, m_a, m_b_model = get_resources()
        
        timeline = []
        mes_cal_atual = req.mes_calendario_inicio
        
        for mes_ciclo_agora in range(1, req.meses_projecao + 1):
            
            # 1. Predição Modelo A (Leads Brutos via OLS Log-Log)
            leads_res = modelo_a.predict_leads(
                m_a, req.investimento_mensal, req.praca, req.produto, 
                mes_ciclo_agora, mes_cal_atual
            )
            leads_est = leads_res["estimativa"]
            
            # 2. Predição Modelo B (Leads Qualificados)
            pred_b = modelo_b.predict_qualificados(
                model_dict=m_b_model,
                leads=leads_est,
                praca=req.praca,
                produto=req.produto,
                mes_ciclo=mes_ciclo_agora,
                mes_calendario=mes_cal_atual,
                df_historico=df,
            )
            
            cpl = req.investimento_mensal / leads_est if leads_est > 0 else 0
            
            timeline.append({
                "mes_ciclo": mes_ciclo_agora,
                "mes_calendario": mes_cal_atual,
                "leads": int(leads_est),
                "leads_qualificados": int(pred_b["pred_modelo"]),
                "cpl": round(cpl, 2)
            })
            
            # Rotação do calendário anual
            mes_cal_atual += 1
            if mes_cal_atual > 12:
                mes_cal_atual = 1
                
        return {"timeline": timeline}
        
    except Exception as e:
        print(f"ERRO NO LIFECYCLE: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("\n" + "="*50)
    print("--- SERVIDOR PRESTES FASTAPI (TIME-SERIES) ---")
    print(f"Base de dados: {DATA_PATH}")
    print("="*50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
