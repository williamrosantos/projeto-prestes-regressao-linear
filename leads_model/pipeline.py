"""
pipeline.py — Leitura, limpeza e engenharia de variáveis
"""

import pandas as pd
import numpy as np


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
    
    # Se a base não tiver a coluna produto por alguma falha manual, protege o fluxo fornecendo default
    if "produto" not in df.columns:
        df["produto"] = "Produto 1"
        
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
