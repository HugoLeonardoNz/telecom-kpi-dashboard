# Audit Report — Telecom KPI Dashboard

**Data:** 2026-04-27  
**Auditor:** Hugo Leonardo  
**Versão:** v2.0 (refatorado)

---

## Resumo do Projeto

Dashboard operacional em tempo real com KPIs críticos de ISP — base de clientes, churn, ARPU, NPS, cohort de retenção, NOC/SLA e MTTR — construído sobre o universo sintético FiberNet (~82.500 clientes, 5 regiões nacionais). Interface Streamlit com filtros persistentes por período, região e plano.

Projeto 2 de 3 da série FiberNet Analytics: SQL Pack → **KPI Dashboard** → Churn Predictor.

---

## Tecnologias

- **Python 3.10+** — linguagem principal
- **Streamlit** — interface interativa com 5 abas
- **Plotly** — 15 tipos de gráficos (scatter, bar, heatmap, funnel, pie)
- **Pandas / NumPy** — geração de dados sintéticos e transformações

---

## Arquitetura de Módulos (v2.0)

```
telecom-kpi-dashboard/
├── app.py              — Entry point: CSS + sidebar + layout das 5 abas (~451 linhas)
├── src/
│   ├── constants.py    — Constantes globais (COLORS, REGIONS, PLANS, datas)
│   ├── data_loader.py  — 5 funções @st.cache_data de geração de dados
│   ├── charts.py       — 15 funções make_*() retornando go.Figure prontas
│   └── kpis.py         — kpi_card(), mini_kpi(), dpct(), compute_filter_scales()
└── data/
    └── README.md       — Documentação dos dados sintéticos e sementes numpy
```

---

## Status da Estrutura

| Item | Status |
|---|---|
| README.md real com seção de arquitetura | ✅ |
| requirements.txt | ✅ |
| .gitignore Python | ✅ |
| src/ com 4 módulos coerentes | ✅ |
| data/README.md | ✅ |
| AUDIT_REPORT.md | ✅ (criado 2026-04-27) |
| Live demo | ✅ [Streamlit Cloud](https://hugoleonardonz-telecom-kpi-dashboard.streamlit.app) |

---

## Pontos Fortes

- Cohort de retenção trimestral com decréscimo monotônico garantido por código
- Filtros persistentes entre abas via `st.session_state`
- 5 abas funcionais: Overview, Retenção & Churn, Receita, NOC/SLA, Exportar
- Resumo executivo gerado automaticamente em TXT exportável
- Dados 100% sintéticos com seeds fixos — reprodutibilidade total

---

## Melhorias Aplicadas (2026-04-27)

- **Refatoração v1 → v2:** `app.py` de 951 → 451 linhas
- Extraídos 4 módulos em `src/`: `constants.py`, `data_loader.py`, `charts.py`, `kpis.py`
- Criada `data/README.md` documentando os dados sintéticos e as sementes numpy
- Adicionado `.gitignore` Python padrão
- README atualizado com seção de arquitetura de módulos em texto
- Criado `AUDIT_REPORT.md` para rastreabilidade
