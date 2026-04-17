"""
pipeline.py — Leitura, limpeza e engenharia de variáveis
"""

import pandas as pd
import numpy as np

# Mapeamento empreendimento → produto (tipologia)
EMPREENDIMENTO_PRODUTO = {
    "Empreendimento 1":  "Produto 1",
    "Empreendimento 2":  "Produto 1",
    "Empreendimento 3":  "Produto 1",
    "Empreendimento 4":  "Produto 2",
    "Empreendimento 5":  "Produto 3",
    "Empreendimento 6":  "Produto 3",
    "Empreendimento 7":  "Produto 1",
    "Empreendimento 8":  "Produto 3",
    "Empreendimento 9":  "Produto 4",
    "Empreendimento 10": "Produto 3",
    "Empreendimento 11": "Produto 6",
    "Empreendimento 12": "Produto 4",
    "Empreendimento 13": "Produto 1",
    "Empreendimento 14": "Produto 5",
    "Empreendimento 15": "Produto 1",
    "Empreendimento 16": "Produto 1",
    "Empreendimento 17": "Produto 4",
}


def load_and_prepare(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath, sheet_name="base dados")

    # Renomear colunas para snake_case
    df.columns = [
        "mes", "praca", "empreendimento",
        "investimento", "leads", "leads_qualificados",
        "visitas_agendadas", "visitas_realizadas",
        "reservas", "reservas_house", "reservas_imob",
        "reservas_digital_house", "reservas_digital_imob"
    ]

    # Garantir tipo datetime
    df["mes"] = pd.to_datetime(df["mes"])

    # Remover linhas com investimento zero (meses sem operação ativa)
    df = df[df["investimento"] > 0].copy()

    # Mês do ciclo de vida do empreendimento (1 = primeiro mês ativo)
    df = df.sort_values(["empreendimento", "mes"])
    df["mes_ciclo"] = df.groupby("empreendimento").cumcount() + 1

    # Variáveis derivadas — taxas de conversão
    df["taxa_qualificacao"] = np.where(
        df["leads"] > 0,
        df["leads_qualificados"] / df["leads"],
        0
    )
    df["taxa_visita"] = np.where(
        df["leads_qualificados"] > 0,
        df["visitas_realizadas"] / df["leads_qualificados"],
        0
    )
    df["taxa_reserva"] = np.where(
        df["visitas_realizadas"] > 0,
        df["reservas"] / df["visitas_realizadas"],
        0
    )
    df["cpl"] = np.where(
        df["leads"] > 0,
        df["investimento"] / df["leads"],
        np.nan
    )

    # Mês calendário (1–12) para capturar sazonalidade
    df["mes_calendario"] = df["mes"].dt.month
    
    # NOVAS FEATURES ESTÍSTICAS (Log-Log e Interações)
    df["log_investimento"] = np.log1p(df["investimento"])
    df["log_leads"] = np.log1p(df["leads"])
    # Segurança para mes do ciclo
    df["mes_ciclo"] = df.groupby("empreendimento").cumcount() + 1
    
    # Derivar produto a partir do empreendimento (mapeamento fixo)
    if "produto" not in df.columns:
        df["produto"] = df["empreendimento"].map(EMPREENDIMENTO_PRODUTO).fillna("Produto 1")
        
    df["praca_produto"] = df["praca"].astype(str) + "_" + df["produto"].astype(str)

    return df


def get_summary(df: pd.DataFrame) -> dict:
    """Retorna um resumo estatístico da base processada."""
    return {
        "total_registros": len(df),
        "empreendimentos": df["empreendimento"].nunique(),
        "pracas": df["praca"].nunique(),
        "periodo": f"{df['mes'].min().strftime('%b/%Y')} ate {df['mes'].max().strftime('%b/%Y')}",
        "cpl_medio": round(df["cpl"].mean(), 2),
        "taxa_qualificacao_media": round(df["taxa_qualificacao"].mean(), 4),
        "investimento_total": round(df["investimento"].sum(), 2),
        "leads_total": int(df["leads"].sum()),
    }
