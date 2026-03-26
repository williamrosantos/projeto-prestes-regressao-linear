# Coeficientes e Interceptos dos Modelos

> Base: Jan/2024 → Fev/2026 · **299 observações**
> Algoritmo: Regressão Linear Ordinária (OLS) com One-Hot Encoding para Praça
> Categoria de referência (baseline): **Praça 1**

---

## Modelo A — Investimento → Leads

**Equação:**
```
LEADS = 172,94 + 0,016442 × INVESTIMENTO + 1,2376 × MÊS_CICLO − 3,3042 × MÊS_CAL
       − 136,94 × PRAÇA_2 − 48,08 × PRAÇA_3 − 108,50 × PRAÇA_4
       + 314,43 × PRAÇA_5 − 2,11 × PRAÇA_6
```

### Coeficientes

| Parâmetro | Coeficiente | p-valor | Significância |
|---|---:|---:|:---:|
| Intercepto (β₀) | 172,94 | < 0,0001 | ✓ |
| Investimento (β₁) | 0,016442 | < 0,0001 | ✓ |
| Mês do Ciclo (β₂) | 1,2376 | 0,1786 | — |
| Mês Calendário (β₃) | −3,3042 | 0,0464 | ✓ |
| Praça 2 (β₄) | −136,94 | < 0,0001 | ✓ |
| Praça 3 (β₅) | −48,08 | 0,0063 | ✓ |
| Praça 4 (β₆) | −108,50 | < 0,0001 | ✓ |
| Praça 5 (β₇) | +314,43 | < 0,0001 | ✓ |
| Praça 6 (β₈) | −2,11 | 0,9485 | — |

> ✓ = p < 0,05 · — = não significativo

### Métricas de Ajuste

| Parâmetro | Valor |
|---|---:|
| R² (treino) | 0,5160 |
| R² CV (média 5-fold) | 0,1206 |
| R² CV (desvio-padrão) | 0,2448 |
| MAE | 73,3 leads |
| MAPE | 41,49% |
| N observações | 299 |

---

## Modelo B — Leads → Leads Qualificados

**Equação:**
```
LEADS_QUALIF = −45,13 + 0,3412 × LEADS + 0,8824 × MÊS_CICLO + 0,8378 × MÊS_CAL
              + 44,07 × PRAÇA_2 + 49,48 × PRAÇA_3 + 46,66 × PRAÇA_4
              + 74,83 × PRAÇA_5 + 70,40 × PRAÇA_6
```

### Coeficientes

| Parâmetro | Coeficiente | p-valor | Significância |
|---|---:|---:|:---:|
| Intercepto (β₀) | −45,13 | < 0,0001 | ✓ |
| Leads (β₁) | 0,3412 | < 0,0001 | ✓ |
| Mês do Ciclo (β₂) | 0,8824 | 0,0053 | ✓ |
| Mês Calendário (β₃) | 0,8378 | 0,1587 | — |
| Praça 2 (β₄) | +44,07 | < 0,0001 | ✓ |
| Praça 3 (β₅) | +49,48 | < 0,0001 | ✓ |
| Praça 4 (β₆) | +46,66 | < 0,0001 | ✓ |
| Praça 5 (β₇) | +74,83 | < 0,0001 | ✓ |
| Praça 6 (β₈) | +70,40 | < 0,0001 | ✓ |

> ✓ = p < 0,05 · — = não significativo

### Métricas de Ajuste

| Parâmetro | Valor |
|---|---:|
| R² (treino) | 0,6534 |
| R² CV (média 5-fold) | 0,1909 |
| R² CV (desvio-padrão) | 0,5197 |
| MAE | 24,6 qualificados |
| MAPE | 56,68% |
| N observações | 299 |

---

## Interpretação dos Coeficientes

### Modelo A
- **β₁ (Investimento) = 0,016442** → cada R$ 1.000 investidos geram aproximadamente **16,4 leads** adicionais, mantidos os demais fatores constantes.
- **Praça 5 (+314,43)** é a praça com maior geração de leads em relação à Praça 1 (baseline).
- **Praça 2 (−136,94) e Praça 4 (−108,50)** geram significativamente menos leads pelo mesmo investimento.
- **Mês do ciclo** e **Praça 6** não são estatisticamente significativos neste modelo (p > 0,05).

### Modelo B
- **β₁ (Leads) = 0,3412** → a cada 100 leads gerados, estima-se **34 leads qualificados**, na média geral.
- Todas as praças têm coeficiente positivo — qualificam mais do que a Praça 1 para o mesmo volume de leads.
- **Mês calendário** não é estatisticamente significativo na qualificação (p = 0,1587).

---

## Nota sobre R² CV

O R² de cross-validation (0,12 no Modelo A e 0,19 no Modelo B) é consideravelmente menor que o R² de treino, indicando **overfitting moderado**. Os modelos capturam padrões reais, mas com variância alta entre folds — reflexo da heterogeneidade dos empreendimentos na base histórica.
