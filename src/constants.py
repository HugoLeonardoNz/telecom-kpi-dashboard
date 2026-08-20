from datetime import date

DATE_MIN = date(2024, 1, 1)
DATE_MAX = date(2025, 1, 1)

PALETTE = ["#4f8ef7", "#7c3aed", "#10b981", "#f59e0b", "#ef4444"]

# Escala de arredondamento — um degrau por nivel de superficie, e nada fora dela.
# E a mesma escala usada nos relatorios Power BI do portfolio: paleta e tipografia
# separam as pecas, o acabamento as une. Antes, esta folha tinha seis raios
# diferentes (12, 10, 8, 7, 6, 3) escolhidos um a um, e o conjunto lia como
# telas de produtos distintos coladas.
#
#   chip   marcador, tag, pilula
#   ctrl   controle: campo, botao, aba, item de menu
#   panel  cartao e painel, a maior superficie da tela
#
# O raio acompanha o tamanho da superficie: raio unico em elementos de tamanhos
# diferentes faz o pequeno parecer redondo demais e o grande, duro.
RADIUS = {"chip": 10, "ctrl": 14, "panel": 20}

COLORS = {
    "blue":   "#4f8ef7",
    "purple": "#7c3aed",
    "green":  "#10b981",
    "amber":  "#f59e0b",
    "red":    "#ef4444",
    "muted":  "#8b92a5",
    "text":   "#e2e8f0",
    "dim":    "#4b5468",
}

REGIONS   = ["Norte", "Sul", "Leste", "Oeste", "Centro"]
REGION_W  = [0.22, 0.24, 0.20, 0.18, 0.16]

PLANS     = ["Fibra 100MB", "Fibra 200MB", "Fibra 500MB", "Fibra 1GB"]
PLAN_W    = [0.33, 0.28, 0.23, 0.16]
PLAN_PRICE = {
    "Fibra 100MB": 89.90,
    "Fibra 200MB": 109.90,
    "Fibra 500MB": 139.90,
    "Fibra 1GB":   179.90,
}

REGION_SLA   = {"Norte": 91.8, "Leste": 93.2, "Oeste": 94.7, "Sul": 96.4, "Centro": 97.1}
REGION_CHURN = {"Norte": 3.7,  "Leste": 3.2,  "Oeste": 2.9,  "Sul": 2.4,  "Centro": 2.6}
