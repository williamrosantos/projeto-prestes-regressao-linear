import os
import sys
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan

# Adicionar o diretório atual ao path para importar pipeline
sys.path.append(os.getcwd())
from pipeline import load_and_prepare

def run_diagnostics():
    DATA_PATH = os.path.join("data", "base_de_dados.xlsx")
    df = load_and_prepare(DATA_PATH)
    
    pracas = sorted(df["praca"].unique())
    results = []

    for praca in pracas:
        subset = df[df["praca"] == praca].copy()
        n = len(subset)
        if n < 5: continue # Ignorar se poucos dados

        # ── Modelo A (Investimento -> Leads) ────────────────
        X_a = subset["investimento"]
        y_a = subset["leads"]
        
        # Pearson
        r_a, _ = pearsonr(X_a, y_a)
        
        # OLS para Breusch-Pagan
        X_ols_a = sm.add_constant(X_a)
        model_a = sm.OLS(y_a, X_ols_a).fit()
        _, p_bp_a, _, _ = het_breuschpagan(model_a.resid, X_ols_a)
        
        # ── Modelo B (Leads -> Qualificados) ───────────────
        X_b = subset["leads"]
        y_b = subset["leads_qualificados"]
        
        # Pearson
        r_b, _ = pearsonr(X_b, y_b)
        
        # OLS para Breusch-Pagan
        X_ols_b = sm.add_constant(X_b)
        model_b = sm.OLS(y_b, X_ols_b).fit()
        _, p_bp_b, _, _ = het_breuschpagan(model_b.resid, X_ols_b)
        
        results.append({
            "Praça": praca,
            "N": n,
            "R (Mod A)": f"{r_a:.4f}",
            "P-BP (Mod A)": f"{p_bp_a:.4f}",
            "R (Mod B)": f"{r_b:.4f}",
            "P-BP (Mod B)": f"{p_bp_b:.4f}"
        })

    # Gerar Markdown
    report = []
    report.append("# Relatório 04 — Diagnóstico Estatístico Individual por Praça\n")
    report.append("> **Objetivo:** Auditar a linearidade (Pearson) e a variância dos resíduos (Breusch-Pagan) segmentados por região.\n")
    report.append("| Praça | Amostra (N) | Corr R (A) | BP p-valor (A) | Corr R (B) | BP p-valor (B) |")
    report.append("|---|---|---|---|---|---|")
    
    for r in results:
        status_a = "⛔ Het" if float(r["P-BP (Mod A)"]) < 0.05 else "✅ Hom"
        status_b = "⛔ Het" if float(r["P-BP (Mod B)"]) < 0.05 else "✅ Hom"
        
        report.append(f"| {r['Praça']} | {r['N']} | {r['R (Mod A)']} | {r['P-BP (Mod A)']} ({status_a}) | {r['R (Mod B)']} | {r['P-BP (Mod B)']} ({status_b}) |")

    report.append("\n## Conclusões Técnicas\n")
    report.append("- **Linearidade (R):** Valores próximos de 1 indicam forte relação linear. Praças com R baixo sugerem que outros fatores (como concorrência ou maturidade) pesam mais que o investimento.")
    report.append("- **Heterocedasticidade (BP):** Se p-valor < 0,05 (⛔ Het), a margem de erro aumenta conforme o volume cresce. Recomenda-se uso de intervalos de confiança.")
    report.append("- **Observação:** Algumas praças com amostras pequenas (N < 20) podem apresentar resultados menos estáveis nos testes de resíduos.")

    with open(os.path.join("testes", "04_diagnostico_individual_pracas.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print("Diagnóstico individual gerado com sucesso.")

if __name__ == "__main__":
    run_diagnostics()
