# Passo a Passo — Treinamento dos Modelos de Leads (Prestes)

---

## 1. Estrutura do Projeto

```
leads_model/
├── data/
│   └── base_de_dados.xlsx       ← base histórica
├── models/
│   ├── modelo_a.pkl             ← gerado no treinamento
│   └── modelo_b.pkl             ← gerado no treinamento
├── docs/
│   ├── treinamento.md           ← este documento
│   └── uso.md                   ← guia de uso operacional
├── pipeline.py                  ← leitura e preparo dos dados
├── modelo_a.py                  ← Modelo A: Investimento ↔ Leads
├── modelo_b.py                  ← Modelo B: Leads → Qualificados
├── train.py                     ← executa o treinamento completo
└── predict.py                   ← predições via linha de comando
```

---

## 2. Preparação da Base de Dados (`pipeline.py`)

A função `load_and_prepare()` executa as seguintes etapas sobre o Excel:

### 2.1 Leitura e renomeação de colunas
O Excel (`sheet: "base dados"`) tem 13 colunas que são renomeadas para nomes padronizados:

| Original | Renomeado |
|---|---|
| MÊS | `mes` |
| PRAÇA | `praca` |
| EMPREENDIMENTO2 | `empreendimento` |
| INVESTIMENTO TOTAL | `investimento` |
| LEADS | `leads` |
| LEADS QUALIFICADOS | `leads_qualificados` |
| VISITAS AGENDADAS | `visitas_agendadas` |
| VISITAS REALIZADAS | `visitas_realizadas` |
| RESERVAS | `reservas` |
| ... | ... |

### 2.2 Filtro de registros ativos
Linhas com `investimento = 0` são removidas (meses sem operação). Restaram **299 registros** dos 302 originais.

### 2.3 Engenharia de variáveis
Novas colunas criadas a partir dos dados brutos:

| Variável | Fórmula |
|---|---|
| `mes_ciclo` | Posição sequencial do mês de cada empreendimento (1 = primeiro mês ativo) |
| `mes_calendario` | Mês do ano (1–12) — captura sazonalidade |
| `taxa_qualificacao` | `leads_qualificados / leads` |
| `taxa_visita` | `visitas_realizadas / leads_qualificados` |
| `taxa_reserva` | `reservas / visitas_realizadas` |
| `cpl` | `investimento / leads` |

---

## 3. Modelo A — Investimento → Leads (`modelo_a.py`)

### 3.1 Variáveis

| Tipo | Variável |
|---|---|
| Feature numérica | `investimento`, `mes_ciclo`, `mes_calendario` |
| Feature categórica | `praca` (One-Hot Encoding) |
| **Target** | `leads` |

### 3.2 Pré-processamento
- Variáveis numéricas: passadas diretamente (`passthrough`)
- `praca`: codificada com **One-Hot Encoding** (`drop="first"`)

### 3.3 Treinamento
Algoritmo: **Regressão Linear** (`sklearn.linear_model.LinearRegression`)
Pipeline: `ColumnTransformer → LinearRegression`

### 3.4 Métricas obtidas

| Métrica | Valor |
|---|---|
| R² treino | **0.5160** |
| R² CV (5-fold, média ± std) | 0.1206 ± 0.2448 |
| MAE | **73.3 leads** |
| Observações | 299 |

### 3.5 Inversão do modelo (modo A2)
Para responder "quanto preciso investir para gerar X leads?", uma **busca binária** é aplicada sobre o modelo direto — sem precisar treinar um modelo reverso separado.

---

## 4. Modelo B — Leads → Leads Qualificados (`modelo_b.py`)

### 4.1 Variáveis

| Tipo | Variável |
|---|---|
| Feature numérica | `leads`, `mes_ciclo`, `mes_calendario` |
| Feature categórica | `praca` (One-Hot Encoding) |
| **Target** | `leads_qualificados` |

### 4.2 Treinamento
Mesma arquitetura do Modelo A: `ColumnTransformer → LinearRegression`

### 4.3 Métricas obtidas

| Métrica | Valor |
|---|---|
| R² treino | **0.6534** |
| R² CV (5-fold, média ± std) | 0.1909 ± 0.5197 |
| MAE | **24.6 leads qualificados** |
| Observações | 299 |

### 4.4 Estimativa dupla
O Modelo B retorna **duas estimativas** para comparação:
1. **Regressão linear** — aprende o padrão estatístico de qualificação
2. **Taxa histórica** — aplica a taxa média histórica da praça diretamente sobre os leads

---

## 5. Taxas Históricas por Praça

| Praça | CPL Médio (R$) | Taxa de Qualificação | Meses na base |
|---|---|---|---|
| Praça 1 | R$ 34,15 | 26,2% | 78 |
| Praça 2 | R$ 62,64 | 39,9% | 58 |
| Praça 3 | R$ 31,97 | 41,4% | 68 |
| Praça 4 | R$ 46,25 | 44,2% | 75 |
| Praça 5 | R$ 12,91 | 39,9% | 8 |
| Praça 6 | R$ 31,23 | 46,4% | 12 |

---

## 6. Sequência de Treinamento (`train.py`)

O script `train.py` executa sequencialmente:

1. `pipeline.load_and_prepare()` — carrega e prepara o DataFrame
2. `modelo_a.train(df)` — treina e avalia o Modelo A
3. Salva `models/modelo_a.pkl` via `joblib.dump()`
4. `modelo_b.train(df)` — treina e avalia o Modelo B
5. Salva `models/modelo_b.pkl` via `joblib.dump()`
6. Exibe exemplos de predição e tabela de taxas por praça

**Comando executado:**
```bash
python train.py
```

---

## 7. Exemplos de Predição Validados

### A1 — Investimento → Leads
```
Praça 1 | Mês ciclo 8 | Mês 5 | R$12.000
→ 364 leads estimados
```

### A2 — Meta de Leads → Investimento
```
Praça 1 | Mês ciclo 4 | Mês 9 | Meta: 250 leads
→ Investimento necessário: R$6.225,59
```

### Completo — Cadeia Investimento → Leads → Qualificados
```
Praça 1 | Mês ciclo 6 | Mês 3 | R$15.000
→ 417 leads estimados
→ 105 qualificados (modelo de regressão)
→ 109 qualificados (taxa histórica 26,2%)
→ CPL implícito: R$35,96
```

---

## 8. Nota sobre o R² de Cross-Validation

O R² de CV baixo (~0.12 no Modelo A) é esperado por três razões:

1. **Amostra pequena**: 299 linhas com CV de 5 folds = ~59 registros por fold de teste
2. **Alta variabilidade**: cada empreendimento tem comportamento diferente
3. **Folds aleatórios**: um fold pode conter apenas empreendimentos que o modelo nunca viu

Os modelos funcionam como **ferramenta de planejamento de budget**. A confiabilidade aumentará conforme mais dados históricos forem incorporados.
