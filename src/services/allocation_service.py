from typing import Dict, List, Any
import numpy as np
import pandas as pd
from src.database.repository import PortfolioRepository

class AllocationService:
    @classmethod
    def calculate_macro_allocation(cls, fii_total: float, stock_total: float, other_total: float = 0.0) -> Dict[str, Any]:
        """
        Analisa a distribuição macro da carteira comparando com as metas cadastradas.
        """
        total_portfolio = fii_total + stock_total + other_total
        targets = PortfolioRepository.get_macro_allocations()

        classes = [
            {"type": "FII", "name": "Fundos Imobiliários", "current_value": fii_total, "target_pct": targets.get("FII", 50.0)},
            {"type": "ACAO", "name": "Ações", "current_value": stock_total, "target_pct": targets.get("ACAO", 40.0)},
            {"type": "RENDA_FIXA", "name": "Renda Fixa / Caixa", "current_value": other_total, "target_pct": targets.get("RENDA_FIXA", 10.0)}
        ]

        result_classes = []
        for item in classes:
            cur_pct = (item["current_value"] / total_portfolio * 100.0) if total_portfolio > 0 else 0.0
            target_pct = item["target_pct"]
            diff_pct = cur_pct - target_pct
            
            # Status
            if diff_pct < -2.0:
                status = "Abaixo da Meta (Aportar)"
            elif diff_pct > 2.0:
                status = "Acima da Meta (Segurar)"
            else:
                status = "Balanceado"

            result_classes.append({
                "type": item["type"],
                "name": item["name"],
                "current_value": round(item["current_value"], 2),
                "current_pct": round(cur_pct, 2),
                "target_pct": round(target_pct, 2),
                "diff_pct": round(diff_pct, 2),
                "status": status
            })

        return {
            "total_portfolio": round(total_portfolio, 2),
            "classes": result_classes
        }

    @classmethod
    def calculate_smart_contribution(cls, new_money: float, macro_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calcula a sugestão de aporte inteligente para um novo valor disponível,
        priorizando as classes e ativos que estão mais distantes da meta.
        """
        total_current = macro_data["total_portfolio"]
        new_total = total_current + new_money
        classes = macro_data["classes"]

        # Calcula o valor ideal de cada classe no novo total
        suggestions = []
        shortfalls = []

        for item in classes:
            ideal_value = (item["target_pct"] / 100.0) * new_total
            shortfall = max(0.0, ideal_value - item["current_value"])
            shortfalls.append(shortfall)

        total_shortfall = sum(shortfalls)

        for i, item in enumerate(classes):
            if total_shortfall > 0:
                suggested_amount = (shortfalls[i] / total_shortfall) * new_money
            else:
                # Se tudo já estiver equilibrado, reparte proporcional à meta
                suggested_amount = (item["target_pct"] / 100.0) * new_money

            new_projected_value = item["current_value"] + suggested_amount
            new_projected_pct = (new_projected_value / new_total) * 100.0 if new_total > 0 else 0.0

            suggestions.append({
                "name": item["name"],
                "current_value": item["current_value"],
                "current_pct": item["current_pct"],
                "target_pct": item["target_pct"],
                "suggested_amount": round(suggested_amount, 2),
                "projected_value": round(new_projected_value, 2),
                "projected_pct": round(new_projected_pct, 2)
            })

        return suggestions
