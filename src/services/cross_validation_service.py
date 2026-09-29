import logging
from typing import Dict, Any, Optional, List
from src.services.fundos_net_service import FundosNetService
from src.services.bolsai_service import BolsaiService
from src.services.market_data import MarketDataService

logger = logging.getLogger(__name__)

# Segmentos padronizados do ecossistema de FIIs
FII_CATEGORIES = {
    "LOGISTICA": "Logística e Renda Urbana",
    "PAPEL": "Papel e Recebíveis (CRIs)",
    "SHOPPING": "Shoppings Centers",
    "LAJES": "Lajes Corporativas / Escritórios",
    "FOF": "Fundos de Fundos (FOFs)",
    "AGRO": "Fiagros e Terras Agrícolas",
    "HIBRIDO": "Fundos Híbridos e Renda Urbana Mista"
}

# Mapeamento conhecido para os principais FIIs do mercado
KNOWN_SEGMENTS = {
    "KNCR11": "PAPEL", "KNIP11": "PAPEL", "MXRF11": "PAPEL", "CPTS11": "PAPEL",
    "KNSC11": "PAPEL", "VGIR11": "PAPEL", "RBRR11": "PAPEL", "HGCR11": "PAPEL",
    "IRDM11": "PAPEL", "MCCI11": "PAPEL", "CVBI11": "PAPEL", "VRTA11": "PAPEL",
    "BTCI11": "PAPEL", "RBRY11": "PAPEL",
    "XPML11": "SHOPPING", "VISC11": "SHOPPING", "HGBS11": "SHOPPING", "HSML11": "SHOPPING",
    "MALL11": "SHOPPING", "PMLL11": "SHOPPING", "BBRC11": "SHOPPING",
    "PVBI11": "LAJES", "HGRE11": "LAJES", "BRCR11": "LAJES", "JSRE11": "LAJES", "RCRB11": "LAJES",
    "HGLG11": "LOGISTICA", "BTLG11": "LOGISTICA", "XPLG11": "LOGISTICA", "GGRC11": "LOGISTICA",
    "TRXF11": "LOGISTICA", "VILG11": "LOGISTICA", "LVBI11": "LOGISTICA", "BRCO11": "LOGISTICA",
    "GARE11": "LOGISTICA", "GALG11": "LOGISTICA",

    "HFOF11": "FOF", "BCFF11": "FOF", "RBRF11": "FOF", "KFOF11": "FOF", "CXCI11": "FOF",
    "RZTR11": "AGRO", "VGIA11": "AGRO", "KNCA11": "AGRO", "RURA11": "AGRO", "FGAA11": "AGRO",
    "HGRU11": "HIBRIDO", "ALZR11": "HIBRIDO", "TGAR11": "HIBRIDO", "RBVA11": "HIBRIDO", "VGHF11": "HIBRIDO"
}

class CrossValidationService:
    """
    Motor de Validação Cruzada entre os documentos oficiais do Fundos.NET (B3/CVM)
    e a API de inteligência de mercado da BolsaAI.
    """

    @classmethod
    def detect_segment(cls, ticker: str, fnet_data: Dict[str, Any], bolsai_data: Optional[Dict[str, Any]]) -> str:
        """Identifica com precisão o segmento do FII."""
        ticker = ticker.upper().strip().replace(".SA", "")
        
        # 1. Mapeamento estático prioritário
        if ticker in KNOWN_SEGMENTS:
            return KNOWN_SEGMENTS[ticker]

        # 2. Informação da BolsaAI
        if bolsai_data:
            fund_type = str(bolsai_data.get("fund_type", "")).upper()
            seg_b = str(bolsai_data.get("segment", "")).upper()
            
            if "PAPEL" in fund_type or "RECEB" in seg_b or "CRI" in seg_b:
                return "PAPEL"
            if "SHOPPING" in seg_b:
                return "SHOPPING"
            if "LAJE" in seg_b or "ESCRIT" in seg_b:
                return "LAJES"
            if "AGRO" in seg_b or "FIAGRO" in seg_b or "CRA" in seg_b:
                return "AGRO"
            if "FOF" in seg_b or "FUNDO DE FUNDO" in seg_b:
                return "FOF"
            if "HIBRID" in seg_b or "MIST" in seg_b or "MULTIESTRAT" in seg_b or "DESENVOLV" in seg_b or "RENDA URBANA" in seg_b:
                return "HIBRIDO"
            if "LOG" in seg_b or "GALP" in seg_b:
                return "LOGISTICA"

        # 3. Informação do Fundos.NET / CVM
        seg_fnet = str(fnet_data.get("segmento", "")).upper()
        nome_fnet = str(fnet_data.get("razao_social", "")).upper()

        if any(w in seg_fnet or w in nome_fnet for w in ["CRI", "PAPEL", "RECEBÍVEIS", "RECEBIVEIS", "CRÉDITO"]):
            return "PAPEL"
        if any(w in seg_fnet or w in nome_fnet for w in ["SHOPPING", "MALL"]):
            return "SHOPPING"
        if any(w in seg_fnet or w in nome_fnet for w in ["LAJE", "ESCRITÓRIO", "ESCRITORIO", "CORPORATIV"]):
            return "LAJES"
        if any(w in seg_fnet or w in nome_fnet for w in ["AGRO", "FIAGRO", "TERRA"]):
            return "AGRO"
        if any(w in seg_fnet or w in nome_fnet for w in ["FUNDO DE FUNDO", "FOF", "TÍTULOS E VALORES"]):
            return "FOF"
        if any(w in seg_fnet or w in nome_fnet for w in ["HÍBRIDO", "HIBRIDO", "MISTO", "MULTIESTRATÉGIA", "RENDA URBANA", "DESENVOLVIMENTO"]):
            return "HIBRIDO"

        # Default inteligente
        return "LOGISTICA"

    @classmethod
    def validate_and_reconcile(cls, ticker: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa a validação cruzada completa confrontando Fundos.NET com BolsaAI.
        """
        ticker = ticker.upper().strip().replace(".SA", "")

        # 1. Coleta dados oficiais do Fundos.NET (CVM)
        fnet_data = FundosNetService.get_latest_fii_data(ticker)

        # 2. Coleta dados da BolsaAI
        bolsai_fii = BolsaiService.get_fii_details(ticker, api_key=api_key)
        bolsai_macro = BolsaiService.get_macro_indicators(api_key=api_key)
        if hasattr(BolsaiService, "get_fii_distributions_summary"):
            bolsai_dist = BolsaiService.get_fii_distributions_summary(ticker, years=3, api_key=api_key)
        else:
            bolsai_dist = {}
        
        # 3. Coleta dados de mercado fallback (Yahoo Finance / Brapi) se necessário
        market = MarketDataService.get_market_data(ticker)

        # Identifica segmento
        segment_code = cls.detect_segment(ticker, fnet_data, bolsai_fii)
        segment_name = FII_CATEGORIES.get(segment_code, "Logística e Renda Urbana")

        # Dados Reconciliados
        vpc_fnet = float(fnet_data.get("vpc", 0.0) or 0.0)
        pl_fnet = float(fnet_data.get("patrimonio_liquido", 0.0) or 0.0)
        cotistas_fnet = int(fnet_data.get("cotistas", 0) or 0)
        alavancagem_fnet = float(fnet_data.get("alavancagem_pl_pct", 0.0) or 0.0)
        divida_fnet = float(fnet_data.get("divida_cris", 0.0) or 0.0)

        # Mercado BolsaAI
        if bolsai_fii:
            price_market = float(bolsai_fii.get("close_price") or market.get("current_price", 0.0) or 0.0)
            pvp_market = round(price_market / vpc_fnet, 2) if (vpc_fnet > 0 and price_market > 0) else (float(bolsai_fii.get("pvp")) if bolsai_fii.get("pvp") else None)
            cotistas_market = int(bolsai_fii.get("total_shareholders") or cotistas_fnet)
            properties_info = {
                "property_count": bolsai_fii.get("property_count"),
                "total_area_sqm": bolsai_fii.get("total_area_sqm"),
                "vacancy_pct": bolsai_fii.get("vacancy_pct"),
                "delinquency_pct": bolsai_fii.get("delinquency_pct"),
                "top_properties": bolsai_fii.get("top_properties", []) or [],
                "asset_composition": bolsai_fii.get("asset_composition", {}) or {}
            }
        else:
            price_market = float(market.get("current_price", 0.0) or 0.0)
            pvp_market = round(price_market / vpc_fnet, 2) if (vpc_fnet > 0 and price_market > 0) else None
            cotistas_market = cotistas_fnet
            properties_info = {}

        # Auditoria e Reconciliação de Proventos: Recorrente (Run-Rate) vs TTM Histórico
        dy_ttm = float(bolsai_dist.get("dividend_yield_ttm") or (bolsai_fii.get("dividend_yield_ttm") if bolsai_fii else 0.0) or market.get("dy_12m", 0.0) or 0.0)
        last_div = float(bolsai_dist.get("latest_dividend") or market.get("last_dividend") or 0.0)
        if last_div <= 0.0 and dy_ttm > 0 and price_market > 0:
            last_div = round((price_market * (dy_ttm / 100.0)) / 12.0, 3)

        ttm_per_share = float(bolsai_dist.get("ttm_per_share") or 0.0)
        if ttm_per_share <= 0.0 and dy_ttm > 0 and price_market > 0:
            ttm_per_share = round((dy_ttm / 100.0) * price_market, 4)

        if price_market > 0 and last_div > 0:
            dy_recorrente = round((last_div * 12.0 / price_market) * 100.0, 2)
        else:
            dy_recorrente = dy_ttm

        recorrente_anual = last_div * 12.0
        extraordinarios_cota = round(max(0.0, ttm_per_share - recorrente_anual), 4)

        # Reconciliação de Preço x VPC
        divergences = []
        if vpc_fnet > 0 and price_market > 0:
            desagio_pct = ((price_market / vpc_fnet) - 1.0) * 100.0
            if abs(desagio_pct) > 25.0:
                divergences.append(f"Forte descolamento de mercado: Cota negociando com {desagio_pct:+.1f}% de diferença frente ao VPC oficial.")
        else:
            desagio_pct = 0.0

        # Detecção de Distorção em Proventos Extraordinários
        if abs(dy_ttm - dy_recorrente) >= 0.75:
            divergences.append(
                f"Distorção de Proventos: DY TTM histórico ({dy_ttm:.2f}%) diverge do DY Recorrente anualizado ({dy_recorrente:.2f}%). "
                f"O histórico de 12M inclui ~R$ {extraordinarios_cota:.2f}/cota em proventos extraordinários ou amortizações."
            )

        # Análise Macro: Spread de Risco frente à SELIC / CDI (baseado no Yield Recorrente)
        cdi_atual = float(bolsai_macro.get("cdi", 14.15))
        selic_atual = float(bolsai_macro.get("selic", 14.25))
        ipca_atual = float(bolsai_macro.get("ipca_12m", 4.50))
        
        spread_vs_cdi = round(dy_recorrente - cdi_atual, 2)
        spread_vs_ipca = round(dy_recorrente - ipca_atual, 2)
        spread_ttm_vs_cdi = round(dy_ttm - cdi_atual, 2)

        if spread_vs_cdi >= 0:
            spread_status = "Prêmio Atrativo: Dividend Yield Recorrente supera a taxa CDI atual."
        elif spread_vs_cdi > -2.0:
            spread_status = "Prêmio Competitivo: Isenção de IR compensa proximidade com o CDI."
        else:
            spread_status = "Spread Negativo: Yield recorrente abaixo do CDI; tese depende de valorização patrimonial."

        return {
            "ticker": ticker,
            "segment_code": segment_code,
            "segment_name": segment_name,
            "fnet": {
                "razao_social": fnet_data.get("razao_social"),
                "cnpj": fnet_data.get("cnpj"),
                "administrador": fnet_data.get("administrador"),
                "gestor": fnet_data.get("gestor"),
                "vpc": vpc_fnet,
                "pl": pl_fnet,
                "cotistas": cotistas_fnet,
                "alavancagem_pct": alavancagem_fnet,
                "divida_cris": divida_fnet,
                "data_referencia": fnet_data.get("data_referencia"),
                "data_protocolo_fnet": fnet_data.get("data_protocolo_fnet")
            },
            "bolsai": {
                "price": price_market,
                "pvp": pvp_market,
                "dy_anual": dy_recorrente,
                "dy_recorrente": dy_recorrente,
                "dy_ttm": dy_ttm,
                "ttm_per_share": ttm_per_share,
                "extraordinarios_cota": extraordinarios_cota,
                "adtv_milhoes": float(market.get("adtv_milhoes") or 0.0),
                "cotistas": cotistas_market,
                "properties_info": properties_info,
                "distributions_summary": bolsai_dist,
                "macro": {
                    "cdi": cdi_atual,
                    "selic": selic_atual,
                    "ipca": ipca_atual,
                    "spread_vs_cdi": spread_vs_cdi,
                    "spread_vs_ipca": spread_vs_ipca,
                    "spread_ttm_vs_cdi": spread_ttm_vs_cdi,
                    "spread_status": spread_status
                }
            },
            "reconciliation": {
                "desagio_pct": round(desagio_pct, 2),
                "last_dividend": round(last_div, 3),
                "dy_recorrente": dy_recorrente,
                "dy_ttm": dy_ttm,
                "extraordinarios_cota": extraordinarios_cota,
                "adtv_milhoes": float(market.get("adtv_milhoes") or 0.0),
                "divergences": divergences,
                "validated": True
            }
        }
