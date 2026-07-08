# Dados — Telecom KPI Dashboard

Todos os dados deste projeto são **100% sintéticos** — gerados programaticamente em `src/data_loader.py` com `numpy.random.seed` fixo para reprodutibilidade total. Nenhuma informação real de clientes foi utilizada.

## Universo FiberNet

| Dimensão | Valor |
|---|---|
| Clientes ativos (base) | ~82.500 |
| Período | Jan/2024 → Jan/2025 (13 meses) |
| Regiões | Norte, Sul, Leste, Oeste, Centro |
| Planos | Fibra 100MB, 200MB, 500MB, 1GB |
| Sementes numpy | 42, 43, 44, 45, 46 (por função) |

## Funções de geração (src/data_loader.py)

| Função | Descrição | Linhas retornadas |
|---|---|---|
| `build_monthly()` | KPIs mensais: clientes, churn, ARPU, MRR, NPS, tickets | 13 meses |
| `build_plans()` | Breakdown por plano: clientes, MRR, churn rate | 4 planos |
| `build_regions(arpu_ref)` | Breakdown por região: clientes, ARPU, MRR, SLA | 5 regiões |
| `build_cohort()` | Cohort de retenção trimestral | Q1–Q4 × meses |
| `build_support()` | Tickets por categoria + tendência mensal SLA | 5 categorias + 13 meses |

## Como reproduzir

Os dados são gerados automaticamente quando o app é iniciado via `@st.cache_data`. Não há CSVs para baixar — os DataFrames são construídos em memória a cada sessão.

```bash
streamlit run app.py
```
