import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Any
from src.database.connection import get_connection

class PortfolioRepository:
    @staticmethod
    def get_all_assets(asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna todos os ativos ou filtrados por tipo (FII, ACAO, etc)."""
        conn = get_connection()
        cursor = conn.cursor()
        if asset_type:
            cursor.execute("SELECT * FROM portfolio WHERE asset_type = ? ORDER BY ticker ASC", (asset_type,))
        else:
            cursor.execute("SELECT * FROM portfolio ORDER BY asset_type, ticker ASC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_asset_by_ticker(ticker: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolio WHERE ticker = ?", (ticker.upper().strip(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def upsert_asset(ticker: str, asset_type: str, quantity: float, average_price: float, 
                     target_percent: float = 0.0, segment: Optional[str] = None, notes: str = "") -> None:
        """Insere ou atualiza um ativo na carteira."""
        conn = get_connection()
        cursor = conn.cursor()
        ticker = ticker.upper().strip()
        cursor.execute("""
            INSERT INTO portfolio (ticker, asset_type, quantity, average_price, target_percent, segment, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ticker) DO UPDATE SET
                asset_type = excluded.asset_type,
                quantity = excluded.quantity,
                average_price = excluded.average_price,
                target_percent = excluded.target_percent,
                segment = COALESCE(excluded.segment, portfolio.segment),
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
        """, (ticker, asset_type.upper().strip(), quantity, average_price, target_percent, segment, notes))
        conn.commit()
        conn.close()

    @staticmethod
    def update_target_percent(ticker: str, target_percent: float) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE portfolio SET target_percent = ?, updated_at = CURRENT_TIMESTAMP WHERE ticker = ?", 
                       (target_percent, ticker.upper().strip()))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_asset(ticker: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker.upper().strip(),))
        conn.commit()
        conn.close()

    @staticmethod
    def clear_portfolio() -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolio")
        conn.commit()
        conn.close()

    # --- Metas de Alocação Macro ---
    @staticmethod
    def get_macro_allocations() -> Dict[str, float]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT asset_type, target_percent FROM macro_allocation")
        rows = cursor.fetchall()
        conn.close()
        return {row["asset_type"]: row["target_percent"] for row in rows}

    @staticmethod
    def update_macro_allocation(asset_type: str, target_percent: float) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO macro_allocation (asset_type, target_percent)
            VALUES (?, ?)
            ON CONFLICT(asset_type) DO UPDATE SET target_percent = excluded.target_percent
        """, (asset_type, target_percent))
        conn.commit()
        conn.close()

    # --- Cache de Mercado ---
    @staticmethod
    def get_cached_market_data(ticker: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM market_cache WHERE ticker = ?", (ticker.upper().strip(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def set_cached_market_data(ticker: str, current_price: float, pvp: Optional[float] = None, 
                               dy_12m: Optional[float] = None, last_dividend: Optional[float] = None,
                               vp_per_share: Optional[float] = None, segment: Optional[str] = None, 
                               data_json: str = "{}") -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO market_cache (ticker, current_price, pvp, dy_12m, last_dividend, vp_per_share, segment, data_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ticker) DO UPDATE SET
                current_price = excluded.current_price,
                pvp = excluded.pvp,
                dy_12m = excluded.dy_12m,
                last_dividend = excluded.last_dividend,
                vp_per_share = excluded.vp_per_share,
                segment = COALESCE(excluded.segment, market_cache.segment),
                data_json = excluded.data_json,
                updated_at = CURRENT_TIMESTAMP
        """, (ticker.upper().strip(), current_price, pvp, dy_12m, last_dividend, vp_per_share, segment, data_json))
        conn.commit()
        conn.close()

class AuditHistoryRepository:
    """Repositório para persistência do histórico de auditorias e notas dos FIIs."""

    @staticmethod
    def save_audit_snapshot(data: Dict[str, Any]) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_history (
                ticker, audit_date, score, veredicto, preco_mercado, vpc, pvp, dy_anual,
                preco_teto, alocacao_sugerida, ffo_cota, cobertura_ffo, alavancagem_pct,
                vacancia_fisica, trend_status, reserva_cota, guidance_proximo_mes,
                extraordinario_estimado, real_yield_pct, custom_params_json, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("ticker", "").upper().strip(),
            data.get("audit_date", ""),
            data.get("score"),
            data.get("veredicto"),
            data.get("preco_mercado"),
            data.get("vpc"),
            data.get("pvp"),
            data.get("dy_anual"),
            data.get("preco_teto"),
            data.get("alocacao_sugerida"),
            data.get("ffo_cota"),
            data.get("cobertura_ffo"),
            data.get("alavancagem_pct"),
            data.get("vacancia_fisica"),
            data.get("trend_status", "ESTAVEL"),
            data.get("reserva_cota"),
            data.get("guidance_proximo_mes"),
            data.get("extraordinario_estimado"),
            data.get("real_yield_pct"),
            data.get("custom_params_json", "{}"),
            data.get("notes", "")
        ))
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id

    @staticmethod
    def get_audit_history(ticker: str, limit: int = 12) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM audit_history 
            WHERE ticker = ? 
            ORDER BY audit_date DESC, created_at DESC 
            LIMIT ?
        """, (ticker.upper().strip(), limit))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_latest_audit(ticker: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM audit_history 
            WHERE ticker = ? 
            ORDER BY audit_date DESC, created_at DESC 
            LIMIT 1
        """, (ticker.upper().strip(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_latest_audits() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.* FROM audit_history a
            INNER JOIN (
                SELECT ticker, MAX(created_at) as max_created
                FROM audit_history
                GROUP BY ticker
            ) b ON a.ticker = b.ticker AND a.created_at = b.max_created
            ORDER BY a.score DESC, a.ticker ASC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows


class GerencialHistoryRepository:
    """Repositório para séries temporais mensais extraídas dos relatórios gerenciais."""

    @staticmethod
    def upsert_period(ticker: str, periodo: str, metrics: Dict[str, Any]) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        ticker = ticker.upper().strip()
        cursor.execute("""
            INSERT INTO gerencial_history (
                ticker, periodo, ano, mes, vacancia_fisica, vacancia_financeira, ocupacao_pct,
                sss_pct, ssr_pct, aluguel_medio_m2, ocr_pct, inadimplencia_pct, ffo_cota,
                provento_cota, cobertura_ffo, alavancagem_pl_pct, ltv_pct, reserva_acumulada_cota,
                raw_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ticker, periodo) DO UPDATE SET
                ano = COALESCE(excluded.ano, gerencial_history.ano),
                mes = COALESCE(excluded.mes, gerencial_history.mes),
                vacancia_fisica = COALESCE(excluded.vacancia_fisica, gerencial_history.vacancia_fisica),
                vacancia_financeira = COALESCE(excluded.vacancia_financeira, gerencial_history.vacancia_financeira),
                ocupacao_pct = COALESCE(excluded.ocupacao_pct, gerencial_history.ocupacao_pct),
                sss_pct = COALESCE(excluded.sss_pct, gerencial_history.sss_pct),
                ssr_pct = COALESCE(excluded.ssr_pct, gerencial_history.ssr_pct),
                aluguel_medio_m2 = COALESCE(excluded.aluguel_medio_m2, gerencial_history.aluguel_medio_m2),
                ocr_pct = COALESCE(excluded.ocr_pct, gerencial_history.ocr_pct),
                inadimplencia_pct = COALESCE(excluded.inadimplencia_pct, gerencial_history.inadimplencia_pct),
                ffo_cota = COALESCE(excluded.ffo_cota, gerencial_history.ffo_cota),
                provento_cota = COALESCE(excluded.provento_cota, gerencial_history.provento_cota),
                cobertura_ffo = COALESCE(excluded.cobertura_ffo, gerencial_history.cobertura_ffo),
                alavancagem_pl_pct = COALESCE(excluded.alavancagem_pl_pct, gerencial_history.alavancagem_pl_pct),
                ltv_pct = COALESCE(excluded.ltv_pct, gerencial_history.ltv_pct),
                reserva_acumulada_cota = COALESCE(excluded.reserva_acumulada_cota, gerencial_history.reserva_acumulada_cota),
                raw_json = COALESCE(excluded.raw_json, gerencial_history.raw_json),
                created_at = CURRENT_TIMESTAMP
        """, (
            ticker,
            periodo,
            metrics.get("ano"),
            metrics.get("mes"),
            metrics.get("vacancia_fisica"),
            metrics.get("vacancia_financeira"),
            metrics.get("ocupacao_pct"),
            metrics.get("sss_pct"),
            metrics.get("ssr_pct"),
            metrics.get("aluguel_medio_m2"),
            metrics.get("ocr_pct"),
            metrics.get("inadimplencia_pct"),
            metrics.get("ffo_cota"),
            metrics.get("provento_cota"),
            metrics.get("cobertura_ffo"),
            metrics.get("alavancagem_pl_pct"),
            metrics.get("ltv_pct"),
            metrics.get("reserva_acumulada_cota"),
            metrics.get("raw_json", "{}")
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_history(ticker: str, limit: int = 12) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM gerencial_history 
            WHERE ticker = ? 
            ORDER BY ano DESC, mes DESC, periodo DESC 
            LIMIT ?
        """, (ticker.upper().strip(), limit))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_periods_for_ticker(ticker: str) -> List[str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT periodo FROM gerencial_history 
            WHERE ticker = ? 
            ORDER BY ano DESC, mes DESC, periodo DESC
        """, (ticker.upper().strip(),))
        periods = [r["periodo"] for r in cursor.fetchall()]
        conn.close()
        return periods


class PricingParametersRepository:
    """Repositório de taxas e parâmetros macroeconômicos de precificação."""

    @staticmethod
    def get_parameters() -> Dict[str, float]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT param_name, param_value FROM pricing_parameters")
        rows = cursor.fetchall()
        conn.close()
        defaults = {
            "ntnb_reference_rate": 6.50,
            "projected_ipca": 4.00,
            "real_risk_spread": 2.00
        }
        for r in rows:
            defaults[r["param_name"]] = float(r["param_value"])
        return defaults

    @staticmethod
    def set_parameter(param_name: str, param_value: float, description: str = "") -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pricing_parameters (param_name, param_value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(param_name) DO UPDATE SET
                param_value = excluded.param_value,
                description = COALESCE(excluded.description, pricing_parameters.description),
                updated_at = CURRENT_TIMESTAMP
        """, (param_name, float(param_value), description))
        conn.commit()
        conn.close()

    update_parameter = set_parameter


