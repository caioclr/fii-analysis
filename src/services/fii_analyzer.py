from typing import List, Dict, Any, Optional
import pandas as pd
from src.services.market_data import MarketDataService

# Mapeamento auxiliar de segmentos para os principais FIIs do mercado
FII_DEFAULT_SEGMENTS = {
    "HGLG11": "Logística / Galpões",
    "BTLG11": "Logística / Galpões",
    "XPLG11": "Logística / Galpões",
    "BRCO11": "Logística / Galpões",
    "VILG11": "Logística / Galpões",
    "LVBI11": "Logística / Galpões",
    "GALG11": "Logística / Galpões",
    "XPML11": "Shoppings",
    "VISC11": "Shoppings",
    "HGBS11": "Shoppings",
    "HSML11": "Shoppings",
    "MALL11": "Shoppings",
    "KNCR11": "Papel / CRI",
    "KNIP11": "Papel / CRI",
    "KNSC11": "Papel / CRI",
    "MXRF11": "Papel / Híbrido",
    "CPTS11": "Papel / CRI",
    "VGIR11": "Papel / CRI",
    "RBRR11": "Papel / CRI",
    "HGCR11": "Papel / CRI",
    "IRDM11": "Papel / CRI",
    "HGRE11": "Lajes Corporativas",
    "PVBI11": "Lajes Corporativas",
    "BRCR11": "Lajes Corporativas",
    "KNRI11": "Híbrido",
    "JSRE11": "Híbrido",
    "TGAR11": "Desenvolvimento",
    "BCFF11": "Fundos de Fundos (FOF)",
    "HFOF11": "Fundos de Fundos (FOF)",
    "RBRF11": "Fundos de Fundos (FOF)",
    "RZTR11": "Agro (Fiagro)",
    "VGIA11": "Agro (Fiagro)",
    "KNCA11": "Agro (Fiagro)",
    "HGRU11": "Renda Urbana / Varejo",
    "TRXF11": "Renda Urbana / Varejo"
}

class FIIAnalyzer:
    @classmethod
    def analyze_positions(cls, positions: List[Dict[str, Any]], force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analisa a lista de posições de FIIs da carteira, buscando cotações, P/VP, DY,
        calculando rentabilidade, dividendos estimados e número mágico.
        """
        if not positions:
            return {
                "items": [],
                "total_invested": 0.0,
                "total_current_value": 0.0,
                "total_profit_loss": 0.0,
                "total_profit_loss_pct": 0.0,
                "weighted_dy": 0.0,
                "weighted_pvp": 0.0,
                "monthly_income_est": 0.0,
                "annual_income_est": 0.0,
                "segment_distribution": {},
                "summary": "Nenhum FII cadastrado na carteira."
            }

        analyzed_items = []
        total_invested = 0.0
        total_current_value = 0.0
        total_monthly_income = 0.0

        for pos in positions:
            ticker = pos["ticker"].upper().strip()
            qty = float(pos.get("quantity", 0))
            avg_price = float(pos.get("average_price", 0))
            invested = qty * avg_price

            # Segmento
            segment = pos.get("segment")
            if not segment or segment == "Outros":
                segment = FII_DEFAULT_SEGMENTS.get(ticker, "Outros")

            # Busca dados de mercado
            market = MarketDataService.get_market_data(ticker, force_refresh=force_refresh)
            current_price = market.get("current_price") or avg_price
            pvp = market.get("pvp")
            dy_12m = market.get("dy_12m") or 0.0
            last_div = market.get("last_dividend") or 0.0

            # Se não tiver last_dividend mas tiver DY, estima dividendo mensal
            if last_div <= 0 and dy_12m > 0 and current_price > 0:
                last_div = round((current_price * (dy_12m / 100.0)) / 12.0, 2)

            current_value = qty * current_price
            profit_loss = current_value - invested
            profit_loss_pct = ((current_value / invested) - 1.0) * 100.0 if invested > 0 else 0.0

            # Estimativa de renda mensal deste fundo
            monthly_income = qty * last_div

            # Cálculo do Número Mágico (Magic Number): cotas para reinvestimento autônomo
            magic_number = None
            magic_progress = 0.0
            if last_div > 0 and current_price > 0:
                magic_number = int(current_price // last_div) + 1
                magic_progress = round(min(100.0, (qty / magic_number) * 100.0), 1)

            # Classificação P/VP
            pvp_status = "N/D"
            if pvp is not None:
                if pvp < 0.95:
                    pvp_status = "Desconto (P/VP < 0.95)"
                elif pvp <= 1.05:
                    pvp_status = "Preço Justo (0.95 - 1.05)"
                else:
                    pvp_status = "Ágio (P/VP > 1.05)"

            total_invested += invested
            total_current_value += current_value
            total_monthly_income += monthly_income

            analyzed_items.append({
                "ticker": ticker,
                "segment": segment,
                "quantity": qty,
                "average_price": avg_price,
                "invested_value": round(invested, 2),
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_loss_pct": round(profit_loss_pct, 2),
                "pvp": pvp,
                "pvp_status": pvp_status,
                "dy_12m": round(dy_12m, 2),
                "last_dividend": round(last_div, 2),
                "monthly_income_est": round(monthly_income, 2),
                "magic_number": magic_number,
                "magic_progress": magic_progress,
                "target_percent": pos.get("target_percent", 0.0)
            })

        # Calcula pesos e médias ponderadas
        weighted_dy = 0.0
        weighted_pvp = 0.0
        segment_distribution = {}

        for item in analyzed_items:
            weight = (item["current_value"] / total_current_value) if total_current_value > 0 else 0.0
            item["portfolio_weight_pct"] = round(weight * 100.0, 2)
            
            if item["dy_12m"]:
                weighted_dy += item["dy_12m"] * weight
            if item["pvp"]:
                weighted_pvp += item["pvp"] * weight

            seg = item["segment"]
            segment_distribution[seg] = round(segment_distribution.get(seg, 0.0) + item["current_value"], 2)

        total_profit_loss = total_current_value - total_invested
        total_profit_loss_pct = ((total_current_value / total_invested) - 1.0) * 100.0 if total_invested > 0 else 0.0

        return {
            "items": analyzed_items,
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_value, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_profit_loss_pct": round(total_profit_loss_pct, 2),
            "weighted_dy": round(weighted_dy, 2),
            "weighted_pvp": round(weighted_pvp, 2),
            "monthly_income_est": round(total_monthly_income, 2),
            "annual_income_est": round(total_monthly_income * 12.0, 2),
            "segment_distribution": segment_distribution
        }
