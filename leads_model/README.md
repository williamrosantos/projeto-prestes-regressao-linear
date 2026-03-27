# Projeto de Regressão Linear — Predição de Leads

Manual de execução do sistema simulador.

## 🚀 Como rodar

### 1. Backend API
Para iniciar o servidor de predição, execute os seguintes comandos no terminal:

```bash
cd leads_model
python -m uvicorn api:app --reload --port 8000
```

O servidor estará disponível em: `http://127.0.0.1:8000`.

### 2. Frontend HTML
O frontend deve ser aberto através do **Live Server** no VS Code para garantir que as chamadas de API funcionem corretamente:

1.  Abra o arquivo `leads_model/static/index.html`.
2.  Clique com o botão direito e selecione **"Open with Live Server"**.
3.  A porta padrão será `5500`.

---
**Nota**: Certifique-se de que o backend está rodando antes de realizar simulações no frontend.
