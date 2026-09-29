import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union

def render_metric_card(title: str, value: str, delta: str = None, delta_type: str = "positive"):
    """Renderiza um cartão visual de métrica."""
    delta_html = ""
    if delta:
        css_class = "metric-delta-positive" if delta_type == "positive" else "metric-delta-negative"
        delta_html = f'<div class="{css_class}">{delta}</div>'
    
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def plot_segment_distribution(segment_data: Dict[str, float]):
    """Gráfico de Rosca de Alocação por Segmento."""
    if not segment_data or sum(segment_data.values()) == 0:
        st.info("Sem dados suficientes para o gráfico de segmentos.")
        return

    df = pd.DataFrame([
        {"Segmento": k, "Valor (R$)": v}
        for k, v in segment_data.items() if v > 0
    ])

    fig = px.pie(
        df,
        values="Valor (R$)",
        names="Segmento",
        hole=0.45,
        title="<b>Distribuição por Segmento</b>",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>"
    )
    fig.update_layout(
        margin=dict(t=50, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_asset_distribution(items: List[Dict[str, Any]]):
    """Gráfico de Rosca de Alocação por Ativo/Ticker."""
    if not items:
        return

    df = pd.DataFrame(items)
    fig = px.pie(
        df,
        values="current_value",
        names="ticker",
        hole=0.45,
        title="<b>Participação por Ativo na Carteira</b>",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Peso: %{percent}<extra></extra>"
    )
    fig.update_layout(
        margin=dict(t=50, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_pvp_vs_dy(items: List[Dict[str, Any]]):
    """
    Gráfico de Dispersão: Matriz de Oportunidade FIIs (P/VP vs Dividend Yield).
    Ideal para identificar fundos descontados que pagam bons dividendos.
    """
    valid_items = [i for i in items if i.get("pvp") and i.get("dy_12m")]
    if not valid_items:
        st.info("Aguardando cotações com P/VP e Dividend Yield para exibir a matriz.")
        return

    df = pd.DataFrame(valid_items)

    fig = px.scatter(
        df,
        x="pvp",
        y="dy_12m",
        text="ticker",
        size="current_value",
        color="segment",
        title="<b>Matriz de Oportunidades: P/VP vs. Dividend Yield (12M)</b>",
        labels={"pvp": "P/VP (Preço / Valor Patrimonial)", "dy_12m": "Dividend Yield 12M (%)"},
        hover_data=["quantity", "current_price", "monthly_income_est"]
    )

    # Linha de referência P/VP = 1.0 (Preço Justo)
    fig.add_vline(x=1.0, line_dash="dash", line_color="rgba(150, 150, 150, 0.7)", annotation_text="Preço Justo (P/VP = 1.0)")

    fig.update_traces(
        textposition="top center",
        marker=dict(sizemin=10, opacity=0.85, line=dict(width=1, color="DarkSlateGrey"))
    )
    fig.update_layout(
        margin=dict(t=50, b=30, l=30, r=30),
        xaxis=dict(title="P/VP (Menor que 1.0 = Desconto)"),
        yaxis=dict(title="Dividend Yield Anualizado (%)")
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_monthly_income_bar(items: List[Dict[str, Any]]):
    """Gráfico de barras da renda passiva mensal estimada por FII."""
    valid_items = [i for i in items if i.get("monthly_income_est", 0) > 0]
    if not valid_items:
        return

    df = pd.DataFrame(valid_items).sort_values("monthly_income_est", ascending=True)

    fig = px.bar(
        df,
        x="monthly_income_est",
        y="ticker",
        orientation="h",
        title="<b>Renda Mensal Estimada por Fundo (R$)</b>",
        labels={"monthly_income_est": "Renda Mensal (R$)", "ticker": "FII"},
        color="monthly_income_est",
        color_continuous_scale="Blues"
    )
    fig.update_traces(
        texttemplate="R$ %{x:,.2f}",
        textposition="outside"
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=50, b=30, l=30, r=60)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_valuation_vs_quality_scatter(df_sector: pd.DataFrame, selected_tickers: Optional[List[str]] = None):
    """
    Gráfico de Dispersão 2x2: Valuation (P/VP) vs Qualidade Fundamentalista (Score).
    Divide a tela em 4 quadrantes analíticos.
    """
    if df_sector.empty:
        return

    df = df_sector.copy()
    if selected_tickers:
        df["destaque"] = df["ticker"].apply(lambda t: "Selecionado" if t in selected_tickers else "Setor")
    else:
        df["destaque"] = "Setor"

    fig = px.scatter(
        df,
        x="pvp",
        y="score",
        text="ticker",
        size="dy_anual",
        color="destaque",
        color_discrete_map={"Selecionado": "#38bdf8", "Setor": "#64748b"},
        hover_data={
            "fund_name": True,
            "pvp": ":.2f",
            "score": ":.1f",
            "dy_anual": ":.2f%",
            "real_yield_pct": ":.2f%",
            "preco_teto": ":.2f",
            "destaque": False
        },
        labels={
            "pvp": "Múltiplo P/VP (Mais barato para a esquerda)",
            "score": "Score Técnico Fundamentalista (0 a 10)",
            "dy_anual": "Dividend Yield (%)"
        },
        title="<b>Matriz Estratégica: Valuation (P/VP) vs Qualidade (Score)</b>"
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(size=14, line=dict(width=1.5, color="#f8fafc"))
    )

    # Linhas de referência dos quadrantes (P/VP = 1.00 e Score = 8.0)
    fig.add_vline(x=1.00, line_width=1.5, line_dash="dash", line_color="#94a3b8")
    fig.add_hline(y=8.0, line_width=1.5, line_dash="dash", line_color="#94a3b8")

    # Anotações dos 4 Quadrantes
    x_min = min(df["pvp"].min() - 0.05, 0.75)
    x_max = max(df["pvp"].max() + 0.05, 1.15)
    y_min = max(0.0, df["score"].min() - 1.0)
    y_max = 10.2

    fig.add_annotation(x=0.88, y=9.8, text="💎 <b>Oportunidade Clara</b><br>(Alto Score + Desconto)", showarrow=False, font=dict(color="#4ade80", size=10))
    fig.add_annotation(x=1.08, y=9.8, text="⭐ <b>Qualidade com Ágio</b><br>(Alto Score + P/VP > 1)", showarrow=False, font=dict(color="#38bdf8", size=10))
    fig.add_annotation(x=0.88, y=y_min + 0.6, text="⚠️ <b>Armadilha / Risco</b><br>(Descontado + Score Baixo)", showarrow=False, font=dict(color="#fbbf24", size=10))
    fig.add_annotation(x=1.08, y=y_min + 0.6, text="❌ <b>Evitar / Caro</b><br>(Score Baixo + Ágio)", showarrow=False, font=dict(color="#f87171", size=10))

    fig.update_layout(
        xaxis=dict(range=[x_min, x_max], showgrid=True, gridcolor="#334155"),
        yaxis=dict(range=[y_min, y_max], showgrid=True, gridcolor="#334155"),
        margin=dict(t=50, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_radar_comparison(df_selected: pd.DataFrame):
    """
    Gráfico Radar Multidimensional normalizado (0 a 100) para comparar até 4 FIIs selecionados.
    """
    if df_selected.empty:
        return

    # Limita a 4 FIIs para preservar clareza visual
    df = df_selected.head(4).copy()
    categories = [
        "Desconto (Valuation)",
        "Retorno Real (IPCA+)",
        "Solvência (Baixa Dívida)",
        "Qualidade Operacional",
        "Colchão de Reserva"
    ]

    fig = go.Figure()
    colors = ["#38bdf8", "#4ade80", "#f59e0b", "#a855f7"]

    for i, (_, row) in enumerate(df.iterrows()):
        # Normalização dos scores de 0 a 100
        # 1. Valuation: P/VP <= 0.80 -> 100, P/VP >= 1.20 -> 0
        pvp = float(row.get("pvp", 1.0))
        val_score = max(0, min(100, int((1.20 - pvp) / (1.20 - 0.80) * 100)))

        # 2. Retorno Real: 6% -> 0, 15% -> 100
        real_y = float(row.get("real_yield_pct", 10.0))
        yield_score = max(0, min(100, int((real_y - 6.0) / (15.0 - 6.0) * 100)))

        # 3. Solvência: Alavancagem 0% -> 100, >= 25% -> 0
        alav = float(row.get("alavancagem_pl", 0.0))
        solv_score = max(0, min(100, int((25.0 - alav) / 25.0 * 100)))

        # 4. Qualidade Operacional: Score * 10
        score = float(row.get("score", 7.0))
        qual_score = max(0, min(100, int(score * 10)))

        # 5. Colchão de Reserva: 0 meses -> 0, >= 2.5 meses -> 100
        meses_res = float(row.get("meses_reserva", 0.5))
        res_score = max(0, min(100, int(meses_res / 2.5 * 100)))

        values = [val_score, yield_score, solv_score, qual_score, res_score]
        # Fecha o polígono
        values.append(values[0])
        cats = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill='toself',
            name=row["ticker"],
            line=dict(color=colors[i % len(colors)], width=2),
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#334155", color="#94a3b8"),
            angularaxis=dict(gridcolor="#334155", color="#f8fafc")
        ),
        title="<b>Raio-X Comparativo Multidimensional (Radar)</b>",
        margin=dict(t=50, b=30, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_trend_timeline(history_records: List[Dict[str, Any]], metric_key: str, title: str, unit: str = "%"):
    """
    Gráfico de evolução temporal de métrica operacional ao longo dos meses.
    """
    if not history_records:
        return

    df = pd.DataFrame(history_records).sort_values(by=["ano", "mes", "periodo"], ascending=True)
    if metric_key not in df.columns:
        return

    fig = px.line(
        df,
        x="periodo",
        y=metric_key,
        markers=True,
        title=f"<b>Evolução Histórica: {title}</b>",
        labels={"periodo": "Competência / Relatório", metric_key: f"{title} ({unit})"}
    )
    fig.update_traces(
        line=dict(color="#38bdf8", width=3),
        marker=dict(size=9, color="#f8fafc", line=dict(width=2, color="#0284c7"))
    )
    fig.update_layout(
        margin=dict(t=50, b=30, l=30, r=30),
        xaxis=dict(showgrid=True, gridcolor="#334155"),
        yaxis=dict(showgrid=True, gridcolor="#334155")
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_dividend_projection_chart(proj_data: Dict[str, Any]):
    """
    Gráfico em barras mostrando o dividendo regular atual, o projetado e o extraordinário semestral.
    """
    prov_atual = proj_data.get("provento_atual", 0.80)
    prov_proj = proj_data.get("provento_projetado_mes", prov_atual)
    extraordinario = proj_data.get("extraordinario_estimado_fim_semestre", 0.0)

    meses = [
        "Mês Atual",
        "Próximo Mês",
        "Mês +2",
        "Mês +3",
        "Fechamento Semestre (6º Mês)"
    ]

    valores_base = [prov_atual, prov_proj, prov_proj, prov_proj, prov_proj]
    valores_extra = [0.0, 0.0, 0.0, 0.0, extraordinario]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=meses,
        y=valores_base,
        name="Dividendo Regular / FFO",
        marker_color="#0284c7",
        text=[f"R$ {v:.2f}" for v in valores_base],
        textposition="inside"
    ))
    if extraordinario > 0:
        fig.add_trace(go.Bar(
            x=meses,
            y=valores_extra,
            name="Extraordinário Semestral (Lei 8.668/93)",
            marker_color="#f59e0b",
            text=["", "", "", "", f"+ R$ {extraordinario:.2f}"],
            textposition="outside"
        ))

    fig.update_layout(
        barmode='stack',
        title="<b>Projeção de Rendimentos Futuros & Extraordinário Semestral</b>",
        yaxis=dict(title="Rendimento por Cota (R$)", gridcolor="#334155"),
        xaxis=dict(gridcolor="#334155"),
        margin=dict(t=50, b=30, l=30, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_audit_history_timeline(audit_records: List[Dict[str, Any]]):
    """
    Gráfico de evolução das auditorias passadas (Score Técnico e Cotação vs Preço-Teto).
    """
    if not audit_records:
        return

    df = pd.DataFrame(audit_records).sort_values("audit_date", ascending=True)

    fig = go.Figure()
    if "score" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["audit_date"],
            y=df["score"],
            name="Score Técnico (0-10)",
            line=dict(color="#4ade80", width=3),
            yaxis="y2"
        ))
    if "preco_mercado" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["audit_date"],
            y=df["preco_mercado"],
            name="Cotação de Mercado (R$)",
            line=dict(color="#38bdf8", width=2, dash="solid")
        ))
    if "preco_teto" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["audit_date"],
            y=df["preco_teto"],
            name="Preço-Teto de Compra (R$)",
            line=dict(color="#f59e0b", width=2, dash="dash")
        ))

    fig.update_layout(
        title="<b>Histórico de Auditorias: Evolução da Nota e Preço vs Teto</b>",
        xaxis=dict(title="Data da Análise", gridcolor="#334155"),
        yaxis=dict(title="Preço (R$)", gridcolor="#334155"),
        yaxis2=dict(title="Score (0-10)", overlaying="y", side="right", range=[0, 10.5]),
        margin=dict(t=50, b=30, l=30, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

