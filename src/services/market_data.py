import time
import json
import logging
from typing import Dict, Any, Optional
import requests
import yfinance as yf
from src.database.repository import PortfolioRepository
from src.config import CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)

class MarketDataService:
    @staticmethod
    def format_ticker_yf(ticker: str) -> str:
        """Adiciona o sufixo .SA se for ativo da B3."""
        ticker = ticker.upper().strip()
        if not ticker.endswith(".SA") and not ticker.startswith("^"):
            return f"{ticker}.SA"
        return ticker

    @classmethod
    def get_market_data(cls, ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Obtém cotação e indicadores fundamentalistas de um ticker (FII ou Ação).
        Usa cache local SQLite se recente, senão consulta Yahoo Finance / Brapi.
        """
        ticker = ticker.upper().strip()
        
        # 1. Verifica cache no banco SQLite
        if not force_refresh:
            cached = PortfolioRepository.get_cached_market_data(ticker)
            if cached and cached.get("updated_at"):
                # Se cache existir e não for muito antigo
                # Para simplificar, se tiver preço válido e não for forçado, podemos retornar
                # Mas vamos verificar timestamp se necessário
                if cached.get("current_price") and cached.get("current_price") > 0:
                    ret = {
                        "ticker": ticker,
                        "current_price": cached.get("current_price", 0.0),
                        "pvp": cached.get("pvp"),
                        "dy_12m": cached.get("dy_12m"),
                        "last_dividend": cached.get("last_dividend"),
                        "vp_per_share": cached.get("vp_per_share"),
                        "segment": cached.get("segment"),
                        "from_cache": True
                    }
                    if cached.get("data_json"):
                        try:
                            extra = json.loads(cached["data_json"])
                            if "adtv_milhoes" in extra and extra["adtv_milhoes"] is not None:
                                ret["adtv_milhoes"] = extra["adtv_milhoes"]
                            if "adtv" in extra and extra["adtv"] is not None:
                                ret["adtv"] = extra["adtv"]
                        except Exception:
                            pass
                    # Se o cache já possui adtv_milhoes calculado, retorna; senão busca para enriquecer
                    if "adtv_milhoes" in ret and ret["adtv_milhoes"] is not None:
                        return ret

        # 2. Busca prioritária na BolsaAI (se configurada)
        from src.services.bolsai_service import BolsaiService
        if BolsaiService.get_api_key():
            try:
                b_fii = BolsaiService.get_fii_details(ticker)
                if b_fii and b_fii.get("close_price"):
                    price = float(b_fii.get("close_price") or 0.0)
                    vpc = float(b_fii.get("book_value_per_share") or 0.0)
                    pvp = float(b_fii.get("pvp") or (round(price / vpc, 2) if vpc > 0 else 1.0))
                    dy_12m = float(b_fii.get("dividend_yield_ttm") or 0.0)
                    
                    data = {
                        "ticker": ticker,
                        "current_price": price,
                        "pvp": pvp,
                        "dy_12m": dy_12m,
                        "last_dividend": None,
                        "vp_per_share": vpc,
                        "segment": b_fii.get("segment"),
                        "name": b_fii.get("name") or ticker,
                        "source": "bolsai"
                    }
                    
                    dist = BolsaiService.get_fii_distributions_summary(ticker, years=1)
                    if dist and dist.get("latest_dividend"):
                        data["last_dividend"] = float(dist.get("latest_dividend") or 0.0)
                    
                    PortfolioRepository.set_cached_market_data(
                        ticker=ticker,
                        current_price=data["current_price"],
                        pvp=data["pvp"],
                        dy_12m=data["dy_12m"],
                        last_dividend=data.get("last_dividend"),
                        vp_per_share=data["vp_per_share"],
                        segment=data.get("segment"),
                        data_json=json.dumps(b_fii)
                    )
                    return data
            except Exception as e:
                logger.warning(f"Falha ao consultar BolsaAI no MarketDataService para {ticker}: {e}")

        # 3. Fallback: Busca dados via yfinance
        data = cls._fetch_from_yfinance(ticker)
        
        # 3. Fallback ou enriquecimento com brapi se yfinance faltar dados críticos
        if not data.get("current_price") or data.get("current_price") == 0:
            brapi_data = cls._fetch_from_brapi(ticker)
            if brapi_data.get("current_price"):
                data.update(brapi_data)

        # 3.1 Se faltar vp_per_share ou pvp, enriquece com FundosNetService (CVM)
        if not data.get("vp_per_share") or data.get("vp_per_share") <= 0:
            try:
                from src.services.fundos_net_service import FundosNetService
                fnet = FundosNetService.get_latest_fii_data(ticker)
                if fnet and fnet.get("vpc") and float(fnet["vpc"]) > 0:
                    data["vp_per_share"] = round(float(fnet["vpc"]), 2)
                    if data.get("current_price") and data["current_price"] > 0:
                        data["pvp"] = round(data["current_price"] / data["vp_per_share"], 2)
            except Exception as e:
                logger.debug(f"FundosNet enrichment falhou para {ticker}: {e}")

        # 4. Salva no cache se obteve preço
        if data.get("current_price") and data.get("current_price") > 0:
            PortfolioRepository.set_cached_market_data(
                ticker=ticker,
                current_price=data.get("current_price", 0.0),
                pvp=data.get("pvp"),
                dy_12m=data.get("dy_12m"),
                last_dividend=data.get("last_dividend"),
                vp_per_share=data.get("vp_per_share"),
                segment=data.get("segment"),
                data_json=json.dumps(data)
            )

        return data

    @classmethod
    def _fetch_from_yfinance(cls, ticker: str) -> Dict[str, Any]:
        yf_symbol = cls.format_ticker_yf(ticker)
        result = {
            "ticker": ticker,
            "current_price": 0.0,
            "pvp": None,
            "dy_12m": None,
            "last_dividend": None,
            "vp_per_share": None,
            "segment": None,
            "name": ticker
        }

        try:
            ticker_obj = yf.Ticker(yf_symbol)
            
            # Tenta pegar preço rápido primeiro
            fast_info = getattr(ticker_obj, "fast_info", None)
            current_price = 0.0
            if fast_info:
                current_price = fast_info.last_price or fast_info.previous_close or 0.0

            # Tenta pegar info completa
            info = {}
            try:
                info = ticker_obj.info or {}
            except Exception:
                info = {}

            if not current_price and info:
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0.0

            pvp = info.get("priceToBook")
            vp_per_share = info.get("bookValue")
            dy = info.get("dividendYield")
            
            # Ajuste de Dividend Yield (algumas vezes vem em decimal 0.09, outras já 9.0)
            if dy is not None:
                dy_val = float(dy)
                if dy_val < 1.0:
                    dy_val = dy_val * 100.0
                result["dy_12m"] = round(dy_val, 2)

            # Histórico de dividendos para pegar o último provento
            try:
                dividends = ticker_obj.dividends
                if dividends is not None and not dividends.empty:
                    result["last_dividend"] = float(dividends.iloc[-1])
                    if not result["dy_12m"] and current_price > 0:
                        # Estima anualizando os últimos 12 meses
                        last_12m_divs = dividends.last("365D").sum()
                        if last_12m_divs > 0:
                            result["dy_12m"] = round((float(last_12m_divs) / current_price) * 100.0, 2)
            except Exception:
                pass

            # Volume Médio Diário de Negociação (ADTV) dos últimos 30 dias (1 mês)
            try:
                hist = ticker_obj.history(period="1mo")
                if hist is not None and not hist.empty:
                    fin_vol = hist["Volume"] * hist["Close"]
                    adtv_calc = float(fin_vol.mean())
                    result["adtv"] = round(adtv_calc, 2)
                    result["adtv_milhoes"] = round(adtv_calc / 1e6, 2)
                else:
                    result["adtv_milhoes"] = None
            except Exception:
                result["adtv_milhoes"] = None

            result["current_price"] = round(float(current_price), 2)
            if pvp:
                result["pvp"] = round(float(pvp), 2)
            if vp_per_share:
                result["vp_per_share"] = round(float(vp_per_share), 2)
            result["segment"] = info.get("industry") or info.get("sector")
            result["name"] = info.get("shortName") or info.get("longName") or ticker

        except Exception as e:
            logger.warning(f"Erro ao buscar {ticker} no yfinance: {e}")

        return result

    @classmethod
    def _fetch_from_brapi(cls, ticker: str) -> Dict[str, Any]:
        """Consulta pública brapi.dev para cotações da B3."""
        result = {}
        clean_ticker = ticker.upper().replace(".SA", "").strip()
        url = f"https://brapi.dev/api/quote/{clean_ticker}?range=1d&interval=1d&fundamental=true&dividends=true"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    item = results[0]
                    result["current_price"] = round(float(item.get("regularMarketPrice", 0.0)), 2)
                    result["name"] = item.get("longName") or item.get("shortName") or clean_ticker
                    
                    # Indicadores se disponíveis
                    if item.get("priceEarnings") is not None:
                        result["pl"] = item.get("priceEarnings")
                    
                    # Histórico de dividendos brapi
                    divs = item.get("dividendsData", {}).get("cashDividends", [])
                    if divs:
                        result["last_dividend"] = round(float(divs[0].get("rate", 0)), 2)
        except Exception as e:
            logger.debug(f"Brapi fetch falhou para {ticker}: {e}")
        return result
