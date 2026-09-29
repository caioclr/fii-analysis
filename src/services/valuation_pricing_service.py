import logging
from typing import Dict, Any, Optional
from src.database.repository import PricingParametersRepository

logger = logging.getLogger(__name__)

class ValuationPricingService:
    """
    Serviço especializado em metodologias institucionais de Preço-Teto para FIIs
    (Spread sobre NTN-B, Gordon DCF e Patrimonial Prudencial) e cálculo do Retorno Real (IPCA + X% a.a.).
    Metodologia de Bazin expressamente desconsiderada.
    """

    @classmethod
    def calculate_real_yield(cls, ticker: str, dy_anual: float, segment_code: str, 
                             cri_coupon_ipca: Optional[float] = None) -> Dict[str, Any]:
        """
        Calcula a remuneração real do FII em relação à inflação (IPCA + X% a.a.) e o spread sobre a NTN-B.
        
        Para FIIs de Tijolo (SHOPPING, LOGISTICA, LAJES, HIBRIDO):
          - Como os contratos de locação repassam a inflação anualmente via IPCA/IGP-M, o próprio
            Dividend Yield de mercado já representa uma taxa real líquida de inflação.
        
        Para FIIs de Papel (PAPEL, AGRO):
          - Se a carteira for indexada ao IPCA+, o cupom médio contratado é o retorno real direto.
          - Se a carteira for indexada ao CDI+, o retorno real é deduzido pela inflação projetada (Equação de Fisher).
        """
        params = PricingParametersRepository.get_parameters()
        ntnb_rate = params.get("ntnb_reference_rate", 6.50)
        proj_ipca = params.get("projected_ipca", 4.00)

        # 1. Determina a taxa real
        is_tijolo = segment_code in ["SHOPPING", "LOGISTICA", "LAJES", "HIBRIDO"]
        
        if is_tijolo:
            # Em tijolo, o aluguel repõe a inflação, logo o DY é taxa real pura
            real_yield = float(dy_anual)
            metodologia_real = "Yield Real Direto (Contratos de Tijolo repõem IPCA/IGP-M)"
        else:
            if cri_coupon_ipca and cri_coupon_ipca > 0:
                real_yield = float(cri_coupon_ipca)
                metodologia_real = "Cupom Médio Contratado da Carteira IPCA+"
            else:
                # Fisher: (1 + dy) / (1 + ipca) - 1
                dy_dec = dy_anual / 100.0
                ipca_dec = proj_ipca / 100.0
                fisher_real = ((1.0 + dy_dec) / (1.0 + ipca_dec) - 1.0) * 100.0
                real_yield = round(fisher_real, 2)
                metodologia_real = f"Equação de Fisher (DY {dy_anual:.1f}% deflacionado do IPCA {proj_ipca:.1f}%)"

        # 2. Spread sobre o Tesouro IPCA+ longo (NTN-B)
        spread_ntnb = real_yield - ntnb_rate

        # 3. Equivalência em Renda Fixa Tributada (% do CDI aproximado)
        # Assumindo CDI ~ 10,75% e alíquota de 15% de IR
        cdi_base = 10.75
        cdi_gross_equiv = (dy_anual / (1.0 - 0.15)) / cdi_base * 100.0

        return {
            "ticker": ticker.upper(),
            "real_yield_pct": round(real_yield, 2),
            "label_real": f"IPCA + {real_yield:.2f}% a.a.",
            "ntnb_reference_rate": ntnb_rate,
            "spread_vs_ntnb": round(spread_ntnb, 2),
            "spread_vs_ntnb_label": f"{'+' if spread_ntnb >= 0 else ''}{spread_ntnb:.2f}% a.a. vs NTN-B",
            "cdi_gross_equivalent_pct": round(cdi_gross_equiv, 1),
            "cdi_gross_label": f"{cdi_gross_equiv:.0f}% do CDI",
            "metodologia_real": metodologia_real,
            "is_isento_ir": True
        }

    @classmethod
    def calculate_ceiling_spread_ntnb(cls, ffo_anual_cota: float, 
                                      ntnb_rate: Optional[float] = None, 
                                      risk_spread: Optional[float] = None) -> float:
        """
        Calcula o Preço-Teto pelo Spread sobre o Tesouro IPCA+ (Custo de Oportunidade Soberano).
        Teto = FFO Recorrente Anual / (Taxa NTN-B + Prêmio de Risco)
        """
        params = PricingParametersRepository.get_parameters()
        ntnb = (ntnb_rate if ntnb_rate is not None else params.get("ntnb_reference_rate", 6.50)) / 100.0
        spread = (risk_spread if risk_spread is not None else params.get("real_risk_spread", 2.00)) / 100.0
        
        discount_rate = ntnb + spread
        if discount_rate <= 0 or ffo_anual_cota <= 0:
            return 0.0
        return round(ffo_anual_cota / discount_rate, 2)

    @classmethod
    def calculate_ceiling_gordon(cls, dividendo_anual_d1: float, 
                                 ke: float = 0.115, 
                                 g_inflation: Optional[float] = None) -> float:
        """
        Calcula o Preço-Teto pelo Modelo de Gordon / DCF Imobiliário com Repasse de Inflação.
        Teto = D1 / (Ke - g)
        Onde:
          - D1: Dividendo projetado do próximo ano
          - Ke: Custo de oportunidade de capital total exigido (ex: 11,5% a.a.)
          - g: Crescimento perpétuo dos aluguéis pela inflação (ex: IPCA 4,0% a.a.)
        """
        params = PricingParametersRepository.get_parameters()
        g = (g_inflation if g_inflation is not None else params.get("projected_ipca", 4.00)) / 100.0
        
        denom = ke - g
        if denom <= 0.01 or dividendo_anual_d1 <= 0:
            return 0.0
        return round(dividendo_anual_d1 / denom, 2)

    @classmethod
    def calculate_ceiling_patrimonial(cls, vpc: float, segment_code: str) -> float:
        """
        Calcula o Preço-Teto pelo critério Patrimonial Prudencial (P/VP Limite):
          - PAPEL (CRIs): VPC * 1,02 (teto máximo de 2% de ágio sobre dívida)
          - FOF: VPC * 0,95 (desconto mínimo de 5% por sobreposição de taxas)
          - TIJOLO / HIBRIDO / AGRO: VPC * 1,00
        """
        if vpc <= 0:
            return 0.0
        if segment_code == "PAPEL":
            return round(vpc * 1.02, 2)
        elif segment_code == "FOF":
            return round(vpc * 0.95, 2)
        else:
            return round(vpc * 1.00, 2)

    @classmethod
    def calculate_consolidated_pricing(cls, ticker: str, metrics: Dict[str, Any], 
                                      segment_code: str) -> Dict[str, Any]:
        """
        Gera o parecer consolidado de precificação com as 3 metodologias e margem de segurança.
        """
        preco_mercado = float(metrics.get("preco_mercado") or 100.0)
        vpc = float(metrics.get("vpc") or 100.0)
        provento_mes = float(metrics.get("provento_mes") or 0.80)
        ffo_cota_mes = float(metrics.get("ffo_cota") or provento_mes)
        dy_anual = float(metrics.get("dy_anual") or (provento_mes * 12 / preco_mercado * 100.0 if preco_mercado > 0 else 10.0))

        ffo_anual = ffo_cota_mes * 12.0
        dividendo_anual = provento_mes * 12.0

        # 1. Metodologias Individuais
        teto_spread_ntnb = cls.calculate_ceiling_spread_ntnb(ffo_anual)
        teto_gordon = cls.calculate_ceiling_gordon(dividendo_anual)
        teto_patrimonial = cls.calculate_ceiling_patrimonial(vpc, segment_code)

        # 2. Seleção do Preço-Teto Recomendado por Segmento
        if segment_code == "PAPEL":
            # Para Papel, o teto patrimonial (VPC * 1,02) é a âncora principal
            teto_recomendado = min(teto_spread_ntnb, teto_patrimonial) if teto_spread_ntnb > 0 else teto_patrimonial
            metodologia_recomendada = "Spread NTN-B com Trava Patrimonial (VPC +2%)"
        elif segment_code == "FOF":
            # Para FOFs, o teto é travado em 95% do VPC
            teto_recomendado = teto_patrimonial
            metodologia_recomendada = "Patrimonial Prudencial (VPC com 5% de Desconto)"
        else:
            # Para Tijolo e Híbridos, o Spread sobre NTN-B é o padrão institucional
            teto_recomendado = teto_spread_ntnb if teto_spread_ntnb > 0 else teto_patrimonial
            metodologia_recomendada = "Spread Real sobre NTN-B 2035 (FFO / 8,5% a.a.)"

        # 3. Margem de Segurança Fundamentalista
        if preco_mercado > 0 and teto_recomendado > 0:
            margem_seguranca_pct = round(((teto_recomendado / preco_mercado) - 1.0) * 100.0, 2)
        else:
            margem_seguranca_pct = 0.0

        # 4. Retorno Real (IPCA + X%)
        real_yield_info = cls.calculate_real_yield(ticker, dy_anual, segment_code)

        return {
            "ticker": ticker.upper(),
            "preco_mercado": preco_mercado,
            "vpc": vpc,
            "preco_teto_recomendado": teto_recomendado,
            "metodologia_recomendada": metodologia_recomendada,
            "margem_seguranca_pct": margem_seguranca_pct,
            "tem_margem_seguranca": margem_seguranca_pct > 0,
            "teto_spread_ntnb": teto_spread_ntnb,
            "teto_gordon": teto_gordon,
            "teto_patrimonial": teto_patrimonial,
            "tetos_detalhados": {
                "spread_ntnb": {
                    "valor": teto_spread_ntnb,
                    "descricao": "Spread Real NTN-B 2035 + 2,0% a.a. (Taxa de Desconto 8,5% a.a.)"
                },
                "gordon_dcf": {
                    "valor": teto_gordon,
                    "descricao": "Gordon DCF Imobiliário (Ke 11,5% a.a. - Inflação g 4,0% a.a.)"
                },
                "patrimonial": {
                    "valor": teto_patrimonial,
                    "descricao": f"Patrimonial Regulatório ({segment_code})"
                }
            },
            "real_yield": real_yield_info
        }
