# Guia de Uso — Modelos Preditivos de Leads (Prestes)

---

## Pré-requisitos

Instalar as dependências (apenas na primeira vez):
```bash
pip install -r requirements.txt
```

---

## 1. Treinar os Modelos

**Obrigatório na primeira vez** ou sempre que a base de dados for atualizada:

```bash
python train.py
```

O treinamento vai exibir:
- Resumo da base (registros, empreendimentos, praças, período)
- Métricas de R² e MAE de cada modelo
- Exemplos de predição automáticos
- Tabela de taxas históricas por praça

Para usar uma base de dados alternativa:
```bash
python train.py --data caminho/para/nova_base.xlsx
```

---

## 2. Modos de Predição

### Modo A1 — "Se eu investir X, quantos leads vou gerar?"

```bash
python predict.py --modo a1 \
  --investimento 12000 \
  --praca "Praça 1" \
  --mes_ciclo 8 \
  --mes 5
```

### Modo A2 — "Quanto preciso investir para gerar X leads?"

```bash
python predict.py --modo a2 \
  --leads_meta 250 \
  --praca "Praça 1" \
  --mes_ciclo 4 \
  --mes 9
```

### Modo Completo — Cadeia: Investimento → Leads → Qualificados

```bash
python predict.py --modo completo \
  --investimento 15000 \
  --praca "Praça 1" \
  --mes_ciclo 6 \
  --mes 3
```

Com taxa de qualificação manual (sobrescreve o histórico):
```bash
python predict.py --modo completo \
  --investimento 15000 \
  --praca "Praça 1" \
  --mes_ciclo 6 \
  --mes 3 \
  --taxa_qualif 0.38
```

---

## 3. Parâmetros

| Parâmetro | Descrição | Exemplo |
|---|---|---|
| `--praca` | Nome da praça conforme a base | `"Praça 1"` |
| `--mes_ciclo` | Mês no ciclo de vida do empreendimento (1 = lançamento) | `6` |
| `--mes` | Mês calendário (1–12) | `3` = março |
| `--investimento` | Verba de mídia em R$ | `12000` |
| `--leads_meta` | Meta de leads a atingir | `200` |
| `--taxa_qualif` | Taxa de qualificação manual (opcional) | `0.35` |

---

## 4. Praças Disponíveis na Base

| Praça | CPL Médio | Taxa Qualificação |
|---|---|---|
| Praça 1 | R$ 34,15 | 26,2% |
| Praça 2 | R$ 62,64 | 39,9% |
| Praça 3 | R$ 31,97 | 41,4% |
| Praça 4 | R$ 46,25 | 44,2% |
| Praça 5 | R$ 12,91 | 39,9% |
| Praça 6 | R$ 31,23 | 46,4% |

---

## 5. Entendendo o `mes_ciclo`

O `mes_ciclo` representa **quantos meses aquele empreendimento já está ativo** no mercado:

- `1` → lançamento (primeiro mês)
- `6` → 6 meses no mercado
- `18` → 1 ano e meio

**Como calcular:** Abra o Excel e conte a partir do primeiro mês com investimento do empreendimento.

---

## 6. Exemplos de Saída Esperada

### Modo A1
```
──────────────────────────────────────────────────
  Praça        : Praça 1
  Mês do ciclo : 8
  Mês calendário: 5
──────────────────────────────────────────────────

  Investimento   : R$ 12.000,00
  Leads estimados: 364
```

### Modo Completo
```
  ── CADEIA COMPLETA ──────────────────────────
  Investimento          : R$ 15.000,00
  Leads estimados       : 417
  Leads qualif. (modelo): 105
  Leads qualif. (taxa 26,2%): 109  [histórico (Praça 1)]
```

---

## 7. Interfaces Web

### Simulador Interativo (Streamlit)
Interface visual para simulações rápidas e visualização de taxas históricas.
```bash
streamlit run app.py
```
Acesse em: `http://localhost:8501`

### API e Dashboard Estático (FastAPI)
Para integração com outros sistemas ou uso do dashboard HTML leve.
```bash
python server.py
```
Acesse o simulador estático em: `http://127.0.0.1:8000`
Acesse a documentação da API em: `http://127.0.0.1:8000/docs`
