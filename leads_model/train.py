"""
train.py — Treina os modelos A e B, salva artefatos e exibe diagnóstico completo.

Uso:
    python train.py
    python train.py --data caminho/para/base.xlsx
"""

import argparse
import json
import os
import pandas as pd

from pipeline import load_and_prepare, get_summary
import modelo_a
import modelo_b


import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")


def print_section(title: str):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def print_metrics(name: str, result: dict):
    print(f"\n  [{name}]")
    print(f"  R² treino     : {result['r2_treino']:.4f}")
    print(f"  R² CV (média) : {result['r2_cv_media']:.4f} ± {result['r2_cv_std']:.4f}")
    print(f"  MAE           : {result['mae']:.1f}")
    print(f"  Observações   : {result['n_obs']}")


def main(data_path: str):
    print_section("CARREGANDO BASE")
    df = load_and_prepare(data_path)
    summary = get_summary(df)

    print(f"  Registros ativos : {summary['total_registros']}")
    print(f"  Empreendimentos  : {summary['empreendimentos']}")
    print(f"  Praças           : {summary['pracas']}")
    print(f"  Período          : {summary['periodo']}")
    print(f"  CPL médio        : R$ {summary['cpl_medio']:.2f}")
    print(f"  Taxa qualif. med : {summary['taxa_qualificacao_media']:.1%}")

    # ── Modelo A ──────────────────────────────────────────────
    print_section("TREINANDO MODELO A  (Investimento → Leads)")
    result_a = modelo_a.train(df)
    print_metrics("Modelo A", result_a)

    os.makedirs("models", exist_ok=True)
    modelo_a.save_model(result_a, MODEL_A_PATH)
    print(f"\n  Modelo salvo em: {MODEL_A_PATH}")

    # ── Modelo B ──────────────────────────────────────────────
    print_section("TREINANDO MODELO B  (Leads → Leads Qualificados)")
    result_b = modelo_b.train(df)
    print_metrics("Modelo B", result_b)

    modelo_b.save_model(result_b, MODEL_B_PATH)
    print(f"\n  Modelo salvo em: {MODEL_B_PATH}")

    # ── Exemplo de uso ────────────────────────────────────────
    print_section("EXEMPLOS DE PREDIÇÃO")

    praca_exemplo = df["praca"].value_counts().idxmax()
    mes_ciclo_ex = 6
    mes_cal_ex = 3

    # A1 — dado investimento, estimar leads
    inv_exemplo = 10_000
    leads_res = modelo_a.predict_leads(
        result_a, inv_exemplo, praca_exemplo, mes_ciclo_ex, mes_cal_ex
    )
    leads_pred = leads_res["estimativa"]
    print(f"\n  [A1] Investimento R$ {inv_exemplo:,.0f} → {leads_pred:.0f} leads estimados [Piso: {leads_res['piso']:.0f} | Teto: {leads_res['teto']:.0f}]")
    print(f"       (praça: {praca_exemplo}, mês ciclo: {mes_ciclo_ex}, mês: {mes_cal_ex})")

    # A2 — dada meta de leads, estimar investimento
    meta_leads = 200
    inv_necessario = modelo_a.predict_investimento(
        result_a, meta_leads, praca_exemplo, mes_ciclo_ex, mes_cal_ex
    )
    print(f"\n  [A2] Meta de {meta_leads} leads → R$ {inv_necessario:,.2f} estimados")

    # B — leads qualificados
    pred_b = modelo_b.predict_qualificados(
        model_dict=result_b,
        leads=leads_pred,
        praca=praca_exemplo,
        mes_ciclo=mes_ciclo_ex,
        mes_calendario=mes_cal_ex,
        df_historico=df,
    )
    print(f"\n  [B]  {leads_pred:.0f} leads → {pred_b['pred_modelo']:.0f} qualificados (modelo) [Piso: {pred_b['piso_modelo']:.0f} | Teto: {pred_b['teto_modelo']:.0f}]")
    print(f"       {leads_pred:.0f} leads → {pred_b['pred_taxa']:.0f} qualificados (taxa histórica {pred_b['taxa_usada']:.1%})")

    # ── Taxas históricas por praça ─────────────────────────────
    print_section("TAXAS HISTÓRICAS POR PRAÇA")
    taxas = df.groupby("praca").agg(
        cpl_medio=("cpl", "mean"),
        taxa_qualif=("taxa_qualificacao", "mean"),
        taxa_visita=("taxa_visita", "mean"),
        taxa_reserva=("taxa_reserva", "mean"),
        meses=("mes", "count"),
    ).round(4)

    print(taxas.to_string())

    print_section("CONCLUÍDO")
    print("  Use predict.py para predições interativas.\n")

    return result_a, result_b, df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DATA_PATH)
    args = parser.parse_args()
    main(args.data)
