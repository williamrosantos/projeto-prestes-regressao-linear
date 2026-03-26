"""
app.py — Interface web local (Streamlit) para o Modelo Preditivo de Leads
Prestes — Construtora/Incorporadora

Uso:
    streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import numpy as np

from pipeline import load_and_prepare
import modelo_a
import modelo_b

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Simulador de Leads — Prestes")

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
@st.cache_data
def load_data():
    return load_and_prepare(DATA_PATH)


@st.cache_resource
def load_models():
    # Tenta carregar os modelos salvos; se falhar por qualquer motivo,
    # treina em memória a partir dos dados (regressão linear é rápida).
    try:
        m_a = modelo_a.load_model(MODEL_A_PATH)
        m_b = modelo_b.load_model(MODEL_B_PATH)
        return m_a, m_b
    except Exception:
        pass

    try:
        df = load_and_prepare(DATA_PATH)
        m_a = modelo_a.train(df)
        m_b = modelo_b.train(df)
        return m_a, m_b
    except Exception as e:
        return None, None


# ── Helper: card de resultado ─────────────────────────────────────────────────
def card_html(label, valor, subtitulo):
    return f"""
<div style="background:#ffffff; border-left:4px solid #84e115; border-radius:6px;
            box-shadow:0 1px 4px rgba(0,0,0,.08); padding:1.25rem 1.5rem; margin-bottom:1rem;">
  <div style="font-size:0.65rem; font-weight:700; letter-spacing:1px; color:#044d41;
              text-transform:uppercase;">{label}</div>
  <div style="font-size:1.8rem; font-weight:700; color:#044d41; line-height:1.2;">{valor}</div>
  <div style="font-size:0.8rem; color:#323232; margin-top:0.25rem;">{subtitulo}</div>
</div>"""


# ── CSS Global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Lufga', 'Inter', sans-serif;
}

/* Esconder toolbar/header padrão do Streamlit */
header[data-testid="stHeader"] {
    display: none !important;
}
#MainMenu {
    display: none !important;
}
footer {
    display: none !important;
}

/* Fundo geral */
.stApp {
    background-color: #f4f4f4;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* ── Painel branco — coluna esquerda ── */
section[data-testid="column"]:first-child > div > div {
    background: #ffffff;
    border-radius: 6px;
    padding: 2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 2px solid #e8e8e8;
    margin-bottom: 1.5rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Lufga', 'Inter', sans-serif;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #6b6b6b;
    padding: 0.85rem 1.5rem;
    background: transparent;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}

.stTabs [aria-selected="true"] {
    color: #044d41 !important;
    border-bottom: 3px solid #84e115 !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* ── Input labels ── */
.stSelectbox label,
.stNumberInput label,
.stTextInput label {
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 0.7rem !important;
    color: #044d41 !important;
}

/* ── Input fields ── */
.stSelectbox > div > div,
.stNumberInput input,
.stTextInput input {
    border-radius: 6px !important;
    background-color: #f9f9f9 !important;
    border: 1px solid rgba(4, 77, 65, 0.18) !important;
}

.stTextInput input::placeholder {
    color: #aaaaaa;
    font-style: italic;
    font-weight: 300;
}

/* ── Botão Calcular ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #044d41 0%, #00342c 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    border-radius: 6px !important;
    border: none !important;
    padding: 0.65rem 2rem !important;
    text-transform: uppercase !important;
    width: 100% !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #84e115 !important;
    color: #044d41 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Verificar modelos ─────────────────────────────────────────────────────────
model_a, model_b_model = load_models()
df = load_data()

if model_a is None or model_b_model is None:
    st.error(
        "⚠️ Erro ao carregar os modelos e ao tentar treinamento automático. "
        "Verifique se o arquivo de dados está acessível em `leads_model/data/base_de_dados.xlsx`."
    )
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Simulador", "Taxas Históricas"])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — SIMULADOR
# ═════════════════════════════════════════════════════════════════════════════
with tab1:

    col_esq, col_dir = st.columns([1, 1], gap="large")

    # ── Coluna esquerda: painel de inputs ─────────────────────────────────────
    with col_esq:
        st.markdown("""
<h1 style="font-family:'Lufga','Inter',sans-serif; font-weight:700; color:#044d41; margin:0;">
  Simulador de Leads
</h1>
<div style="width:48px; height:4px; background:#84e115; border-radius:2px; margin:0.5rem 0 0.25rem;"></div>
<p style="font-weight:300; color:#323232; font-size:0.9rem; margin:0 0 1.25rem;">
  Modelo preditivo · Jan/2024 → Fev/2026
</p>
""", unsafe_allow_html=True)

        praca = st.selectbox("Praça", options=PRACAS)

        empreendimentos_da_praca = sorted(
            df[df["praca"] == praca]["empreendimento"].unique().tolist()
        )
        empreendimento = st.selectbox("Empreendimento", options=empreendimentos_da_praca)

        mes_ciclo = int(df[df["empreendimento"] == empreendimento]["mes_ciclo"].max())
        st.markdown(
            f'<p style="font-size:0.8rem; color:#323232; margin:0.25rem 0 0.75rem;">'
            f'<span style="font-weight:700; color:#044d41;">Mês do ciclo:</span> '
            f'{mes_ciclo} (calculado automaticamente)</p>',
            unsafe_allow_html=True,
        )

        investimento = st.number_input(
            "Investimento em R$",
            min_value=0.0,
            value=15000.0,
            step=500.0,
            format="%.2f",
        )

        mes_label = st.selectbox(
            "Mês calendário",
            options=list(MESES_LABEL.keys()),
            format_func=lambda m: MESES_LABEL[m],
            index=2,
        )
        mes_calendario = mes_label

        taxa_input = st.text_input(
            "Taxa de qualificação manual (%) — opcional",
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

        # Botão alinhado à direita
        col1, col2 = st.columns([3, 1])
        with col2:
            calcular = st.button("CALCULAR", type="primary", use_container_width=True)

    # ── Coluna direita: cards de resultado ────────────────────────────────────
    with col_dir:
        st.markdown("<div style='margin-top:155px;'>", unsafe_allow_html=True)
        if calcular:
            if investimento <= 0:
                st.error("Informe um investimento maior que zero.")
            else:
                # ── Predições ──────────────────────────────────────────────
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

                # Formatar valores
                leads_est_fmt   = f"{int(leads_est):,}".replace(",", ".")
                pred_modelo_fmt = f"{int(pred_b['pred_modelo']):,}".replace(",", ".")
                qualif_taxa_fmt = f"{int(qualif_taxa):,}".replace(",", ".")
                cpl_fmt = (
                    f"R$ {cpl:,.2f}"
                    .replace(",", "X").replace(".", ",").replace("X", ".")
                )
                subtitulo_taxa = f"Baseado na taxa {origem_taxa}" if origem_taxa else "Taxa histórica da praça"

                # ── Grid 2×2 de cards ─────────────────────────────────────
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(
                        card_html("LEADS ESTIMADOS", leads_est_fmt, "Total estimado para o período"),
                        unsafe_allow_html=True,
                    )
                with r2:
                    st.markdown(
                        card_html("LEADS QUALIF. (MODELO)", pred_modelo_fmt, "Baseado no modelo preditivo"),
                        unsafe_allow_html=True,
                    )

                r3, r4 = st.columns(2)
                with r3:
                    st.markdown(
                        card_html("LEADS QUALIF. (TAXA)", qualif_taxa_fmt, subtitulo_taxa),
                        unsafe_allow_html=True,
                    )
                with r4:
                    st.markdown(
                        card_html("CPL IMPLÍCITO", cpl_fmt, "Investimento total / Leads estimados"),
                        unsafe_allow_html=True,
                    )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabela de taxas históricas (largura total) ────────────────────────────
    st.markdown("""
<div style="margin-top:2.5rem; margin-bottom:0.5rem;">
  <span style="font-size:0.7rem; font-weight:700; letter-spacing:1px;
               color:#044d41; text-transform:uppercase;">Taxas Históricas por Praça</span>
</div>
""", unsafe_allow_html=True)

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

    taxas_display = taxas.rename(columns={
        "praca": "Praça",
        "cpl_medio": "CPL Médio",
        "taxa_qualificacao": "Taxa Qualificação",
        "taxa_visita": "Taxa Visita",
        "taxa_reserva": "Taxa Reserva",
        "meses": "Meses na base",
    })

    taxas_display["CPL Médio"] = taxas_display["CPL Médio"].map(lambda x: f"R$ {x:,.2f}")
    taxas_display["Taxa Qualificação"] = taxas_display["Taxa Qualificação"].map(lambda x: f"{x:.0%}")
    taxas_display["Taxa Visita"] = taxas_display["Taxa Visita"].map(lambda x: f"{x:.0%}")
    taxas_display["Taxa Reserva"] = taxas_display["Taxa Reserva"].map(lambda x: f"{x:.0%}")

    header_cells = "".join(
        f'<th style="background:#044d41; color:#ffffff; font-weight:700; letter-spacing:1px; '
        f'text-transform:uppercase; font-size:0.73rem; padding:0.75rem 1rem; '
        f'text-align:{"left" if i == 0 else "right"};">{col}</th>'
        for i, col in enumerate(taxas_display.columns)
    )

    body_rows = ""
    for idx, row in taxas_display.iterrows():
        row_bg = "#ffffff" if idx % 2 == 0 else "#f4f4f4"
        cells = "".join(
            f'<td style="padding:0.65rem 1rem; font-size:0.85rem; color:#323232; '
            f'background:{row_bg}; text-align:{"left" if i == 0 else "right"};">{val}</td>'
            for i, val in enumerate(row)
        )
        body_rows += f"<tr>{cells}</tr>"

    st.markdown(f"""
<div style="border-radius:6px; overflow:hidden; box-shadow:0 1px 4px rgba(0,0,0,.08);">
  <table style="width:100%; border-collapse:collapse;">
    <thead><tr>{header_cells}</tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — TAXAS HISTÓRICAS (RESUMO GERAL)
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
<h2 style="font-family:'Lufga','Inter',sans-serif; font-weight:700; color:#044d41; margin:0 0 0.25rem;">
  Taxas Históricas por Praça
</h2>
<div style="width:48px; height:4px; background:#84e115; border-radius:2px; margin:0.5rem 0 0.25rem;"></div>
<p style="font-weight:300; color:#323232; margin:0 0 1.5rem; font-size:0.9rem;">
  Valores calculados dinamicamente a partir da base de dados histórica.
</p>
""", unsafe_allow_html=True)

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    def _metric_card(label, value):
        return f"""
<div style="background:#ffffff; border-left:4px solid #84e115; border-radius:6px;
            box-shadow:0 1px 4px rgba(0,0,0,.08); padding:1rem 1.5rem;">
  <div style="font-size:0.7rem; font-weight:700; letter-spacing:1px; color:#044d41;
              text-transform:uppercase; margin-bottom:0.4rem;">{label}</div>
  <div style="font-size:1.75rem; font-weight:700; color:#044d41; line-height:1.1;">{value}</div>
</div>"""

    col_r1.markdown(
        _metric_card("Total de Registros", f"{len(df):,}".replace(",", ".")),
        unsafe_allow_html=True,
    )
    col_r2.markdown(
        _metric_card("Empreendimentos", df["empreendimento"].nunique()),
        unsafe_allow_html=True,
    )
    col_r3.markdown(
        _metric_card("Praças", df["praca"].nunique()),
        unsafe_allow_html=True,
    )
    col_r4.markdown(
        _metric_card(
            "Período",
            f"{df['mes'].min().strftime('%b/%Y')} → {df['mes'].max().strftime('%b/%Y')}",
        ),
        unsafe_allow_html=True,
    )
