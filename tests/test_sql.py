"""
Camada SQL (src/db.py) contra os mesmos numeros que o pandas ja calcula.

Existe para a mesma razao dos outros testes deste arquivo: numero que aparece
em dois lugares (aqui, pandas vs. SQL) ou se deriva de um so, ou se testa.
LAG/RANK/SUM OVER sao reimplementacao deliberada da logica que ja existe em
pandas -- o risco e as duas contas divergirem em silencio.
"""

import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.filterwarnings("ignore")

import pytest

from src.data_loader import build_monthly, build_regions
from src.db import cohort_retention_sql, monthly_mom_sql, regions_ranked_sql


def test_mom_sql_bate_com_pct_change_pandas():
    monthly = build_monthly().sort_values("month").reset_index(drop=True)
    esperado = (monthly["active_clients"].pct_change() * 100).round(2)

    sql = monthly_mom_sql()
    obtido = sql["mom_clientes_pct"]

    assert obtido.isna().iloc[0], "primeiro mes nao tem mes anterior — deve ser nulo"
    for i in range(1, len(monthly)):
        assert abs(obtido.iloc[i] - esperado.iloc[i]) < 0.01, (
            f"MoM SQL diverge do pandas no indice {i}: {obtido.iloc[i]} vs {esperado.iloc[i]}"
        )


def test_regioes_ranked_sql_bate_com_pandas():
    regions = build_regions(105.0)
    total_mrr = regions["mrr"].sum()

    sql = regions_ranked_sql()

    assert int(sql["clients"].sum()) == int(regions["clients"].sum())
    assert abs(sql["share_pct"].sum() - 100.0) < 0.1, "participacoes nao somam 100%"
    assert sql["rank_mrr"].tolist() == sorted(sql["rank_mrr"].tolist()), "ranking fora de ordem"
    assert sql.iloc[0]["mrr"] == pytest.approx(regions["mrr"].max()), (
        "rank 1 deveria ser a regiao de maior MRR"
    )
    _ = total_mrr  # usado so para deixar explicito o que a soma representa


def test_cohort_retention_sql_decresce_por_coorte():
    sql = cohort_retention_sql()
    for cohort, grupo in sql.groupby("cohort"):
        grupo = grupo.sort_values("month")
        quedas = grupo["queda_vs_mes_anterior"].dropna()
        assert (quedas <= 0).all(), (
            f"coorte {cohort} tem retencao subindo mes a mes, o que nao pode acontecer"
        )
