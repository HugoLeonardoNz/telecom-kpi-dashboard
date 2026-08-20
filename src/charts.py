import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .constants import COLORS, PALETTE


def apply_dark_theme(fig: go.Figure, title: str = "", height: int = 320) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["muted"], family="Inter,sans-serif", size=11),
        title=dict(text=title, font=dict(color=COLORS["text"], size=13, family="Inter")),
        margin=dict(l=12, r=12, t=44 if title else 12, b=12),
        height=height,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color=COLORS["muted"])),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color=COLORS["muted"])),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["muted"])),
    )
    return fig


def make_overview_chart(filt_m: pd.DataFrame) -> go.Figure:
    """Base ativa e churn. Duas séries, dois eixos, os dois rotulados.

    Antes havia uma terceira série aqui — "Novos Clientes", em barras, num
    `yaxis3` com `showticklabels=False`. Novos clientes é da ordem de 3 mil por
    mês e a base é da ordem de 88 mil; num eixo próprio e invisível, as barras
    subiam até o topo do gráfico e ficavam da altura da linha da base. Quem
    lesse comparando as duas alturas concluiria que a operadora troca a base
    inteira todo mês. Eixo sem rótulo é o jeito mais barato de mentir num
    gráfico, e não custa nada evitar: a série ganhou o gráfico ao lado, onde ela
    tem escala própria e legítima (ver make_movimento_chart).
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filt_m["month"], y=filt_m["active_clients"],
        name="Clientes Ativos", mode="lines",
        line=dict(color=COLORS["blue"], width=2.5),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.07)",
    ))
    fig.add_trace(go.Scatter(
        x=filt_m["month"], y=filt_m["churn_rate"],
        name="Churn Rate (%)", mode="lines+markers",
        line=dict(color=COLORS["red"], width=1.8, dash="dot"),
        marker=dict(size=5), yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title=dict(text="Clientes ativos",
                              font=dict(color=COLORS["blue"]))),
        yaxis2=dict(overlaying="y", side="right",
                    title=dict(text="Churn %", font=dict(color=COLORS["red"])),
                    gridcolor="rgba(0,0,0,0)", tickfont=dict(color=COLORS["red"]),
                    ticksuffix="%"),
    )
    return apply_dark_theme(fig, "Base ativa e churn", height=380)


def make_movimento_chart(filt_m: pd.DataFrame) -> go.Figure:
    """Entradas × saídas no mesmo eixo — é a conta que explica a linha ao lado.

    As duas séries têm a mesma unidade (clientes/mês) e a mesma ordem de
    grandeza, então dividem eixo sem distorcer nada. A leitura é a distância
    entre as barras: onde a vermelha passa a verde, a base encolheu naquele mês.
    """
    saldo = filt_m["new_clients"] - filt_m["churned"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=filt_m["month"], y=filt_m["new_clients"],
        name="Entradas", marker_color="rgba(16,185,129,0.75)",
    ))
    fig.add_trace(go.Bar(
        x=filt_m["month"], y=-filt_m["churned"],
        name="Cancelamentos", marker_color="rgba(239,68,68,0.75)",
    ))
    fig.add_trace(go.Scatter(
        x=filt_m["month"], y=saldo, name="Saldo", mode="lines+markers",
        line=dict(color=COLORS["muted"], width=2), marker=dict(size=5),
    ))
    fig.update_layout(barmode="relative",
                      yaxis=dict(title=dict(text="Clientes no mês")))
    return apply_dark_theme(fig, "Entradas × cancelamentos", height=380)


def make_nps_chart(filt_m: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=filt_m["month"], y=filt_m["nps"],
        mode="lines+markers", name="NPS",
        line=dict(color=COLORS["purple"], width=2.5),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.07)",
        marker=dict(color=COLORS["purple"], size=7),
    ))
    fig.add_hline(y=50, line_dash="dash",
                  line_color="rgba(255,255,255,0.12)",
                  annotation_text="Meta 50",
                  annotation_font_color=COLORS["muted"])
    return apply_dark_theme(fig, "NPS Score (promotores − detratores)", height=260)


def make_arpu_chart(filt_m: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=filt_m["month"], y=filt_m["arpu"],
        mode="lines+markers", name="ARPU",
        line=dict(color=COLORS["green"], width=2.5),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.07)",
        marker=dict(color=COLORS["green"], size=7),
    ))
    return apply_dark_theme(fig, "ARPU Mensal — R$/cliente (mix planos filtrado)", height=260)


def make_cohort_chart(cohort_df: pd.DataFrame) -> go.Figure:
    pivot = cohort_df.pivot(index="cohort", columns="month", values="retention")
    pivot = pivot.reindex(sorted(pivot.index))
    cols_sorted = sorted(pivot.columns)
    for i in range(len(pivot)):
        for j in range(1, len(cols_sorted)):
            c_prev, c_curr = cols_sorted[j - 1], cols_sorted[j]
            vp = pivot.iloc[i][c_prev]
            vc = pivot.iloc[i][c_curr]
            if not (np.isnan(vp) or np.isnan(vc)) and vc > vp:
                pivot.iat[i, pivot.columns.get_loc(c_curr)] = vp

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"Mês {m}" for m in pivot.columns],
        y=pivot.index.astype(str),
        colorscale=[
            [0.0, "#1e1b4b"], [0.4, "rgba(79,142,247,0.6)"],
            [0.7, "#22d3ee"], [1.0, "#10b981"],
        ],
        text=[[f"{v:.0f}%" if not np.isnan(v) else "—" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(color="#f0f2f8", size=11),
        showscale=True,
        colorbar=dict(
            title=dict(text="% Retidos", font=dict(color=COLORS["muted"])),
            tickfont=dict(color=COLORS["muted"]),
        ),
        zmin=70, zmax=100,
    ))
    return apply_dark_theme(fig, "", height=270)


def make_plan_churn_chart(plan_df_f: pd.DataFrame) -> go.Figure:
    pch = plan_df_f.sort_values("churn_rate")
    fig = go.Figure(go.Bar(
        x=pch["churn_rate"], y=pch["plan"], orientation="h",
        marker=dict(color=pch["churn_rate"],
                    colorscale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                    cmin=0.8, cmax=4.5),
        text=[f"{v:.2f}%" for v in pch["churn_rate"]],
        textposition="outside", textfont=dict(color=COLORS["muted"], size=11),
    ))
    return apply_dark_theme(fig, "", height=270)


def make_funnel_chart(funnel_x: list[int]) -> go.Figure:
    fig = go.Figure(go.Funnel(
        y=["Clientes em Risco", "Acionamento Comercial",
           "Proposta Enviada", "Negociando", "Retidos"],
        x=funnel_x,
        marker=dict(color=PALETTE),
        textinfo="value+percent initial",
        textfont=dict(color="#f0f2f8"),
    ))
    return apply_dark_theme(fig, "Funil de Recuperação — Clientes em Risco / Cancelados", height=320)


def make_mrr_chart(filt_m: pd.DataFrame) -> go.Figure:
    churn_loss = (filt_m["churned"] * filt_m["arpu"]) / 1e6
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filt_m["month"], y=filt_m["mrr"] / 1e6,
        name="MRR (R$M)", mode="lines",
        line=dict(color=COLORS["blue"], width=2.5),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.08)",
    ))
    fig.add_trace(go.Bar(
        x=filt_m["month"], y=-churn_loss,
        name="Receita Perdida (Churn)",
        marker_color="rgba(239,68,68,0.45)", yaxis="y2",
    ))
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right",
                    title=dict(text="Churn Loss (R$M)", font=dict(color=COLORS["red"])),
                    gridcolor="rgba(0,0,0,0)", tickfont=dict(color=COLORS["red"])),
    )
    return apply_dark_theme(fig, "MRR (R$ M) vs. Receita Perdida por Churn", height=320)


def make_revenue_pie(plan_df_f: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=plan_df_f["plan"], values=plan_df_f["mrr"],
        hole=0.50, marker=dict(colors=PALETTE[:len(plan_df_f)]),
        textfont=dict(color="#f0f2f8", size=11),
    ))
    fig.update_traces(textinfo="label+percent")
    return apply_dark_theme(fig, "Revenue Mix por Plano (filtrado)", height=320)


def make_region_mrr_chart(region_df_f: pd.DataFrame) -> go.Figure:
    rg = region_df_f.sort_values("mrr")
    fig = go.Figure(go.Bar(
        x=rg["mrr"] / 1e6, y=rg["region"], orientation="h",
        marker=dict(color=PALETTE[:len(rg)]),
        text=[f"R$ {v/1e6:.2f}M" for v in rg["mrr"]],
        textposition="outside", textfont=dict(color=COLORS["muted"], size=11),
    ))
    return apply_dark_theme(fig, "MRR por Região (R$ milhões)", height=280)


def make_region_arpu_chart(region_df_f: pd.DataFrame) -> go.Figure:
    rg = region_df_f.sort_values("arpu", ascending=False)
    fig = go.Figure(go.Bar(
        x=rg["arpu"], y=rg["region"], orientation="h",
        marker=dict(color=rg["arpu"], colorscale=[[0, "#7c3aed"], [1, "#4f8ef7"]]),
        text=[f"R$ {v:.2f}" for v in rg["arpu"]],
        textposition="outside", textfont=dict(color=COLORS["muted"], size=11),
    ))
    return apply_dark_theme(fig, "ARPU por Região (R$)", height=280)


def make_ticket_pie(cat_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=cat_df["category"], values=cat_df["volume"],
        hole=0.50, marker=dict(colors=PALETTE),
        textfont=dict(color="#f0f2f8", size=10),
    ))
    fig.update_traces(textinfo="label+percent")
    return apply_dark_theme(fig, "Tickets por Categoria", height=300)


def make_sla_bar_chart(region_df_f: pd.DataFrame) -> go.Figure:
    rg = region_df_f.sort_values("sla")
    c_sla = [COLORS["red"] if v < 92 else COLORS["amber"] if v < 95 else COLORS["green"]
              for v in rg["sla"]]
    fig = go.Figure(go.Bar(
        y=rg["region"], x=rg["sla"], orientation="h",
        marker_color=c_sla,
        text=[f"{v:.1f}%" for v in rg["sla"]],
        textposition="outside", textfont=dict(color=COLORS["muted"], size=11),
    ))
    fig.add_vline(x=95, line_dash="dash",
                  line_color="rgba(255,255,255,0.18)",
                  annotation_text="Meta 95%",
                  annotation_font_color=COLORS["muted"])
    return apply_dark_theme(fig, "SLA Compliance por Região (%) — filtrado", height=300)


def make_sla_trend_chart(filt_trend: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=filt_trend["month"], y=filt_trend["sla"],
        mode="lines+markers", name="SLA %",
        line=dict(color=COLORS["green"], width=2),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.07)",
        marker=dict(size=5, color=COLORS["green"]),
    ))
    fig.add_hline(y=95, line_dash="dash",
                  line_color="rgba(255,255,255,0.15)",
                  annotation_text="Meta 95%",
                  annotation_font_color=COLORS["muted"])
    return apply_dark_theme(fig, "SLA Compliance — Tendência Mensal", height=260)


def make_volume_trend_chart(filt_trend: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=filt_trend["month"], y=filt_trend["volume"],
        marker_color="rgba(79,142,247,0.55)", name="Volume",
    ))
    return apply_dark_theme(fig, "Volume de Tickets — Tendência Mensal", height=260)


def make_mttr_chart(cat_df: pd.DataFrame) -> go.Figure:
    cat_s  = cat_df.sort_values("mttr_hours")
    c_mttr = [COLORS["green"] if v <= 36 else COLORS["amber"] if v <= 60 else COLORS["red"]
               for v in cat_s["mttr_hours"]]
    fig = go.Figure(go.Bar(
        x=cat_s["mttr_hours"], y=cat_s["category"], orientation="h",
        marker_color=c_mttr,
        text=[f"{v:.0f}h" for v in cat_s["mttr_hours"]],
        textposition="outside", textfont=dict(color=COLORS["muted"], size=11),
    ))
    fig.add_vline(x=48, line_dash="dash",
                  line_color="rgba(255,255,255,0.18)",
                  annotation_text="Meta 48h",
                  annotation_font_color=COLORS["muted"])
    return apply_dark_theme(fig, "MTTR por Categoria — horas", height=260)
