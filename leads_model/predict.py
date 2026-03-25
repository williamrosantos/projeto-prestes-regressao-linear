"""
predict.py — Interface de predição para uso operacional.

Permite responder as duas perguntas centrais sem abrir código:

  Pergunta A1: Quanto vou gerar de leads se investir X?
  Pergunta A2: Quanto preciso investir para gerar X leads?
  Pergunta B:  Quantos leads qualificados vou ter?

Uso:
    python predict.py --modo a1 --investimento 12000 --praca "Praça 1" --mes_ciclo 8 --mes 5
    python predict.py --modo a2 --leads_meta 250 --praca "Praça 3" --mes_ciclo 4 --mes 9
    python predict.py --modo completo --investimento 15000 --praca "Praça 2" --mes_ciclo 6 --mes 3
    python predict.py --modo completo --investimento 15000 --praca "Praça 2" --mes_ciclo 6 --mes 3 --taxa_qualif 0.38
"""

import argparse
import sys
import pandas as pd

from pipeline import load_and_prepare
import modelo_a
import modelo_b


import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join(BASE_DIR, "models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join(BASE_DIR, "models", "modelo_b.pkl")


def load_models():
    try:
        model_a = modelo_a.load_model(MODEL_A_PATH)
        model_b = modelo_b.load_model(MODEL_B_PATH)
    except FileNotFoundError:
        print("\n  ⚠ Modelos não encontrados. Execute primeiro: python train.py\n")
        sys.exit(1)
    return model_a, model_b


def run(args):
    model_a, model_b_model = load_models()
    df = load_and_prepare(DATA_PATH)

    praca = args.praca
    mes_ciclo = args.mes_ciclo
    mes_cal = args.mes

    print(f"\n{'─'*50}")
    print(f"  Praça        : {praca}")
    print(f"  Mês do ciclo : {mes_ciclo}")
    print(f"  Mês calendário: {mes_cal}")
    print(f"{'─'*50}")

    if args.modo == "a1":
        res = modelo_a.predict_leads(model_a, args.investimento, praca, mes_ciclo, mes_cal)
        print(f"\n  Investimento  : R$ {args.investimento:,.2f}")
        print(f"  Leads estimados: {res['estimativa']:.0f}  [Piso: {res['piso']:.0f} | Teto: {res['teto']:.0f}]")

    elif args.modo == "a2":
        investimento = modelo_a.predict_investimento(model_a, args.leads_meta, praca, mes_ciclo, mes_cal)
        print(f"\n  Meta de leads : {args.leads_meta}")
        print(f"  Investimento necessário: R$ {investimento:,.2f}")

    elif args.modo == "completo":
        # Passo 1: investimento → leads
        res_a = modelo_a.predict_leads(model_a, args.investimento, praca, mes_ciclo, mes_cal)
        leads = res_a["estimativa"]

        # Passo 2: leads → qualificados
        taxa_manual = args.taxa_qualif if args.taxa_qualif else None
        pred_b = modelo_b.predict_qualificados(
            model_dict=model_b_model,
            leads=leads,
            praca=praca,
            mes_ciclo=mes_ciclo,
            mes_calendario=mes_cal,
            taxa_manual=taxa_manual,
            df_historico=df,
        )

        # Investimento necessário para a meta reversa (se leads conhecido)
        investimento_reverso = modelo_a.predict_investimento(
            model_a, leads, praca, mes_ciclo, mes_cal
        )

        print(f"\n  ── CADEIA COMPLETA ──────────────────────────")
        print(f"  Investimento         : R$ {args.investimento:,.2f}")
        print(f"  Leads estimados      : {leads:.0f}  [Piso: {res_a['piso']:.0f} | Teto: {res_a['teto']:.0f}]")
        print(f"  Leads qualif. (modelo): {pred_b['pred_modelo']:.0f}  [Piso: {pred_b['piso_modelo']:.0f} | Teto: {pred_b['teto_modelo']:.0f}]")
        if pred_b["pred_taxa"] is not None:
            print(f"  Leads qualif. (taxa {pred_b['taxa_usada']:.1%}): {pred_b['pred_taxa']:.0f}  [{pred_b['origem_taxa']}]")
        print(f"  CPL implícito        : R$ {args.investimento / leads:.2f}" if leads > 0 else "")
        print(f"{'─'*50}")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preditor de Leads — Modelos A e B")
    parser.add_argument("--modo", choices=["a1", "a2", "completo"], required=True)
    parser.add_argument("--praca", type=str, required=True)
    parser.add_argument("--mes_ciclo", type=int, required=True, help="Mês no ciclo do empreendimento (1–26)")
    parser.add_argument("--mes", type=int, required=True, help="Mês calendário (1–12)")
    parser.add_argument("--investimento", type=float, default=None)
    parser.add_argument("--leads_meta", type=float, default=None)
    parser.add_argument("--taxa_qualif", type=float, default=None, help="Taxa de qualificação manual (ex: 0.35)")
    args = parser.parse_args()

    # Validações mínimas
    if args.modo in ("a1", "completo") and args.investimento is None:
        parser.error("--investimento é obrigatório para os modos a1 e completo")
    if args.modo == "a2" and args.leads_meta is None:
        parser.error("--leads_meta é obrigatório para o modo a2")

    run(args)
