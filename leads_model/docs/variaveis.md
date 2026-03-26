# Variáveis do Modelo — Estatísticas Descritivas

> Base: Jan/2024 → Fev/2026 · **299 observações** (linhas com investimento = 0 removidas)
> Fonte: `pipeline.load_and_prepare()` aplicado sobre `data/base_de_dados.xlsx`

---

## 1. Variáveis de Investimento e Resultado

| Variável | Média | Desvio-padrão | Mín | Máx |
|---|---:|---:|---:|---:|
| Investimento Total (R$) | 8.270,07 | 3.908,27 | 654,30 | 21.566,23 |
| Leads | 245,48 | 145,55 | 9 | 895 |
| Leads Qualificados | 90,18 | 62,04 | 0 | 414 |

---

## 2. Variáveis de Funil de Vendas

| Variável | Média | Desvio-padrão | Mín | Máx |
|---|---:|---:|---:|---:|
| Visitas Agendadas | 15,64 | 12,11 | 0 | 99 |
| Visitas Realizadas | 12,32 | 10,13 | 0 | 87 |
| Reservas (total) | 10,17 | 13,02 | 0 | 86 |
| Reservas House | 4,23 | 5,91 | 0 | 65 |
| Reservas Imob | 5,95 | 9,12 | 0 | 70 |
| Reservas Digital (House) | 1,39 | 1,87 | 0 | 11 |
| Reservas Digital (Imob) | 0,66 | 1,42 | 0 | 8 |

---

## 3. Variáveis Temporais

| Variável | Média | Desvio-padrão | Mín | Máx |
|---|---:|---:|---:|---:|
| Mês do Ciclo do Empreendimento | 11,23 | 7,24 | 1 | 26 |
| Mês Calendário (1–12) | 6,34 | 3,67 | 1 | 12 |

---

## 4. Taxas de Conversão (variáveis derivadas)

| Variável | Média | Desvio-padrão | Mín | Máx |
|---|---:|---:|---:|---:|
| Taxa de Qualificação | 37,97% | 14,43% | 0,00% | 80,00% |
| Taxa de Visita | 15,80% | 11,54% | 0,00% | 100,00% |
| Taxa de Reserva | 84,48% | 88,30% | 0,00% | 700,00% |

> **Taxa de Qualificação** = Leads Qualificados / Leads
> **Taxa de Visita** = Visitas Realizadas / Leads Qualificados
> **Taxa de Reserva** = Reservas / Visitas Realizadas — pode superar 100% em meses com reservas de visitas anteriores

---

## 5. CPL — Custo por Lead

| Variável | Média | Desvio-padrão | Mín | Máx |
|---|---:|---:|---:|---:|
| CPL (R$) | 41,53 | 26,29 | 10,02 | 202,96 |

> **CPL** = Investimento / Leads

---

## 6. Variáveis Categóricas

| Variável | Tipo | Cardinalidade |
|---|---|---|
| Praça | Categórica — One-Hot Encoding | 6 praças |
| Empreendimento | Identificador — não entra no modelo | 17 empreendimentos |
