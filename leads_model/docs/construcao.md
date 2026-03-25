# Como a Ferramenta Foi Criada — Passo a Passo Completo

> Documentação do processo de construção e configuração do modelo preditivo de leads.

---

## Passo 1 — Leitura dos Requisitos

O primeiro passo foi ler a conversa de especificação no Claude AI, que definia:

- **Contexto**: A Prestes precisava de uma ferramenta para planejar budget de marketing com base em dados históricos de leads
- **Duas perguntas centrais a responder**:
  - *"Quanto preciso investir para gerar X leads?"*
  - *"Com X leads, quantos vou qualificar?"*
- **Base de dados**: histórico de Jan/2024 a Fev/2026 (302 linhas, 17 empreendimentos, 6 praças)
- **Abordagem**: dois modelos de Regressão Linear encadeados

---

## Passo 2 — Mapeamento dos Arquivos Existentes

Foi feita a leitura de todos os arquivos já presentes na pasta `leads_model/`:

| Arquivo | Responsabilidade |
|---|---|
| `pipeline.py` | Leitura, limpeza e engenharia de variáveis |
| `modelo_a.py` | Modelo A: Investimento ↔ Leads |
| `modelo_b.py` | Modelo B: Leads → Leads Qualificados |
| `train.py` | Orquestra o treinamento dos dois modelos |
| `predict.py` | Interface de linha de comando para predições |
| `requirements.txt` | Dependências Python |
| `README.md` | Documentação de uso |

Todos os arquivos estavam estruturados e prontos. A etapa seguinte foi validar a base de dados.

---

## Passo 3 — Inserção da Base de Dados

O arquivo `base de dados - IA.xlsx` estava na pasta raiz do projeto. Ele foi copiado para dentro da pasta esperada pelo código:

```
Origem:  projeto-regressao-linear/base de dados - IA.xlsx
Destino: leads_model/data/base_de_dados.xlsx
```

**Comando executado:**
```powershell
Copy-Item "base de dados - IA.xlsx" -Destination "leads_model\data\base_de_dados.xlsx" -Force
```

---

## Passo 4 — Verificação da Estrutura do Excel

Antes de treinar, foi confirmado que a planilha tinha a estrutura correta esperada pelo `pipeline.py`:

- **Sheet name**: `"base dados"` ✅
- **13 colunas** na ordem correta ✅
- **Tipos de dados** compatíveis ✅

```
Colunas encontradas:
MÊS | PRAÇA | EMPREENDIMENTO2 | INVESTIMENTO TOTAL | LEADS |
LEADS QUALIFICADOS | VISITAS AGENDADAS | VISITAS REALIZADAS |
RESERVAS | RESERVAS HOUSE | RESERVAS IMOB |
RESERVAS DIGITAL (HOUSE) | RESERVAS DIGITAL (IMOB)
```

---

## Passo 5 — Instalação das Dependências

```bash
pip install pandas openpyxl scikit-learn statsmodels numpy joblib
```

Pacotes instalados com sucesso. Versões utilizadas:
- `pandas` 3.0.1
- `scikit-learn` (versão mais recente)
- `numpy` 2.4.3
- `joblib` 1.5.3
- `openpyxl`, `statsmodels`

---

## Passo 6 — Treinamento dos Modelos

```bash
python train.py
```

O script executou a seguinte sequência internamente:

### 6.1 Carregamento e preparo da base (`pipeline.py`)
1. Leu o Excel (sheet `"base dados"`)
2. Renomeou as 13 colunas para snake_case
3. Converteu a coluna `mes` para datetime
4. **Removeu linhas com investimento = 0** (ficaram 299 de 302)
5. Criou `mes_ciclo` (posição sequencial de cada empreendimento)
6. Criou variáveis derivadas: `taxa_qualificacao`, `taxa_visita`, `taxa_reserva`, `cpl`, `mes_calendario`

### 6.2 Treinamento do Modelo A (Investimento → Leads)
1. Selecionou features: `investimento`, `praca`, `mes_ciclo`, `mes_calendario`
2. Aplicou One-Hot Encoding na coluna `praca`
3. Treinou `LinearRegression` via sklearn Pipeline
4. Avaliou com Cross-Validation de 5 folds
5. Salvou o modelo em `models/modelo_a.pkl`

### 6.3 Treinamento do Modelo B (Leads → Qualificados)
1. Selecionou features: `leads`, `praca`, `mes_ciclo`, `mes_calendario`
2. Aplicou One-Hot Encoding na coluna `praca`
3. Treinou `LinearRegression` via sklearn Pipeline
4. Avaliou com Cross-Validation de 5 folds
5. Salvou o modelo em `models/modelo_b.pkl`

### 6.4 Métricas obtidas

| Modelo | R² Treino | R² CV (média) | MAE |
|---|---|---|---|
| A — Investimento → Leads | 0.5160 | 0.1206 | 73,3 leads |
| B — Leads → Qualificados | 0.6534 | 0.1909 | 24,6 qualificados |

---

## Passo 7 — Testes de Predição

Foram testados os três modos do `predict.py` para validar o funcionamento end-to-end:

### Teste 1 — Modo A1 (Investimento → Leads)
```bash
python predict.py --modo a1 --investimento 12000 --praca "Praça 1" --mes_ciclo 8 --mes 5
```
**Resultado:** `364 leads estimados` ✅

### Teste 2 — Modo A2 (Meta → Investimento)
```bash
python predict.py --modo a2 --leads_meta 250 --praca "Praça 1" --mes_ciclo 4 --mes 9
```
**Resultado:** `Investimento necessário: R$ 6.225,59` ✅

### Teste 3 — Modo Completo (Cadeia Completa)
```bash
python predict.py --modo completo --investimento 15000 --praca "Praça 1" --mes_ciclo 6 --mes 3
```
**Resultado:**
```
→ 417 leads estimados
→ 105 qualificados (modelo de regressão)
→ 109 qualificados (taxa histórica 26,2%)
→ CPL implícito: R$ 35,96
```
✅

---

## Passo 8 — Criação da Documentação

Criada a pasta `docs/` e os seguintes arquivos:

| Arquivo | Conteúdo |
|---|---|
| `docs/treinamento.md` | Detalhes técnicos do processo de treinamento, variáveis e métricas |
| `docs/uso.md` | Guia operacional: como instalar, treinar e usar os modelos |
| `docs/construcao.md` | Este documento — passo a passo da criação da ferramenta |

---

## Resumo Final

```
✅ Base de dados inserida em data/base_de_dados.xlsx
✅ Dependências instaladas
✅ Modelo A treinado e salvo (R² treino: 0.516, MAE: 73 leads)
✅ Modelo B treinado e salvo (R² treino: 0.653, MAE: 25 qualificados)
✅ Modos a1, a2 e completo testados e funcionando
✅ Documentação criada em docs/
```
