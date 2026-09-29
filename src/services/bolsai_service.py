import os
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from src.config import DATA_DIR

logger = logging.getLogger(__name__)

CONFIG_FILE = DATA_DIR / "bolsai_config.json"

class BolsaiService:
    """
    Cliente de integração com a API da BolsaAI (https://usebolsai.com/mcp e https://usebolsai.com/api/v1).
    Acessa cotações, dividendos, fundamentos, DRE e indicadores macro (SELIC, IPCA, CDI).
    """
    BASE_URL = os.environ.get("BOLSAI_BASE_URL", "https://usebolsai.com/api/v1")

    @classmethod
    def get_api_key(cls, explicit_key: Optional[str] = None) -> str:
        """Recupera a chave de API fornecida explicitamente, por env ou por arquivo de config."""
        if explicit_key and explicit_key.strip():
            return explicit_key.strip()
        
        env_key = os.environ.get("BOLSAI_API_KEY", "")
        if env_key:
            return env_key.strip()

        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    return cfg.get("api_key", "").strip()
            except Exception:
                pass
        return ""

    @classmethod
    def save_api_key(cls, api_key: str) -> None:
        """Salva a chave da API localmente em arquivo de configuração."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"api_key": api_key.strip()}, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar chave BolsaAI: {e}")

    @classmethod
    def _headers(cls, api_key: Optional[str] = None) -> Dict[str, str]:
        key = cls.get_api_key(api_key)
        headers = {"Content-Type": "application/json"}
        if key:
            headers["X-API-Key"] = key
        return headers

    @classmethod
    def test_connection(cls, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Testa se a chave da BolsaAI é válida fazendo uma requisição simples."""
        key = cls.get_api_key(api_key)
        if not key:
            return {
                "success": False,
                "message": "Nenhuma chave de API configurada. Obtenha gratuitamente em https://usebolsai.com/dashboard"
            }
        
        url = f"{cls.BASE_URL}/stocks/ITUB4/quote"
        try:
            resp = requests.get(url, headers=cls._headers(key), timeout=8)
            if resp.status_code == 200:
                return {"success": True, "message": "Conexão com BolsaAI estabelecida com sucesso!"}
            elif resp.status_code == 401:
                return {"success": False, "message": "Chave de API inválida ou expirada na BolsaAI."}
            else:
                return {"success": False, "message": f"Resposta da API ({resp.status_code}): {resp.text}"}
        except Exception as e:
            return {"success": False, "message": f"Erro de conexão com BolsaAI: {str(e)}"}

    @classmethod
    def get_fii_screener(cls, limit: int = 400, offset: int = 0, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Consulta o Screener oficial da BolsaAI retornando a base de FIIs com cotações, P/VP, DY e métricas consolidadas.
        Endpoint: GET /fiis/screener?limit={limit}&offset={offset}
        """
        url = f"{cls.BASE_URL}/fiis/screener?limit={limit}&offset={offset}"
        try:
            resp = requests.get(url, headers=cls._headers(api_key), timeout=15)
            if resp.status_code == 200:
                payload = resp.json()
                return payload.get("data", [])
            logger.warning(f"BolsaAI /fiis/screener status: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Erro ao buscar screener na BolsaAI: {e}")
        return []

    @classmethod
    def get_fii_details(cls, ticker: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Busca fundamentos e dados de um FII na BolsaAI."""
        ticker = ticker.upper().strip().replace(".SA", "")
        url = f"{cls.BASE_URL}/fiis/{ticker}"
        try:
            resp = requests.get(url, headers=cls._headers(api_key), timeout=10)
            if resp.status_code == 200:
                return resp.json()
            logger.debug(f"BolsaAI /fiis/{ticker} status: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Erro ao buscar FII na BolsaAI para {ticker}: {e}")
        return None

    @classmethod
    def get_fii_distributions(cls, ticker: str, years: int = 3, api_key: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Busca histórico de distribuições e proventos do FII na BolsaAI."""
        ticker = ticker.upper().strip().replace(".SA", "")
        url = f"{cls.BASE_URL}/fiis/{ticker}/distributions?years={years}"
        try:
            resp = requests.get(url, headers=cls._headers(api_key), timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"Erro ao buscar distribuições BolsaAI para {ticker}: {e}")
        return None

    @classmethod
    def get_macro_indicators(cls, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Busca taxas macroeconômicas (SELIC, IPCA, CDI) na BolsaAI."""
        result = {"selic": 14.25, "cdi": 14.15, "ipca_12m": 4.50}
        key = cls.get_api_key(api_key)
        if not key:
            return result

        url = f"{cls.BASE_URL}/macro/"
        try:
            resp = requests.get(url, headers=cls._headers(key), timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    result.update(data)
        except Exception as e:
            logger.debug(f"Erro ao buscar macro BolsaAI: {e}")
        return result

    @classmethod
    def get_stock_fundamentals(cls, ticker: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Busca os 27+ múltiplos fundamentalistas de uma ação na BolsaAI."""
        ticker = ticker.upper().strip().replace(".SA", "")
        url = f"{cls.BASE_URL}/fundamentals/{ticker}"
        try:
            resp = requests.get(url, headers=cls._headers(api_key), timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"Erro ao buscar fundamentos de ações na BolsaAI para {ticker}: {e}")
        return None

    @classmethod
    def get_fii_property_details(cls, ticker: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Busca detalhamento de imóveis físicos, shoppings ou lajes cadastrados no FII."""
        fii = cls.get_fii_details(ticker, api_key=api_key)
        if fii:
            return {
                "property_count": fii.get("property_count"),
                "total_area_sqm": fii.get("total_area_sqm"),
                "vacancy_pct": fii.get("vacancy_pct"),
                "delinquency_pct": fii.get("delinquency_pct"),
                "leased_pct": fii.get("leased_pct"),
                "top_properties": fii.get("top_properties", []) or [],
                "asset_composition": fii.get("asset_composition", {}) or {}
            }
        return None

    @classmethod
    def get_fii_distributions_summary(cls, ticker: str, years: int = 3, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Consolida histórico de dividendos para avaliar consistência de proventos."""
        dist = cls.get_fii_distributions(ticker, years=years, api_key=api_key)
        if not dist:
            return {
                "count": 0,
                "average_dividend": 0.0,
                "latest_dividend": 0.0,
                "consistency": "Dados insuficientes",
                "history": [],
                "ttm_per_share": 0.0,
                "dividend_yield_ttm": 0.0
            }

        # BolsaAI retorna um dict com payments, ttm_per_share e dividend_yield_ttm, ou uma lista direta
        if isinstance(dist, dict):
            payments = dist.get("payments", [])
            ttm_per_share = float(dist.get("ttm_per_share") or 0.0)
            dy_ttm = float(dist.get("dividend_yield_ttm") or 0.0)
            close_price = float(dist.get("close_price") or 0.0)
        elif isinstance(dist, list):
            payments = dist
            ttm_per_share = 0.0
            dy_ttm = 0.0
            close_price = 0.0
        else:
            payments = []
            ttm_per_share = 0.0
            dy_ttm = 0.0
            close_price = 0.0

        rates = []
        for item in payments:
            if isinstance(item, dict):
                r = item.get("value_per_share") or item.get("rate") or item.get("value") or item.get("amount") or 0.0
            elif isinstance(item, (int, float)):
                r = float(item)
            else:
                r = 0.0
            if r > 0:
                rates.append(float(r))

        if not rates:
            return {
                "count": 0,
                "average_dividend": 0.0,
                "latest_dividend": 0.0,
                "consistency": "Sem histórico recente",
                "history": [],
                "ttm_per_share": ttm_per_share,
                "dividend_yield_ttm": dy_ttm
            }

        avg_div = sum(rates) / len(rates)
        latest_div = rates[0]

        # Se ttm_per_share não veio no payload, soma os pagamentos dos últimos 12 meses
        if ttm_per_share <= 0:
            ttm_per_share = sum(rates[:12]) if len(rates) >= 12 else sum(rates)

        # Avalia consistência e tendência
        if len(rates) >= 6:
            recent_avg = sum(rates[:3]) / 3
            past_avg = sum(rates[-3:]) / 3
            if recent_avg > past_avg * 1.05:
                trend = "Crescente"
            elif recent_avg < past_avg * 0.95:
                trend = "Em queda"
            else:
                trend = "Estável e consistente"
        else:
            trend = "Estável"

        return {
            "count": len(rates),
            "average_dividend": round(avg_div, 3),
            "latest_dividend": round(latest_div, 3),
            "consistency": trend,
            "history": payments[:12],
            "ttm_per_share": round(ttm_per_share, 4),
            "dividend_yield_ttm": dy_ttm,
            "close_price": close_price
        }

