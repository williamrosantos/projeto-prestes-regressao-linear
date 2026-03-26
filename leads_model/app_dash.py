"""
app_dash.py — Interface Dash para o Simulador de Leads
Prestes Construtora/Incorporadora

Para rodar localmente:
    cd leads_model && uv run --with "dash>=2.16.0,dash-bootstrap-components>=1.5.0,
    pandas>=2.0.0,openpyxl>=3.1.0,scikit-learn>=1.3.0,statsmodels>=0.14.0,
    numpy>=1.24.0,joblib>=1.3.0" python app_dash.py
"""

import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from pipeline import load_and_prepare
import modelo_a
import modelo_b

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_PATH    = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")

MESES = {
    1: "Janeiro",   2: "Fevereiro", 3: "Março",    4: "Abril",
    5: "Maio",      6: "Junho",     7: "Julho",     8: "Agosto",
    9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro",
}

# ── Dados e modelos (carregados uma vez no startup) ────────────────────────────
df = load_and_prepare(DATA_PATH)

try:
    m_a     = modelo_a.load_model(MODEL_A_PATH)
    m_b_mdl = modelo_b.load_model(MODEL_B_PATH)
except Exception:
    m_a     = modelo_a.train(df)
    m_b_mdl = modelo_b.train(df)

PRACAS_LIST = sorted(df["praca"].unique().tolist())
_emps_init  = sorted(df[df["praca"] == PRACAS_LIST[0]]["empreendimento"].unique().tolist())

# ── Paleta ─────────────────────────────────────────────────────────────────────
C = {
    "primary": "#044d41",
    "accent":  "#84e115",
    "bg":      "#f0f2f0",
    "white":   "#ffffff",
    "text":    "#323232",
    "muted":   "#888888",
    "border":  "rgba(4,77,65,0.18)",
}

# ── Componentes auxiliares ─────────────────────────────────────────────────────
def _label(text):
    return html.Div(text, style={
        "fontSize": "0.6rem", "fontWeight": "700",
        "letterSpacing": "1.2px", "textTransform": "uppercase",
        "color": C["primary"], "marginBottom": "5px",
    })


def _result_card(value_id, sub_id, label):
    return html.Div([
        html.Div(label, style={
            "fontSize": "0.58rem", "fontWeight": "700",
            "letterSpacing": "1px", "textTransform": "uppercase",
            "color": C["primary"], "marginBottom": "6px",
        }),
        html.Div(id=value_id, children="—", style={
            "fontSize": "1.5rem", "fontWeight": "700",
            "color": C["primary"], "lineHeight": "1.1",
        }),
        html.Div(id=sub_id, children="", style={
            "fontSize": "0.7rem", "color": C["muted"], "marginTop": "4px",
        }),
    ], style={
        "background": C["white"],
        "borderLeft": f"4px solid {C['accent']}",
        "borderRadius": "6px",
        "boxShadow": "0 1px 8px rgba(0,0,0,0.07)",
        "padding": "14px 16px",
        "height": "100%",
    })


def _build_table(df_t, first_col_key, first_col_label, title):
    th = {
        "padding": "9px 14px", "color": "#fff", "fontWeight": "700",
        "fontSize": "0.78rem", "background": C["primary"], "border": "none",
        "whiteSpace": "nowrap",
    }

    rows = []
    for i, row in df_t.iterrows():
        bg = C["white"] if i % 2 == 0 else "#f8f8f8"
        td = {
            "padding": "9px 14px", "fontSize": "0.82rem",
            "color": C["text"], "borderBottom": "1px solid #ebebeb",
            "background": bg, "whiteSpace": "nowrap",
        }
        cells = [html.Td(row[first_col_key], style={**td, "fontWeight": "600"})]
        if "praca" in df_t.columns and first_col_key != "praca":
            cells.append(html.Td(row["praca"], style={**td, "color": C["muted"]}))
        cells += [
            html.Td(f"R$ {row['cpl_medio']:.2f}",   style={**td, "textAlign": "center"}),
            html.Td(f"{row['taxa_qualif']:.0%}",     style={**td, "textAlign": "center"}),
            html.Td(f"{row['taxa_visita']:.0%}",     style={**td, "textAlign": "center"}),
            html.Td(f"{row['taxa_reserva']:.0%}",    style={**td, "textAlign": "center"}),
            html.Td(str(int(row["meses"])),          style={**td, "textAlign": "center"}),
        ]
        rows.append(html.Tr(cells))

    header_cells = [html.Th(first_col_label, style=th)]
    if "praca" in df_t.columns and first_col_key != "praca":
        header_cells.append(html.Th("Praça", style=th))
    header_cells += [
        html.Th("CPL Médio",     style={**th, "textAlign": "center"}),
        html.Th("Taxa Qualif.",  style={**th, "textAlign": "center"}),
        html.Th("Taxa Visita",   style={**th, "textAlign": "center"}),
        html.Th("Taxa Reserva",  style={**th, "textAlign": "center"}),
        html.Th("Meses na Base", style={**th, "textAlign": "center"}),
    ]

    return html.Div([
        html.Div(title, style={
            "fontSize": "0.6rem", "fontWeight": "700", "letterSpacing": "1.2px",
            "textTransform": "uppercase", "color": C["primary"], "marginBottom": "10px",
        }),
        html.Div(
            html.Table([
                html.Thead(html.Tr(header_cells)),
                html.Tbody(rows),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
            style={
                "borderRadius": "6px", "overflow": "hidden",
                "boxShadow": "0 1px 8px rgba(0,0,0,0.07)",
            },
        ),
    ], style={"marginTop": "28px"})


def _make_hist_table():
    df_t = (
        df.groupby("praca")
        .agg(
            cpl_medio    =("cpl",               "mean"),
            taxa_qualif  =("taxa_qualificacao",  "mean"),
            taxa_visita  =("taxa_visita",        "mean"),
            taxa_reserva =("taxa_reserva",       "mean"),
            meses        =("mes",                "count"),
        )
        .round(4)
        .reset_index()
    )
    return _build_table(df_t, "praca", "Praça", "Taxas Históricas por Praça")


def _make_emp_table():
    df_t = (
        df.groupby(["empreendimento", "praca"])
        .agg(
            cpl_medio    =("cpl",               "mean"),
            taxa_qualif  =("taxa_qualificacao",  "mean"),
            taxa_visita  =("taxa_visita",        "mean"),
            taxa_reserva =("taxa_reserva",       "mean"),
            meses        =("mes",                "count"),
        )
        .round(4)
        .reset_index()
        .sort_values(["praca", "empreendimento"])
    )
    return _build_table(df_t, "empreendimento", "Empreendimento", "Taxas Históricas por Empreendimento")


# ── Painel de inputs ───────────────────────────────────────────────────────────
input_panel = html.Div([

    html.H1("Simulador de Leads", style={
        "fontSize": "1.35rem", "fontWeight": "700",
        "color": C["primary"], "margin": "0 0 6px",
    }),
    html.Div(style={
        "width": "36px", "height": "3px",
        "background": C["accent"], "borderRadius": "2px", "marginBottom": "6px",
    }),
    html.P("Modelo preditivo · Jan/2024 → Fev/2026", style={
        "fontSize": "0.78rem", "color": C["muted"],
        "fontWeight": "300", "margin": "0 0 20px",
    }),

    _label("Praça"),
    dcc.Dropdown(
        id="praca-dd",
        options=[{"label": p, "value": p} for p in PRACAS_LIST],
        value=PRACAS_LIST[0],
        clearable=False,
        style={"marginBottom": "14px", "fontSize": "0.88rem"},
    ),

    _label("Empreendimento"),
    dcc.Dropdown(
        id="emp-dd",
        options=[{"label": e, "value": e} for e in _emps_init],
        value=_emps_init[0],
        clearable=False,
        style={"marginBottom": "4px", "fontSize": "0.88rem"},
    ),
    html.Div(id="mes-ciclo-info", style={
        "fontSize": "0.73rem", "color": C["muted"], "marginBottom": "14px",
    }),

    _label("Investimento em R$"),
    dbc.Input(
        id="investimento-input",
        type="number", min=0, step=500, value=15000,
        style={
            "marginBottom": "14px", "fontSize": "0.88rem",
            "border": f"1px solid {C['border']}",
            "background": "#f9f9f9", "color": C["text"],
        },
    ),

    _label("Mês calendário"),
    dcc.Dropdown(
        id="mes-cal-dd",
        options=[{"label": v, "value": k} for k, v in MESES.items()],
        value=3,
        clearable=False,
        style={"marginBottom": "14px", "fontSize": "0.88rem"},
    ),

    _label("Taxa de qualificação manual (%) — opcional"),
    dbc.Input(
        id="taxa-input",
        type="text",
        placeholder="Ex: 35  →  deixe vazio para usar histórico",
        style={
            "marginBottom": "20px", "fontSize": "0.88rem",
            "border": f"1px solid {C['border']}",
            "background": "#f9f9f9", "color": C["text"],
        },
    ),

    html.Button("CALCULAR", id="btn-calcular", n_clicks=0, style={
        "width": "100%", "padding": "10px 0",
        "background": f"linear-gradient(135deg, {C['primary']} 0%, #00342c 100%)",
        "color": "#fff", "fontWeight": "700", "letterSpacing": "1.5px",
        "fontSize": "0.82rem", "border": "none", "borderRadius": "6px",
        "cursor": "pointer", "textTransform": "uppercase",
    }),

    html.Div(id="input-error", style={"marginTop": "10px"}),

], style={
    "background": C["white"],
    "borderRadius": "8px",
    "padding": "22px 24px",
    "boxShadow": "0 1px 8px rgba(0,0,0,0.08)",
})


# ── Off-canvas histórico ───────────────────────────────────────────────────────
offcanvas_historico = dbc.Offcanvas(
    html.Div([
        _make_hist_table(),
        _make_emp_table(),
    ], style={"paddingBottom": "2rem"}),
    id="offcanvas-historico",
    placement="end",
    scrollable=True,
    style={"width": "min(860px, 96vw)"},
    title=html.Span("Dados Históricos", style={
        "fontSize": "1rem", "fontWeight": "700",
        "color": C["primary"], "letterSpacing": "0.5px",
    }),
)


# ── Painel de resultados ───────────────────────────────────────────────────────
results_panel = html.Div([
    html.Div([
        html.Div("Resultados", style={
            "fontSize": "0.6rem", "fontWeight": "700", "letterSpacing": "1.2px",
            "textTransform": "uppercase", "color": C["muted"],
        }),
        html.Button("Ver histórico →", id="btn-historico", n_clicks=0, style={
            "background": "transparent",
            "border": f"1px solid {C['border']}",
            "borderRadius": "4px",
            "color": C["primary"],
            "fontSize": "0.72rem",
            "fontWeight": "600",
            "letterSpacing": "0.5px",
            "padding": "4px 12px",
            "cursor": "pointer",
        }),
    ], style={
        "display": "flex", "justifyContent": "space-between",
        "alignItems": "center", "marginBottom": "14px",
    }),
    dbc.Row([
        dbc.Col(_result_card("v-leads",  "s-leads",  "Leads Estimados"),               width=6),
        dbc.Col(_result_card("v-modelo", "s-modelo", "Qualificados — Modelo Preditivo"), width=6),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(_result_card("v-taxa",   "s-taxa",   "Qualificados — Histórico da Praça"), width=6),
        dbc.Col(_result_card("v-cpl",    "s-cpl",    "CPL Estimado"),                      width=6),
    ], className="g-3"),
])


# ── App e layout ───────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap",
    ],
    title="Simulador de Leads — Prestes",
)
server = app.server  # expõe para deploy (Render, Railway, Gunicorn)

app.layout = html.Div([
    offcanvas_historico,
    html.Div([
        dbc.Row([
            dbc.Col(input_panel,   md=5),
            dbc.Col(results_panel, md=7),
        ], className="g-4 mb-2"),
    ], style={
        "maxWidth": "960px",
        "margin": "0 auto",
        "padding": "2rem 1rem 3rem",
    }),
], style={
    "minHeight": "100vh",
    "background": C["bg"],
    "fontFamily": "'Inter', sans-serif",
})


# ── Callbacks ──────────────────────────────────────────────────────────────────
@app.callback(
    Output("offcanvas-historico", "is_open"),
    Input("btn-historico", "n_clicks"),
    State("offcanvas-historico", "is_open"),
    prevent_initial_call=True,
)
def toggle_historico(_, is_open):
    return not is_open


@app.callback(
    Output("emp-dd", "options"),
    Output("emp-dd", "value"),
    Input("praca-dd", "value"),
)
def cb_empreendimentos(praca):
    emps = sorted(df[df["praca"] == praca]["empreendimento"].unique().tolist())
    return [{"label": e, "value": e} for e in emps], (emps[0] if emps else None)


@app.callback(
    Output("mes-ciclo-info", "children"),
    Input("emp-dd", "value"),
)
def cb_mes_ciclo(emp):
    if not emp:
        return ""
    subset = df[df["empreendimento"] == emp]
    mc     = int(subset["mes_ciclo"].max())
    taxa   = subset["taxa_qualificacao"].mean()
    return [
        html.Span("Mês do ciclo: ", style={"fontWeight": "600", "color": C["primary"]}),
        html.Span(f"{mc}  (calculado automaticamente)"),
        html.Br(),
        html.Span("Taxa qualif. histórica: ", style={"fontWeight": "600", "color": C["primary"]}),
        html.Span(f"{taxa:.0%}  (média do empreendimento)"),
    ]


@app.callback(
    Output("v-leads",  "children"), Output("s-leads",  "children"),
    Output("v-modelo", "children"), Output("s-modelo", "children"),
    Output("v-taxa",   "children"), Output("s-taxa",   "children"),
    Output("v-cpl",    "children"), Output("s-cpl",    "children"),
    Output("input-error", "children"),
    Input("btn-calcular", "n_clicks"),
    State("praca-dd", "value"),
    State("emp-dd",   "value"),
    State("investimento-input", "value"),
    State("mes-cal-dd", "value"),
    State("taxa-input", "value"),
    prevent_initial_call=True,
)
def cb_calcular(_, praca, emp, investimento, mes_cal, taxa_str):
    blank = ("—", "", "—", "", "—", "", "—", "")

    if not investimento or investimento <= 0:
        err = dbc.Alert("Informe um investimento maior que zero.", color="warning", className="py-2 mb-0")
        return *blank, err

    mes_ciclo = int(df[df["empreendimento"] == emp]["mes_ciclo"].max())

    taxa_manual = None
    if taxa_str and taxa_str.strip():
        try:
            taxa_manual = float(taxa_str.strip().replace(",", ".")) / 100
        except ValueError:
            pass

    leads_res = modelo_a.predict_leads(m_a, investimento, praca, mes_ciclo, mes_cal)
    leads_est = leads_res["estimativa"]

    pred_b = modelo_b.predict_qualificados(
        model_dict   = m_b_mdl,
        leads        = leads_est,
        praca        = praca,
        mes_ciclo    = mes_ciclo,
        mes_calendario = mes_cal,
        taxa_manual  = taxa_manual,
        df_historico = df,
    )

    cpl          = investimento / leads_est if leads_est > 0 else 0
    qualif_taxa  = pred_b["pred_taxa"]   or 0
    pred_modelo  = pred_b["pred_modelo"] or 0
    origem_final = pred_b["origem_taxa"] or ""

    def fmt_n(v):
        return f"{int(v):,}".replace(",", ".")

    def fmt_brl(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    sub_taxa = f"Taxa {origem_final}" if origem_final else "Taxa histórica da praça"

    return (
        fmt_n(leads_est),   "Total estimado para o período",
        fmt_n(pred_modelo), "Baseado no modelo preditivo",
        fmt_n(qualif_taxa), sub_taxa,
        fmt_brl(cpl),       "Investimento / Leads estimados",
        "",
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
