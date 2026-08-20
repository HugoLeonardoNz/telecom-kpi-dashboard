import pandas as pd
import numpy as np
import streamlit as st

from .constants import (
    REGIONS, REGION_W, REGION_SLA, REGION_CHURN,
    PLANS, PLAN_W, PLAN_PRICE,
)


@st.cache_data
def build_monthly() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    months = pd.date_range("2024-01-01", "2025-01-01", freq="MS")

    # Sazonalidade de churn: pico no verão (rescisão de contrato de temporada e
    # mudança de endereço no início do ano), vale no meio do ano. O 13º ponto é
    # jan/2025 e repete o patamar de jan/2024 — antes era 2.1, um degrau de -45%
    # contra dezembro que não vinha de lógica nenhuma e virava a única variação
    # visível do painel: o cartão de churn abria com "▼ 44,7% vs. mês anterior".
    churn_seasonal = np.array([3.2, 3.5, 3.1, 2.9, 2.7, 2.5, 2.4, 2.6, 2.8, 3.0, 3.4, 3.8, 3.3])
    churn_rates    = np.clip(churn_seasonal + rng.normal(0, 0.06, 13), 2.0, 4.0)
    arpu_base      = np.clip(np.linspace(92.0, 107.0, 13) + rng.normal(0, 1.2, 13), 89, 134)

    prom_fracs = np.clip(rng.uniform(0.44, 0.62, 13), 0.30, 0.70)
    detr_fracs = np.clip(rng.uniform(0.08, 0.18, 13), 0.05, 0.25)
    detr_fracs = np.minimum(detr_fracs, 1 - prom_fracs - 0.15)
    nps_vals   = np.clip(((prom_fracs - detr_fracs) * 100).round().astype(int), 27, 70)

    rows, clients = [], 82_500
    for i, m in enumerate(months):
        # A aquisição precisa cobrir o churn para a base andar. Com churn de
        # 2,4% a 3,8% ao mês e captação de 1,8% a 2,5%, a base só caía — e o
        # `max(..., 75_000)` que existia aqui prendia o resultado no piso.
        # O efeito era o pior possível num painel: o KPI de abertura mostrava
        # 75.000 clientes e "+0,0% vs. mês anterior" o ano inteiro, porque o
        # número não era um resultado, era o próprio limite da conta.
        new_c   = int(clients * rng.uniform(0.030, 0.042))
        churned = int(clients * churn_rates[i] / 100)
        clients = clients - churned + new_c
        rows.append({
            "month":          m,
            "month_label":    m.strftime("%b/%y"),
            "active_clients": clients,
            "new_clients":    new_c,
            "churned":        churned,
            "churn_rate":     round(float(churn_rates[i]), 2),
            "arpu":           round(float(arpu_base[i]), 2),
            "mrr":            round(clients * arpu_base[i], 2),
            "nps":            int(nps_vals[i]),
            "tickets":        int(clients * rng.uniform(0.009, 0.014)),
        })
    return pd.DataFrame(rows).sort_values("month").reset_index(drop=True)


@st.cache_data
def build_plans() -> pd.DataFrame:
    rng = np.random.default_rng(43)
    total = 85_250
    plan_churn_base = {
        "Fibra 100MB": 4.1, "Fibra 200MB": 3.3,
        "Fibra 500MB": 2.4, "Fibra 1GB":   1.8,
    }
    rows = []
    for plan, w in zip(PLANS, PLAN_W):
        n = int(total * w)
        rows.append({
            "plan":       plan,
            "clients":    n,
            "price":      PLAN_PRICE[plan],
            "churn_rate": round(max(plan_churn_base[plan] + rng.normal(0, 0.12), 0.8), 2),
            "mrr":        n * PLAN_PRICE[plan],
        })
    return pd.DataFrame(rows)


@st.cache_data
def build_regions(arpu_ref: float) -> pd.DataFrame:
    rng = np.random.default_rng(44)
    rows = []
    for region, w in zip(REGIONS, REGION_W):
        n      = int(85_250 * w)
        arpu_f = arpu_ref * rng.uniform(0.90, 1.10)
        rows.append({
            "region":     region,
            "clients":    n,
            "arpu":       round(arpu_f, 2),
            "mrr":        round(n * arpu_f, 2),
            "churn_rate": REGION_CHURN[region],
            "sla":        REGION_SLA[region],
        })
    return pd.DataFrame(rows)


@st.cache_data
def build_cohort() -> pd.DataFrame:
    rng = np.random.default_rng(45)
    cohorts      = ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"]
    avail_months = {
        "2024-Q1": [0, 1, 2, 3, 6, 9, 12],
        "2024-Q2": [0, 1, 2, 3, 6, 9],
        "2024-Q3": [0, 1, 2, 3, 6],
        "2024-Q4": [0, 1, 2, 3],
    }
    base_ret = {0: 100.0, 1: 97.8, 2: 95.6, 3: 93.1, 6: 87.5, 9: 83.2, 12: 78.8}
    rows = []
    for q_idx, cohort in enumerate(cohorts):
        bonus = q_idx * 0.5
        prev  = 100.0
        for m in avail_months[cohort]:
            if m == 0:
                val = 100.0
            else:
                noise = rng.normal(0, 0.5)
                val   = min(prev - 0.3, base_ret[m] + bonus + noise)
                val   = round(max(val, 70.0), 1)
            prev = val
            rows.append({"cohort": cohort, "month": m, "retention": val})
    return pd.DataFrame(rows).sort_values(["cohort", "month"]).reset_index(drop=True)


@st.cache_data
def build_support() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(46)
    categories = [
        "Lentidão / Instabilidade", "Sem Conexão",
        "Configuração de Equipamento", "Faturamento",
        "Cancelamento / Portabilidade",
    ]
    w_cat  = [0.32, 0.28, 0.18, 0.13, 0.09]
    mttr_vals = rng.uniform(18, 68, len(categories))
    cat_df = pd.DataFrame([
        {"category": cat, "volume": int(1_240 * w),
         "mttr_hours": round(float(mttr_vals[i]), 1)}
        for i, (cat, w) in enumerate(zip(categories, w_cat))
    ])
    months   = pd.date_range("2024-01-01", "2025-01-01", freq="MS")
    volumes  = 1_180 + rng.integers(-120, 160, len(months))
    sla_vals = rng.uniform(91.5, 98.0, len(months))
    trend_df = pd.DataFrame([
        {"month":  m,
         "volume": int(volumes[i]),
         "sla":    round(float(sla_vals[i]), 1)}
        for i, m in enumerate(months)
    ]).sort_values("month").reset_index(drop=True)
    return cat_df, trend_df
