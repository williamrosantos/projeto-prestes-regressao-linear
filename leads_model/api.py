import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import uvicorn

# Importar lógica local do projeto
from pipeline import load_and_prepare, get_summary
from modelo_a import load_model as load_model_a, predict_leads
from modelo_b import load_model as load_model_b, predict_qualificados

app = FastAPI()

# Configuração de CORS Universal conforme solicitado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")

# Carregamento inicial de recursos
df = load_and_prepare(DATA_PATH)
model_a = load_model_a(MODEL_A_PATH)
model_b = load_model_b(MODEL_B_PATH)

@app.get("/api/metadata")
def metadata():
    pracas = sorted(df["praca"].unique().tolist())
    
    mapping = {
        p: sorted(df[df["praca"] == p]["empreendimento"].unique().tolist())
        for p in pracas
    }
    
    historico = df.groupby("praca").agg(
        cpl_medio=("cpl", "mean"),
        taxa_qualif=("taxa_qualificacao", "mean"),
        taxa_visita=("taxa_visita", "mean"),
        taxa_reserva=("taxa_reserva", "mean"),
        meses=("mes", "count"),
    ).reset_index().round(4)
    
    summary = get_summary(df)
    
    return {
        "pracas": pracas,
        "mapping": mapping,
        "historico": historico.to_dict(orient="records"),
        "summary": {
            "total_registros": summary["total_registros"],
            "periodo": summary["periodo"],
        }
    }

@app.get("/api/ciclo")
def get_ciclo(empreendimento: str):
    mes_ciclo = int(df[df["empreendimento"] == empreendimento]["mes_ciclo"].max())
    return {"mes_ciclo": mes_ciclo}

@app.get("/api/historico-empreendimentos")
def historico_empreendimentos():
    hist = df.groupby(["empreendimento", "praca"]).agg(
        cpl_medio=("cpl", "mean"),
        taxa_qualif=("taxa_qualificacao", "mean"),
        taxa_visita=("taxa_visita", "mean"),
        taxa_reserva=("taxa_reserva", "mean"),
        meses=("mes", "count"),
    ).reset_index().round(4)
    hist = hist.sort_values(["praca", "empreendimento"])
    return hist.to_dict(orient="records")

class PredictRequest(BaseModel):
    praca: str
    empreendimento: str
    investimento: float
    mes_calendario: int
    taxa_manual: Optional[float] = None

@app.post("/api/predict")
def predict(req: PredictRequest):
    try:
        # Cálculo automático de mes_ciclo
        subset = df[df["empreendimento"] == req.empreendimento]
        if subset.empty:
            raise HTTPException(status_code=400, detail="Empreendimento não encontrado")
        
        mes_ciclo = int(subset["mes_ciclo"].max())
        
        # Predição Modelo A (Investimento -> Leads)
        # Extraímos "estimativa" porque a função retorna um dict {estimativa, piso, teto}
        leads_res = predict_leads(model_a, req.investimento, req.praca, mes_ciclo, req.mes_calendario)
        leads = leads_res["estimativa"]
        
        # Predição Modelo B (Leads -> Leads Qualificados)
        pred_b = predict_qualificados(
            model_dict=model_b,
            leads=leads,
            praca=req.praca,
            mes_ciclo=mes_ciclo,
            mes_calendario=req.mes_calendario,
            taxa_manual=req.taxa_manual,
            df_historico=df,
        )
        
        cpl = round(req.investimento / leads, 2) if leads > 0 else 0
        
        return {
            "leads_estimados": int(leads),
            "leads_qualificados_modelo": int(pred_b["pred_modelo"]),
            "leads_qualificados_taxa": int(pred_b["pred_taxa"] or 0),
            "origem_taxa": pred_b["origem_taxa"],
            "cpl": cpl,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Servir frontend estático para facilitar o acesso
static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
