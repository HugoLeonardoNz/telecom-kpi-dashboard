import streamlit as st

from .constants import RADIUS


from .format import pct

def dpct(a: float, b: float) -> float:
    return float((a - b) / b * 100) if b and b != 0 else 0.0


def kpi_card(title: str, value: str, delta_pct: float, delta_label: str,
             color: str = "#4f8ef7", invert: bool = False) -> None:
    """Cartao de KPI: rotulo, numero grande e variacao.

    `invert=True` para metrica em que cair e bom (churn): a seta continua
    apontando para onde o numero foi, mas a cor diz se isso e bom.

    Sem icone: o rotulo ja diz o que e, e um emoji por cartao acrescenta cinco
    cores fora da paleta na faixa mais importante da tela.
    """
    is_pos  = delta_pct >= 0
    good    = is_pos if not invert else not is_pos
    d_color = "#10b981" if good else "#ef4444"
    arrow   = "▲" if is_pos else "▼"
    sign    = "+" if is_pos else ""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1f2e 0%,#1e2438 100%);
                border:1px solid rgba(79,142,247,0.15);border-radius:{RADIUS["panel"]}px;
                padding:1.25rem;position:relative;overflow:hidden;min-height:110px;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,{color},{color}55);"></div>
      <div style="color:#64748b;font-size:.68rem;text-transform:uppercase;
                  letter-spacing:.1em;margin-bottom:.5rem;
                  font-family:'JetBrains Mono',monospace;">{title}</div>
      <div style="color:#f1f5f9;font-size:1.85rem;font-weight:700;line-height:1;
                  font-family:'JetBrains Mono',monospace;">{value}</div>
      <div style="color:{d_color};font-size:.78rem;margin-top:.45rem;font-weight:500;">
        {arrow} {sign}{pct(abs(delta_pct))} {delta_label}
      </div>
    </div>""", unsafe_allow_html=True)


def mini_kpi(title: str, value: str, note: str, accent: str = "#4f8ef7") -> None:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1f2e,#1e2438);border:1px solid rgba(79,142,247,0.15);
                border-radius:{RADIUS["panel"]}px;padding:1.25rem;position:relative;overflow:hidden;min-height:110px;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{accent};"></div>
      <div style="color:#64748b;font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;
                  margin-bottom:.5rem;font-family:'JetBrains Mono',monospace;">{title}</div>
      <div style="color:#f1f5f9;font-size:1.85rem;font-weight:700;font-family:'JetBrains Mono',monospace;">{value}</div>
      <div style="color:{accent};font-size:.78rem;margin-top:.45rem;">{note}</div>
    </div>""", unsafe_allow_html=True)


def compute_filter_scales(regioes_ativas: list, planos_ativos: list,
                           regions: list, region_w: list,
                           plans: list, plan_w: list, plan_price: dict) -> tuple:
    region_scale = sum(region_w[regions.index(r)] for r in regioes_ativas)
    plan_w_sum   = sum(plan_w[plans.index(p)] for p in planos_ativos)
    plan_arpu = (
        sum(plan_w[plans.index(p)] * plan_price[p] for p in planos_ativos) / plan_w_sum
        if plan_w_sum > 0
        else sum(w * plan_price[p] for p, w in zip(plans, plan_w))
    )
    combined_scale = region_scale * plan_w_sum
    return region_scale, plan_w_sum, plan_arpu, combined_scale
