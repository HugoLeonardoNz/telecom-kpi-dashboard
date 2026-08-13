# 📡 Telecom KPI Dashboard — FiberNet ISP

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Domain](https://img.shields.io/badge/Domain-Telecom%20%2F%20ISP-0ea5e9?style=for-the-badge)
![Status](https://img.shields.io/badge/Rodar-local%20em%202%20comandos-10b981?style=for-the-badge)

**Projeto 2 de 3 da série FiberNet Analytics.**  
Dashboard operacional em tempo real com KPIs críticos de ISP — do churn ao SLA — construído para decisão de negócio, não para relatório.

[Como rodar](#como-rodar) · [Ver Série](#-série-fibernet-analytics)

</div>

---

![Visão geral do dashboard](docs/img/overview.png)

*Aba Overview: KPIs com variação mês a mês e evolução de base, churn e novos clientes num só gráfico.*

---

## Universo FiberNet — Escala Canônica

Os 3 projetos desta série representam a **mesma empresa fictícia** em granularidades complementares:

| Granularidade | Projetos | Escala | Abrangência |
|---|---|---|---|
| **Análise Regional** | SQL Analytics Pack · Churn Predictor | 300 contratos | Região Centro-MG: Betim, Contagem, Ribeirão das Neves, Esmeraldas, Ibirité |
| **Visão Operacional Nacional** | Telecom KPI Dashboard | ~82.500 clientes | 5 regiões nacionais (Norte, Sul, Leste, Oeste, Centro) |

A divergência de escala é **intencional**: o SQL Pack e o Churn Predictor mergulham numa amostra regional de alta granularidade para análise SQL profunda e modelagem preditiva. O KPI Dashboard consolida a operação completa para monitoramento em tempo real — os mesmos padrões de negócio (churn por plano, inadimplência, MRR), em escala nacional.

---

## Contexto de Negócio

Um ISP sem visibilidade operacional centralizada toma decisões no escuro. Este dashboard entrega em uma tela única os KPIs que definem se a operação está crescendo ou contraindo: base de clientes, churn por segmento, ARPU, NPS, receita por região e desempenho de rede (SLA/MTTR).

Construído sobre o universo sintético **FiberNet** — mesmos planos, mesmas regiões e mesma lógica de negócio dos projetos [SQL Analytics Pack](https://github.com/HugoLeonardoNz/SQL-Analytics-Pack) e [Customer Churn Predictor](https://github.com/HugoLeonardoNz/churn-predictor).

---

## Funcionalidades

### 📈 Overview
- Clientes ativos, Churn Rate, ARPU e NPS com delta mês a mês
- Evolução mensal de base, churn e novos clientes (gráfico multi-eixo)
- NPS Score e ARPU com tendência mensal

### 🔁 Retenção & Churn
- **Cohort de Retenção** — heatmap trimestral com decréscimo monotônico garantido (Mês 0 = 100%)
- **Churn Rate por Plano** — correlação inversa entre preço e evasão
- **Funil de Recuperação** — do cliente em risco ao cliente retido

### 💰 Receita
- MRR mensal vs Receita perdida por churn (gráfico combinado)
- Revenue mix por plano (donut chart)
- ARPU e MRR por região

### 🛠️ NOC / SLA
- SLA médio, MTTR médio, volume de tickets e pior SLA regional
- Distribuição de tickets por categoria (Lentidão, Sem Conexão, Faturamento...)
- SLA Compliance por região com meta de 95% marcada
- Tendência mensal de SLA e volume de chamados

### 📤 Exportar
- CSV com KPIs mensais, dados por plano e dados por região
- Resumo executivo gerado automaticamente em TXT

---

## Filtros Persistentes

Todos os gráficos respondem a:
- **Período** — seletor de datas com validação de intervalo
- **Região** — seleção múltipla (vazio = todas as regiões)
- **Plano** — seleção múltipla (vazio = todos os planos)

Os filtros persistem entre abas dentro da mesma sessão.

---

## Série FiberNet Analytics

Este é o **Projeto 2 de 3** de uma série coesa sobre inteligência de dados em ISP:

| # | Projeto | Foco | Link |
|---|---------|------|------|
| 1 | [SQL Analytics Pack](https://github.com/HugoLeonardoNz/SQL-Analytics-Pack) | SQL analítico · 10 queries · insights brutos | GitHub |
| 2 | **Telecom KPI Dashboard** | BI operacional · visualização em tempo real | **Este repo** |
| 3 | [Customer Churn Predictor](https://github.com/HugoLeonardoNz/churn-predictor) | ML · RandomForest · predição e priorização de risco | GitHub |

A progressão é intencional: identificar o problema (SQL) → monitorar em escala (Dashboard) → prever e agir preventivamente (ML).

---

## Arquitetura de Módulos

```
telecom-kpi-dashboard/
├── app.py              — Entry point: CSS global, sidebar, layout das 5 abas
├── requirements.txt    — Dependências pinadas
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── constants.py    — Constantes globais (COLORS, REGIONS, PLANS, datas)
│   ├── data_loader.py  — Funções @st.cache_data: build_monthly/plans/regions/cohort/support
│   ├── charts.py       — Funções que retornam go.Figure prontas para st.plotly_chart
│   └── kpis.py         — Helpers de UI: kpi_card(), mini_kpi(), dpct(), compute_filter_scales()
└── data/
    └── README.md       — Documentação dos dados sintéticos e sementes numpy
```

**Fluxo:**  
`app.py` importa de `src/` → chama `build_*()` para obter DataFrames → aplica filtros → chama `make_*()` para obter figuras → renderiza com `st.plotly_chart`.

---

## Como Rodar

```bash
git clone https://github.com/HugoLeonardoNz/telecom-kpi-dashboard.git
cd telecom-kpi-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Acesse em `http://localhost:8501`



---

## Stack

`Python` · `Streamlit` · `Plotly` · `Pandas` · `NumPy`

---

## Autor

**Hugo Leonardo**  
Analista de Dados Pleno — SQL · Python · Power BI  
Speed Fibra · Santa Luzia, MG

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Hugo%20Leonardo-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/hugo-leonardo-data-analyst/)
[![GitHub](https://img.shields.io/badge/GitHub-HugoLeonardoNz-181717?style=flat&logo=github)](https://github.com/HugoLeonardoNz)

---

<div align="center">
<sub>Dados 100% sintéticos gerados para fins de portfólio. Nenhuma informação real de clientes foi utilizada.</sub>
</div>
