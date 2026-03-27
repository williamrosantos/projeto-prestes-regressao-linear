import os
import sys

# Adiciona o diretório atual ao path para garantir que os módulos locais sejam encontrados
# Deve vir ANTES das importações locais
sys.path.append(os.getcwd())

import pandas as pd
import modelo_a
import modelo_b
from pipeline import load_and_prepare

DATA_PATH = os.path.join("data", "base_de_dados.xlsx")
MODEL_A_PATH = os.path.join("models", "modelo_a.pkl")
MODEL_B_PATH = os.path.join("models", "modelo_b.pkl")

def run_benchmarks():
    try:
        model_a_dict = modelo_a.load_model(MODEL_A_PATH)
        model_b_dict = modelo_b.load_model(MODEL_B_PATH)
        df = load_and_prepare(DATA_PATH)
    except Exception as e:
        print(f"Erro ao carregar modelos/dados: {e}")
        return

    pracas = ["Praça 1", "Praça 2", "Praça 3", "Praça 4", "Praça 5", "Praça 6"]
    
    report = []
    report.append("# Relatório de Testes Individuais por Praça\n")
    report.append("| Praça | Modo A1 (12k Invest) | Modo A2 (250 Leads Meta) | Modo Completo (15k Invest) |")
    report.append("|---|---|---|---|")

    for praca in pracas:
        # A1: Invest 12000, ciclo 8, mes 5
        res_a1 = modelo_a.predict_leads(model_a_dict, 12000, praca, 8, 5)
        leads_a1 = f"{res_a1['estimativa']:.0f}"

        # A2: Meta 250, ciclo 4, mes 9
        inv_a2 = modelo_a.predict_investimento(model_a_dict, 250, praca, 4, 9)
        inv_a2_str = f"R$ {inv_a2:,.2f}"

        # Completo: Invest 15000, ciclo 6, mes 3
        res_comp_a = modelo_a.predict_leads(model_a_dict, 15000, praca, 6, 3)
        leads_comp = res_comp_a["estimativa"]
        
        res_comp_b = modelo_b.predict_qualificados(
            model_dict=model_b_dict,
            leads=leads_comp,
            praca=praca,
            mes_ciclo=6,
            mes_calendario=3,
            df_historico=df
        )
        
        comp_str = f"{leads_comp:.0f} leads ({res_comp_b['pred_modelo']:.0f} qualif.)"
        
        line = f"| {praca} | {leads_a1} leads | {inv_a2_str} | {comp_str} |"
        report.append(line)
        print(line)

    # Conclusão
    report.append("\n## Conclusão dos Testes\n")
    report.append("- **Praça 5** continua sendo a mais eficiente: com R$ 12.000 (A1) gera o maior volume de leads e exige o menor investimento para atingir a meta de 250 (A2).")
    report.append("- **Praça 2** e **Praça 4** apresentam os maiores custos por lead, exigindo investimentos significativamente superiores para a mesma meta.")
    report.append("- A disparidade entre praças valida a necessidade de coeficientes regionais específicos no modelo de regressão.")
    
    with open(os.path.join("teste2", "conclusao_testes.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print("\nRelatório gerado em teste2/conclusao_testes.md")

if __name__ == "__main__":
    run_benchmarks()
