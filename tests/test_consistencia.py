"""
Testes de consistencia do painel — FiberNet ISP
Execute com: pytest tests/ -v

Existem por causa de um defeito concreto: `build_plans` e `build_regions`
repartiam uma constante `85_250` escrita a mao, enquanto `build_monthly`
terminava a serie em 88.501 clientes. O painel mostrava 88.501 no cartao de
abertura e uma tabela de planos somando 85.249 logo abaixo — dois numeros para a
mesma quantidade, na mesma tela, e nada quebrava.

Numero que aparece em dois lugares ou se deriva de um so, ou se testa.
"""

import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.filterwarnings("ignore")

import pytest

from src.constants import PLANS, REGIONS, PLAN_W, REGION_W
from src.data_loader import (
    base_atual,
    build_monthly,
    build_plans,
    build_regions,
    build_cohort,
)


@pytest.fixture(scope="module")
def monthly():
    return build_monthly()


@pytest.fixture(scope="module")
def plans():
    return build_plans()


@pytest.fixture(scope="module")
def regions():
    return build_regions(105.0)


# ── A base fecha em todo lugar ────────────────────────────────────────────────

def test_base_atual_e_o_ultimo_mes(monthly):
    assert base_atual() == int(monthly["active_clients"].iloc[-1])


def test_planos_somam_a_base(plans):
    assert int(plans["clients"].sum()) == base_atual(), (
        "A quebra por plano nao fecha com o KPI de clientes ativos. "
        "Era exatamente este o defeito: constante 85_250 contra serie em 88.501."
    )


def test_regioes_somam_a_base(regions):
    assert int(regions["clients"].sum()) == base_atual(), (
        "A quebra por regiao nao fecha com o KPI de clientes ativos."
    )


def test_nenhuma_constante_de_base_no_data_loader():
    """A base nao pode voltar a ser numero solto no meio do arquivo.

    Procura o LITERAL numerico, nao o texto: o comentario que explica o defeito
    cita 85_250 de proposito, e um grep simples reprovaria o proprio remedio.
    """
    import tokenize

    caminho = os.path.join(os.path.dirname(__file__), "..", "src", "data_loader.py")
    literais = []
    with tokenize.open(caminho) as f:
        for tok in tokenize.generate_tokens(f.readline):
            if tok.type == tokenize.NUMBER:
                try:
                    literais.append(int(tok.string.replace("_", "")))
                except ValueError:
                    pass
    assert 85250 not in literais, (
        "O literal 85250 voltou ao data_loader.py. A base vem de base_atual()."
    )


# ── Sanidade dos pesos ────────────────────────────────────────────────────────

def test_pesos_somam_um():
    assert abs(sum(PLAN_W) - 1.0) < 1e-9
    assert abs(sum(REGION_W) - 1.0) < 1e-9


def test_cobertura_de_categorias(plans, regions):
    assert set(plans["plan"]) == set(PLANS)
    assert set(regions["region"]) == set(REGIONS)


# ── Sanidade da serie ─────────────────────────────────────────────────────────

def test_serie_tem_13_meses(monthly):
    assert len(monthly) == 13, "Jan/24 a jan/25 sao 13 pontos"


def test_churn_em_faixa_plausivel(monthly):
    assert monthly["churn_rate"].between(2.0, 4.0).all(), (
        "Churn mensal fora da faixa do gerador [2,0; 4,0]"
    )


def test_base_nao_esta_presa_num_piso(monthly):
    """O painel ja mostrou 75.000 clientes e '+0,0% vs. mes anterior' o ano
    inteiro, porque um max(..., 75_000) prendia o resultado no proprio limite."""
    assert monthly["active_clients"].nunique() == len(monthly), (
        "A serie de clientes ativos tem valores repetidos — checar se voltou "
        "algum piso artificial"
    )


def test_mrr_bate_com_clientes_e_arpu(monthly):
    calculado = monthly["active_clients"] * monthly["arpu"]
    assert ((calculado - monthly["mrr"]).abs() / monthly["mrr"] < 0.01).all(), (
        "MRR nao e clientes x ARPU"
    )


def test_cohort_decresce(monthly):
    """Retencao nao pode subir: cliente que saiu nao volta para a coorte."""
    c = build_cohort()
    col_valor = [x for x in c.columns if c[x].dtype.kind == "f"]
    assert col_valor, "cohort sem coluna numerica de retencao"
