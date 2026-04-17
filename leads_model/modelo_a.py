"""
modelo_a.py — Modelo A (Otimizado): Investimento ↔ Leads

Responde duas perguntas:
  1. Para gerar X leads, quanto preciso investir?
  2. Se investir X, quantos leads vou gerar?

Abordagem: Regressão Linear Múltipla OLS com Transformação Logarítmica 
e Interações de Matriz (Praça x Produto).
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score


FEATURES = ["log_investimento", "mes_ciclo", "mes_calendario", "praca", "produto", "praca_produto"]
TARGET_LEADS = "log_leads"


def build_preprocessor():
    numeric = ["log_investimento", "mes_ciclo", "mes_calendario"]
    categorical = ["praca", "produto", "praca_produto"]

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), numeric),
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

    # Métricas com cross-validation (5 folds) na escala LOG
    cv_r2 = cross_val_score(model, X, y, cv=5, scoring="r2")
    
    # Para validar MAE real, reverte ao mundo físico (exponencial)
    pred_log = model.predict(X)
    y_pred_real = np.expm1(pred_log)
    y_real = np.expm1(y)
    
    mae = mean_absolute_error(y_real, y_pred_real)
    r2 = r2_score(y_real, y_pred_real)
    mape = np.mean(np.abs((y_real - y_pred_real) / np.maximum(y_real, 1)))

    return {
        "model": model,
        "r2_treino": round(r2, 4),
        "r2_cv_media": round(cv_r2.mean(), 4),
        "r2_cv_std": round(cv_r2.std(), 4),
        "mae": round(mae, 1),
        "mape": round(mape, 4),
        "n_obs": len(df),
    }


def predict_leads(model_input, investimento: float, praca: str, produto: str,
                  mes_ciclo: int, mes_calendario: int) -> dict:
    """Dado investimento, praça e produto → retorna dict com leads estimados."""
    
    # Prepara Input com as mesmas features exatas do Treino
    log_inv = np.log1p(max(investimento, 0))
    praca_produto = f"{praca}_{produto}"
    
    X = pd.DataFrame([{
        "log_investimento": log_inv,
        "mes_ciclo": mes_ciclo,
        "mes_calendario": mes_calendario,
        "praca": praca,
        "produto": produto,
        "praca_produto": praca_produto
    }])
    
    # Robustez (Compatibilidade Opcional do Dict do modelo gerado)
    if isinstance(model_input, dict):
        model = model_input["model"]
        mape = model_input.get("mape", 0.2)
    else:
        model = model_input
        mape = 0.2  # Default se não houver MAPE salvo
    
    # Como o modelo retorna log_leads, usamos expm1
    pred_log = model.predict(X)[0]
    leads = np.expm1(pred_log)
    pred = max(0, round(leads, 1))
    
    return {
        "estimativa": pred,
        "piso": max(0, round(pred * (1 - mape), 1)),
        "teto": round(pred * (1 + mape), 1)
    }


def predict_investimento(model_dict: dict, leads_meta: float, praca: str, produto: str,
                         mes_ciclo: int, mes_calendario: int,
                         tol: float = 1.0, max_iter: int = 1000) -> float:
    """
    Dado meta de leads → estima investimento necessário via busca binária.
    """
    low, high = 0.0, 1_000_000.0  # Teto um pouco mais alto devido ao Log

    for _ in range(max_iter):
        mid = (low + high) / 2
        res = predict_leads(model_dict, mid, praca, produto, mes_ciclo, mes_calendario)
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
