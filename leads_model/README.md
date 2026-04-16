# Lead Predictor — Prestes (Modelo e Scripts)

Este diretório contém a lógica de processamento, treinamento e predição dos modelos de leads da Prestes.

> [!TIP]
> Para uma visão completa do histórico, métricas e status do projeto, consulte o arquivo **[PROJETO_RESUMO.md](../PROJETO_RESUMO.md)** na raiz.

---

## 🚀 Como Executar

O projeto possui duas interfaces principais:

### 1. Simulador Interativo (Oficial)
Recomendado para simulações rápidas pela equipe de marketing.
```bash
streamlit run app.py
```

### 2. API de Integração
Servidor FastAPI que disponibiliza endpoints para outros sistemas e serve o dashboard estático.
```bash
python server.py
```

### 3. Linha de Comando (CLI)
Para predições rápidas diretamente no terminal:
```bash
python predict.py --modo completo --investimento 15000 --praca "Praça 1" --mes_ciclo 6 --mes 3
```

---

## 🛠️ Manutenção

Sempre que a base de dados em `data/` for alterada, execute o retreinamento:
```bash
python train.py
```

---

## 📂 Pasta de Documentação
Para guias detalhados, consulte a pasta **[docs/](./docs/)**:
- [Uso Operacional](./docs/uso.md)
- [Detalhes do Treinamento](./docs/treinamento.md)
- [Passo a Passo de Construção](./docs/construcao.md)
