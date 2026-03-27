import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# Adicionar o diretório atual ao path para importar pipeline
sys.path.append(os.getcwd())
try:
    from pipeline import load_and_prepare
except ImportError:
    # Se rodar de dentro de 'testes', adiciona o pai
    sys.path.append(os.path.dirname(os.getcwd()))
    from pipeline import load_and_prepare

def generate_plots():
    DATA_PATH = os.path.join("data", "base_de_dados.xlsx")
    if not os.path.exists(DATA_PATH):
        # Tenta subir um nível se estiver em subpasta
        DATA_PATH = os.path.join("..", "data", "base_de_dados.xlsx")
    
    df = load_and_prepare(DATA_PATH)
    
    pracas = sorted(df["praca"].unique())
    sns.set_theme(style="whitegrid")

    for praca in pracas:
        subset = df[df["praca"] == praca].copy()
        if len(subset) < 5: 
            print(f"Pulando {praca} (Amostra insuficiente: {len(subset)})")
            continue

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Diagnóstico de Modelos — {praca}", fontsize=20, fontweight='bold', y=0.98)
        
        # ── 1. Linearidade Modelo A ────────────────────────
        sns.regplot(data=subset, x="investimento", y="leads", ax=axes[0,0], 
                    scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
        axes[0,0].set_title("Modelo A: Investimento vs Leads", fontsize=14)
        axes[0,0].set_xlabel("Investimento (R$)", fontsize=12)
        axes[0,0].set_ylabel("Leads", fontsize=12)

        # ── 2. Linearidade Modelo B ────────────────────────
        sns.regplot(data=subset, x="leads", y="leads_qualificados", ax=axes[0,1], 
                    scatter_kws={'alpha':0.5}, line_kws={'color':'green'})
        axes[0,1].set_title("Modelo B: Leads vs Qualificados", fontsize=14)
        axes[0,1].set_xlabel("Leads", fontsize=12)
        axes[0,1].set_ylabel("Qualificados", fontsize=12)

        # ── 3. Resíduos Modelo A (Heterocedasticidade) ────
        X_ols_a = sm.add_constant(subset["investimento"])
        model_a = sm.OLS(subset["leads"], X_ols_a).fit()
        pred_a = model_a.predict(X_ols_a)
        resid_a = model_a.resid
        
        axes[1,0].scatter(pred_a, resid_a, alpha=0.5)
        axes[1,0].axhline(y=0, color='red', linestyle='--')
        axes[1,0].set_title("Resíduos Modelo A", fontsize=14)
        axes[1,0].set_xlabel("Valores Previstos (Leads)", fontsize=12)
        axes[1,0].set_ylabel("Resíduos", fontsize=12)

        # ── 4. Resíduos Modelo B (Heterocedasticidade) ────
        X_ols_b = sm.add_constant(subset["leads"])
        model_b = sm.OLS(subset["leads_qualificados"], X_ols_b).fit()
        pred_b = model_b.predict(X_ols_b)
        resid_b = model_b.resid
        
        axes[1,1].scatter(pred_b, resid_b, alpha=0.5, color='green')
        axes[1,1].axhline(y=0, color='red', linestyle='--')
        axes[1,1].set_title("Resíduos Modelo B", fontsize=14)
        axes[1,1].set_xlabel("Valores Previstos (Qualificados)", fontsize=12)
        axes[1,1].set_ylabel("Resíduos", fontsize=12)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Salvar imagem (usa nome seguro sem espaços/caracteres especiais no FS se necessário, ou literal)
        # Manteremos literal conforme plano
        filename = f"diag_{praca.lower().replace(' ', '_')}.png"
        
        # Garante que salva na pasta 'testes'
        target_dir = "testes"
        if os.path.basename(os.getcwd()) == "testes":
            target_dir = "."
        
        filepath = os.path.join(target_dir, filename)
        plt.savefig(filepath, dpi=120) # Reduzi um pouco o DPI para ser mais leve
        plt.close(fig)
        print(f"Gráfico salvo: {filepath}")

if __name__ == "__main__":
    generate_plots()
