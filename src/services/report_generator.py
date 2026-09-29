import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.config import DATA_DIR
from src.services.fundos_net_service import FundosNetService
from src.services.market_data import MarketDataService
from src.services.bolsai_service import BolsaiService
from src.services.cross_validation_service import CrossValidationService, FII_CATEGORIES
from src.services.shopping_report_renderer import ShoppingReportRenderer, SHOPPING_KNOWLEDGE_BASE
from src.services.logistica_report_renderer import LogisticaReportRenderer, LOGISTICA_KNOWLEDGE_BASE
from src.services.papel_report_renderer import PapelReportRenderer, PAPEL_KNOWLEDGE_BASE
from src.services.lajes_report_renderer import LajesReportRenderer, LAJES_KNOWLEDGE_BASE
from src.services.fof_report_renderer import FofReportRenderer, FOF_KNOWLEDGE_BASE
from src.services.agro_report_renderer import AgroReportRenderer, AGRO_KNOWLEDGE_BASE
from src.services.hibrido_report_renderer import HibridoReportRenderer, HIBRIDO_KNOWLEDGE_BASE
from src.services.valuation_pricing_service import ValuationPricingService

REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Base de conhecimento especializada por segmento
FII_KNOWLEDGE_BASE = {
    # --- LOGÍSTICA & RENDA URBANA ---
    "TRXF11": {
        "segment_code": "LOGISTICA",
        "score": 7.4,
        "veredicto": "Aprovado com Ressalva",
        "veredicto_tipo": "warning",
        "teto": 86.95,
        "alocacao_sugerida": "5,0% a 8,0%",
        "vacancia_fisica": 0.5,
        "vacancia_financeira": 0.3,
        "contratos_atipicos_pct": 72.66,
        "wault_anos": 13.14,
        "adtv_milhoes": 46.51,
        "preco_mercado": 79.30,
        "dy_anual": 14.07,
        "provento_mes": 0.93,
        "ffo_cota": 0.72,
        "cobertura_ffo": 0.77,
        "tipologia_abl": [
            ("Galpões Logísticos", 56.3, "#38bdf8"),
            ("Varejo Big Box / Lojas", 28.3, "#22c55e"),
            ("Saúde / Hospitais", 8.4, "#f59e0b"),
            ("Shoppings Centers", 5.0, "#a855f7"),
            ("Educacional & Outros", 2.0, "#ec4899")
        ],
        "top_inquilinos": [
            ("Mercado Livre", "E-commerce / Logística", 14.51, "Atípico (BTS)", "Corporativo AAA", "> 2035"),
            ("Assaí Atacadista", "Varejo Alimentar (Atacarejo)", 11.38, "Atípico (SLB)", "Rating AA+", "2035 a 2040"),
            ("Grupo Mateus", "Supermercados / Atacarejo", 10.88, "Atípico (BTS)", "Rating AA", "> 2038"),
            ("Hospital Albert Einstein", "Saúde / Infraestrutura", 10.13, "Atípico (BTS)", "Triple A", "> 2045"),
            ("Grupo Pão de Açúcar (GPA)", "Varejo Supermercadista", 7.66, "Atípico (SLB)", "Rating A-", "Desinvestimento"),
            ("Demais Locatários (Shopee, Leroy)", "Diversos (709 inquilinos)", 45.44, "Típico / Atípico", "Pulverizado", "Diversos")
        ],
        "indexadores": {"IPCA": 75.91, "IGP-M & IPC": 5.89, "IGP-M": 5.13, "Outros / Típicos": 13.07},
        "green_flags": [
            "WAULT excepcional de 13,14 anos com 72,66% em contratos atípicos invioláveis.",
            "Vacância física residual de apenas 0,5% e financeira de 0,3% em 123 ativos.",
            "Qualidade superior dos ativos: Hospital Einstein Parque Global, Shopee, Meli e Assaí.",
            "Desconto patrimonial expressivo negociando abaixo do valor patrimonial contábil.",
            "Altíssima liquidez secundária na B3 (ADTV > R$ 45 milhões/dia)."
        ],
        "red_flags": [
            "Déficit no Índice de Cobertura (0,77): FFO gerado inferior ao provento distribuído.",
            "Alavancagem elevada (acima de 45% do PL) em securitizações de CRIs.",
            "Exposição a CDI em período de juros elevados consumindo receitas financeiras."
        ]
    },
    "GGRC11": {
        "segment_code": "LOGISTICA",
        "score": 7.8,
        "veredicto": "Aprovado com Ressalva",
        "veredicto_tipo": "warning",
        "teto": 10.90,
        "alocacao_sugerida": "4,0% a 6,0%",
        "vacancia_fisica": 0.14,
        "vacancia_financeira": 0.00,
        "contratos_atipicos_pct": 79.50,
        "wault_anos": 6.80,
        "adtv_milhoes": 20.93,
        "preco_mercado": 9.13,
        "dy_anual": 13.14,
        "provento_mes": 0.10,
        "ffo_cota": 0.101,
        "cobertura_ffo": 1.01,
        "tipologia_abl": [
            ("Logístico", 79.09, "#2563eb"),
            ("Híbrido", 11.43, "#0ea5e9"),
            ("Industrial", 9.48, "#f59e0b")
        ],
        "top_inquilinos": [
            ("Renault", "Automotivo / Multinacional", 8.80, "Atípico", "Corporativo Multilatina", "Longo Prazo"),
            ("Ambev", "Bens de Consumo / Bebidas", 8.00, "Atípico", "Grau de Investimento AAA", "Longo Prazo"),
            ("Americanas", "Varejo / E-commerce", 7.90, "Atípico", "Em Recuperação Judicial", "Contrato Atípico"),
            ("Triple A (Casas Bahia)", "Varejo / Logística", 5.80, "Atípico (Indireto)", "Em Recuperação Judicial", "Garantia Integral"),
            ("Ligga / Copel Telecom", "Telecom / Infraestrutura", 4.60, "Atípico", "Infraestrutura", "Longo Prazo")
        ],
        "indexadores": {"IPCA": 88.50, "IGP-M": 9.20, "Outros": 2.30},
        "green_flags": [
            "Valuation com 17% de deságio patrimonial (P/VP de 0,83).",
            "Vacância física de apenas 0,14% e vacância financeira zerada.",
            "Alavancagem muito conservadora (8,8% do PL), bem abaixo do limite de 25%.",
            "Cobertura de 101% do dividendo pelo lucro caixa operacional (FFO)."
        ],
        "red_flags": [
            "Exposição a devedores em Recuperação Judicial (Americanas e Casas Bahia somando 13,7%).",
            "Necessidade de auditoria jurídica contínua sobre as garantias das locações."
        ]
    },
    "HGLG11": {
        "segment_code": "LOGISTICA",
        "score": 8.8,
        "veredicto": "Aprovado",
        "veredicto_tipo": "success",
        "teto": 162.20,
        "alocacao_sugerida": "10,0% a 15,0%",
        "vacancia_fisica": 4.90,
        "vacancia_financeira": 5.20,
        "contratos_atipicos_pct": 32.00,
        "wault_anos": 3.80,
        "adtv_milhoes": 10.80,
        "preco_mercado": 147.50,
        "dy_anual": 9.48,
        "provento_mes": 1.17,
        "ffo_cota": 1.21,
        "cobertura_ffo": 1.03,
        "tipologia_abl": [
            ("Galpões Logísticos", 88.0, "#38bdf8"),
            ("Híbrido / Industrial", 12.0, "#f59e0b")
        ],
        "top_inquilinos": [
            ("Mercado Livre", "E-commerce / Logística", 14.04, "Atípico", "AAA (Sólido)", "> 2030"),
            ("Volkswagen", "Automotivo", 11.20, "Atípico", "Multinacional", "> 2032"),
            ("Lojas Renner", "Varejo", 5.40, "Típico", "Resiliente", "Revisional Trienal"),
            ("Carrefour / Atacadão", "Supermercados", 4.60, "Típico", "Grau Investimento", "Longo Prazo"),
            ("Amazon Brasil", "Tecnologia / Logística", 4.10, "Atípico", "AAA Global", "> 2030")
        ],
        "indexadores": {"IPCA": 79.20, "IGP-M": 18.50, "INPC / Outros": 2.30},
        "green_flags": [
            "Ativos Tier 1: Padrão construtivo A+/AAA, pé-direito 12m-14m e piso 6 ton/m².",
            "Localização prime: 76,4% em SP com quase metade em raio < 30 km (last mile).",
            "Cobertura sadia (1,03x) gerando lucro caixa suficiente para cobrir os proventos.",
            "Baixa alavancagem financeira (8,6% do PL) e indexador casado no IPCA."
        ],
        "red_flags": [
            "Top 2 locatários (Meli e VW) concentram mais de 25% da receita.",
            "68% em contratos típicos sujeitos a revisionais periódicas."
        ]
    },
    "VILG11": {
        "segment_code": "LOGISTICA",
        "score": 8.6,
        "veredicto": "Aprovado",
        "veredicto_tipo": "success",
        "teto": 108.50,
        "alocacao_sugerida": "7,5% a 10,0%",
        "vacancia_fisica": 3.50,
        "vacancia_financeira": 2.80,
        "contratos_atipicos_pct": 55.00,
        "wault_anos": 4.50,
        "adtv_milhoes": 4.20,
        "preco_mercado": 91.68,
        "dy_anual": 10.73,
        "provento_mes": 0.82,
        "ffo_cota": 0.83,
        "cobertura_ffo": 1.012,
        "tipologia_abl": [
            ("Galpões Logísticos Classe A", 68.5, "#38bdf8"),
            ("Centros de Distribuição E-Commerce", 22.5, "#22c55e"),
            ("Hubs Regionais / Cross-Docking", 9.0, "#f59e0b")
        ],
        "top_inquilinos": [
            ("Tok&Stok", "Móveis & Decoração", 14.00, "Atípico", "Varejo", "> 2029"),
            ("Mercado Livre", "E-commerce & Fulfillment", 11.50, "Atípico (BTS)", "AAA", "> 2031"),
            ("Ambev S.A.", "Bens de Consumo / Bebidas", 8.50, "Atípico", "AAA", "> 2030"),
            ("DHL Logistics", "Operador Global", 7.00, "Típico", "AAA", "2028"),
            ("Magazine Luiza", "Varejo Eletrodomésticos", 6.00, "Atípico", "AA", "2029")
        ],
        "indexadores": {"IPCA": 84.00, "IGP-M": 16.00},
        "green_flags": [
            "Desconto patrimonial expressivo com P/VP de 0,84 frente ao VPC de R$ 108,69.",
            "Portfólio 100% Galpões Classe A modernos (pé-direito > 12m e piso 6 ton/m²).",
            "Vacância física controlada em 3,5% com 96,5% de taxa de ocupação.",
            "Alavancagem saudável e conservadora de 13,09% do PL em CRIs sem risco de curto prazo.",
            "Forte liquidez diária de R$ 4,2 milhões e 149 mil cotistas na B3."
        ],
        "red_flags": [
            "Exposição a Tok&Stok (14% da receita) demanda monitoramento constante.",
            "45% em contratos típicos sujeitos a revisionais trienais."
        ]
    },

    # --- PAPEL & RECEBÍVEIS (CRIs) ---
    "KNCR11": {
        "segment_code": "PAPEL",
        "score": 9.1,
        "veredicto": "Aprovado",
        "veredicto_tipo": "success",
        "teto": 105.00,
        "alocacao_sugerida": "10,0% a 15,0%",
        "taxa_media": "CDI + 2,15% a.a.",
        "duration_anos": 2.4,
        "ltv_medio": 54.0,
        "perfil_credito": "High Grade Puro",
        "preco_mercado": 105.87,
        "dy_anual": 14.76,
        "provento_mes": 1.15,
        "ffo_cota": 1.18,
        "cobertura_ffo": 1.02,
        "adtv_milhoes": 12.40,
        "indexadores": {"CDI": 98.2, "IPCA": 1.8},
        "subordinacao": {"Sênior": 92.5, "Mezanino": 7.5, "Subordinada": 0.0},
        "top_devedores": [
            ("Brookfield / Brascan", "Corporativo / Comercial", 7.8, "CDI + 1,90%", 48.0, "Alienação Fiduciária de Edifícios AAA"),
            ("JHSF Participações", "Shoppings / Luxo", 6.9, "CDI + 2,10%", 52.0, "Cessão de Recebíveis + Hipoteca"),
            ("Iguatemi Empresa de Shopping", "Shoppings Centers", 5.8, "CDI + 1,80%", 45.0, "Alienação Fiduciária de Shoppings"),
            ("Cyrela Commercial Properties", "Lajes Corporativas", 5.2, "CDI + 2,05%", 50.0, "Garantia Real Imobiliária"),
            ("GLP Logística", "Galpões Logísticos", 4.9, "CDI + 1,95%", 55.0, "Alienação Fiduciária de Galpões")
        ],
        "green_flags": [
            "Carteira 98% indexada ao CDI, capturando integralmente a taxa SELIC elevada sem descasamento.",
            "Perfil High Grade de altíssima segurança: Devedores de primeira linha com LTV médio de 54%.",
            "Inadimplência histórica zerada: Excelente esteira de crédito estruturada pela Kinea/Itaú.",
            "Liquidez excepcional: Maior FII de papel da B3 com mais de 570 mil cotistas."
        ],
        "red_flags": [
            "Sensibilidade a cortes na taxa SELIC: Em ciclos de afrouxamento monetário, o rendimento nominal reduz proporcionalmente.",
            "Cota negociando com leve ágio sobre o valor patrimonial contábil (P/VP ~1,03)."
        ]
    },
    "MXRF11": {
        "segment_code": "PAPEL",
        "score": 8.0,
        "veredicto": "Aprovado",
        "veredicto_tipo": "success",
        "teto": 10.20,
        "alocacao_sugerida": "8,0% a 12,0%",
        "taxa_media": "CDI + 2,50% / IPCA + 7,80%",
        "duration_anos": 3.1,
        "ltv_medio": 58.0,
        "perfil_credito": "Middle / High Grade",
        "preco_mercado": 9.01,
        "dy_anual": 13.29,
        "provento_mes": 0.10,
        "ffo_cota": 0.102,
        "cobertura_ffo": 1.02,
        "adtv_milhoes": 18.50,
        "indexadores": {"CDI": 68.0, "IPCA": 32.0},
        "subordinacao": {"Sênior": 88.0, "Mezanino": 12.0, "Subordinada": 0.0},
        "top_devedores": [
            ("CRI GPA / Pão de Açúcar", "Varejo Alimentar", 4.8, "IPCA + 7,20%", 55.0, "Alienação de Lojas"),
            ("CRI Mateus Supermercados", "Varejo", 4.2, "CDI + 2,30%", 50.0, "Garantia Real Imobiliária"),
            ("CRI Lavvi Residencial", "Incorporação SP", 3.9, "CDI + 2,60%", 60.0, "Cessão Fiduciária de Recebíveis"),
            ("CRI Rede D'Or São Luiz", "Saúde / Hospitalar", 3.5, "IPCA + 6,80%", 48.0, "Alienação Fiduciária Hospital")
        ],
        "green_flags": [
            "Portfólio com mais de 1,1 milhão de cotistas e liquidez diária entre as maiores da bolsa.",
            "Carteira diversificada balanceando tranches atreladas a CDI e IPCA.",
            "Desconto patrimonial atraente com cotação abaixo de R$ 10,00."
        ],
        "red_flags": [
            "Exposição a permutas financeiras residenciais que dependem de velocidade de vendas.",
            "Giro de carteira frequente exigindo alocações contínuas da gestão."
        ]
    },

    # --- SHOPPINGS CENTERS ---
    "XPML11": {
        "segment_code": "SHOPPING",
        "score": 8.6,
        "veredicto": "Aprovado",
        "veredicto_tipo": "success",
        "teto": 108.00,
        "alocacao_sugerida": "8,0% a 12,0%",
        "sss_pct": 7.8,
        "ssr_pct": 8.4,
        "noi_margem_pct": 89.2,
        "custo_ocupacao_pct": 11.6,
        "inadimplencia_lojistas_pct": 2.76,
        "vacancia_fisica": 5.2,
        "preco_mercado": 97.70,
        "dy_anual": 12.47,
        "provento_mes": 0.92,
        "ffo_cota": 0.95,
        "cobertura_ffo": 1.03,
        "adtv_milhoes": 16.80,
        "top_shoppings": [
            ("Praia de Belas Shopping", "Porto Alegre / RS", 49087, 9.71, 8.15, "Multiplan / Domínio Consolidado"),
            ("Shopping Pátio Higienópolis", "São Paulo / SP", 34132, 5.65, 1.75, "Região Nobre / Alta Renda"),
            ("Shopping Iguatemi Ribeirão Preto", "Ribeirão Preto / SP", 46560, 5.65, 11.38, "Interior Paulista / Prime"),
            ("Shopping Iguatemi Alphaville", "Barueri / SP", 30967, 5.65, 3.99, "Pólo Corporativo e Residencial"),
            ("Shopping Bela Vista", "Salvador / BA", 51200, 4.80, 6.20, "Consumo Regional")
        ],
        "green_flags": [
            "Portfólio com 17 shopping centers consolidados em capitais e regiões nobres.",
            "Crescimento consistente nas Vendas Mesmas Lojas (SSS +7,8%) e Aluguel (SSR +8,4%).",
            "Custo de ocupação saudável (11,6%) garantindo adimplência e atratividade para lojistas.",
            "Deságio relevante de mais de 11% frente ao valor patrimonial dos imóveis."
        ],
        "red_flags": [
            "Sensibilidade a recessão ou aperto do poder de compra no varejo discricionário.",
            "Alavancagem em CRIs para expansões e aquisições recentes requerendo amortizações regulares."
        ]
    },

    # --- LAJES CORPORATIVAS ---
    "PVBI11": {
        "segment_code": "LAJES",
        "score": 8.5,
        "veredicto": "Aprovado",
        "veredicto_tipo": "success",
        "teto": 105.00,
        "alocacao_sugerida": "6,0% a 10,0%",
        "aluguel_medio_m2": 195.0,
        "vacancia_fisica": 4.1,
        "eixos_prime_pct": 94.0,
        "certificacao_verde_pct": 100.0,
        "preco_mercado": 89.50,
        "dy_anual": 9.20,
        "provento_mes": 0.68,
        "ffo_cota": 0.70,
        "cobertura_ffo": 1.03,
        "adtv_milhoes": 8.50,
        "top_edificios": [
            ("Faria Lima 4440", "Faria Lima / SP", 14500, "Triple A / LEED Gold", "UBS, Credit Suisse", "> 2028"),
            ("Vila Olímpia Corporate", "Vila Olímpia / SP", 18200, "Triple A / LEED Gold", "Multinacionais de Tecnologia", "> 2029"),
            ("JK Financial Center", "Itaim Bibi / SP", 11400, "Triple A", "Bancos e Family Offices", "> 2030")
        ],
        "green_flags": [
            "Mais de 90% dos ativos localizados nos eixos mais nobres de São Paulo (Faria Lima e Itaim).",
            "Vacância física baixa (4,1%) frente à média da cidade (superior a 18%).",
            "Padrão construtivo Triple A com certificação sustentável e inquilinos multinacionais."
        ],
        "red_flags": [
            "Ticket de locação por m² elevado, dependente da absorção do setor financeiro e tech.",
            "Concentração geográfica integral na capital paulista."
        ]
    }
}
FII_KNOWLEDGE_BASE.update(SHOPPING_KNOWLEDGE_BASE)
FII_KNOWLEDGE_BASE.update(LOGISTICA_KNOWLEDGE_BASE)
FII_KNOWLEDGE_BASE.update(PAPEL_KNOWLEDGE_BASE)
FII_KNOWLEDGE_BASE.update(LAJES_KNOWLEDGE_BASE)
FII_KNOWLEDGE_BASE.update(FOF_KNOWLEDGE_BASE)
FII_KNOWLEDGE_BASE.update(AGRO_KNOWLEDGE_BASE)
FII_KNOWLEDGE_BASE.update(HIBRIDO_KNOWLEDGE_BASE)

class ReportGenerator:
    """
    Gerador de Dossiês e Relatórios de Auditoria Fundamentalista de FIIs
    com suporte multi-segmento e validação cruzada Fundos.NET + BolsaAI.
    """

    @classmethod
    def generate_html_report(cls, ticker: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ticker = ticker.upper().strip().replace(".SA", "")

        # 1. Executa validação cruzada entre Fundos.NET e BolsaAI
        cross = CrossValidationService.validate_and_reconcile(ticker)
        seg_code = cross["segment_code"]
        seg_name = cross["segment_name"]

        # Se for do segmento SHOPPING, renderiza via ShoppingReportRenderer padronizado
        if seg_code == "SHOPPING":
            html = ShoppingReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_shop = SHOPPING_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_shop.get("score", 8.0)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_shop.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_shop.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_shop.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_shop.get("pvp", 0.85),
                "dy_anual": bolsai.get("dy_anual") or kb_shop.get("dy_anual", 10.5),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_shop.get("dy_anual", 10.5),
                "dy_ttm": bolsai.get("dy_ttm") or kb_shop.get("dy_anual", 10.5),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_shop.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_shop.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_shop.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        # Se for do segmento LOGISTICA, renderiza via LogisticaReportRenderer padronizado
        if seg_code == "LOGISTICA":
            html = LogisticaReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_log = LOGISTICA_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_log.get("score", 8.5)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_log.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_log.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_log.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_log.get("pvp", 0.90),
                "dy_anual": bolsai.get("dy_anual") or kb_log.get("dy_anual", 9.5),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_log.get("dy_anual", 9.5),
                "dy_ttm": bolsai.get("dy_ttm") or kb_log.get("dy_anual", 9.5),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_log.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_log.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_log.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        # Se for do segmento PAPEL, renderiza via PapelReportRenderer padronizado
        if seg_code == "PAPEL":
            html = PapelReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_papel = PAPEL_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_papel.get("score", 8.8)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_papel.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_papel.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_papel.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_papel.get("pvp", 0.98),
                "dy_anual": bolsai.get("dy_anual") or kb_papel.get("dy_anual", 13.5),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_papel.get("dy_anual", 13.5),
                "dy_ttm": bolsai.get("dy_ttm") or kb_papel.get("dy_anual", 13.5),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_papel.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_papel.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_papel.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        # Se for do segmento LAJES, renderiza via LajesReportRenderer padronizado
        if seg_code == "LAJES":
            html = LajesReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_lajes = LAJES_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_lajes.get("score", 8.3)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_lajes.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_lajes.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_lajes.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_lajes.get("pvp", 0.80),
                "dy_anual": bolsai.get("dy_anual") or kb_lajes.get("dy_anual", 9.5),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_lajes.get("dy_anual", 9.5),
                "dy_ttm": bolsai.get("dy_ttm") or kb_lajes.get("dy_anual", 9.5),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_lajes.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_lajes.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_lajes.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        # Se for do segmento FOF, renderiza via FofReportRenderer padronizado
        if seg_code == "FOF":
            html = FofReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_fof = FOF_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_fof.get("score", 8.5)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_fof.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_fof.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_fof.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_fof.get("pvp", 0.85),
                "dy_anual": bolsai.get("dy_anual") or kb_fof.get("dy_anual", 10.5),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_fof.get("dy_anual", 10.5),
                "dy_ttm": bolsai.get("dy_ttm") or kb_fof.get("dy_anual", 10.5),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_fof.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_fof.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_fof.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        # Se for do segmento AGRO, renderiza via AgroReportRenderer padronizado
        if seg_code == "AGRO":
            html = AgroReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_agro = AGRO_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_agro.get("score", 8.8)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_agro.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_agro.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_agro.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_agro.get("pvp", 0.92),
                "dy_anual": bolsai.get("dy_anual") or kb_agro.get("dy_anual", 13.8),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_agro.get("dy_anual", 13.8),
                "dy_ttm": bolsai.get("dy_ttm") or kb_agro.get("dy_anual", 13.8),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_agro.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_agro.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_agro.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        # Se for do segmento HIBRIDO, renderiza via HibridoReportRenderer padronizado
        if seg_code == "HIBRIDO":
            html = HibridoReportRenderer.render(ticker, cross, custom_params=custom_params)
            report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html)

            kb_hib = HIBRIDO_KNOWLEDGE_BASE.get(ticker, {})
            score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else kb_hib.get("score", 8.8)
            veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else kb_hib.get("veredicto", "Aprovado")
            teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else kb_hib.get("teto")
            alocacao_sug = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else kb_hib.get("alocacao_sugerida")
            fnet = cross.get("fnet", {})
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})

            return {
                "ticker": ticker,
                "segment_code": seg_code,
                "segment_name": seg_name,
                "html_path": str(report_file),
                "html_content": html,
                "score": score,
                "veredicto": veredicto,
                "teto": teto,
                "alocacao_sugerida": alocacao_sug,
                "pvp": bolsai.get("pvp") or kb_hib.get("pvp", 0.95),
                "dy_anual": bolsai.get("dy_anual") or kb_hib.get("dy_anual", 10.5),
                "dy_recorrente": bolsai.get("dy_recorrente") or kb_hib.get("dy_anual", 10.5),
                "dy_ttm": bolsai.get("dy_ttm") or kb_hib.get("dy_anual", 10.5),
                "extraordinarios_cota": bolsai.get("extraordinarios_cota", 0.0),
                "cotistas": int(fnet.get("cotistas") or bolsai.get("cotistas") or kb_hib.get("cotistas") or 0),
                "pl": float(fnet.get("patrimonio_liquido") or (kb_hib.get("pl_bi", 0) * 1e9)),
                "alavancagem_pct": float(fnet.get("alavancagem_pl_pct") or kb_hib.get("alavancagem_pl") or 0.0),
                "spread_vs_cdi": macro.get("spread_vs_cdi")
            }

        fnet = cross["fnet"]
        bolsai = cross["bolsai"]
        reconcil = cross["reconciliation"]
        macro = bolsai["macro"]

        # 2. Base técnica (se configurada manualmente para o ticker)
        kb = FII_KNOWLEDGE_BASE.get(ticker, {})

        # Score Técnico e Veredicto: se fornecido pelo usuário, usa. Se não, usa KB. Se não houver, None.
        user_score = custom_params.get("score") if (custom_params and custom_params.get("score") is not None) else None
        score = float(user_score) if user_score is not None else (float(kb["score"]) if "score" in kb else None)

        user_veredicto = custom_params.get("veredicto") if (custom_params and custom_params.get("veredicto")) else None
        veredicto = user_veredicto if (user_veredicto and user_veredicto != "Em Análise (-)") else kb.get("veredicto")
        veredicto_str = veredicto if veredicto else "Em Análise"
        veredicto_tipo = "success" if veredicto == "Aprovado" else ("danger" if veredicto == "Reprovado" else "warning")

        # Cotação e VPC oficiais
        preco_mercado = float(bolsai.get("price") or 0.0)
        vpc = float(fnet.get("vpc") or 0.0)
        pvp = round(preco_mercado / vpc, 2) if (vpc > 0 and preco_mercado > 0) else None

        # Yield Recorrente e Histórico TTM
        dy_recorrente = float(bolsai.get("dy_recorrente") or reconcil.get("dy_recorrente") or 0.0)
        dy_ttm = float(bolsai.get("dy_ttm") or reconcil.get("dy_ttm") or dy_recorrente)
        dy_anual = dy_recorrente
        extraordinarios = float(bolsai.get("extraordinarios_cota", 0.0) or reconcil.get("extraordinarios_cota", 0.0))

        # Proventos do mês
        provento_mes = float(reconcil.get("last_dividend") or kb.get("provento_mes") or 0.0)

        # FFO e Cobertura (Não inventar dados!)
        ffo_cota = float(kb["ffo_cota"]) if ("ffo_cota" in kb and kb["ffo_cota"] is not None) else None
        cobertura_ffo = float(kb["cobertura_ffo"]) if ("cobertura_ffo" in kb and kb["cobertura_ffo"] is not None) else None
        if ffo_cota is not None and provento_mes > 0 and cobertura_ffo is None:
            cobertura_ffo = round(ffo_cota / provento_mes, 2)

        # Preço-Teto e Alocação Sugerida
        user_teto = custom_params.get("teto") if (custom_params and custom_params.get("teto") is not None) else None
        teto = float(user_teto) if (user_teto and float(user_teto) > 0) else (float(kb["teto"]) if ("teto" in kb and kb["teto"]) else None)
        if teto is None and preco_mercado > 0 and vpc > 0:
            calc_p = ValuationPricingService.calculate_consolidated_pricing(
                ticker=ticker,
                metrics={
                    "preco_mercado": preco_mercado,
                    "vpc": vpc,
                    "provento_mes": provento_mes,
                    "ffo_cota": ffo_cota,
                    "dy_anual": dy_recorrente
                },
                segment_code=seg_code
            )
            teto = calc_p.get("preco_teto_recomendado")

        user_aloc = custom_params.get("alocacao_sugerida") if (custom_params and custom_params.get("alocacao_sugerida")) else None
        alocacao_sug = user_aloc if (user_aloc and user_aloc != "-") else kb.get("alocacao_sugerida")

        # Dados Patrimoniais
        pl = float(fnet.get("pl") or 0.0)
        cotistas = int(bolsai.get("cotistas") or fnet.get("cotistas") or 0)
        alavancagem_pct = float(fnet.get("alavancagem_pct") or 0.0)
        divida_cris = float(fnet.get("divida_cris") or 0.0)
        adtv = float(reconcil.get("adtv_milhoes") or bolsai.get("adtv_milhoes") or 0.0)

        # Formatações com '-' para dados não disponíveis
        pl_format = f"R$ {pl / 1e9:.2f} Bi" if pl >= 1e9 else (f"R$ {pl / 1e6:.1f} Mi" if pl > 0 else "-")
        divida_format = f"R$ {divida_cris / 1e9:.2f} Bi" if divida_cris >= 1e9 else (f"R$ {divida_cris / 1e6:.1f} Mi" if divida_cris > 0 else "R$ 0,00")
        preco_str = f"R$ {preco_mercado:,.2f}" if preco_mercado > 0 else "-"
        vpc_str = f"R$ {vpc:,.2f}" if vpc > 0 else "-"
        pvp_str = f"{pvp:.2f}" if pvp is not None else "-"
        dy_rec_str = f"{dy_recorrente:.2f}% a.a." if dy_recorrente > 0 else "-"
        provento_str = f"R$ {provento_mes:,.3f}/mês" if provento_mes > 0 else "-"
        dy_ttm_str = f"{dy_ttm:.2f}%" if dy_ttm > 0 else "-"
        cotistas_str = f"{cotistas:,}" if cotistas > 0 else "-"
        adtv_str = f"R$ {adtv:.2f} mi" if adtv > 0 else "-"
        teto_str = f"R$ {teto:,.2f}" if teto is not None else "-"
        alocacao_str = alocacao_sug if alocacao_sug else "-"
        score_html = f"{score:.1f}<span style='font-size: 1rem; color: var(--text-muted); font-weight: 500;'>/10</span>" if score is not None else "<span style='color: var(--text-muted); font-size:1.4rem;'>-</span>"
        ffo_cota_str = f"R$ {ffo_cota:,.3f}" if ffo_cota is not None else "-"
        cobertura_str = f"{cobertura_ffo:.2f} ({cobertura_ffo*100:.1f}%)" if cobertura_ffo is not None else "-"

        props_info = bolsai.get("properties_info", {}) or {}
        real_top_properties = props_info.get("top_properties", []) or []
        asset_comp = props_info.get("asset_composition", {}) or {}

        vac_fis = props_info.get("vacancy_pct") if props_info.get("vacancy_pct") is not None else kb.get("vacancia_fisica")
        vac_fin = kb.get("vacancia_financeira")
        atip_pct = kb.get("contratos_atipicos_pct")
        wault_val = kb.get("wault_anos")

        # --- SEÇÕES DINÂMICAS BASEADAS NO SEGMENTO ---
        if seg_code == "PAPEL":
            kpi_especifico_1_label = "Taxa Média da Carteira"
            kpi_especifico_1_val = kb.get("taxa_media") or "-"
            kpi_especifico_1_sub = f"Spread vs CDI: {macro.get('spread_vs_cdi'):+0.2f} p.p." if macro.get("spread_vs_cdi") is not None else "Spread: -"

            kpi_especifico_2_label = "Duration Média"
            kpi_especifico_2_val = f"{kb.get('duration_anos'):.1f} Anos" if kb.get("duration_anos") is not None else "-"
            kpi_especifico_2_sub = f"LTV Médio: {kb.get('ltv_medio'):.0f}%" if kb.get("ltv_medio") is not None else "LTV: -"

            kpi_especifico_3_label = "Perfil de Crédito"
            kpi_especifico_3_val = kb.get("perfil_credito") or "-"
            kpi_especifico_3_sub = "Garantias da Carteira" if kb.get("perfil_credito") else "-"

            # Gráficos de Papel (Indexadores e Risco)
            idx_data = kb.get("indexadores") or {}
            c_cdi = float(idx_data.get("CDI") or 0.0)
            c_ipca = float(idx_data.get("IPCA") or 0.0)
            if c_cdi + c_ipca > 0:
                donut_1_style = f"background: conic-gradient(#38bdf8 0% {c_cdi}%, #22c55e {c_cdi}% 100%);"
                donut_1_title = "Indexador dos CRIs"
                donut_1_hole = f"{c_cdi:.0f}% CDI"
                donut_1_legends = f"""
                    <li class="legend-item"><span><span class="legend-color" style="background:#38bdf8;"></span>Atrelado ao CDI</span><strong>{c_cdi:.1f}%</strong></li>
                    <li class="legend-item"><span><span class="legend-color" style="background:#22c55e;"></span>Atrelado ao IPCA</span><strong>{c_ipca:.1f}%</strong></li>
                """
            else:
                donut_1_style = "background: #334155;"
                donut_1_title = "Indexador dos CRIs"
                donut_1_hole = "-"
                donut_1_legends = """<li class="legend-item"><span>Indexadores detalhados não reportados (-)</span></li>"""

            donut_2_title = "Subordinação de Cotas"
            donut_2_hole = "-"
            donut_2_style = "background: #334155;"
            donut_2_legends = """<li class="legend-item"><span>Subordinação detalhada não reportada (-)</span></li>"""

            # Tabela de Devedores
            top_devedores = kb.get("top_devedores", [])
            secao_3_title = "3. Auditoria da Carteira de Crédito & Garantias Reais dos CRIs"
            if top_devedores:
                rows_html = "".join([f'''<tr>
                    <td><strong>{d[0]}</strong></td>
                    <td>{d[1]}</td>
                    <td class="text-center kpi-highlight-blue">{d[2]:.1f}%</td>
                    <td class="text-center">{d[3]}</td>
                    <td class="text-center"><span class="badge-tag tag-aa">{d[4]:.0f}%</span></td>
                    <td>{d[5]}</td>
                  </tr>''' for d in top_devedores])
            else:
                rows_html = '''<tr><td colspan="6" class="text-center" style="color:var(--text-muted); padding:32px 16px; font-style:italic;">
                    Detalhamento individual de CRIs e devedores não disponível no informe padronizado CVM (-). Consulte o anexo de carteira do informe mensal ou o relatório gerencial.
                </td></tr>'''

            secao_3_table = f"""
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Devedor / Operação</th>
                    <th>Setor Econômico</th>
                    <th class="text-center">% do PL</th>
                    <th class="text-center">Taxa Ponderada</th>
                    <th class="text-center">LTV</th>
                    <th>Estrutura de Garantia Principal</th>
                  </tr>
                </thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            """

        elif seg_code == "SHOPPING":
            kpi_especifico_1_label = "Vendas Mesmas Lojas (SSS)"
            kpi_especifico_1_val = f"+{kb.get('sss_pct'):.1f}%" if kb.get("sss_pct") is not None else "-"
            kpi_especifico_1_sub = f"Aluguel Mesmas Lojas (SSR): +{kb.get('ssr_pct'):.1f}%" if kb.get("ssr_pct") is not None else "SSR: -"

            kpi_especifico_2_label = "Custo de Ocupação (OCR)"
            kpi_especifico_2_val = f"{kb.get('custo_ocupacao_pct'):.1f}%" if kb.get("custo_ocupacao_pct") is not None else "-"
            kpi_especifico_2_sub = "Margem NOI Caixa" if kb.get("custo_ocupacao_pct") is not None else "-"

            kpi_especifico_3_label = "Vacância dos Shoppings"
            kpi_especifico_3_val = f"{vac_fis:.1f}%" if vac_fis is not None else "-"
            kpi_especifico_3_sub = f"Inadimplência: {kb.get('inadimplencia_lojistas_pct'):.1f}%" if kb.get("inadimplencia_lojistas_pct") is not None else "Inadimplência: -"

            donut_1_style = "background: #334155;"
            donut_1_title = "Distribuição por Ativo"
            donut_1_hole = "-"
            donut_1_legends = """<li class="legend-item"><span>Distribuição por ativo não reportada (-)</span></li>"""

            donut_2_style = "background: #334155;"
            donut_2_title = "Composição Patrimonial"
            donut_2_hole = "-"
            donut_2_legends = """<li class="legend-item"><span>Composição patrimonial não reportada (-)</span></li>"""

            top_shoppings = kb.get("top_shoppings", [])
            secao_3_title = "3. Auditoria Operacional dos Shopping Centers & Métricas de Varejo"
            if top_shoppings:
                rows_html = "".join([f'''<tr>
                    <td><strong>{s[0]}</strong></td>
                    <td>{s[1]}</td>
                    <td class="text-right">{s[2]:,}</td>
                    <td class="text-center kpi-highlight-blue">{s[3]:.1f}%</td>
                    <td class="text-center"><span class="badge-tag tag-aa">{s[4]:.1f}%</span></td>
                    <td>{s[5]}</td>
                  </tr>''' for s in top_shoppings])
            elif real_top_properties:
                rows_html = "".join([f'''<tr>
                    <td><strong>{p.get("name", "-")}</strong></td>
                    <td>{p.get("address", "-")}</td>
                    <td class="text-right">{f"{float(p.get('area_sqm', 0)):,.0f} m²" if p.get('area_sqm') else "-"}</td>
                    <td class="text-center kpi-highlight-blue">{f"{float(p.get('revenue_pct')):.1f}%" if p.get('revenue_pct') is not None else "-"}</td>
                    <td class="text-center"><span class="badge-tag tag-aa">{f"{float(p.get('vacancy_pct')):.1f}%" if p.get('vacancy_pct') is not None else "0.0%"}</span></td>
                    <td>{p.get("asset_class", "-")}</td>
                  </tr>''' for p in real_top_properties])
            else:
                rows_html = '''<tr><td colspan="6" class="text-center" style="color:var(--text-muted); padding:32px 16px; font-style:italic;">
                    Detalhamento individual de shopping centers não disponível via dados abertos estruturados (-). Consulte o relatório gerencial.
                </td></tr>'''

            secao_3_table = f"""
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Shopping Center</th>
                    <th>Localização / Praça</th>
                    <th class="text-right">ABL Total (m²)</th>
                    <th class="text-center">% Receita</th>
                    <th class="text-center">Vacância</th>
                    <th>Perfil de Domínio / Gestão</th>
                  </tr>
                </thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            """

        else:
            # Padrão: LOGÍSTICA / RENDA URBANA / LAJES
            kpi_especifico_1_label = "Vacância Física"
            kpi_especifico_1_val = f"{vac_fis:.1f}%" if vac_fis is not None else "-"
            kpi_especifico_1_sub = f"Vacância Financeira: {vac_fin:.1f}%" if vac_fin is not None else "Vacância Financeira: -"

            kpi_especifico_2_label = "% Contratos Atípicos"
            kpi_especifico_2_val = f"{atip_pct:.1f}%" if atip_pct is not None else "-"
            kpi_especifico_2_sub = f"WAULT Médio: {wault_val:.1f} anos" if wault_val is not None else "WAULT: -"

            kpi_especifico_3_label = "Alavancagem / PL"
            kpi_especifico_3_val = f"{alavancagem_pct:.1f}%"
            kpi_especifico_3_sub = f"Trava: <25% ({divida_format})" if divida_cris > 0 else "Sem dívida de CRIs"

            # Gráficos de Portfólio (usando dados reais de asset_composition se existirem!)
            fii_pct = float(asset_comp.get("fii_holdings_pct") or 0.0)
            re_pct = float(asset_comp.get("real_estate_leased_pct") or 0.0) + float(asset_comp.get("real_estate_under_construction_pct") or 0.0)
            cri_pct = float(asset_comp.get("cri_pct") or 0.0)
            cash_pct = float(asset_comp.get("cash_pct") or 0.0)
            total_comp = fii_pct + re_pct + cri_pct + cash_pct

            if total_comp > 0:
                p1 = round(re_pct, 1)
                p2 = round(p1 + fii_pct, 1)
                p3 = round(p2 + cri_pct, 1)
                donut_1_style = f"background: conic-gradient(#38bdf8 0% {p1}%, #818cf8 {p1}% {p2}%, #f59e0b {p2}% {p3}%, #22c55e {p3}% 100%);"
                donut_1_title = "Composição Patrimonial"
                donut_1_hole = "Ativos"
                donut_1_legends = f"""
                    <li class="legend-item"><span><span class="legend-color" style="background:#38bdf8;"></span>Imóveis Físicos</span><strong>{re_pct:.1f}%</strong></li>
                    <li class="legend-item"><span><span class="legend-color" style="background:#818cf8;"></span>Cotas de FIIs</span><strong>{fii_pct:.1f}%</strong></li>
                    <li class="legend-item"><span><span class="legend-color" style="background:#f59e0b;"></span>CRIs / Crédito</span><strong>{cri_pct:.1f}%</strong></li>
                    <li class="legend-item"><span><span class="legend-color" style="background:#22c55e;"></span>Caixa & Renda Fixa</span><strong>{cash_pct:.1f}%</strong></li>
                """
            else:
                donut_1_style = "background: #334155;"
                donut_1_title = "Composição do Patrimônio"
                donut_1_hole = "-"
                donut_1_legends = """<li class="legend-item"><span>Composição patrimonial não reportada (-)</span></li>"""

            donut_2_style = "background: #334155;"
            donut_2_title = "Tipologia da ABL"
            donut_2_hole = "-"
            donut_2_legends = """<li class="legend-item"><span>Tipologia detalhada de ABL não reportada (-)</span></li>"""

            # Tabela de Ativos / Locatários
            top_inq = kb.get("top_inquilinos", [])
            secao_3_title = "3. Auditoria dos Imóveis, Locatários e Contratos"
            if top_inq:
                rows_html = "".join([f'''<tr>
                    <td><strong>{l[0]}</strong></td>
                    <td>{l[1]}</td>
                    <td class="text-center kpi-highlight-blue">{l[2]:.1f}%</td>
                    <td class="text-center">{l[3]}</td>
                    <td class="text-center"><span class="badge-tag tag-aa">{l[4]}</span></td>
                    <td>{l[5]}</td>
                  </tr>''' for l in top_inq])
                thead_html = """<tr>
                    <th>Locatário Principal</th>
                    <th>Setor Econômico</th>
                    <th class="text-center">% Receita</th>
                    <th class="text-center">Tipo Contrato</th>
                    <th class="text-center">Rating</th>
                    <th>Vencimento Médio</th>
                  </tr>"""
            elif real_top_properties:
                rows_html = "".join([f'''<tr>
                    <td><strong>{p.get("name", "-")}</strong></td>
                    <td>{p.get("address", "-")}</td>
                    <td class="text-right">{f"{float(p.get('area_sqm', 0)):,.0f} m²" if p.get('area_sqm') else "-"}</td>
                    <td class="text-center kpi-highlight-blue">{f"{float(p.get('revenue_pct')):.1f}%" if p.get('revenue_pct') is not None else "-"}</td>
                    <td class="text-center"><span class="badge-tag tag-aa">{f"{float(p.get('vacancy_pct')):.1f}%" if p.get('vacancy_pct') is not None else "0.0%"}</span></td>
                    <td>{p.get("asset_class", "-")}</td>
                  </tr>''' for p in real_top_properties])
                thead_html = """<tr>
                    <th>Imóvel / Ativo</th>
                    <th>Endereço / Praça</th>
                    <th class="text-right">Área (m²)</th>
                    <th class="text-center">% Receita</th>
                    <th class="text-center">Vacância</th>
                    <th>Tipologia / Classe</th>
                  </tr>"""
            else:
                thead_html = """<tr>
                    <th>Ativo / Locatário</th>
                    <th>Setor Econômico</th>
                    <th class="text-center">% Receita</th>
                    <th class="text-center">Tipo Contrato</th>
                    <th class="text-center">Rating</th>
                    <th>Vencimento</th>
                  </tr>"""
                rows_html = '''<tr><td colspan="6" class="text-center" style="color:var(--text-muted); padding:32px 16px; font-style:italic;">
                    Detalhamento individual de contratos e inquilinos não reportado no informe padronizado CVM (-). Consulte o Relatório Gerencial oficial divulgado mensalmente pela administradora.
                </td></tr>'''

            secao_3_table = f"""
            <div class="table-container">
              <table>
                <thead>{thead_html}</thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            """

        # Green Flags & Red Flags dinâmicos baseados em fatos reais apurados
        green_flags = kb.get("green_flags", [])
        if not green_flags:
            green_flags = []
            if pvp is not None and pvp < 1.0:
                green_flags.append(f"Desconto patrimonial: Cota negociando a P/VP de {pvp:.2f} com deságio frente ao VPC contábil.")
            if dy_recorrente > 0:
                green_flags.append(f"Yield recorrente projetado de {dy_recorrente:.2f}% a.a. ({provento_str}).")
            if adtv > 0:
                green_flags.append(f"Liquidez diária ativa na B3: ADTV de {adtv_str}/dia.")
            if alavancagem_pct <= 5.0:
                green_flags.append(f"Baixa alavancagem estrutural ({alavancagem_pct:.1f}% do PL).")
            if vac_fis is not None and vac_fis <= 2.0:
                green_flags.append(f"Vacância física controlada de apenas {vac_fis:.1f}%.")
            if not green_flags:
                green_flags.append("Ativo em fase de acompanhamento fundamentalista (-).")

        red_flags = kb.get("red_flags", [])
        if not red_flags:
            red_flags = []
            if pvp is not None and pvp > 1.05:
                red_flags.append(f"Ágio de mercado: Cota negociando com {((pvp - 1.0)*100):+.1f}% de sobrepreço frente ao VPC oficial.")
            if alavancagem_pct > 20.0:
                red_flags.append(f"Alavancagem financeira elevada ({alavancagem_pct:.1f}% do PL em dívida de CRIs).")
            if ffo_cota is None:
                red_flags.append("FFO gerencial e índice de cobertura não padronizados no informe CVM (exige conferência manual no relatório gerencial).")
            if macro.get("spread_vs_cdi", 0) < 0:
                red_flags.append(f"Spread de risco negativo frente ao CDI ({macro.get('spread_vs_cdi'):+0.2f} p.p.): tese depende de valorização da cota.")
            if not red_flags:
                red_flags.append("Monitoramento contínuo das divulgações e relatórios oficiais (-).")

        # HTML COMPLETO
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ticker} - Auditoria Especializada ({seg_name})</title>
  <style>
    :root {{
      --bg-main: #0f172a;
      --bg-card: #1e293b;
      --border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-dim: rgba(56, 189, 248, 0.15);
      --success: #22c55e;
      --success-dim: rgba(34, 197, 94, 0.15);
      --warning: #f59e0b;
      --warning-dim: rgba(245, 158, 11, 0.15);
      --danger: #ef4444;
      --danger-dim: rgba(239, 68, 68, 0.15);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg-main); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.5; padding: 24px; }}
    .container {{ max-width: 1240px; margin: 0 auto; }}

    /* HEADER */
    .header-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px 28px; margin-bottom: 20px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 20px; }}
    .header-left {{ flex: 1 1 500px; }}
    .ticker-badge {{ display: inline-block; background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; font-size: 1.5rem; font-weight: 800; padding: 4px 14px; border-radius: 8px; margin-right: 12px; }}
    .segment-badge {{ display: inline-block; background: rgba(56, 189, 248, 0.15); color: var(--primary); border: 1px solid var(--primary); font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; margin-right: 8px; vertical-align: middle; }}
    .fund-name {{ display: inline-block; font-size: 1.2rem; font-weight: 700; color: var(--text-main); vertical-align: middle; }}
    .header-meta {{ display: flex; flex-wrap: wrap; gap: 16px; margin-top: 12px; font-size: 0.85rem; color: var(--text-muted); }}
    .header-meta span strong {{ color: var(--text-main); }}
    .audit-stamp {{ display: inline-flex; align-items: center; gap: 6px; background-color: var(--success-dim); border: 1px solid var(--success); color: var(--success); font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; }}

    .score-card {{ background: #0b1329; border: 1px solid var(--border); padding: 14px 22px; border-radius: 10px; text-align: center; min-width: 140px; }}
    .score-label {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }}
    .score-value {{ font-size: 2.1rem; font-weight: 800; color: var(--primary); line-height: 1.1; margin: 4px 0; }}
    .verdict-badge {{ display: inline-block; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 4px; background: {"var(--success-dim)" if veredicto_tipo == "success" else "var(--warning-dim)"}; color: {"var(--success)" if veredicto_tipo == "success" else "var(--warning)"}; border: 1px solid {"var(--success)" if veredicto_tipo == "success" else "var(--warning)"}; text-transform: uppercase; }}

    /* KPI GRID */
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 14px; margin-bottom: 24px; }}
    .kpi-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }}
    .kpi-title {{ font-size: 0.75rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }}
    .kpi-value {{ font-size: 1.35rem; font-weight: 800; color: var(--text-main); letter-spacing: -0.5px; }}
    .kpi-sub {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; }}
    .kpi-highlight-green {{ color: var(--success); }}
    .kpi-highlight-blue {{ color: var(--primary); }}
    .kpi-highlight-amber {{ color: var(--warning); }}
    .kpi-highlight-red {{ color: var(--danger); }}

    /* SECTIONS */
    .section-title {{ font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; border-left: 4px solid var(--primary); padding-left: 10px; }}
    .card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 24px; }}
    .metrics-subgrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 18px; }}
    .metric-box {{ background: #0f172a; border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; }}
    .metric-box-title {{ font-size: 0.75rem; color: var(--text-muted); font-weight: 600; }}
    .metric-box-val {{ font-size: 1.2rem; font-weight: 700; margin-top: 4px; }}

    /* TABLES */
    .table-container {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }}
    th {{ background: #0b1329; color: var(--text-muted); padding: 10px 14px; font-weight: 600; text-transform: uppercase; font-size: 0.72rem; border-bottom: 1px solid var(--border); }}
    td {{ padding: 10px 14px; border-bottom: 1px solid #1e293b; color: var(--text-main); }}
    tr:last-child td {{ border-bottom: none; }}
    .text-right {{ text-align: right; }}
    .text-center {{ text-align: center; }}

    .diagnostic-box {{ background: {"var(--danger-dim)" if (cobertura_ffo is not None and cobertura_ffo < 1.0) else ("var(--primary-dim)" if cobertura_ffo is None else "var(--success-dim)")}; border: 1px solid {"var(--danger)" if (cobertura_ffo is not None and cobertura_ffo < 1.0) else ("var(--border)" if cobertura_ffo is None else "var(--success)")}; border-radius: 8px; padding: 14px 18px; font-size: 0.85rem; line-height: 1.5; }}
    .diagnostic-box strong {{ color: {"var(--danger)" if (cobertura_ffo is not None and cobertura_ffo < 1.0) else ("var(--primary)" if cobertura_ffo is None else "var(--success)")}; }}

    /* CHARTS SECTION */
    .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
    .chart-panel {{ background: #0f172a; border: 1px solid var(--border); border-radius: 8px; padding: 18px; display: flex; flex-direction: column; align-items: center; }}
    .chart-header {{ font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 14px; text-align: center; text-transform: uppercase; }}
    .donut-container {{ position: relative; width: 170px; height: 170px; margin: 10px 0 16px 0; }}
    .donut-chart-1 {{ width: 170px; height: 170px; border-radius: 50%; {donut_1_style} display: flex; align-items: center; justify-content: center; }}
    .donut-chart-2 {{ width: 170px; height: 170px; border-radius: 50%; {donut_2_style} display: flex; align-items: center; justify-content: center; }}
    .donut-hole {{ width: 105px; height: 105px; border-radius: 50%; background-color: var(--bg-card); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); }}
    .donut-hole-title {{ font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; }}
    .donut-hole-val {{ font-size: 0.95rem; font-weight: 800; color: var(--text-main); }}
    .legend-list {{ width: 100%; list-style: none; font-size: 0.75rem; color: var(--text-muted); }}
    .legend-item {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
    .legend-color {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; }}

    .badge-tag {{ display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }}
    .tag-aa {{ background: var(--primary-dim); color: var(--primary); border: 1px solid var(--primary); }}

    /* MATRIX FLAGS */
    .matrix-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    @media (max-width: 768px) {{ .matrix-grid {{ grid-template-columns: 1fr; }} }}
    .flag-card {{ border-radius: 8px; padding: 16px 18px; }}
    .flag-card-green {{ background: var(--success-dim); border: 1px solid rgba(34, 197, 94, 0.4); }}
    .flag-card-red {{ background: var(--danger-dim); border: 1px solid rgba(239, 68, 68, 0.4); }}
    .flag-header {{ font-size: 0.9rem; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
    .flag-header-green {{ color: var(--success); }}
    .flag-header-red {{ color: var(--danger); }}
    .flag-list {{ list-style-type: none; font-size: 0.82rem; line-height: 1.5; }}
    .flag-list li {{ margin-bottom: 8px; padding-left: 14px; position: relative; }}
    .flag-card-green li::before {{ content: "✓"; position: absolute; left: 0; color: var(--success); font-weight: 700; }}
    .flag-card-red li::before {{ content: "✕"; position: absolute; left: 0; color: var(--danger); font-weight: 700; }}

    /* VERDICT */
    .verdict-box {{ background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid var(--border); border-radius: 10px; padding: 22px; }}
    .verdict-summary-row {{ display: flex; flex-wrap: wrap; gap: 20px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 16px; }}
    .verdict-title {{ font-size: 1.1rem; font-weight: 700; }}
    .teto-val {{ font-size: 1.35rem; font-weight: 800; color: var(--primary); }}
    .verdict-text {{ font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; }}
    .verdict-text strong {{ color: var(--text-main); }}

    .footer-stamp {{ margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--text-muted); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }}
    .footer-stamp a {{ color: var(--primary); text-decoration: none; }}
    .footer-stamp a:hover {{ text-decoration: underline; }}

    @media print {{
      body {{ background: #fff !important; color: #0f172a !important; padding: 0; font-size: 9.5pt; }}
      .container {{ max-width: 100%; }}
      .header-card, .card, .kpi-card, .metric-box, .chart-panel, .score-card, .verdict-box {{ background: #fff !important; border: 1px solid #cbd5e1 !important; color: #0f172a !important; box-shadow: none !important; }}
      .header-meta, .kpi-sub, .metric-box-title, .score-label, .chart-header, .legend-list, .verdict-text, .footer-stamp {{ color: #475569 !important; }}
      .donut-hole {{ background: #fff !important; color: #0f172a !important; }}
      .donut-hole-val, .kpi-value, .metric-box-val, .fund-name, .section-title, .verdict-title {{ color: #0f172a !important; }}
      .flag-card-green {{ background: #f0fdf4 !important; border: 1px solid #86efac !important; }}
      .flag-card-red {{ background: #fef2f2 !important; border: 1px solid #fca5a5 !important; }}
      table th {{ background: #f1f5f9 !important; color: #334155 !important; }}
      table td {{ border-bottom: 1px solid #e2e8f0 !important; color: #0f172a !important; }}
    }}
  </style>
</head>
<body>

<div class="container">

  <!-- HEADER EXECUTIVO -->
  <header class="header-card">
    <div class="header-left">
      <div>
        <span class="ticker-badge">{ticker}</span>
        <span class="segment-badge">{seg_name}</span>
        <span class="fund-name">{fnet.get('razao_social')}</span>
      </div>
      <div class="header-meta">
        <span><strong>Gestão:</strong> {fnet.get('gestor')}</span>
        <span><strong>Administrador:</strong> {fnet.get('administrador')}</span>
        <span><strong>Data-Base CVM:</strong> {fnet.get('data_referencia')}</span>
        <span><strong>Protocolo B3/Fundos.NET:</strong> {fnet.get('data_protocolo_fnet')}</span>
        <span class="audit-stamp">Validação Cruzada CVM + BolsaAI</span>
      </div>
    </div>
    <div class="header-right">
      <div class="score-card">
        <div class="score-label">Score Técnico</div>
        <div class="score-value">{score_html}</div>
        <div class="verdict-badge verdict-{veredicto_tipo}">{veredicto_str}</div>
      </div>
    </div>
  </header>

  <!-- PAINEL SUPERIOR: 8 CARDS DE KPIS -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-title">P/VP</div>
      <div class="kpi-value {'kpi-highlight-green' if (pvp is not None and pvp <= 1.0) else ('kpi-highlight-amber' if pvp is not None else '')}">{pvp_str}</div>
      <div class="kpi-sub">Mercado: {preco_str} | VPC: {vpc_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Dividend Yield Recorrente</div>
      <div class="kpi-value kpi-highlight-blue">{dy_rec_str}</div>
      <div class="kpi-sub">{provento_str} | Histórico 12M: {dy_ttm_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">{kpi_especifico_1_label}</div>
      <div class="kpi-value kpi-highlight-green">{kpi_especifico_1_val}</div>
      <div class="kpi-sub">{kpi_especifico_1_sub}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">{kpi_especifico_2_label}</div>
      <div class="kpi-value kpi-highlight-blue">{kpi_especifico_2_val}</div>
      <div class="kpi-sub">{kpi_especifico_2_sub}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">{kpi_especifico_3_label}</div>
      <div class="kpi-value">{kpi_especifico_3_val}</div>
      <div class="kpi-sub">{kpi_especifico_3_sub}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Cotistas</div>
      <div class="kpi-value">{cotistas_str}</div>
      <div class="kpi-sub">Base oficial CVM</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">ADTV (Mês)</div>
      <div class="kpi-value">{adtv_str}</div>
      <div class="kpi-sub">Liquidez secundária B3</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Patrimônio Líquido</div>
      <div class="kpi-value">{pl_format}</div>
      <div class="kpi-sub">VPC: {vpc_str}</div>
    </div>
  </div>

  <!-- SEÇÃO 1: DRE AUDITADA E SUSTENTABILIDADE -->
  <section class="card">
    <h2 class="section-title">1. Demonstração de Resultados (DRE Auditada) & Sustentabilidade de Proventos</h2>

    <div class="metrics-subgrid">
      <div class="metric-box">
        <div class="metric-box-title">Patrimônio Contábil Auditado</div>
        <div class="metric-box-val kpi-highlight-blue">{pl_format}</div>
        <div class="kpi-sub">VPC Oficial: {vpc_str}</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Obrigações / Securitizações (CRIs)</div>
        <div class="metric-box-val {'kpi-highlight-green' if alavancagem_pct <= 25 else 'kpi-highlight-red'}">{divida_format}</div>
        <div class="kpi-sub">Alavancagem: {alavancagem_pct:.2f}% do PL</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">FFO Operacional Estimado / Cota</div>
        <div class="metric-box-val">{ffo_cota_str}</div>
        <div class="kpi-sub">{'Geração de caixa recorrente' if ffo_cota is not None else 'Não reportado na CVM'}</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Índice de Cobertura do FFO</div>
        <div class="metric-box-val">{cobertura_str}</div>
        <div class="kpi-sub">{'Superávit operacional retido' if (cobertura_ffo and cobertura_ffo >= 1.0) else ('Consumo de reserva' if cobertura_ffo else 'Exige relatório gerencial')}</div>
      </div>
    </div>

    <div class="diagnostic-box">
      <strong>Diagnóstico Auditorial de Cobertura:</strong> O fundo apresenta dividendo recorrente de <strong>{provento_str}</strong>.
      {" O FFO operacional estimado é de <strong>" + ffo_cota_str + "/cota</strong> com Índice de Cobertura de <strong>" + cobertura_str + "</strong>. " + ("Os proventos são integralmente sustentados pela geração de caixa operacional recorrente." if (cobertura_ffo and cobertura_ffo >= 1.0) else "O provento atual exige monitoramento do consumo de reservas.") if ffo_cota is not None else " O FFO operacional gerencial e o índice de cobertura oficial são publicados exclusivamente no relatório gerencial da administradora/gestora, não constando na DRE padronizada do informe mensal CVM."}
      <br><strong>Spread Macro:</strong> {macro.get('spread_status')} (Yield Recorrente {dy_rec_str} vs CDI {macro.get('cdi'):.2f}% = {macro.get('spread_vs_cdi'):+0.2f} p.p. | TTM Passado: {dy_ttm_str}).
      {f'<br><span style="color:#b45309; font-weight:600;">⚠️ Auditoria de Proventos: O Yield histórico TTM ({dy_ttm_str}) inclui eventos extraordinários/amortizações (~R$ {extraordinarios:,.2f}/cota). O Yield Recorrente projetado baseado no fluxo atual é de {dy_rec_str}.</span>' if (abs(dy_ttm - dy_recorrente) >= 0.75 or extraordinarios > 0.05) else ''}
    </div>
  </section>

  <!-- SEÇÃO 2: PORTFÓLIO E GRÁFICOS ESPECIALIZADOS -->
  <section class="card">
    <h2 class="section-title">2. Alocação de Ativos e Estrutura Especializada ({seg_name})</h2>
    
    <div class="charts-grid">
      <div class="chart-panel">
        <div class="chart-header">{donut_1_title}</div>
        <div class="donut-container">
          <div class="donut-chart-1">
            <div class="donut-hole">
              <span class="donut-hole-title">{donut_1_title}</span>
              <span class="donut-hole-val">{donut_1_hole}</span>
            </div>
          </div>
        </div>
        <ul class="legend-list">{donut_1_legends}</ul>
      </div>

      <div class="chart-panel">
        <div class="chart-header">{donut_2_title}</div>
        <div class="donut-container">
          <div class="donut-chart-2">
            <div class="donut-hole">
              <span class="donut-hole-title">{donut_2_title}</span>
              <span class="donut-hole-val">{donut_2_hole}</span>
            </div>
          </div>
        </div>
        <ul class="legend-list">{donut_2_legends}</ul>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 3: AUDITORIA OPERACIONAL / CRÉDITO ESPECÍFICA -->
  <section class="card">
    <h2 class="section-title">{secao_3_title}</h2>
    {secao_3_table}
  </section>

  <!-- SEÇÃO 4: MATRIZ CRÍTICA DE RISCOS -->
  <section class="card">
    <h2 class="section-title">4. Matriz Crítica de Riscos e Oportunidades ({seg_name})</h2>
    <div class="matrix-grid">
      <div class="flag-card flag-card-green">
        <div class="flag-header flag-header-green"><span>●</span> GREEN FLAGS (Pontos Fortes)</div>
        <ul class="flag-list">
          {"".join([f'<li>{f}</li>' for f in green_flags])}
        </ul>
      </div>
      <div class="flag-card flag-card-red">
        <div class="flag-header flag-header-red"><span>●</span> RED FLAGS (Pontos de Atenção)</div>
        <ul class="flag-list">
          {"".join([f'<li>{f}</li>' for f in red_flags])}
        </ul>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 5: VEREDITO E PARECER DE ALOCAÇÃO -->
  <section class="verdict-box">
    <div class="verdict-summary-row">
      <div>
        <div class="verdict-title">5. Parecer Executivo de Auditoria & Recomendação Fundamentalista</div>
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Auditoria Especializada para {seg_name} (Validação Cruzada CVM + BolsaAI)</div>
      </div>
      <div>
        <span class="verdict-badge verdict-{veredicto_tipo}" style="font-size: 0.9rem; padding: 6px 14px;">{veredicto_str}</span>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Preço-Teto de Segurança</div>
        <div class="teto-val">{teto_str}</div>
      </div>
    </div>

    <div class="verdict-text">
      <p style="margin-bottom: 10px;">
        <strong>Conclusão da Auditoria:</strong> O fundo <strong>{ticker} ({fnet.get('razao_social') or '-'})</strong>, classificado no segmento de <strong>{seg_name}</strong>, possui patrimônio líquido auditado de <strong>{pl_format}</strong> e base oficial de <strong>{cotistas_str} cotistas</strong>. A análise cruzada entre os informes contábeis do Fundos.NET e os dados de mercado da BolsaAI consolida a rastreabilidade patrimonial e fiduciária.
      </p>
      <p style="margin-bottom: 10px;">
        <strong>Diretriz Prudencial de Alocação:</strong> Alocação sugerida: <strong>{alocacao_str}</strong>. Com a cota de mercado cotada a <strong>{preco_str}</strong> {f"frente ao Preço-Teto Fundamentalista de <strong>{teto_str}</strong>" if teto is not None else "(Preço-Teto não calibrado -)"}, o ativo apresenta Spread de Risco de <strong>{macro.get('spread_vs_cdi'):+0.2f} p.p.</strong> sobre a taxa CDI de {macro.get('cdi'):.2f}%.
      </p>
    </div>

    <div class="footer-stamp">
      <span><strong>Fontes Oficiais:</strong> <a href="https://fnet.bmfbovespa.com.br/fnet/publico/abrirGerenciadorDocumentosCVM" target="_blank" rel="noopener">Protocolo B3 / Fundos.NET</a> &amp; <a href="https://usebolsai.com/mcp" target="_blank" rel="noopener">BolsaAI API / MCP</a></span>
      <span>Impressão: Ctrl + P (Otimizado via @media print)</span>
    </div>
  </section>

</div>

</body>
</html>"""

        # Salva o arquivo HTML em disco
        report_file = REPORTS_DIR / f"{ticker}_auditoria.html"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html)

        return {
            "ticker": ticker,
            "segment_code": seg_code,
            "segment_name": seg_name,
            "html_path": str(report_file),
            "html_content": html,
            "score": score,
            "veredicto": veredicto,
            "teto": teto,
            "alocacao_sugerida": alocacao_sug,
            "pvp": pvp,
            "dy_anual": dy_recorrente,
            "dy_recorrente": dy_recorrente,
            "dy_ttm": dy_ttm,
            "extraordinarios_cota": extraordinarios,
            "cotistas": cotistas,
            "pl": pl,
            "alavancagem_pct": alavancagem_pct,
            "spread_vs_cdi": macro.get("spread_vs_cdi")
        }
