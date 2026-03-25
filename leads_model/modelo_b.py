"""
modelo_b.py — Modelo B: Leads → Leads Qualificados

Responde: Se investir X e gerar Y leads com taxa de qualificação Z,
          quantos leads qualificados vou ter?

A taxa de qualificação pode ser:
  - Informada manualmente (premissa do usuário)
  - Estimada pelo modelo com base no histórico da praça/empreendimento
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score


FEATURES = ["leads", "praca", "mes_ciclo", "mes_calendario"]
TARGET = "leads_qualificados"


def build_preprocessor():
    numeric = ["leads", "mes_ciclo", "mes_calendario"]
    categorical = ["praca"]

    preprocessor = ColumnTransformer([
        ("num", "passthrough", numeric),
        ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), categorical),
    ])
    return preprocessor


def train(df: pd.DataFrame) -> dict:
    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    preprocessor = build_preprocessor()
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression()),
    ])

    model.fit(X, y)

    cv_r2 = cross_val_score(model, X, y, cv=5, scoring="r2")
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    mape = np.mean(np.abs((y - y_pred) / np.maximum(y, 1)))

    return {
        "model": model,
        "r2_treino": round(r2, 4),
        "r2_cv_media": round(cv_r2.mean(), 4),
        "r2_cv_std": round(cv_r2.std(), 4),
        "mae": round(mae, 1),
        "mape": round(mape, 4),
        "n_obs": len(df),
    }


def get_taxa_historica(df: pd.DataFrame, praca: str) -> float:
    """Retorna a taxa de qualificação histórica média da praça."""
    subset = df[df["praca"] == praca]
    if len(subset) == 0:
        return df["taxa_qualificacao"].mean()
    return round(subset["taxa_qualificacao"].mean(), 4)


def predict_qualificados(
    model_dict: dict,
    leads: float,
    praca: str,
    mes_ciclo: int,
    mes_calendario: int,
    taxa_manual: float = None,
    df_historico: pd.DataFrame = None,
) -> dict:
    """
    Prediz leads qualificados.

    Se taxa_manual fornecida: aplica diretamente sobre os leads.
    Senão: usa o modelo de regressão treinado.

    Retorna dict com ambas as estimativas para comparação.
    """
    # Estimativa pelo modelo de regressão
    X = pd.DataFrame([{
        "leads": leads,
        "praca": praca,
        "mes_ciclo": mes_ciclo,
        "mes_calendario": mes_calendario,
    }])
    # Robustez: aceita tanto o dicionário novo quanto o modelo antigo
    if isinstance(model_dict, dict):
        model = model_dict["model"]
        mape = model_dict.get("mape", 0.2)
    else:
        model = model_dict
        mape = 0.2
    
    pred_modelo = max(0, round(model.predict(X)[0], 1))
    piso_modelo = max(0, round(pred_modelo * (1 - mape), 1))
    teto_modelo = round(pred_modelo * (1 + mape), 1)

    # Estimativa pela taxa (manual ou histórica)
    if taxa_manual is not None:
        taxa = taxa_manual
        origem_taxa = "manual"
    elif df_historico is not None:
        taxa = get_taxa_historica(df_historico, praca)
        origem_taxa = f"histórico ({praca})"
    else:
        taxa = None
        origem_taxa = None

    pred_taxa = round(leads * taxa, 1) if taxa is not None else None

    return {
        "leads_entrada": leads,
        "pred_modelo": pred_modelo,
        "piso_modelo": piso_modelo,
        "teto_modelo": teto_modelo,
        "pred_taxa": pred_taxa,
        "taxa_usada": taxa,
        "origem_taxa": origem_taxa,
    }


def save_model(result: dict, path: str):
    joblib.dump(result, path)


def load_model(path: str):
    return joblib.load(path)
