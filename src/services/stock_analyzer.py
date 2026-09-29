from typing import List, Dict, Any, Optional
import pandas as pd
from src.services.market_data import MarketDataService
from src.services.bolsai_service import BolsaiService

class StockAnalyzer:
    @classmethod
    def analyze_positions(cls, positions: List[Dict[str, Any]], force_refresh: bool = False, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Analisa posições de Ações na carteira, calculando rentabilidade,
        indicadores de valuation (P/L, P/VP, ROE, ROIC, Margem Líquida) via BolsaAI e distribuição setorial.
        """
        if not positions:
            return {
                "items": [],
                "total_invested": 0.0,
                "total_current_value": 0.0,
                "total_profit_loss": 0.0,
                "total_profit_loss_pct": 0.0,
                "weighted_dy": 0.0,
                "weighted_roe": 0.0,
                "weighted_pl": 0.0,
                "sector_distribution": {},
                "summary": "Nenhuma ação cadastrada na carteira."
            }

        analyzed_items = []
        total_invested = 0.0
        total_current_value = 0.0

        for pos in positions:
            ticker = pos["ticker"].upper().strip().replace(".SA", "")
            qty = float(pos.get("quantity", 0))
            avg_price = float(pos.get("average_price", 0))
            invested = qty * avg_price

            # 1. Busca dados de cotação padrão
            market = MarketDataService.get_market_data(ticker, force_refresh=force_refresh)
            current_price = market.get("current_price") or avg_price
            pvp = market.get("pvp")
            dy_12m = market.get("dy_12m") or 0.0
            last_div = market.get("last_dividend") or 0.0
            sector = pos.get("segment") or market.get("segment") or "Geral"

            # 2. Busca fundamentos completos na BolsaAI
            bolsai_funds = BolsaiService.get_stock_fundamentals(ticker, api_key=api_key) or {}
            
            pl = bolsai_funds.get("pl") or market.get("pl")
            if bolsai_funds.get("pvp"):
                pvp = bolsai_funds.get("pvp")
            if bolsai_funds.get("close_price"):
                current_price = float(bolsai_funds.get("close_price"))
            
            roe = bolsai_funds.get("roe")
            roic = bolsai_funds.get("roic")
            net_margin = bolsai_funds.get("net_margin")
            ev_ebitda = bolsai_funds.get("ev_ebitda")
            net_debt_ebitda = bolsai_funds.get("net_debt_ebitda")
            corp_name = bolsai_funds.get("corporate_name") or market.get("name") or ticker

            # Diagnóstico de Valuation
            status_diag = "Múltiplos Padrão"
            if roe and pl:
                if roe >= 15.0 and pl <= 10.0:
                    status_diag = "Excelente (ROE > 15% e P/L < 10)"
                elif roe >= 18.0:
                    status_diag = "Alta Rentabilidade (ROE > 18%)"
                elif pl <= 8.0:
                    status_diag = "Descontada (P/L < 8)"
                elif pl > 25.0:
                    status_diag = "Múltiplo Elevado (P/L > 25)"

            current_value = qty * current_price
            profit_loss = current_value - invested
            profit_loss_pct = ((current_value / invested) - 1.0) * 100.0 if invested > 0 else 0.0

            total_invested += invested
            total_current_value += current_value

            analyzed_items.append({
                "ticker": ticker,
                "name": corp_name,
                "sector": sector,
                "quantity": qty,
                "average_price": avg_price,
                "invested_value": round(invested, 2),
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_loss_pct": round(profit_loss_pct, 2),
                "pl": round(float(pl), 2) if pl is not None else None,
                "pvp": round(float(pvp), 2) if pvp is not None else None,
                "roe": round(float(roe), 2) if roe is not None else None,
                "roic": round(float(roic), 2) if roic is not None else None,
                "net_margin": round(float(net_margin), 2) if net_margin is not None else None,
                "ev_ebitda": round(float(ev_ebitda), 2) if ev_ebitda is not None else None,
                "net_debt_ebitda": round(float(net_debt_ebitda), 2) if net_debt_ebitda is not None else None,
                "status_diag": status_diag,
                "dy_12m": round(dy_12m, 2),
                "last_dividend": round(last_div, 2),
                "target_percent": pos.get("target_percent", 0.0)
            })

        weighted_dy = 0.0
        weighted_roe = 0.0
        weighted_pl = 0.0
        sector_distribution = {}

        for item in analyzed_items:
            weight = (item["current_value"] / total_current_value) if total_current_value > 0 else 0.0
            item["portfolio_weight_pct"] = round(weight * 100.0, 2)
            
            if item["dy_12m"]:
                weighted_dy += item["dy_12m"] * weight
            if item["roe"]:
                weighted_roe += item["roe"] * weight
            if item["pl"] and item["pl"] > 0:
                weighted_pl += item["pl"] * weight

            sec = item["sector"]
            sector_distribution[sec] = round(sector_distribution.get(sec, 0.0) + item["current_value"], 2)

        total_profit_loss = total_current_value - total_invested
        total_profit_loss_pct = ((total_current_value / total_invested) - 1.0) * 100.0 if total_invested > 0 else 0.0

        return {
            "items": analyzed_items,
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_value, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_profit_loss_pct": round(total_profit_loss_pct, 2),
            "weighted_dy": round(weighted_dy, 2),
            "weighted_roe": round(weighted_roe, 2),
            "weighted_pl": round(weighted_pl, 2),
            "sector_distribution": sector_distribution
        }
