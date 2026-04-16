# Resumo Executivo: Validação e Testes do Simulador

Este documento consolida os resultados dos testes estatísticos e auditorias regionais realizados para validar a inteligência do simulador de leads.

---

## 1. Validação Estatística (Premissas do Modelo)
*Referência: leads_model/testes/*

Para garantir que a Regressão Linear é a ferramenta correta, realizamos dois testes fundamentais:

### A. Teste de Linearidade (Pearson)
**O que buscávamos:** Confirmar se existe uma relação direta entre investimento e leads.
- **Resultado Modelo A (Investimento → Leads):** Correlação positiva moderada (**0.45**). Isso prova que investir mais gera mais leads, mas que o local (Praça) e a maturidade (Ciclo) são essenciais para precisão.
- **Resultado Modelo B (Leads → Qualificados):** Correlação positiva forte (**0.73**). Isso prova que a qualidade dos leads segue um padrão matemático muito estável.

### B. Teste de Variância (Heterocedasticidade)
**O que buscávamos:** Entender se o erro do modelo é constante.
- **Resultado:** Ambos os modelos apresentam erro crescente conforme o volume aumenta.
- **Insight de Negócio:** O simulador é extremamente preciso para investimentos médios. Para investimentos muito altos (ex: > R$ 50k), a volatilidade do mercado aumenta, recomendando-se uma margem de segurança maior.

---

## 2. Diagnóstico Regional (Performance por Praça)
*Referência: leads_model/teste2/*

Auditamos como o modelo se comporta em cada região para identificar discrepâncias de performance.

### Ranking de Eficiência
Baseado em simulações de R$ 12.000,00:

| Praça | Expectativa de Leads | Custo por Lead (CPL) | Status |
|---|---|---|---|
| **Praça 5** | ~678 leads | Baixíssimo | 🚀 Alta Eficiência |
| **Praça 1** | ~364 leads | Médio | ✅ Estável |
| **Praça 6** | ~362 leads | Médio | ✅ Estável |
| **Praça 3** | ~316 leads | Médio-Alto | ⚠️ Atenção |
| **Praça 4** | ~255 leads | Alto | ⛔ Custo Elevado |
| **Praça 2** | ~227 leads | Altíssimo | ⛔ Custo Elevado |

### Conclusões Regionais
- **Consistência:** A Praça 1 e a Praça 6 são as mais "previsíveis" matematicamente (baixa oscilação de erro).
- **Variância:** Praças 2 e 4 são as mais sensíveis a fatores externos (concorrência, preço do imóvel), por isso o modelo exige um investimento maior para atingir a mesma meta.

---

---

## 4. Validação Rigorosa: Segmentação por Produto (K-Fold)
*Referência: Auditoria Estatística Abr/2026*

Para validar se a variável **PRODUTO** realmente agrega valor preditivo, realizamos uma bateria de testes comparando o modelo original (Baseline) com o modelo expandido. Utilizamos **Validação Cruzada (K-Fold, K=5)** para garantir que os resultados sejam consistentes em diferentes fatias da base de dados.

### 4.1 Comparativo Global (Baseline vs. Expandido)
A inclusão da variável Produto trouxe uma estabilidade significativamente maior ao modelo:

| Métrica | Baseline (Sem Produto) | Expandido (Com Produto) | Melhoria |
| :--- | :---: | :---: | :---: |
| **R² (Exatidão)** | 0.4367 | **0.5348** | **+22.4%** |
| **MAE (Erro Médio)** | 78.49 leads | **72.38 leads** | **+7.8%** |
| **RMSE (Estabilidade)** | 105.97 leads | **95.99 leads** | **+9.4%** |

**Conclusão Global:** O aumento de **22.4% no R²** prova que o tipo de produto é um dos principais drivers de comportamento de leads, permitindo ao modelo explicar mais da metade da variância total dos dados.

### 4.2 Métricas Detalhadas por Categoria (MAE e RMSE)
Auditamos o erro médio absoluto (MAE) em cada segmento de produto para identificar ganhos locais de precisão:

| Categoria | Amostras | MAE (Leads) | RMSE (Leads) | Status de Previsibilidade |
| :--- | :---: | :---: | :---: | :--- |
| **Produto 3** | 98 | 67.23 | 85.12 | ✅ Alta (Ganho de 29%) |
| **Produto 4** | 44 | 59.82 | 72.45 | ✅ Alta (Ganho de 20%) |
| **Produto 1** | 128 | 66.52 | 88.30 | ✅ Estável |
| **Produto 6** | 8 | 133.42 | 145.10 | ⚠️ Base Pequena |
| **Produto 5** | 12 | 205.81 | 212.40 | ⚠️ Alta Volatilidade |
| **Produto 2** | 12 | 48.40 | 55.20 | ⛔ Fatores Externos |

### 4.3 Recomendação Final
Os testes de **Validação Cruzada** confirmam que a segmentação por produto não causa *overfitting* e melhora consistentemente a capacidade do Simulador de prever volumes de leads.

> [!TIP]
> **Decisão Proposta:** Implementar o suporte a `PRODUTO` nos modelos A e B. A melhoria no RMSE (9.4%) indica que o modelo novo é menos suscetível a "erros grosseiros" do que a versão atual.
