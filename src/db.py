"""
db.py
Camada SQL sobre os mesmos dados que o painel usa — não é um dataset paralelo.

Por que existe: as métricas de MoM, ranking e retenção do app inteiro eram
calculadas em pandas (`.shift()`, `.rank()`, soma acumulada manual). Isso
funciona, mas não é o que a maior parte das vagas de Analista de Dados pede
quando fala em "SQL avançado" — window functions rodando de verdade contra
uma base relacional. Aqui os mesmos DataFrames de `data_loader.py` são
carregados num SQLite (em memória, porque o Streamlit Cloud tem filesystem
efêmero) e consultados com LAG/RANK/SUM OVER. `tools/build_db.py` grava a
mesma base num arquivo .db, para quem quiser abrir num client SQL fora do app.
"""

from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from .data_loader import build_cohort, build_monthly, build_plans, build_regions, build_support


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    build_monthly().to_sql("monthly", conn, index=False, if_exists="replace")
    build_plans().to_sql("plans", conn, index=False, if_exists="replace")
    build_regions(105.0).to_sql("regions", conn, index=False, if_exists="replace")
    build_cohort().to_sql("cohort", conn, index=False, if_exists="replace")
    cat_df, trend_df = build_support()
    cat_df.to_sql("support_categories", conn, index=False, if_exists="replace")
    trend_df.to_sql("support_trend", conn, index=False, if_exists="replace")
    return conn


MOM_QUERY = """
SELECT
    month_label,
    active_clients,
    mrr,
    ROUND(
        (active_clients - LAG(active_clients) OVER (ORDER BY month)) * 100.0
        / LAG(active_clients) OVER (ORDER BY month), 2
    ) AS mom_clientes_pct,
    ROUND(
        (mrr - LAG(mrr) OVER (ORDER BY month)) * 100.0
        / LAG(mrr) OVER (ORDER BY month), 2
    ) AS mom_mrr_pct
FROM monthly
ORDER BY month;
""".strip()


def monthly_mom_sql() -> pd.DataFrame:
    """Variação mês a mês via LAG() — equivalente SQL do `.shift(1)` do pandas."""
    return pd.read_sql_query(MOM_QUERY, get_connection())


REGIONS_QUERY = """
SELECT
    region,
    clients,
    mrr,
    churn_rate,
    sla,
    RANK() OVER (ORDER BY mrr DESC) AS rank_mrr,
    ROUND(mrr * 100.0 / SUM(mrr) OVER (), 2) AS share_pct,
    ROUND(
        SUM(mrr) OVER (ORDER BY mrr DESC) * 100.0 / SUM(mrr) OVER (), 2
    ) AS share_acumulado_pct
FROM regions
ORDER BY mrr DESC;
""".strip()


def regions_ranked_sql() -> pd.DataFrame:
    """Ranking de região por MRR com participação acumulada — RANK() + SUM() OVER."""
    return pd.read_sql_query(REGIONS_QUERY, get_connection())


COHORT_QUERY = """
SELECT
    cohort,
    month,
    retention,
    ROUND(
        retention - LAG(retention) OVER (PARTITION BY cohort ORDER BY month), 2
    ) AS queda_vs_mes_anterior
FROM cohort
ORDER BY cohort, month;
""".strip()


def cohort_retention_sql() -> pd.DataFrame:
    """Queda de retenção mês a mês por coorte — LAG() particionado por coorte."""
    return pd.read_sql_query(COHORT_QUERY, get_connection())
