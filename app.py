import streamlit as st
import pandas as pd
import io
from datetime import datetime
from src.database.connection import init_db
from src.database.repository import (
    PortfolioRepository,
    AuditHistoryRepository,
    GerencialHistoryRepository,
    PricingParametersRepository
)
from src.services.fii_analyzer import FIIAnalyzer, FII_DEFAULT_SEGMENTS
from src.services.stock_analyzer import StockAnalyzer
from src.services.allocation_service import AllocationService
from src.services.import_service import ImportService
from src.services.report_generator import ReportGenerator, FII_KNOWLEDGE_BASE
from src.services.bolsai_service import BolsaiService
from src.services.fundos_net_service import FundosNetService
from src.services.cross_validation_service import CrossValidationService, FII_CATEGORIES
from src.services.gerencial_extractor import GerencialExtractor
from src.services.valuation_pricing_service import ValuationPricingService
from src.services.dividend_projection_service import DividendProjectionService
from src.services.trend_analysis_service import TrendAnalysisService
from src.services.fii_comparator_service import FIIComparatorService
import streamlit.components.v1 as components
from src.ui.styles import apply_custom_css
from src.ui.components import (
    render_metric_card,
    plot_segment_distribution,
    plot_asset_distribution,
    plot_pvp_vs_dy,
    plot_monthly_income_bar,
    plot_valuation_vs_quality_scatter,
    plot_radar_comparison,
    plot_trend_timeline,
    plot_dividend_projection_chart,
    plot_audit_history_timeline
)
from src.config import FII_SEGMENTS

# Configuração da página Streamlit
st.set_page_config(
    page_title="Carteira & FIIs Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa banco de dados e estilos
init_db()
apply_custom_css()

# Header da aplicação
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.markdown('<div class="main-header">📊 Análise de Carteira & Investimentos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Foco em Fundos Imobiliários, Ações e Balanceamento por Metas de Alocação</div>', unsafe_allow_html=True)

with col_refresh:
    force_refresh = st.button("🔄 Atualizar Cotações", help="Busca cotações mais recentes no mercado ignorando o cache local")

# Carrega ativos da carteira
all_assets = PortfolioRepository.get_all_assets()
fii_assets = [a for a in all_assets if a["asset_type"] == "FII"]
stock_assets = [a for a in all_assets if a["asset_type"] == "ACAO"]
other_assets = [a for a in all_assets if a["asset_type"] in ["RENDA_FIXA", "OUTRO"]]

# Realiza análises
fii_data = FIIAnalyzer.analyze_positions(fii_assets, force_refresh=force_refresh)
stock_data = StockAnalyzer.analyze_positions(stock_assets, force_refresh=force_refresh)
other_total = sum(float(a.get("quantity", 0)) * float(a.get("average_price", 0)) for a in other_assets)

macro_data = AllocationService.calculate_macro_allocation(
    fii_total=fii_data["total_current_value"],
    stock_total=stock_data["total_current_value"],
    other_total=other_total
)

# Abas Principais
tab_fii, tab_comparator, tab_reports, tab_stocks, tab_allocation, tab_management = st.tabs([
    "🏢 Fundos Imobiliários (FIIs)",
    "⚔️ Comparador Setorial de FIIs",
    "📑 Auditoria & Dossiês Oficiais",
    "📈 Ações (B3)",
    "⚖️ Alocação & Metas",
    "📥 Gestão da Carteira & Importação"
])

# ==============================================================================
# ABA 1: FUNDOS IMOBILIÁRIOS (FIIs)
# ==============================================================================
with tab_fii:
    if not fii_assets:
        st.info("💡 Você ainda não possui Fundos Imobiliários cadastrados. Vá na aba **'📥 Gestão da Carteira & Importação'** para importar sua planilha ou cadastrar seus FIIs!")
    else:
        # Métricas em Cards
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            render_metric_card("Total Investido", f"R$ {fii_data['total_invested']:,.2f}")
        with m2:
            delta_val = f"R$ {fii_data['total_profit_loss']:+,.2f} ({fii_data['total_profit_loss_pct']:+.1f}%)"
            delta_type = "positive" if fii_data['total_profit_loss'] >= 0 else "negative"
            render_metric_card("Patrimônio FIIs", f"R$ {fii_data['total_current_value']:,.2f}", delta_val, delta_type)
        with m3:
            render_metric_card("Renda Mensal Est.", f"R$ {fii_data['monthly_income_est']:,.2f}")
        with m4:
            render_metric_card("Renda Anual Est.", f"R$ {fii_data['annual_income_est']:,.2f}")
        with m5:
            render_metric_card("DY Médio (12M)", f"{fii_data['weighted_dy']:.2f}%")
        with m6:
            pvp_color = "positive" if fii_data['weighted_pvp'] <= 1.02 else "negative"
            render_metric_card("P/VP Médio", f"{fii_data['weighted_pvp']:.2f}", "Desconto / Justo" if fii_data['weighted_pvp'] <= 1.0 else "Com Ágio", pvp_color)

        st.write("")

        # Gráficos
        g1, g2 = st.columns(2)
        with g1:
            plot_segment_distribution(fii_data["segment_distribution"])
        with g2:
            plot_monthly_income_bar(fii_data["items"])

        st.write("")
        g3, g4 = st.columns(2)
        with g3:
            plot_pvp_vs_dy(fii_data["items"])
        with g4:
            plot_asset_distribution(fii_data["items"])

        # Tabela Detalhada de FIIs
        st.subheader("📋 Detalhamento dos Fundos Imobiliários")
        
        df_fii_display = pd.DataFrame(fii_data["items"])
        if not df_fii_display.empty:
            cols_order = [
                "ticker", "segment", "quantity", "average_price", "current_price",
                "invested_value", "current_value", "profit_loss_pct", "pvp", "pvp_status",
                "dy_12m", "last_dividend", "monthly_income_est", "portfolio_weight_pct"
            ]
            df_table = df_fii_display[cols_order].copy()
            df_table.columns = [
                "Ticker", "Segmento", "Qtd Cotas", "Preço Médio (R$)", "Cotação Atual (R$)",
                "Total Investido (R$)", "Patrimônio Atual (R$)", "Rentabilidade (%)",
                "P/VP", "Status P/VP", "DY 12M (%)", "Últ. Provento (R$)",
                "Renda Mensal (R$)", "Peso na Carteira (%)"
            ]
            st.dataframe(
                df_table.style.format({
                    "Qtd Cotas": "{:,.0f}",
                    "Preço Médio (R$)": "R$ {:,.2f}",
                    "Cotação Atual (R$)": "R$ {:,.2f}",
                    "Total Investido (R$)": "R$ {:,.2f}",
                    "Patrimônio Atual (R$)": "R$ {:,.2f}",
                    "Rentabilidade (%)": "{:+.2f}%",
                    "P/VP": "{:.2f}",
                    "DY 12M (%)": "{:.2f}%",
                    "Últ. Provento (R$)": "R$ {:,.2f}",
                    "Renda Mensal (R$)": "R$ {:,.2f}",
                    "Peso na Carteira (%)": "{:.2f}%"
                }),
                use_container_width=True,
                height=350
            )

        # Seção do Efeito Bola de Neve (Número Mágico)
        st.write("")
        st.subheader("❄️ Efeito Bola de Neve: O Número Mágico dos FIIs")
        st.markdown("""
        *O **Número Mágico (Magic Number)** representa a quantidade exata de cotas que você precisa ter de um FII para que os dividendos recebidos no mês comprem uma nova cota automaticamente, sem precisar tirar nenhum centavo do bolso.*
        """)

        magic_cols = st.columns(3)
        for i, item in enumerate(fii_data["items"]):
            col_target = magic_cols[i % 3]
            with col_target:
                ticker = item["ticker"]
                mn = item.get("magic_number")
                prog = item.get("magic_progress", 0.0)
                qty = item["quantity"]
                last_div = item.get("last_dividend", 0.0)

                with st.container(border=True):
                    st.markdown(f"#### **{ticker}**")
                    if mn and mn > 0:
                        st.markdown(f"**Cotas Atuais:** `{int(qty)}` / **Meta:** `{mn}` cotas")
                        st.progress(prog / 100.0)
                        st.caption(f"**Progresso:** {prog:.1f}% concluído")
                        if qty >= mn:
                            st.success("🎉 **Bola de neve atingida!** Este fundo já se autofinancia todo mês!")
                        else:
                            needed = int(mn - qty)
                            st.info(f"Faltam **{needed} cotas** (aprox. R$ {needed * item['current_price']:,.2f}) para o fundo comprar 1 cota por mês sozinho.")
                    else:
                        st.caption("Aguardando histórico de dividendos para estimar o número mágico.")

# ==============================================================================
# ABA 2: COMPARADOR SETORIAL DE FIIs & FIAGROS
# ==============================================================================
with tab_comparator:
    st.subheader("⚔️ Comparador Setorial de Fundos Imobiliários & Fiagros")
    st.markdown("""
    Compare lado a lado múltiplos fundos do mesmo segmento com matriz padronizada de múltiplos institucionais, 
    retorno real (**`IPCA + X% a.a.`**), preço-teto institucional (Spread NTN-B 2035 / Gordon DCF / Patrimonial Prudencial), 
    cobertura de caixa operacional (FFO), colchão de reserva e tendências operacionais.
    """)

    col_comp_seg, col_comp_ticks = st.columns([1, 2])
    available_segs = FIIComparatorService.get_available_segments()

    with col_comp_seg:
        selected_seg_code = st.selectbox(
            "Selecione o Segmento para Comparação",
            options=list(available_segs.keys()),
            format_func=lambda k: f"{available_segs[k]} ({k})",
            index=0
        )

    with col_comp_ticks:
        default_sector_tickers = FIIComparatorService.get_tickers_by_segment(selected_seg_code)
        selected_comp_tickers = st.multiselect(
            "Filtrar Fundos do Setor",
            options=default_sector_tickers,
            default=default_sector_tickers
        )

    # Executa a comparação setorial
    comp_result = FIIComparatorService.compare_sector(
        segment_code=selected_seg_code,
        selected_tickers=selected_comp_tickers if selected_comp_tickers else default_sector_tickers
    )
    df_comp = comp_result["df"]
    podium = comp_result["podium"]

    if df_comp.empty:
        st.warning("Nenhum fundo imobiliário encontrado para os filtros selecionados.")
    else:
        # PÓDIO COM OS 5 SELOS
        st.markdown("#### 🏆 Pódio & Destaques Estratégicos do Setor")
        p_cols = st.columns(5)
        
        podium_keys = [
            ("melhor_preco", p_cols[0]),
            ("maior_renda", p_cols[1]),
            ("mais_seguro", p_cols[2]),
            ("maior_extraordinario", p_cols[3]),
            ("lider_geral", p_cols[4])
        ]

        for k, p_col in podium_keys:
            if k in podium:
                p_item = podium[k]
                with p_col:
                    with st.container(border=True):
                        st.markdown(f"<div style='color:{p_item['cor']}; font-weight:800; font-size:0.8rem; text-transform:uppercase;'>{p_item['titulo']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:1.5rem; font-weight:900; color:#f8fafc; margin:4px 0;'>{p_item['ticker']}</div>", unsafe_allow_html=True)
                        st.caption(p_item["motivo"])

        st.write("")

        # TABELA COMPARATIVA COMPLETA
        st.markdown(f"#### 📋 Matriz Analítica do Setor: {comp_result['segment_name']}")
        
        cols_comp_order = [
            "ticker", "fund_name", "preco_mercado", "vpc", "pvp", "dy_anual",
            "real_yield_pct", "spread_vs_ntnb", "preco_teto", "margem_seguranca_pct",
            "provento_mes", "ffo_cota", "cobertura_ffo_pct", "meses_reserva",
            "alavancagem_pl", "vacancia_fisica", "trend_badge", "score", "veredicto"
        ]
        
        valid_cols = [c for c in cols_comp_order if c in df_comp.columns]
        df_comp_table = df_comp[valid_cols].copy()
        
        df_comp_table.rename(columns={
            "ticker": "Ticker",
            "fund_name": "Nome do Fundo",
            "preco_mercado": "Cotação (R$)",
            "vpc": "VPC (R$)",
            "pvp": "P/VP",
            "dy_anual": "DY Anual (%)",
            "real_yield_pct": "Retorno Real (IPCA+)",
            "spread_vs_ntnb": "Spread NTN-B (p.p.)",
            "preco_teto": "Preço-Teto (R$)",
            "margem_seguranca_pct": "Margem Seg. (%)",
            "provento_mes": "Últ. Provento (R$)",
            "ffo_cota": "FFO/Cota (R$)",
            "cobertura_ffo_pct": "Cobertura FFO (%)",
            "meses_reserva": "Meses Reserva",
            "alavancagem_pl": "Alavancagem (%)",
            "vacancia_fisica": "Vacância Física (%)",
            "trend_badge": "Trajetória MoM",
            "score": "Score (0-10)",
            "veredicto": "Veredito"
        }, inplace=True)

        st.dataframe(
            df_comp_table.style.format({
                "Cotação (R$)": "R$ {:,.2f}",
                "VPC (R$)": "R$ {:,.2f}",
                "P/VP": "{:.2f}",
                "DY Anual (%)": "{:.2f}%",
                "Retorno Real (IPCA+)": "IPCA + {:.2f}%",
                "Spread NTN-B (p.p.)": "{:+.2f} p.p.",
                "Preço-Teto (R$)": "R$ {:,.2f}",
                "Margem Seg. (%)": "{:+.1f}%",
                "Últ. Provento (R$)": "R$ {:,.2f}",
                "FFO/Cota (R$)": "R$ {:,.2f}",
                "Cobertura FFO (%)": "{:.1f}%",
                "Meses Reserva": "{:.1f} meses",
                "Alavancagem (%)": "{:.1f}%",
                "Vacância Física (%)": "{:.1f}%",
                "Score (0-10)": "{:.1f}"
            }),
            use_container_width=True,
            height=320
        )

        st.write("")

        # GRÁFICOS VISUAIS: DISPERSÃO 2X2 & RADAR
        st.markdown("#### 📊 Radiografia Visual e Posicionamento Estratégico")
        g_c1, g_c2 = st.columns(2)
        with g_c1:
            plot_valuation_vs_quality_scatter(df_comp, selected_comp_tickers)
        with g_c2:
            plot_radar_comparison(df_comp)

        # PARÂMETROS MACRO DE PRECIFICAÇÃO (EXPANDER)
        with st.expander("⚙️ Calibração de Parâmetros Macroeconômicos de Precificação (Preço-Teto & NTN-B)", expanded=False):
            st.caption("Ajuste as taxas de referência soberanas do Tesouro Direto e inflação projetada para recalibrar a régua institucional de preço-teto.")
            current_pricing_params = PricingParametersRepository.get_parameters()
            
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                new_ntnb = st.number_input(
                    "Taxa Referência NTN-B 2035 (% a.a.)",
                    min_value=3.0,
                    max_value=12.0,
                    value=float(current_pricing_params.get("ntnb_reference_rate", 6.50)),
                    step=0.25
                )
            with p_col2:
                new_ipca = st.number_input(
                    "Inflação Projetada IPCA (% a.a.)",
                    min_value=1.0,
                    max_value=10.0,
                    value=float(current_pricing_params.get("projected_ipca", 4.00)),
                    step=0.25
                )
            with p_col3:
                new_spread = st.number_input(
                    "Spread Real Mínimo Exigido (% a.a.)",
                    min_value=0.5,
                    max_value=6.0,
                    value=float(current_pricing_params.get("real_risk_spread", 2.00)),
                    step=0.25
                )

            if st.button("Salvar Parâmetros e Recalcular Preço-Teto"):
                PricingParametersRepository.update_parameter("ntnb_reference_rate", new_ntnb)
                PricingParametersRepository.update_parameter("projected_ipca", new_ipca)
                PricingParametersRepository.update_parameter("real_risk_spread", new_spread)
                st.success("Parâmetros macro atualizados com sucesso!")
                st.rerun()

# ==============================================================================
# ABA 3: AUDITORIA & RELATÓRIOS OFICIAIS (FUNDOS.NET & BOLSAAI)
# ==============================================================================
with tab_reports:
    st.subheader("📑 Dossiês de Auditoria & Diagnóstico Fundamentalista")
    st.markdown("""
    Gere relatórios executivos de alta fidelidade baseados nos documentos oficiais do **Fundos.NET (B3/CVM)** 
    e enriquecidos com a inteligência e dados de mercado da **BolsaAI**.
    """)

    col_rep_sel, col_rep_info = st.columns([1, 2])

    with col_rep_sel:
        with st.container(border=True):
            st.markdown("##### 🔍 Selecionar Fundo Imobiliário")
            default_tickers = [
                "HSML11", "XPML11", "VISC11", "HGBS11", "PMLL11",
                "HGLG11", "BTLG11", "TRXF11", "GGRC11", "XPLG11",
                "KNCR11", "MXRF11", "CPTS11", "KNSC11", "RBRR11", "BTCI11", "RBRY11",
                "PVBI11", "HGRE11", "BRCR11", "JSRE11", "RCRB11",
                "HFOF11", "BCFF11", "RBRF11", "KFOF11", "CXCI11",
                "RZTR11", "VGIA11", "KNCA11", "RURA11", "FGAA11",
                "HGRU11", "ALZR11", "TGAR11", "RBVA11", "VGHF11"
            ]
            portfolio_fii_tickers = [a["ticker"] for a in fii_assets]
            combined_tickers = list(dict.fromkeys(portfolio_fii_tickers + default_tickers))
            
            selected_ticker = st.selectbox(
                "Escolha o FII para gerar a auditoria",
                combined_tickers,
                index=0
            )
            
            manual_ticker = st.text_input("Ou digite outro ticker (ex: CPTS11)", value="").strip().upper()
            target_report_ticker = manual_ticker if manual_ticker else selected_ticker

            # Ingestão de Relatório Gerencial em PDF
            with st.expander("📁 Upload de Relatório Gerencial (PDF)", expanded=False):
                st.caption("Carregue o PDF do relatório gerencial oficial da gestora para extração automatizada de métricas operacionais (SSS, Vacância, FFO, etc.).")
                uploaded_pdf = st.file_uploader(f"PDF do Relatório Gerencial ({target_report_ticker})", type=["pdf"], key=f"pdf_upload_{target_report_ticker}")
                if uploaded_pdf is not None:
                    with st.spinner("Extraindo métricas do relatório gerencial..."):
                        extracted = GerencialExtractor.extract_from_pdf(uploaded_pdf, ticker=target_report_ticker)
                        if extracted.get("success"):
                            st.success(f"✅ Relatório de {target_report_ticker} processado com sucesso! ({extracted.get('pages_count')} páginas)")
                            ops = extracted.get("metricas_operacionais", {})
                            dre_c = extracted.get("dre_caixa", {})
                            col_p1, col_p2 = st.columns(2)
                            with col_p1:
                                if "sss_pct" in ops:
                                    st.metric("Vendas Mesmas Lojas (SSS)", f"{ops['sss_pct']:+.1f}%")
                                if "vacancia_fisica" in ops:
                                    st.metric("Vacância Física", f"{ops['vacancia_fisica']:.1f}%")
                            with col_p2:
                                if "ffo_cota" in dre_c:
                                    st.metric("FFO / Cota", f"R$ {dre_c['ffo_cota']:.2f}")
                                if "cobertura_ffo" in dre_c:
                                    st.metric("Cobertura do FFO", f"{dre_c['cobertura_ffo']*100:.1f}%")
                        else:
                            st.warning(f"Não foi possível extrair dados: {extracted.get('error')}")

            # Parâmetros de calibração técnica (opcionais pelo usuário)
            kb_info = FII_KNOWLEDGE_BASE.get(target_report_ticker, {})
            with st.expander("⚙️ Calibração Técnica do Relatório", expanded=False):
                st.caption("Defina manualmente parâmetros analíticos ou deixe desmarcado para exibir '-' no dossiê.")
                use_score = st.checkbox("Calibrar Score Técnico", value="score" in kb_info)
                custom_score = st.slider("Score Técnico Fundamentalista (0 a 10)", min_value=1.0, max_value=10.0, value=float(kb_info.get("score", 7.0)), step=0.1) if use_score else None

                veredicto_options = ["Em Análise (-)", "Aprovado", "Aprovado com Ressalva", "Reprovado"]
                default_ver_idx = veredicto_options.index(kb_info.get("veredicto")) if kb_info.get("veredicto") in veredicto_options else 0
                custom_veredicto = st.selectbox("Veredito da Auditoria", veredicto_options, index=default_ver_idx)
                if custom_veredicto == "Em Análise (-)":
                    custom_veredicto = None

                use_teto = st.checkbox("Calibrar Preço-Teto de Segurança", value="teto" in kb_info)
                custom_teto = st.number_input("Preço-Teto de Segurança Fundamentalista (R$)", min_value=0.0, value=float(kb_info.get("teto", 0.0)), step=0.5) if use_teto else None

                custom_alocacao = st.text_input("Alocação Sugerida na Carteira", value=kb_info.get("alocacao_sugerida", "-"))
                if custom_alocacao.strip() == "-" or not custom_alocacao.strip():
                    custom_alocacao = None

            # Configurações da BolsaAI
            with st.expander("🤖 Conexão com API BolsaAI", expanded=False):
                st.markdown("Acesse cotações, dividendos e múltiplos via [BolsaAI](https://usebolsai.com/mcp).")
                current_api_key = BolsaiService.get_api_key()
                input_key = st.text_input("Chave de API BolsaAI (opcional)", value=current_api_key, type="password", help="Chave obtida no painel usebolsai.com/dashboard")
                
                col_save_key, col_test_key = st.columns(2)
                with col_save_key:
                    if st.button("Salvar Chave"):
                        BolsaiService.save_api_key(input_key)
                        st.success("Chave salva com sucesso!")
                with col_test_key:
                    if st.button("Testar Conexão"):
                        test_res = BolsaiService.test_connection(input_key)
                        if test_res["success"]:
                            st.success(test_res["message"])
                        else:
                            st.warning(test_res["message"])
                
                st.caption("💡 Se não tiver uma chave BolsaAI no momento, o gerador opera com os dados oficiais do Fundos.NET/CVM e cotações de mercado.")

            btn_gerar = st.button("⚡ Gerar Relatório de Auditoria", type="primary", use_container_width=True)

    with col_rep_info:
        with st.container(border=True):
            with st.spinner("Executando validação cruzada Fundos.NET (CVM) e BolsaAI..."):
                cross_val = CrossValidationService.validate_and_reconcile(target_report_ticker)
                fnet_data = cross_val["fnet"]
                bolsai_data = cross_val["bolsai"]
                reconcil_data = cross_val["reconciliation"]
                macro_val = bolsai_data["macro"]

            st.markdown(f"##### 🏛️ Validação Cruzada: Fundos.NET & BolsaAI (`{target_report_ticker}`)")
            
            # Badge de segmento detectado
            st.markdown(f'<span class="badge-discount" style="background:#0284c7; color:#fff; font-size:0.85rem; padding:4px 12px;">Segmento Oficial: {cross_val["segment_name"]} ({cross_val["segment_code"]})</span>', unsafe_allow_html=True)
            st.write("")

            c_i1, c_i2 = st.columns(2)
            with c_i1:
                st.markdown(f"**Razão Social:** {fnet_data.get('razao_social')}")
                st.markdown(f"**Administrador:** {fnet_data.get('administrador')}")
                st.markdown(f"**Gestão:** {fnet_data.get('gestor')}")
                st.markdown(f"**Cotação BolsaAI:** `R$ {bolsai_data.get('price', 0.0):.2f}`")
                st.markdown(f"**VPC Contábil (CVM):** `R$ {fnet_data.get('vpc', 0.0):.2f}`")
            with c_i2:
                pl_val = fnet_data.get('pl', 0.0)
                pl_str = f"R$ {pl_val/1e9:.2f} Bi" if pl_val >= 1e9 else f"R$ {pl_val/1e6:.1f} Mi"
                st.markdown(f"**Patrimônio Líquido:** `{pl_str}`")
                st.markdown(f"**P/VP Reconciliado:** `{bolsai_data.get('pvp', 1.0):.2f}` (Deságio: `{reconcil_data.get('desagio_pct', 0.0):+.1f}%`)")
                dy_rec = float(bolsai_data.get('dy_recorrente') or reconcil_data.get('dy_recorrente') or bolsai_data.get('dy_anual') or 0.0)
                dy_ttm = float(bolsai_data.get('dy_ttm') or reconcil_data.get('dy_ttm') or bolsai_data.get('dy_anual') or dy_rec)
                last_d = float(reconcil_data.get('last_dividend') or 0.0)
                if last_d <= 0.0 and dy_rec > 0 and bolsai_data.get('price', 0) > 0:
                    last_d = round((bolsai_data.get('price') * (dy_rec / 100.0)) / 12.0, 3)
                st.markdown(f"**DY Recorrente Projetado:** `{dy_rec:.2f}% a.a.` (R$ {last_d:.3f}/mês)")
                st.markdown(f"**DY Histórico (12M TTM):** `{dy_ttm:.2f}% a.a.`")
                st.markdown(f"**Spread vs CDI (Recorrente):** `{macro_val.get('spread_vs_cdi'):+0.2f} p.p.` (CDI: `{macro_val.get('cdi'):.2f}%`)")

            st.caption(f"📅 **Data-Base CVM:** {fnet_data.get('data_referencia')} | **Protocolo B3/Fundos.NET:** {fnet_data.get('data_protocolo_fnet')}")
            
            # Alertas de divergência identificados na reconciliação
            if reconcil_data.get("divergences"):
                for div_msg in reconcil_data["divergences"]:
                    st.warning(f"⚠️ **Alerta de Auditoria:** {div_msg}")

            # Cálculos Institucionais Especializados
            ffo_calc_val = float(kb_info.get("ffo_cota") or (last_d if last_d > 0 else 0.80))
            pricing_calc = ValuationPricingService.calculate_consolidated_pricing(
                ticker=target_report_ticker,
                metrics={
                    "preco_mercado": bolsai_data.get("price", 100.0),
                    "vpc": fnet_data.get("vpc", 100.0),
                    "provento_mes": last_d,
                    "ffo_cota": ffo_calc_val,
                    "dy_anual": dy_rec
                },
                segment_code=cross_val["segment_code"]
            )

            reserva_calc_val = float(kb_info.get("reserva_acumulada_cota") or 0.0)
            proj_calc = DividendProjectionService.project_and_analyze(
                ticker=target_report_ticker,
                ffo_cota=ffo_calc_val,
                provento_atual=last_d,
                reserva_acumulada_cota=reserva_calc_val,
                segment_code=cross_val["segment_code"]
            )

            trend_calc = TrendAnalysisService.analyze_ticker_trend(target_report_ticker)

            st.write("")
            st.markdown("##### 💎 Análise Fundamentalista Avançada (Sem Bazin)")
            
            c_adv1, c_adv2 = st.columns(2)
            with c_adv1:
                with st.container(border=True):
                    real_info = pricing_calc.get("real_yield", {})
                    st.markdown(f"**💰 Retorno Real Líquido:** <span style='color:#22c55e; font-weight:800; font-size:1.1rem;'>{real_info.get('label_real')}</span>", unsafe_allow_html=True)
                    st.caption(f"Spread de **{real_info.get('spread_vs_ntnb_label')}** (NTN-B 2035: {real_info.get('ntnb_reference_rate'):.2f}% a.a.)")
                    st.markdown(f"**Equiv. Bruto Renda Fixa:** `{real_info.get('cdi_gross_label')}` *(Isento de IR)*")
                    st.caption(f"ℹ️ {real_info.get('metodologia_real')}")

            with c_adv2:
                with st.container(border=True):
                    teto_rec = pricing_calc.get("preco_teto_recomendado", 0.0)
                    m_seg = pricing_calc.get("margem_seguranca_pct", 0.0)
                    seg_color = "#22c55e" if m_seg > 0 else "#ef4444"
                    st.markdown(f"**🎯 Preço-Teto Recomendado:** <span style='color:#38bdf8; font-weight:800; font-size:1.1rem;'>R$ {teto_rec:,.2f}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Margem de Segurança:** <span style='color:{seg_color}; font-weight:700;'>{m_seg:+.1f}%</span> (Cotação: R$ {pricing_calc['preco_mercado']:,.2f})", unsafe_allow_html=True)
                    st.caption(f"Âncora: {pricing_calc.get('metodologia_recomendada')}")
                    with st.popover("Ver Metodologias Detalhadas"):
                        st.markdown(f"- **Spread NTN-B 2035:** `R$ {pricing_calc['teto_spread_ntnb']:,.2f}`")
                        st.markdown(f"- **Gordon DCF (Inflação):** `R$ {pricing_calc['teto_gordon']:,.2f}`")
                        st.markdown(f"- **Patrimonial Prudencial:** `R$ {pricing_calc['teto_patrimonial']:,.2f}`")

            c_adv3, c_adv4 = st.columns(2)
            with c_adv3:
                with st.container(border=True):
                    st.markdown(f"**🛡️ Sustentabilidade FFO:** <span style='font-weight:700;'>{proj_calc['status_sustentabilidade']}</span> ({proj_calc['cobertura_ffo_pct']:.1f}%)", unsafe_allow_html=True)
                    st.markdown(f"**Colchão de Reserva:** `R$ {proj_calc['reserva_acumulada_cota']:.2f}/cota` ({proj_calc['meses_reserva_cobertura']:.1f} meses de cobertura)")
                    if proj_calc.get("tem_potencial_extraordinario"):
                        st.markdown(f"**🎁 Previsão de Extraordinário:** <span style='color:#f59e0b; font-weight:700;'>+ R$ {proj_calc['extraordinario_estimado_fim_semestre']:.2f}/cota</span> no fim do semestre (Lei 8.668/93)", unsafe_allow_html=True)
                    else:
                        st.caption("Sem retenção excedente obrigatória prevista para fechamento semestral.")

            with c_adv4:
                with st.container(border=True):
                    st.markdown(f"**📈 Trajetória Multi-Mês:** <span style='font-weight:700;'>{trend_calc['badge_geral']}</span>", unsafe_allow_html=True)
                    st.caption(trend_calc.get("resumo_tendencia", ""))
                    deltas_info = trend_calc.get("deltas", {})
                    vac_obj = deltas_info.get("vacancia_fisica", {})
                    ffo_obj = deltas_info.get("ffo_cota", {})
                    d_vac = vac_obj.get("delta", 0.0) if isinstance(vac_obj, dict) else float(vac_obj or 0.0)
                    d_ffo = ffo_obj.get("delta", 0.0) if isinstance(ffo_obj, dict) else float(ffo_obj or 0.0)
                    st.markdown(f"**Deltas MoM:** Vacância `{d_vac:+.2f} p.p.` | FFO `R$ {d_ffo:+.3f}`")

    # Geração e Exibição do Relatório
    if btn_gerar or f"report_generated_{target_report_ticker}" in st.session_state:
        st.session_state[f"report_generated_{target_report_ticker}"] = True
        
        with st.spinner(f"Consolidando auditoria e compilando relatório executivo especializado para {target_report_ticker}..."):
            custom_payload = {
                "score": custom_score,
                "veredicto": custom_veredicto,
                "teto": custom_teto,
                "alocacao_sugerida": custom_alocacao
            }
            report_result = ReportGenerator.generate_html_report(target_report_ticker, custom_params=custom_payload)
            html_content = report_result["html_content"]

        st.write("")
        st.success(f"🎉 Relatório de Auditoria Fundamentalista para **{target_report_ticker}** ({report_result['segment_name']}) gerado com sucesso!")
        
        col_down, col_print = st.columns([1, 3])
        with col_down:
            st.download_button(
                label=f"📥 Baixar Dossiê HTML ({target_report_ticker})",
                data=html_content.encode("utf-8"),
                file_name=f"{target_report_ticker}_auditoria_fundamentalista.html",
                mime="text/html",
                type="primary",
                use_container_width=True
            )
        with col_print:
            st.info("💡 **Dica de Impressão:** Ao abrir o arquivo HTML baixado em seu navegador, pressione **Ctrl + P** para salvar como PDF executivo perfeitamente formatado via regras `@media print`.")

        st.write("")
        st.markdown("#### 🖥️ Pré-visualização Interativa do Dossiê")
        components.html(html_content, height=950, scrolling=True)

        # Painel Visual Analítico e Histórico Persistente
        st.write("")
        st.markdown(f"#### 📊 Painel Analítico: Projeções, Trajetória & Histórico de Auditorias ({target_report_ticker})")
        
        subtab_proj, subtab_trend, subtab_hist = st.tabs([
            "🔮 Projeção de Rendimentos & Extraordinários",
            "📈 Trajetória Temporal de Métricas (MoM)",
            "🏛️ Histórico Persistente de Auditorias"
        ])

        with subtab_proj:
            plot_dividend_projection_chart(proj_calc)
            st.info(f"💡 **Guidance de Proventos:** {proj_calc.get('guidance_faixa')}. {proj_calc.get('desc_extraordinario')}")

        with subtab_trend:
            if trend_calc.get("has_history") and trend_calc.get("series"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    plot_trend_timeline(trend_calc["series"], "vacancia_fisica", "Vacância Física", "%")
                with col_t2:
                    plot_trend_timeline(trend_calc["series"], "ffo_cota", "FFO Líquido por Cota", "R$")
            else:
                st.caption("Histórico insuficiente de relatórios gerenciais para este FII.")

        with subtab_hist:
            col_hist_btn, col_hist_info = st.columns([1, 2])
            with col_hist_btn:
                if st.button("💾 Salvar Snapshot no Histórico", key=f"btn_save_hist_{target_report_ticker}", type="primary"):
                    AuditHistoryRepository.save_audit_snapshot({
                        "ticker": target_report_ticker,
                        "audit_date": datetime.now().strftime("%Y-%m-%d"),
                        "score": custom_score if custom_score is not None else report_result.get("score") or kb_info.get("score", 8.0),
                        "veredicto": custom_veredicto or report_result.get("veredicto") or kb_info.get("veredicto", "Aprovado"),
                        "preco_mercado": bolsai_data.get("price", 0.0),
                        "vpc": fnet_data.get("vpc", 0.0),
                        "pvp": bolsai_data.get("pvp", 1.0),
                        "dy_anual": dy_rec,
                        "preco_teto": custom_teto if custom_teto is not None else pricing_calc.get("preco_teto_recomendado", 0.0),
                        "alocacao_sugerida": custom_alocacao or kb_info.get("alocacao_sugerida", "-"),
                        "ffo_cota": ffo_calc_val,
                        "cobertura_ffo": kb_info.get("cobertura_ffo", 1.0),
                        "alavancagem_pct": fnet_data.get("alavancagem_pl_pct") or kb_info.get("alavancagem_pl", 0.0),
                        "vacancia_fisica": kb_info.get("vacancia_fisica", 0.0),
                        "trend_status": trend_calc.get("status_geral", "ESTAVEL"),
                        "reserva_cota": reserva_calc_val,
                        "guidance_proximo_mes": proj_calc.get("provento_projetado_mes"),
                        "extraordinario_estimado": proj_calc.get("extraordinario_estimado_fim_semestre"),
                        "real_yield_pct": pricing_calc.get("real_yield", {}).get("real_yield_pct"),
                        "notes": f"Snapshot salvo via painel web de auditoria em {datetime.now().strftime('%d/%m/%Y %H:%M')}."
                    })
                    st.success(f"Snapshot de auditoria para {target_report_ticker} gravado no banco de dados SQLite com sucesso!")
                    st.rerun()

            audit_history_records = AuditHistoryRepository.get_audit_history(target_report_ticker)
            if audit_history_records:
                plot_audit_history_timeline(audit_history_records)
                df_audits = pd.DataFrame(audit_history_records)
                cols_hist_show = ["audit_date", "score", "veredicto", "preco_mercado", "preco_teto", "pvp", "real_yield_pct", "trend_status"]
                valid_hist_cols = [c for c in cols_hist_show if c in df_audits.columns]
                st.dataframe(
                    df_audits[valid_hist_cols].rename(columns={
                        "audit_date": "Data",
                        "score": "Score",
                        "veredicto": "Veredito",
                        "preco_mercado": "Cotação (R$)",
                        "preco_teto": "Preço-Teto (R$)",
                        "pvp": "P/VP",
                        "real_yield_pct": "Retorno Real (%)",
                        "trend_status": "Trajetória"
                    }).style.format({
                        "Score": "{:.1f}",
                        "Cotação (R$)": "R$ {:,.2f}",
                        "Preço-Teto (R$)": "R$ {:,.2f}",
                        "P/VP": "{:.2f}",
                        "Retorno Real (%)": "IPCA + {:.2f}%"
                    }),
                    use_container_width=True
                )
            else:
                st.info("Nenhum snapshot de auditoria salvo anteriormente para este fundo. Clique em 'Salvar Snapshot no Histórico' para registrar esta avaliação!")

# ==============================================================================
# ABA 3: AÇÕES (B3)
# ==============================================================================
with tab_stocks:
    if not stock_assets:
        st.info("💡 Nenhuma ação cadastrada no momento. Adicione ações na aba **'📥 Gestão da Carteira & Importação'**!")
    else:
        s1, s2, s3, s4, s5, s6 = st.columns(6)
        with s1:
            render_metric_card("Total Investido", f"R$ {stock_data['total_invested']:,.2f}")
        with s2:
            delta_val = f"R$ {stock_data['total_profit_loss']:+,.2f} ({stock_data['total_profit_loss_pct']:+.1f}%)"
            delta_type = "positive" if stock_data['total_profit_loss'] >= 0 else "negative"
            render_metric_card("Patrimônio Ações", f"R$ {stock_data['total_current_value']:,.2f}", delta_val, delta_type)
        with s3:
            render_metric_card("ROE Médio", f"{stock_data.get('weighted_roe', 0.0):.1f}%")
        with s4:
            render_metric_card("P/L Médio", f"{stock_data.get('weighted_pl', 0.0):.1f}x")
        with s5:
            render_metric_card("DY Médio (12M)", f"{stock_data['weighted_dy']:.2f}%")
        with s6:
            render_metric_card("Empresas", f"{len(stock_data['items'])}")

        st.write("")
        st.subheader("📋 Múltiplos Fundamentalistas e Rentabilidade (BolsaAI & B3)")
        
        df_stocks = pd.DataFrame(stock_data["items"])
        if not df_stocks.empty:
            cols_order = [
                "ticker", "name", "sector", "quantity", "average_price", "current_price",
                "invested_value", "current_value", "profit_loss_pct", "pl", "pvp", "roe", "roic",
                "net_margin", "dy_12m", "status_diag", "portfolio_weight_pct"
            ]
            df_st_table = df_stocks[cols_order].copy()
            df_st_table.columns = [
                "Ticker", "Empresa", "Setor", "Qtd", "Preço Médio (R$)", "Cotação (R$)",
                "Investido (R$)", "Patrimônio (R$)", "Rentabilidade (%)", "P/L", "P/VP", "ROE (%)", "ROIC (%)",
                "Margem Líq (%)", "DY 12M (%)", "Diagnóstico Valuation", "Peso (%)"
            ]
            st.dataframe(
                df_st_table.style.format({
                    "Qtd": "{:,.0f}",
                    "Preço Médio (R$)": "R$ {:,.2f}",
                    "Cotação (R$)": "R$ {:,.2f}",
                    "Investido (R$)": "R$ {:,.2f}",
                    "Patrimônio (R$)": "R$ {:,.2f}",
                    "Rentabilidade (%)": "{:+.2f}%",
                    "P/L": lambda x: f"{x:.1f}x" if pd.notna(x) else "-",
                    "P/VP": lambda x: f"{x:.2f}x" if pd.notna(x) else "-",
                    "ROE (%)": lambda x: f"{x:.1f}%" if pd.notna(x) else "-",
                    "ROIC (%)": lambda x: f"{x:.1f}%" if pd.notna(x) else "-",
                    "Margem Líq (%)": lambda x: f"{x:.1f}%" if pd.notna(x) else "-",
                    "DY 12M (%)": "{:.2f}%",
                    "Peso (%)": "{:.2f}%"
                }),
                use_container_width=True
            )

# ==============================================================================
# ABA 3: ALOCAÇÃO & METAS (ASSET ALLOCATION)
# ==============================================================================
with tab_allocation:
    st.subheader("⚖️ Alocação Macro da Carteira & Metas")
    st.markdown("Defina suas metas percentuais para cada classe de ativos e visualize o rebalanceamento inteligente.")

    c_meta, c_chart = st.columns([1, 2])

    with c_meta:
        with st.container(border=True):
            st.markdown("##### 🎯 Configurar Metas Macro")
            current_targets = PortfolioRepository.get_macro_allocations()
            
            meta_fii = st.number_input("Meta FIIs (%)", min_value=0.0, max_value=100.0, value=float(current_targets.get("FII", 50.0)), step=5.0)
            meta_acao = st.number_input("Meta Ações (%)", min_value=0.0, max_value=100.0, value=float(current_targets.get("ACAO", 40.0)), step=5.0)
            meta_rf = st.number_input("Meta Renda Fixa/Caixa (%)", min_value=0.0, max_value=100.0, value=float(current_targets.get("RENDA_FIXA", 10.0)), step=5.0)

            total_meta = meta_fii + meta_acao + meta_rf
            if abs(total_meta - 100.0) > 0.01:
                st.warning(f"A soma das metas é {total_meta:.1f}%. Ajuste para totalizar 100%.")
            
            if st.button("Salvar Metas de Alocação"):
                PortfolioRepository.update_macro_allocation("FII", meta_fii)
                PortfolioRepository.update_macro_allocation("ACAO", meta_acao)
                PortfolioRepository.update_macro_allocation("RENDA_FIXA", meta_rf)
                st.success("Metas atualizadas com sucesso!")
                st.rerun()

    with c_chart:
        # Tabela Comparativa de Metas
        df_macro = pd.DataFrame(macro_data["classes"])
        if not df_macro.empty:
            st.dataframe(
                df_macro[["name", "current_value", "current_pct", "target_pct", "diff_pct", "status"]].rename(columns={
                    "name": "Classe de Ativo",
                    "current_value": "Valor Atual (R$)",
                    "current_pct": "% Atual",
                    "target_pct": "% Meta",
                    "diff_pct": "Desvio (%)",
                    "status": "Diagnóstico"
                }).style.format({
                    "Valor Atual (R$)": "R$ {:,.2f}",
                    "% Atual": "{:.2f}%",
                    "% Meta": "{:.2f}%",
                    "Desvio (%)": "{:+.2f}%"
                }),
                use_container_width=True
            )

    st.write("")
    st.subheader("💡 Calculadora de Aporte Inteligente (Sem Vender Ativos)")
    st.markdown("""
    Insira quanto dinheiro você tem disponível para aportar neste mês. O algoritmo calculará exatamente onde alocar o capital para aproximar sua carteira das metas sem custos ou impostos de venda.
    """)

    col_aporte_in, col_aporte_res = st.columns([1, 2])
    with col_aporte_in:
        aporte_val = st.number_input("Valor do Novo Aporte (R$)", min_value=100.0, value=2000.0, step=500.0)
        calc_btn = st.button("Calcular Aporte Recomendado", type="primary")

    with col_aporte_res:
        if calc_btn or aporte_val > 0:
            suggestions = AllocationService.calculate_smart_contribution(aporte_val, macro_data)
            df_sug = pd.DataFrame(suggestions)
            st.dataframe(
                df_sug[["name", "current_pct", "target_pct", "suggested_amount", "projected_pct"]].rename(columns={
                    "name": "Classe",
                    "current_pct": "% Atual",
                    "target_pct": "% Meta",
                    "suggested_amount": "Aporte Sugerido (R$)",
                    "projected_pct": "% Projetada Pós-Aporte"
                }).style.format({
                    "% Atual": "{:.2f}%",
                    "% Meta": "{:.2f}%",
                    "Aporte Sugerido (R$)": "R$ {:,.2f}",
                    "% Projetada Pós-Aporte": "{:.2f}%"
                }),
                use_container_width=True
            )

# ==============================================================================
# ABA 4: GESTÃO DA CARTEIRA & IMPORTAÇÃO
# ==============================================================================
with tab_management:
    st.subheader("📥 Importação de Planilha & Cadastro Manual")
    
    col_upload, col_manual = st.columns(2)

    with col_upload:
        with st.container(border=True):
            st.markdown("##### 📄 Importar Arquivo (B3 ou Excel/CSV)")
            st.markdown("Você pode carregar o extrato exportado da B3 ou uma planilha simples contendo as colunas **Ticker**, **Quantidade** e **Preço Médio**.")
            
            uploaded_file = st.file_uploader("Selecione um arquivo .xlsx ou .csv", type=["xlsx", "xls", "csv"])
            if uploaded_file:
                bytes_data = uploaded_file.read()
                records, errors = ImportService.parse_file(bytes_data, uploaded_file.name)
                
                if errors:
                    for err in errors:
                        st.error(err)
                elif records:
                    st.success(f"{len(records)} posições identificadas com sucesso!")
                    st.dataframe(pd.DataFrame(records).head(5), use_container_width=True)
                    if st.button("Confirmar Importação para a Carteira", type="primary"):
                        count = ImportService.import_to_database(records)
                        st.success(f"{count} ativos importados/atualizados!")
                        st.rerun()

            st.write("")
            st.markdown("##### 📥 Baixar Modelo de Planilha")
            template_df = ImportService.get_template_df()
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False, sheet_name='Carteira')
            
            st.download_button(
                label="Baixar Modelo de Planilha (.xlsx)",
                data=buffer.getvalue(),
                file_name="modelo_carteira_investimentos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col_manual:
        with st.container(border=True):
            st.markdown("##### ✍️ Cadastro Manual de Ativo")
            
            ticker_input = st.text_input("Código / Ticker (ex: HGLG11, XPML11, ITUB4)").upper().strip()
            tipo_input = st.selectbox("Tipo de Ativo", ["FII", "ACAO", "RENDA_FIXA", "OUTRO"])
            
            col_q, col_p = st.columns(2)
            with col_q:
                qtd_input = st.number_input("Quantidade de Cotas/Ações", min_value=0.0, value=10.0, step=1.0)
            with col_p:
                preco_input = st.number_input("Preço Médio (R$)", min_value=0.0, value=100.0, step=5.0)

            segmento_default = FII_DEFAULT_SEGMENTS.get(ticker_input, "Outros") if tipo_input == "FII" else "Geral"
            segmento_input = st.text_input("Segmento / Setor", value=segmento_default)

            if st.button("Salvar / Atualizar Ativo"):
                if ticker_input and qtd_input > 0:
                    PortfolioRepository.upsert_asset(
                        ticker=ticker_input,
                        asset_type=tipo_input,
                        quantity=qtd_input,
                        average_price=preco_input,
                        segment=segmento_input
                    )
                    st.success(f"Ativo {ticker_input} salvo com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe um ticker válido e quantidade maior que zero.")

    st.write("")
    st.subheader("🗑️ Ativos Atuais na Base de Dados")
    if all_assets:
        df_all = pd.DataFrame(all_assets)
        st.dataframe(df_all[["id", "ticker", "asset_type", "quantity", "average_price", "segment", "updated_at"]], use_container_width=True)
        
        col_del1, col_del2 = st.columns([1, 3])
        with col_del1:
            ticker_to_delete = st.selectbox("Selecione um ativo para excluir", [a["ticker"] for a in all_assets])
            if st.button("Excluir Ativo Selecionado"):
                PortfolioRepository.delete_asset(ticker_to_delete)
                st.success(f"Ativo {ticker_to_delete} removido.")
                st.rerun()
    else:
        st.info("Nenhum ativo cadastrado ainda.")
