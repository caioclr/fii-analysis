import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from src.services.cross_validation_service import FII_CATEGORIES, KNOWN_SEGMENTS
from src.services.report_generator import FII_KNOWLEDGE_BASE
from src.services.valuation_pricing_service import ValuationPricingService
from src.services.dividend_projection_service import DividendProjectionService
from src.services.trend_analysis_service import TrendAnalysisService
from src.services.market_data import MarketDataService
from src.services.fundos_net_service import FundosNetService

logger = logging.getLogger(__name__)

class FIIComparatorService:
    """
    Serviço de Inteligência para Comparação Setorial de Fundos Imobiliários e Fiagros.
    Gera matriz comparativa padronizada, pódio com 5 selos de liderança setorial e
    dados formatados para gráficos de Dispersão 2x2 e Radar Multidimensional.
    """

    @classmethod
    def get_available_segments(cls) -> Dict[str, str]:
        """Retorna os segmentos disponíveis para comparação."""
        return FII_CATEGORIES

    @classmethod
    def get_tickers_by_segment(cls, segment_code: str) -> List[str]:
        """Retorna a lista de tickers cadastrados para um determinado segmento."""
        segment_code = segment_code.upper().strip()
        tickers = [t for t, s in KNOWN_SEGMENTS.items() if s == segment_code]
        # Garante ordenação consistente
        return sorted(list(set(tickers)))

    @classmethod
    def compare_sector(cls, segment_code: str, selected_tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Consolida a matriz comparativa completa para o segmento informado.
        """
        segment_code = segment_code.upper().strip()
        all_sector_tickers = cls.get_tickers_by_segment(segment_code)
        
        target_tickers = selected_tickers if selected_tickers else all_sector_tickers
        if not target_tickers:
            target_tickers = all_sector_tickers

        rows = []
        for t in target_tickers:
            kb = FII_KNOWLEDGE_BASE.get(t, {})
            dre = kb.get("dre", {})

            # Busca dados de mercado ao vivo e CVM oficial
            md = MarketDataService.get_market_data(t)
            fnet = FundosNetService.get_latest_fii_data(t)

            # Cotações e Múltiplos com Precedência Correta (Mercado/CVM > KB)
            preco = float(md.get("current_price") or kb.get("preco_mercado") or 100.0)
            vpc = float(fnet.get("vpc") or md.get("vp_per_share") or kb.get("vpc") or 100.0)
            pvp = round(preco / vpc, 2) if (vpc > 0 and preco > 0) else float(kb.get("pvp") or 1.0)
            
            provento_mes = float(md.get("last_dividend") or kb.get("provento_mes") or 0.80)
            dy_anual = float(md.get("dy_12m") or ((provento_mes * 12.0 / preco * 100.0) if preco > 0 else (kb.get("dy_anual") or 10.0)))
            
            ffo_cota = float(dre.get("ffo_cota") or kb.get("ffo_cota") or provento_mes)
            cobertura_ffo = float(dre.get("cobertura_ffo") or kb.get("cobertura_ffo") or (round(ffo_cota / provento_mes, 2) if provento_mes > 0 else 1.0))
            alavancagem_pl = float(fnet.get("alavancagem_pl_pct") or kb.get("alavancagem_pl") or 0.0)
            vacancia_fisica = float(kb.get("vacancia_fisica") or 0.0)
            vacancia_financeira = float(kb.get("vacancia_financeira") or 0.0)
            wault_anos = float(kb.get("wault_anos") or kb.get("duration_anos") or 0.0)
            reserva_cota = float(dre.get("reserva_acumulada_cota") or kb.get("reserva_acumulada_cota") or 0.0)
            score = float(kb.get("score") or 8.0)
            veredicto = str(kb.get("veredicto") or "Aprovado")
            pl_bi = float((fnet.get("patrimonio_liquido") or (kb.get("pl_bi", 0) * 1e9)) / 1e9) if (fnet.get("patrimonio_liquido") or kb.get("pl_bi")) else 1.0
            cotistas = int(fnet.get("cotistas") or kb.get("cotistas") or 50000)

            # Métricas Avançadas via Serviços Especializados
            pricing_data = ValuationPricingService.calculate_consolidated_pricing(
                ticker=t,
                metrics={
                    "preco_mercado": preco,
                    "vpc": vpc,
                    "provento_mes": provento_mes,
                    "ffo_cota": ffo_cota,
                    "dy_anual": dy_anual
                },
                segment_code=segment_code
            )

            proj_data = DividendProjectionService.project_and_analyze(
                ticker=t,
                ffo_cota=ffo_cota,
                provento_atual=provento_mes,
                reserva_acumulada_cota=reserva_cota,
                segment_code=segment_code
            )

            trend_data = TrendAnalysisService.analyze_ticker_trend(t)

            real_yield_info = pricing_data.get("real_yield", {})
            real_yield_pct = real_yield_info.get("real_yield_pct", dy_anual)
            preco_teto = pricing_data.get("preco_teto_recomendado", preco)
            margem_seg = pricing_data.get("margem_seguranca_pct", 0.0)

            rows.append({
                "ticker": t,
                "fund_name": kb.get("fund_name", t),
                "gestora": kb.get("gestora", "-"),
                "pl_bi": pl_bi,
                "cotistas": cotistas,
                "preco_mercado": preco,
                "vpc": vpc,
                "pvp": pvp,
                "dy_anual": dy_anual,
                "real_yield_pct": real_yield_pct,
                "label_real_yield": f"IPCA + {real_yield_pct:.2f}% a.a.",
                "spread_vs_ntnb": real_yield_info.get("spread_vs_ntnb", 0.0),
                "preco_teto": preco_teto,
                "margem_seguranca_pct": margem_seg,
                "provento_mes": provento_mes,
                "ffo_cota": ffo_cota,
                "cobertura_ffo_pct": round(cobertura_ffo * 100.0, 1),
                "capacidade_manutencao": proj_data.get("status_sustentabilidade"),
                "reserva_cota": reserva_cota,
                "meses_reserva": proj_data.get("meses_reserva_cobertura", 0.0),
                "extraordinario_semestre": proj_data.get("extraordinario_estimado_fim_semestre", 0.0),
                "tem_extraordinario": proj_data.get("tem_potencial_extraordinario", False),
                "alavancagem_pl": alavancagem_pl,
                "vacancia_fisica": vacancia_fisica,
                "vacancia_financeira": vacancia_financeira,
                "wault_anos": wault_anos,
                "score": score,
                "veredicto": veredicto,
                "trend_status": trend_data.get("status_geral"),
                "trend_badge": trend_data.get("badge_geral"),
                "trend_cor": trend_data.get("badge_cor")
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return {"items": [], "podium": {}, "df": df}

        # 2. Seleção dos Campeões do Pódio (5 Selos)
        podium = cls._generate_podium(df)

        return {
            "segment_code": segment_code,
            "segment_name": FII_CATEGORIES.get(segment_code, segment_code),
            "items": rows,
            "podium": podium,
            "df": df
        }

    @classmethod
    def _generate_podium(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera os 5 vencedores por categoria analítica."""
        podium = {}

        # 1. 🏷️ Melhor Oportunidade de Preço (Maior Margem de Segurança / Menor P/VP com margem)
        df_sorted_price = df.sort_values(by="margem_seguranca_pct", ascending=False)
        best_price = df_sorted_price.iloc[0].to_dict()
        podium["melhor_preco"] = {
            "ticker": best_price["ticker"],
            "titulo": "🏷️ Melhor Oportunidade de Preço",
            "motivo": f"Maior margem de segurança ({best_price['margem_seguranca_pct']:+.1f}% vs Preço-Teto de R$ {best_price['preco_teto']:.2f}) e P/VP de {best_price['pvp']:.2f}.",
            "cor": "#38bdf8"
        }

        # 2. 💰 Maior Dividendo Real (Top Retorno Real IPCA+ com cobertura >= 98%)
        df_cobertos = df[df["cobertura_ffo_pct"] >= 98.0]
        if df_cobertos.empty:
            df_cobertos = df
        best_yield = df_cobertos.sort_values(by="real_yield_pct", ascending=False).iloc[0].to_dict()
        podium["maior_renda"] = {
            "ticker": best_yield["ticker"],
            "titulo": "💰 Maior Retorno Real Líquido",
            "motivo": f"Entrega retorno real de IPCA + {best_yield['real_yield_pct']:.2f}% a.a. isento, com cobertura FFO saudável de {best_yield['cobertura_ffo_pct']:.1f}%.",
            "cor": "#22c55e"
        }

        # 3. 🛡️ Mais Seguro / Menor Risco (Menor Alavancagem + Menor Vacância)
        # Score de risco = Alavancagem + Vacância
        df_risk = df.copy()
        df_risk["risk_metric"] = df_risk["alavancagem_pl"] + (df_risk["vacancia_fisica"] * 1.5)
        safest = df_risk.sort_values(by="risk_metric", ascending=True).iloc[0].to_dict()
        podium["mais_seguro"] = {
            "ticker": safest["ticker"],
            "titulo": "🛡️ Mais Seguro & Conservador",
            "motivo": f"Mínima exposição a riscos: alavancagem de apenas {safest['alavancagem_pl']:.1f}% do PL e vacância física de {safest['vacancia_fisica']:.1f}%.",
            "cor": "#a855f7"
        }

        # 4. 🎁 Maior Potencial de Extraordinário Semestral (Maior Reserva Retida / Meses de Cobertura)
        best_reserve = df.sort_values(by="meses_reserva", ascending=False).iloc[0].to_dict()
        podium["maior_extraordinario"] = {
            "ticker": best_reserve["ticker"],
            "titulo": "🎁 Campeão de Reserva & Extraordinário",
            "motivo": f"Possui {best_reserve['meses_reserva']:.1f} meses de proventos acumulados em reserva (R$ {best_reserve['reserva_cota']:.2f}/cota) para a regra dos 95% CVM.",
            "cor": "#f59e0b"
        }

        # 5. ⭐ Líder Geral do Setor (Maior Score Ponderado)
        best_overall = df.sort_values(by=["score", "margem_seguranca_pct"], ascending=[False, False]).iloc[0].to_dict()
        podium["lider_geral"] = {
            "ticker": best_overall["ticker"],
            "titulo": "⭐ Líder Geral do Setor",
            "motivo": f"Maior pontuação técnica ponderada (Score {best_overall['score']:.1f}/10) com veredito {best_overall['veredicto']}.",
            "cor": "#eab308"
        }

        return podium
