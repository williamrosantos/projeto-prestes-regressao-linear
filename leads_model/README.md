# Modelo Preditivo de Leads — Construtora/Incorporadora

Projeto Python para responder duas perguntas estratégicas de geração de leads:

**A) Quanto preciso investir para gerar X leads?**  
**B) Com X leads e taxa Y, quantos leads qualificados terei?**

---

## Estrutura do Projeto

```
leads_model/
├── data/
│   └── base_de_dados.xlsx        ← base histórica (26 meses, 17 empreendimentos)
├── models/
│   ├── modelo_a.pkl              ← gerado após train.py
│   └── modelo_b.pkl              ← gerado após train.py
├── pipeline.py                   ← leitura, limpeza e engenharia de variáveis
├── modelo_a.py                   ← Modelo A: Investimento ↔ Leads
├── modelo_b.py                   ← Modelo B: Leads → Leads Qualificados
├── train.py                      ← treina os dois modelos e exibe diagnóstico
├── predict.py                    ← predições via linha de comando
├── requirements.txt
└── README.md
```

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Uso

### 1. Treinar os modelos

```bash
python train.py
```

Saída: métricas de R², MAE, cross-validation e exemplos de predição.

Para usar uma base diferente:
```bash
python train.py --data caminho/para/nova_base.xlsx
```

---

### 2. Predições

#### Modo A1 — Investimento → Leads
```bash
python predict.py --modo a1 \
  --investimento 12000 \
  --praca "Praça 1" \
  --mes_ciclo 8 \
  --mes 5
```

#### Modo A2 — Meta de leads → Investimento necessário
```bash
python predict.py --modo a2 \
  --leads_meta 250 \
  --praca "Praça 3" \
  --mes_ciclo 4 \
  --mes 9
```

#### Modo Completo — Cadeia Investimento → Leads → Qualificados
```bash
python predict.py --modo completo \
  --investimento 15000 \
  --praca "Praça 2" \
  --mes_ciclo 6 \
  --mes 3
```

Com taxa de qualificação manual (sobrescreve o histórico):
```bash
python predict.py --modo completo \
  --investimento 15000 \
  --praca "Praça 2" \
  --mes_ciclo 6 \
  --mes 3 \
  --taxa_qualif 0.38
```

---

## Parâmetros

| Parâmetro | Descrição | Exemplo |
|---|---|---|
| `--praca` | Nome da praça conforme a base | `"Praça 1"` |
| `--mes_ciclo` | Mês no ciclo de vida do empreendimento (1 = lançamento) | `6` |
| `--mes` | Mês calendário (1–12) | `3` |
| `--investimento` | Verba de mídia em R$ | `12000` |
| `--leads_meta` | Meta de leads a atingir | `200` |
| `--taxa_qualif` | Taxa de qualificação manual (opcional) | `0.35` |

---

## Variáveis dos Modelos

### Engenharia de variáveis (pipeline.py)
- `mes_ciclo` — posição do empreendimento no seu ciclo de vida (1 a N)
- `mes_calendario` — mês do ano (captura sazonalidade)
- `taxa_qualificacao` — leads qualificados / leads
- `taxa_visita` — visitas realizadas / leads qualificados
- `taxa_reserva` — reservas / visitas realizadas
- `cpl` — custo por lead realizado

### Modelo A
- **Features**: investimento, praça (dummy), mês do ciclo, mês calendário
- **Target**: leads
- **Inversão**: busca binária para estimar investimento dado meta de leads

### Modelo B
- **Features**: leads, praça (dummy), mês do ciclo, mês calendário
- **Target**: leads qualificados
- **Dupla estimativa**: modelo de regressão + taxa histórica/manual

---

## Interface Web (Streamlit)

Execute o simulador interativo localmente no navegador:

```bash
streamlit run app.py
```

A interface abre em `http://localhost:8501` e contém duas abas:

- **🧮 Simulador** — informe praça, mês do ciclo, mês calendário, investimento e taxa opcional; clique em **Calcular** para ver leads estimados, leads qualificados (modelo e taxa), CPL implícito
- **📊 Taxas Históricas por Praça** — tabela gerada dinamicamente com CPL médio, taxa de qualificação, taxa de visita, taxa de reserva e meses na base por praça

> Os modelos precisam estar treinados antes de abrir a interface (`python train.py`).

---

## Próximos Passos

- [ ] Adicionar intervalo de confiança nas predições
- [ ] Exportar predições para Excel
- [ ] Construir API REST (FastAPI) para integração com Power BI ou frontend
- [ ] Expandir cadeia: Leads Qualificados → Visitas → Reservas
- [ ] Incluir variáveis de caracterização do empreendimento (VGV, tipologia)