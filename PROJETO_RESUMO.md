# Resumo Geral do Projeto — Modelo Preditivo de Leads (Prestes)

Este documento consolidado oferece uma visão completa do projeto, desde sua concepção até o status atual, servindo como guia para acompanhamento da equipe.

---

## 1. Objetivo do Projeto
Desenvolver uma ferramenta baseada em inteligência de dados (Regressão Linear) para apoiar o planejamento de marketing da Prestes, respondendo:
- **Investimento necessário** para atingir metas de leads.
- **Previsão de leads qualificados** com base no investimento e praça.

---

## 2. Histórico de Desenvolvimento

### Fase 1 — Planejamento e Preparação
- **Definição de Escopo**: Foco em dois modelos encadeados (Modelo A: Investimento ↔ Leads; Modelo B: Leads → Qualificados).
- **Base de Dados**: Estruturação de dados históricos de Jan/2024 a Fev/2026 (17 empreendimentos, 6 praças).
- **Pipeline de Dados**: Criação de scripts para limpeza, tratamento de nulos (investimento zero) e engenharia de variáveis (`mes_ciclo`, `mes_calendario`).

### Fase 2 — Modelagem Estatística
- **Treinamento**: Utilização de Regressão Linear via `scikit-learn`.
- **Validação**: Testes de Pearson confirmaram correlação positiva entre investimento e leads (0.45) e forte entre leads e qualificados (0.73).
- **Métricas**:
    - Modelo A: R² de ~0.51 (Treino).
    - Modelo B: R² de ~0.65 (Treino).

### Fase 3 — Interfaces e Entrega
- **CLI (`predict.py`)**: Interface de linha de comando para predições rápidas.
- **Web App (`app.py`)**: Simulador interativo em Streamlit para uso da equipe de marketing.
- **API (`server.py`)**: Backend em FastAPI para futuras integrações (Power BI/Web).
- **Documentação**: Criação de guias técnicos e operacionais na pasta `docs/`.

---

## 3. Estrutura Atual Enxuta
Após revisão geral, o projeto foi organizado para evitar redundâncias:

```
leads_model/
├── data/               ← Base histórica oficial
├── docs/               ← Guias detalhados (uso, treinamento, construção)
├── models/             ← Binários dos modelos treinados (.pkl)
├── static/             ← Frontend estático da API
├── app.py              ← Interface Streamlit (Oficial)
├── server.py           ← API FastAPI e Servidor de Estáticos
├── train.py            ← Script de (re)treinamento
├── pipeline.py         ← Lógica de dados
├── modelo_a.py/b.py    ← Definições dos modelos
└── predict.py          ← Ferramenta de linha de comando
```

---

## 4. Principais Insights e Limitações
- **Eficiência Regional**: A Praça 5 apresentou a maior eficiência histórica (CPL baixíssimo).
- **Sazonalidade**: O mês do ciclo de vida e o mês do ano são variáveis críticas no modelo.
- **Volatilidade**: O modelo é mais preciso para investimentos médios. Em budgets muito altos, a variância aumenta.

---

## 5. Status e Próximos Passos
- [x] Modelos treinados e validados.
- [x] Simulador Streamlit funcional.
- [x] API de integração disponível.
- [ ] Exportação de predições para Excel/PDF.
- [ ] Inclusão de variáveis de caracterização do empreendimento (VGV, tipologia).

---
*Atualizado em: 16/04/2026*
