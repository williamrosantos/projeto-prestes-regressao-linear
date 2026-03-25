"""
modelo_a.py — Modelo A: Investimento ↔ Leads

Responde duas perguntas:
  1. Para gerar X leads, quanto preciso investir?
  2. Se investir X, quantos leads vou gerar?

Abordagem: Regressão Linear com efeitos fixos de praça e mês do ciclo.
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


FEATURES = ["investimento", "praca", "mes_ciclo", "mes_calendario"]
TARGET_LEADS = "leads"


def build_preprocessor():
    numeric = ["investimento", "mes_ciclo", "mes_calendario"]
    categorical = ["praca"]

    preprocessor = ColumnTransformer([
        ("num", "passthrough", numeric),
        ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), categorical),
    ])
    return preprocessor


def train(df: pd.DataFrame) -> dict:
    X = df[FEATURES].copy()
    y = df[TARGET_LEADS].copy()

    preprocessor = build_preprocessor()
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression()),
    ])

    model.fit(X, y)

    # Métricas com cross-validation (5 folds)
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


def predict_leads(model_input, investimento: float, praca: str,
                  mes_ciclo: int, mes_calendario: int) -> dict:
    """Dado investimento → retorna dict com leads estimados, piso e teto."""
    X = pd.DataFrame([{
        "investimento": investimento,
        "praca": praca,
        "mes_ciclo": mes_ciclo,
        "mes_calendario": mes_calendario,
    }])
    
    # Robustez: aceita tanto o dicionário novo quanto o modelo antigo
    if isinstance(model_input, dict):
        model = model_input["model"]
        mape = model_input.get("mape", 0.2)
    else:
        model = model_input
        mape = 0.2  # Default se não houver MAPE salvo
    
    leads = model.predict(X)[0]
    pred = max(0, round(leads, 1))
    
    return {
        "estimativa": pred,
        "piso": max(0, round(pred * (1 - mape), 1)),
        "teto": round(pred * (1 + mape), 1)
    }


def predict_investimento(model_dict: dict, leads_meta: float, praca: str,
                         mes_ciclo: int, mes_calendario: int,
                         tol: float = 1.0, max_iter: int = 1000) -> float:
    """
    Dado meta de leads → estima investimento necessário via busca binária.
    Inverte o modelo sem precisar de regressão reversa separada.
    """
    low, high = 0.0, 500_000.0

    for _ in range(max_iter):
        mid = (low + high) / 2
        res = predict_leads(model_dict, mid, praca, mes_ciclo, mes_calendario)
        pred = res["estimativa"]

        if abs(pred - leads_meta) <= tol:
            return round(mid, 2)
        if pred < leads_meta:
            low = mid
        else:
            high = mid

    return round((low + high) / 2, 2)


def save_model(result: dict, path: str):
    joblib.dump(result, path)


def load_model(path: str):
    return joblib.load(path)
