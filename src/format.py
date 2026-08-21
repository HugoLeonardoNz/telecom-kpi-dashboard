"""
Formatacao numerica em pt-BR — fonte unica do painel.

Existe por um defeito visivel na tela: o cartao de abertura mostrava
"88.501" (ponto de milhar, pt-BR) ao lado de "R$ 121.40" e "3.30%" (ponto
decimal, en-US), e o bloco de NOC ainda trazia "1,089" com virgula de milhar.
Tres convencoes na mesma tela, e "88.501" fica ambiguo: em en-US le-se
oitenta e oito mil quinhentos e um, ou 88 virgula 501.

A causa era formatacao ad hoc em cada chamada — vinte e um f-strings com
`:,` e `:.2f` espalhados, cada um resolvendo do seu jeito. Aqui fica a regra:
milhar com ponto, decimal com virgula, sempre.
"""

from __future__ import annotations

_SENTINELA = "\x00"


def num(v: float, casas: int = 0) -> str:
    """1234567.89 -> '1.234.567,89'"""
    s = f"{v:,.{casas}f}"
    return s.replace(",", _SENTINELA).replace(".", ",").replace(_SENTINELA, ".")


def pct(v: float, casas: int = 1, sinal: bool = False) -> str:
    """3.3 -> '3,3%'. Com sinal=True, 3.3 -> '+3,3%'."""
    p = "+" if sinal and v > 0 else ""
    return f"{p}{num(v, casas)}%"


def brl(v: float, casas: int = 2) -> str:
    """1234.5 -> 'R$ 1.234,50'"""
    return "R$ " + num(v, casas)


def brl_mi(v: float, casas: int = 2) -> str:
    """9432209.99 -> 'R$ 9,43M' — para MRR, onde o centavo nao informa nada."""
    return "R$ " + num(v / 1e6, casas) + "M"
