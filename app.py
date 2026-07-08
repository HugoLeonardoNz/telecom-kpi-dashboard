from datetime import date

import pandas as pd
import streamlit as st

from src.constants import (
    DATE_MIN, DATE_MAX, COLORS,
    REGIONS, REGION_W, PLANS, PLAN_W, PLAN_PRICE,
)
from src.data_loader import build_monthly, build_plans, build_regions, build_cohort, build_support
from src.charts import (
    make_overview_chart, make_nps_chart, make_arpu_chart,
    make_cohort_chart, make_plan_churn_chart, make_funnel_chart,
    make_mrr_chart, make_revenue_pie, make_region_mrr_chart, make_region_arpu_chart,
    make_ticket_pie, make_sla_bar_chart, make_sla_trend_chart,
    make_volume_trend_chart, make_mttr_chart,
)
from src.kpis import dpct, kpi_card, mini_kpi, compute_filter_scales

st.set_page_config(
    page_title="Telecom Analytics Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os as _os
_css_path = _os.path.join(_os.path.dirname(__file__), "assets", "style.css")
with open(_css_path) as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)


def main():
    if "_regions" not in st.session_state: st.session_state["_regions"] = []
    if "_plans"   not in st.session_state: st.session_state["_plans"]   = []

    monthly_df       = build_monthly()
    plan_df          = build_plans()
    cohort_df        = build_cohort()
    cat_df, trend_df = build_support()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.markdown(
        "<div style='padding:12px 0 16px'>"
        "<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#4b5468;"
        "letter-spacing:.25em;text-transform:uppercase;margin-bottom:4px'>ISP Analytics</div>"
        "<div style='font-size:16px;font-weight:700;color:#f0f2f8'>📡 FiberNet Pro</div>"
        "</div>", unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "<div style='font-size:11px;color:#64748b;text-transform:uppercase;"
        "letter-spacing:.08em;margin-bottom:6px'>Período</div>",
        unsafe_allow_html=True,
    )
    col_di, col_df = st.sidebar.columns(2)
    with col_di:
        data_inicio = st.date_input("De", value=DATE_MIN, min_value=DATE_MIN, max_value=DATE_MAX,
                                    format="DD/MM/YYYY", key="_data_inicio")
    with col_df:
        data_fim = st.date_input("Até", value=DATE_MAX, min_value=DATE_MIN, max_value=DATE_MAX,
                                  format="DD/MM/YYYY", key="_data_fim")

    if data_inicio > data_fim:
        st.sidebar.error("⚠️ Data inicial maior que a final.")
        st.stop()

    sel_regions = st.sidebar.multiselect("Região", REGIONS, default=[], placeholder="Todas as regiões", key="_regions")
    sel_plans   = st.sidebar.multiselect("Plano",  PLANS,   default=[], placeholder="Todos os planos",  key="_plans")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
        for k in ["_data_inicio", "_data_fim", "_regions", "_plans"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.sidebar.markdown("---")

    regioes_ativas = sel_regions or list(REGIONS)
    planos_ativos  = sel_plans   or list(PLANS)
    regioes_label  = (", ".join(regioes_ativas)
                      if set(regioes_ativas) != set(REGIONS) else "Todas as regiões")
    planos_label   = (", ".join(planos_ativos)
                      if set(planos_ativos) != set(PLANS) else "Todos os planos")

    _, plan_w_sum, plan_arpu, combined_scale = compute_filter_scales(
        regioes_ativas, planos_ativos, REGIONS, REGION_W, PLANS, PLAN_W, PLAN_PRICE
    )

    ts_ini = pd.Timestamp(data_inicio)
    ts_fim = pd.Timestamp(data_fim)
    mask_m     = (monthly_df["month"] >= ts_ini) & (monthly_df["month"] <= ts_fim)
    filt_m     = monthly_df[mask_m].copy()
    mask_t     = (trend_df["month"] >= ts_ini) & (trend_df["month"] <= ts_fim)
    filt_trend = trend_df[mask_t].copy()

    if 0 < combined_scale < 1.0:
        filt_m["active_clients"] = (filt_m["active_clients"] * combined_scale).round().astype(int)
        filt_m["new_clients"]    = (filt_m["new_clients"]    * combined_scale).round().astype(int)
        filt_m["churned"]        = (filt_m["churned"]        * combined_scale).round().astype(int)
        filt_m["arpu"]           = round(plan_arpu, 2)
        filt_m["mrr"]            = filt_m["active_clients"] * filt_m["arpu"]

    region_df   = build_regions(float(monthly_df["arpu"].iloc[-2]))
    region_df_f = region_df[region_df["region"].isin(regioes_ativas)].copy()
    plan_df_f   = plan_df[plan_df["plan"].isin(planos_ativos)].copy()

    cur  = filt_m.iloc[-1] if len(filt_m) > 0 else monthly_df.iloc[-2]
    prev = filt_m.iloc[-2] if len(filt_m) > 1 else cur

    d_clients = dpct(cur["active_clients"], prev["active_clients"])
    d_churn   = dpct(cur["churn_rate"],     prev["churn_rate"])
    d_arpu    = dpct(cur["arpu"],            prev["arpu"])
    d_nps     = dpct(cur["nps"],             prev["nps"])

    var_periodo = dpct(int(filt_m["active_clients"].iloc[0]),
                       int(filt_m["active_clients"].iloc[-1])) if len(filt_m) >= 2 else 0.0
    var_color = "#10b981" if var_periodo >= 0 else "#ef4444"
    var_sign  = "+" if var_periodo >= 0 else ""

    periodo_str      = f"{data_inicio.strftime('%b/%Y')} → {data_fim.strftime('%b/%Y')}"
    avg_churn_filt   = filt_m["churn_rate"].mean() if len(filt_m) else 0.0

    st.sidebar.markdown(f"""
    <div style='background:rgba(79,142,247,0.06);border:1px solid rgba(79,142,247,0.14);
         border-radius:10px;padding:14px 16px;margin-top:4px'>
      <div style='font-size:10px;color:#4b5468;letter-spacing:.1em;text-transform:uppercase;
           font-family:monospace;margin-bottom:6px'>{periodo_str}</div>
      <div style='font-size:22px;font-weight:700;font-family:monospace;color:#4f8ef7'>
        {int(cur["active_clients"]):,}
      </div>
      <div style='font-size:11px;color:#4b5468;margin-top:2px'>clientes (filtrado)</div>
      <div style='margin-top:8px;font-size:11px;color:#8b92a5'>MRR: R$ {cur["mrr"]/1e6:.2f}M</div>
      <div style='font-size:11px;color:#8b92a5'>Churn médio: {avg_churn_filt:.2f}%</div>
      <div style='margin-top:6px;font-size:11px;color:{var_color};font-weight:600'>
        {var_sign}{var_periodo:.1f}% no período
      </div>
    </div>""", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.caption("Dados 100% sintéticos · FiberNet ISP\nPortfólio · Hugo Leonardo")

    st.markdown(f"""
    <div style='margin-bottom:24px'>
      <div style='font-size:10px;color:#4b5468;letter-spacing:.3em;text-transform:uppercase;
           font-family:monospace;margin-bottom:10px'>Real-time KPI Intelligence Platform</div>
      <div style='display:flex;align-items:center;gap:14px;flex-wrap:wrap'>
        <span style='font-size:28px;font-weight:700;color:#f0f2f8;letter-spacing:-0.5px;
              font-family:Inter,sans-serif'>📡 Telecom Analytics Dashboard</span>
        <span style='display:inline-flex;align-items:center;gap:5px;
              background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.25);
              border-radius:999px;padding:4px 12px;font-size:11px;font-family:monospace;color:#10b981'>
          <span class='live-dot'>●</span>&nbsp;LIVE
        </span>
      </div>
      <div style='margin-top:6px;font-size:13px;color:#8b92a5'>
        FiberNet ISP · <span style='color:#4f8ef7;font-family:monospace'>{periodo_str}</span>
        · Hugo Leonardo
      </div>
      <div style='margin-top:16px;height:2px;
           background:linear-gradient(90deg,#4f8ef7,#7c3aed,rgba(0,0,0,0))'></div>
    </div>""", unsafe_allow_html=True)

    r_filtered = set(regioes_ativas) != set(REGIONS)
    p_filtered = set(planos_ativos)  != set(PLANS)
    if r_filtered or p_filtered:
        parts = []
        if r_filtered: parts.append(f"Regiões: **{regioes_label}**")
        if p_filtered: parts.append(f"Planos: **{planos_label}**")
        st.info(f"🔍 Filtrando por: {' · '.join(parts)}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "🔁 Retenção & Churn", "💰 Receita", "🛠️ NOC / SLA", "📤 Exportar",
    ])

    # ══ TAB 1 — OVERVIEW ══════════════════════════════════════════════════════
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi_card("Clientes Ativos", f"{int(cur['active_clients']):,}".replace(",", "."),
                           d_clients, "vs. mês ant.", "👥", COLORS["blue"])
        with c2: kpi_card("Churn Rate", f"{cur['churn_rate']:.2f}%",
                           d_churn, "vs. mês ant.", "📉", COLORS["red"], invert=True)
        with c3: kpi_card("ARPU", f"R$ {cur['arpu']:.2f}",
                           d_arpu, "vs. mês ant.", "💵", COLORS["green"])
        with c4: kpi_card("NPS Score", str(int(cur["nps"])),
                           d_nps, "vs. mês ant.", "⭐", COLORS["purple"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Evolução Mensal — Base & Churn</p>', unsafe_allow_html=True)

        if len(filt_m) > 1:
            st.plotly_chart(make_overview_chart(filt_m), use_container_width=True)
            col_nps, col_arpu_ch = st.columns(2)
            with col_nps:   st.plotly_chart(make_nps_chart(filt_m), use_container_width=True)
            with col_arpu_ch: st.plotly_chart(make_arpu_chart(filt_m), use_container_width=True)
        else:
            st.info("Selecione um intervalo com ao menos 2 meses para exibir os gráficos de evolução.")

    # ══ TAB 2 — RETENÇÃO & CHURN ══════════════════════════════════════════════
    with tab2:
        c_r1, c_r2 = st.columns([3, 2])
        with c_r1:
            st.markdown('<p class="section-label">Cohort de Retenção — % Ativos após N meses</p>', unsafe_allow_html=True)
            st.plotly_chart(make_cohort_chart(cohort_df), use_container_width=True)
            st.caption("Mês 0 = 100% (baseline). Valores sempre decrescem. Células em branco = cohort ainda jovem.")
        with c_r2:
            st.markdown('<p class="section-label">Churn Rate por Plano (filtrado)</p>', unsafe_allow_html=True)
            if len(plan_df_f):
                st.plotly_chart(make_plan_churn_chart(plan_df_f), use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Funil de Recuperação de Clientes</p>', unsafe_allow_html=True)
        scale_f  = max(combined_scale, 0.01)
        funnel_x = [int(v * scale_f) for v in [4_200, 2_800, 1_650, 890, 420]]
        st.plotly_chart(make_funnel_chart(funnel_x), use_container_width=True)

    # ══ TAB 3 — RECEITA ════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<p class="section-label">MRR & Revenue Mix</p>', unsafe_allow_html=True)
        col_rv1, col_rv2 = st.columns([3, 2])
        with col_rv1:
            if len(filt_m) > 1:
                st.plotly_chart(make_mrr_chart(filt_m), use_container_width=True)
        with col_rv2:
            if len(plan_df_f):
                st.plotly_chart(make_revenue_pie(plan_df_f), use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Performance por Região (filtrado)</p>', unsafe_allow_html=True)
        col_rg1, col_rg2 = st.columns(2)
        with col_rg1:
            if len(region_df_f):
                st.plotly_chart(make_region_mrr_chart(region_df_f), use_container_width=True)
        with col_rg2:
            if len(region_df_f):
                st.plotly_chart(make_region_arpu_chart(region_df_f), use_container_width=True)

    # ══ TAB 4 — NOC / SLA ══════════════════════════════════════════════════════
    with tab4:
        avg_sla_r = float(region_df_f["sla"].mean()) if len(region_df_f) else 0.0
        min_sla   = float(region_df_f["sla"].min())  if len(region_df_f) else 0.0
        avg_mttr  = float(cat_df["mttr_hours"].mean())
        total_t   = int(cat_df["volume"].sum())

        n1, n2, n3, n4 = st.columns(4)
        with n1:
            acc  = COLORS["green"] if avg_sla_r >= 95 else COLORS["amber"] if avg_sla_r >= 92 else COLORS["red"]
            note = "✓ Acima da meta 95%" if avg_sla_r >= 95 else "⚠ Abaixo da meta 95%"
            mini_kpi("📶", "SLA Médio (filtrado)", f"{avg_sla_r:.1f}%", note, acc)
        with n2:
            mini_kpi("⏱", "MTTR Médio", f"{avg_mttr:.0f}h", "Meta ≤ 48h",
                     COLORS["green"] if avg_mttr <= 36 else COLORS["amber"])
        with n3:
            mini_kpi("🎫", "Tickets (30d)", f"{total_t:,}", "Total abertos no período", COLORS["blue"])
        with n4:
            acc = COLORS["red"] if min_sla < 92 else COLORS["amber"] if min_sla < 95 else COLORS["green"]
            mini_kpi("📍", "Pior SLA Regional", f"{min_sla:.1f}%", "Região mais crítica", acc)

        st.markdown("<br>", unsafe_allow_html=True)
        cn1, cn2 = st.columns([2, 3])
        with cn1: st.plotly_chart(make_ticket_pie(cat_df), use_container_width=True)
        with cn2:
            if len(region_df_f):
                st.plotly_chart(make_sla_bar_chart(region_df_f), use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        ct1, ct2 = st.columns(2)
        with ct1:
            if len(filt_trend) > 1:
                st.plotly_chart(make_sla_trend_chart(filt_trend), use_container_width=True)
        with ct2:
            if len(filt_trend) > 1:
                st.plotly_chart(make_volume_trend_chart(filt_trend), use_container_width=True)

        st.markdown('<p class="section-label">MTTR por Categoria de Ticket</p>', unsafe_allow_html=True)
        st.plotly_chart(make_mttr_chart(cat_df), use_container_width=True)

    # ══ TAB 5 — EXPORTAR ══════════════════════════════════════════════════════
    with tab5:
        st.markdown('<p class="section-label">Exportar Dados & Resumo Executivo</p>', unsafe_allow_html=True)
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            st.markdown("**Seleção atual**")
            st.markdown(f"- Período: `{periodo_str}`")
            st.markdown(f"- Regiões: `{regioes_label}`")
            st.markdown(f"- Planos: `{planos_label}`")
            st.markdown("<br>", unsafe_allow_html=True)

            if len(filt_m) > 0:
                export_m = filt_m[[
                    "month_label", "active_clients", "new_clients", "churned",
                    "churn_rate", "arpu", "mrr", "nps", "tickets",
                ]].copy()
                export_m.columns = [
                    "Mês", "Clientes Ativos", "Novos", "Cancelamentos",
                    "Churn %", "ARPU (R$)", "MRR (R$)", "NPS", "Tickets",
                ]
                st.download_button("⬇ Exportar KPIs Mensais (CSV)",
                                   data=export_m.to_csv(index=False).encode("utf-8"),
                                   file_name="fibernet_kpis_mensais.csv", mime="text/csv")
            st.download_button("⬇ Exportar Dados por Plano (CSV)",
                               data=plan_df_f.to_csv(index=False).encode("utf-8"),
                               file_name="fibernet_planos.csv", mime="text/csv")
            st.download_button("⬇ Exportar Dados por Região (CSV)",
                               data=region_df_f.to_csv(index=False).encode("utf-8"),
                               file_name="fibernet_regioes.csv", mime="text/csv")

        with col_exp2:
            st.markdown("**Resumo Executivo — gerado automaticamente**")
            if len(filt_m) > 0:
                churn_trend_str = "queda" if cur["churn_rate"] < filt_m["churn_rate"].iloc[0] else "alta"
                arpu_trend_str  = "crescimento" if d_arpu >= 0 else "recuo"
                sla_avg         = filt_trend["sla"].mean() if len(filt_trend) > 0 else 0.0
                resumo = (
                    f"FiberNet ISP — Relatório de Desempenho\n"
                    f"Período  : {periodo_str}\n"
                    f"Regiões  : {regioes_label}\n"
                    f"Planos   : {planos_label}\n\n"
                    f"BASE DE CLIENTES\n"
                    f"  Clientes ativos : {int(cur['active_clients']):,}\n"
                    f"  Variação período: {var_sign}{var_periodo:.1f}%\n"
                    f"  Novos (últ. mês): {int(cur['new_clients']):,}\n\n"
                    f"CHURN & RETENÇÃO\n"
                    f"  Churn rate : {cur['churn_rate']:.2f}% (tendência de {churn_trend_str})\n"
                    f"  Cancelados : {int(cur['churned']):,} clientes no mês\n\n"
                    f"RECEITA\n"
                    f"  MRR        : R$ {cur['mrr']/1e6:.2f}M\n"
                    f"  ARPU       : R$ {cur['arpu']:.2f} ({arpu_trend_str} {abs(d_arpu):.1f}%)\n"
                    f"  MRR acum.  : R$ {filt_m['mrr'].sum()/1e6:.1f}M\n\n"
                    f"QUALIDADE & SLA\n"
                    f"  NPS médio  : {int(filt_m['nps'].mean())} pontos\n"
                    f"  SLA médio  : {sla_avg:.1f}%\n"
                    f"  Tickets    : {filt_m['tickets'].sum():,}\n\n"
                    f"Gerado automaticamente · Dados sintéticos · portfólio\n"
                )
                st.markdown(f'<div class="resumo-box">{resumo}</div>', unsafe_allow_html=True)
                st.download_button("⬇ Exportar Resumo (TXT)",
                                   data=resumo.encode("utf-8"),
                                   file_name="fibernet_resumo_executivo.txt", mime="text/plain")


main()
