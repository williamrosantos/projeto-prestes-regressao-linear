# Equações do Modelo Preditivo de Leads

> Documentação formal de todas as equações utilizadas no pipeline de predição.
> Fonte dos coeficientes: regressão linear treinada sobre Jan/2024 → Fev/2026 (299 observações).

---

## 1. Variáveis de Entrada

| Símbolo | Variável | Tipo |
|---|---|---|
| `INVEST` | Investimento em mídia (R$) | Numérica contínua |
| `MÊS_CICLO` | Mês sequencial de vida do empreendimento (1 = lançamento) | Numérica inteira |
| `MÊS_CAL` | Mês calendário (1–12) | Numérica inteira |
| `PRAÇA` | Praça de atuação (1–6) | Categórica → One-Hot Encoding |

---

## 2. Engenharia de Variáveis — `pipeline.py`

As variáveis derivadas são calculadas na etapa de preparação dos dados antes do treinamento.

### 2.1 Mês do Ciclo

```
MÊS_CICLO = posição sequencial do mês dentro do histórico do empreendimento
            (ordenado por data, iniciando em 1 no primeiro mês ativo)
```

### 2.2 Taxas de Conversão

```
TAXA_QUALIFICAÇÃO  =  LEADS_QUALIFICADOS / LEADS            (se LEADS > 0, senão 0)

TAXA_VISITA        =  VISITAS_REALIZADAS / LEADS_QUALIFICADOS   (se LEADS_QUALIF > 0, senão 0)

TAXA_RESERVA       =  RESERVAS / VISITAS_REALIZADAS          (se VISITAS > 0, senão 0)
```

### 2.3 Custo por Lead Histórico

```
CPL_HISTÓRICO  =  INVESTIMENTO / LEADS      (se LEADS > 0, senão NaN)
```

---

## 3. Modelo A — Investimento → Leads

**Arquivo:** `modelo_a.py`
**Algoritmo:** Regressão Linear Ordinária (OLS) com One-Hot Encoding para `PRAÇA`

### Equação geral

```
LEADS = β₀
      + β₁ × INVESTIMENTO
      + β₂ × MÊS_CICLO
      + β₃ × MÊS_CAL
      + β₄ × PRAÇA_2
      + β₅ × PRAÇA_3
      + β₆ × PRAÇA_4
      + β₇ × PRAÇA_5
      + β₈ × PRAÇA_6
      + ε
```

> **Nota:** `PRAÇA_1` é a categoria de referência (drop="first"). Os coeficientes `β₄…β₈` representam o efeito diferencial de cada praça em relação à Praça 1.

### Intervalo de confiança (piso / teto)

```
LEADS_PISO  =  max(0,  LEADS_EST × (1 − MAPE_A))
LEADS_TETO  =          LEADS_EST × (1 + MAPE_A)
```

onde `MAPE_A` é o Mean Absolute Percentage Error calculado no treino.

### Inversão do modelo — Investimento necessário

Para encontrar o investimento dado uma meta de leads, o modelo é invertido via **busca binária**:

```
Dado:     LEADS_META
Buscar:   INVEST* tal que  Modelo_A(INVEST*) ≈ LEADS_META  (tolerância: ±1 lead)
Intervalo de busca: [0,  R$ 500.000]
```

---

## 4. Modelo B — Leads → Leads Qualificados

**Arquivo:** `modelo_b.py`
**Algoritmo:** Regressão Linear Ordinária (OLS) com One-Hot Encoding para `PRAÇA`

### Equação geral

```
LEADS_QUALIF = β₀
             + β₁ × LEADS
             + β₂ × MÊS_CICLO
             + β₃ × MÊS_CAL
             + β₄ × PRAÇA_2
             + β₅ × PRAÇA_3
             + β₆ × PRAÇA_4
             + β₇ × PRAÇA_5
             + β₈ × PRAÇA_6
             + ε
```

### Intervalo de confiança (piso / teto)

```
QUALIF_PISO  =  max(0,  QUALIF_EST × (1 − MAPE_B))
QUALIF_TETO  =          QUALIF_EST × (1 + MAPE_B)
```

---

## 5. Estimativa por Taxa de Qualificação

Alternativa ao Modelo B: aplica diretamente a taxa sobre os leads estimados.

### 5.1 Taxa manual (fornecida pelo usuário)

```
LEADS_QUALIF_TAXA  =  LEADS_EST × TAXA_MANUAL
```

### 5.2 Taxa histórica da praça (padrão quando não há input manual)

```
TAXA_HISTÓRICA_PRAÇA  =  média(TAXA_QUALIFICAÇÃO)  para todos os meses da praça

LEADS_QUALIF_TAXA  =  LEADS_EST × TAXA_HISTÓRICA_PRAÇA
```

---

## 6. CPL Implícito

Calculado a partir do investimento informado e dos leads estimados pelo Modelo A.

```
CPL_IMPLÍCITO  =  INVESTIMENTO / LEADS_EST      (se LEADS_EST > 0)
```

---

## 7. Cadeia Completa de Predição

O simulador encadeia os dois modelos em sequência:

```
INVESTIMENTO
     │
     ▼
[ Modelo A ]  →  LEADS_EST  ±  LEADS_EST × MAPE_A
                     │
                     ├──────────────────────────────────────────────────────┐
                     ▼                                                      ▼
             [ Modelo B ]                                        TAXA_QUALIFICAÇÃO
          QUALIF_EST  ±  QUALIF_EST × MAPE_B               QUALIF_TAXA = LEADS × TAXA
                     │
                     ▼
             CPL_IMPLÍCITO = INVESTIMENTO / LEADS_EST
```

---

## 8. Métricas de Qualidade (treinamento Jan/2024 → Fev/2026)

| Modelo | R² Treino | R² CV médio | MAE |
|---|---|---|---|
| A — Investimento → Leads | 0.516 | 0.121 | 73,3 leads |
| B — Leads → Qualificados | 0.653 | 0.191 | 24,6 qualificados |

> **R² CV**: média de 5-fold cross-validation — mede a capacidade de generalização.
> **MAE**: erro absoluto médio na base de treino.
