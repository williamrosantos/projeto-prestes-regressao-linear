"""
app.py — Interface web local (Streamlit) para o Modelo Preditivo de Leads
Prestes — Construtora/Incorporadora

Uso:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np

from pipeline import load_and_prepare
import modelo_a
import modelo_b

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Leads — Prestes",
    page_icon="🏗️",
    layout="wide",
)

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")

MESES_LABEL = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

PRACAS = ["Praça 1", "Praça 2", "Praça 3", "Praça 4", "Praça 5", "Praça 6"]


# ── Cache: modelos e base ─────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    # Invalidate cache to load new model structures with MAPE
    try:
        m_a = modelo_a.load_model(MODEL_A_PATH)
        m_b = modelo_b.load_model(MODEL_B_PATH)
        return m_a, m_b
    except FileNotFoundError:
        return None, None


@st.cache_data
def load_data():
    return load_and_prepare(DATA_PATH)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏗️ Simulador de Leads — Prestes")
st.caption("Modelo preditivo de geração e qualificação de leads · Jan/2024 → Fev/2026")

# Verificar modelos
model_a, model_b_model = load_models()
df = load_data()

if model_a is None or model_b_model is None:
    st.error(
        "⚠️ Modelos não encontrados. "
        "Execute `python train.py` no terminal antes de abrir a interface."
    )
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🧮 Simulador", "📊 Taxas Históricas por Praça"])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — SIMULADOR (MODO COMPLETO)
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Simulador — Cadeia Completa")
    st.markdown(
        "Informe os parâmetros abaixo para estimar **leads gerados** e "
        "**leads qualificados** a partir de um investimento."
    )
    st.divider()

    col_inp1, col_inp2 = st.columns(2)

    with col_inp1:
        praca = st.selectbox("🗺️ Praça", options=PRACAS)

        mes_ciclo = st.number_input(
            "📅 Mês do ciclo do empreendimento",
            min_value=1,
            max_value=60,
            value=6,
            step=1,
            help="Quantos meses este empreendimento já está ativo? (1 = lançamento)",
        )

        mes_label = st.selectbox(
            "📆 Mês calendário",
            options=list(MESES_LABEL.keys()),
            format_func=lambda m: MESES_LABEL[m],
            index=2,  # Março como padrão
        )
        mes_calendario = mes_label

    with col_inp2:
        investimento = st.number_input(
            "💰 Investimento em R$",
            min_value=0.0,
            value=15000.0,
            step=500.0,
            format="%.2f",
        )

        taxa_input = st.text_input(
            "📈 Taxa de qualificação manual (%) — opcional",
            placeholder="Ex: 35  →  deixe vazio para usar o histórico da praça",
        )

        # Processar taxa manual
        taxa_manual = None
        taxa_origem = None
        if taxa_input.strip():
            try:
                taxa_manual = float(taxa_input.strip().replace(",", ".")) / 100
                taxa_origem = f"manual ({taxa_manual:.1%})"
            except ValueError:
                st.warning("Taxa inválida — será usada a taxa histórica da praça.")

    st.divider()
    calcular = st.button("🚀 Calcular", type="primary", use_container_width=True)

    if calcular:
        if investimento <= 0:
            st.error("Informe um investimento maior que zero.")
        else:
            # ── Predições ────────────────────────────────────────────────────
            leads_res = modelo_a.predict_leads(
                model_a, investimento, praca, mes_ciclo, mes_calendario
            )
            leads_est = leads_res["estimativa"]

            pred_b = modelo_b.predict_qualificados(
                model_dict=model_b_model,
                leads=leads_est,
                praca=praca,
                mes_ciclo=mes_ciclo,
                mes_calendario=mes_calendario,
                taxa_manual=taxa_manual,
                df_historico=df,
            )

            cpl = investimento / leads_est if leads_est > 0 else 0

            qualif_taxa = pred_b["pred_taxa"] if pred_b["pred_taxa"] is not None else 0
            taxa_usada = pred_b["taxa_usada"] if pred_b["taxa_usada"] is not None else 0
            origem_taxa = pred_b["origem_taxa"] or ""

            # ── Cards de resultado ───────────────────────────────────────────
            st.markdown("### 📋 Resultados")
            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                label="🎯 Leads Estimados",
                value=f"{int(leads_est):,}".replace(",", "."),
                help=f"Margem esperada: {int(leads_res['piso']):,} a {int(leads_res['teto']):,} leads"
            )
            c2.metric(
                label="✅ Qualificados (modelo)",
                value=f"{int(pred_b['pred_modelo']):,}".replace(",", "."),
                help=f"Margem esperada: {int(pred_b['piso_modelo']):,} a {int(pred_b['teto_modelo']):,} qualificados"
            )
            c3.metric(
                label=f"✅ Qualificados (taxa {taxa_usada:.1%})",
                value=f"{int(qualif_taxa):,}".replace(",", "."),
                help=f"Origem da taxa: {origem_taxa}",
            )
            c4.metric(
                label="💸 CPL Implícito",
                value=f"R$ {cpl:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            )

            # ── Detalhe ──────────────────────────────────────────────────────
            with st.expander("📌 Detalhes da simulação"):
                st.markdown(f"""
| Parâmetro | Valor |
|---|---|
| Praça | {praca} |
| Mês do ciclo | {mes_ciclo} |
| Mês calendário | {MESES_LABEL[mes_calendario]} |
| Investimento | R$ {investimento:,.2f} |
| Origem da taxa de qualificação | {origem_taxa} |
""")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — TAXAS HISTÓRICAS POR PRAÇA
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Taxas Históricas por Praça")
    st.markdown(
        "Valores calculados dinamicamente a partir da base de dados histórica."
    )
    st.divider()

    taxas = (
        df.groupby("praca")
        .agg(
            cpl_medio=("cpl", "mean"),
            taxa_qualificacao=("taxa_qualificacao", "mean"),
            taxa_visita=("taxa_visita", "mean"),
            taxa_reserva=("taxa_reserva", "mean"),
            meses=("mes", "count"),
        )
        .round(4)
        .reset_index()
    )

    # Formatar para exibição
    taxas_display = taxas.rename(columns={
        "praca": "Praça",
        "cpl_medio": "CPL Médio (R$)",
        "taxa_qualificacao": "Taxa Qualificação",
        "taxa_visita": "Taxa Visita",
        "taxa_reserva": "Taxa Reserva",
        "meses": "Meses na Base",
    })

    taxas_display["CPL Médio (R$)"] = taxas_display["CPL Médio (R$)"].map(
        lambda x: f"R$ {x:,.2f}"
    )
    taxas_display["Taxa Qualificação"] = taxas_display["Taxa Qualificação"].map(
        lambda x: f"{x:.1%}"
    )
    taxas_display["Taxa Visita"] = taxas_display["Taxa Visita"].map(
        lambda x: f"{x:.1%}"
    )
    taxas_display["Taxa Reserva"] = taxas_display["Taxa Reserva"].map(
        lambda x: f"{x:.1%}"
    )

    st.dataframe(
        taxas_display,
        use_container_width=True,
        hide_index=True,
    )

    # Resumo geral
    st.divider()
    st.markdown("### Resumo Geral da Base")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Total de Registros", f"{len(df):,}".replace(",", "."))
    col_r2.metric("Empreendimentos", df["empreendimento"].nunique())
    col_r3.metric("Praças", df["praca"].nunique())
    col_r4.metric(
        "Período",
        f"{df['mes'].min().strftime('%b/%Y')} → {df['mes'].max().strftime('%b/%Y')}",
    )
