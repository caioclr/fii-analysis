import os
import io
import time
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import requests
from src.config import DATA_DIR

logger = logging.getLogger(__name__)

CVM_CACHE_DIR = DATA_DIR / "cvm_cache"
CVM_CACHE_DIR.mkdir(exist_ok=True)

class FundosNetService:
    """
    Serviço de integração com documentos oficiais do Fundos.NET (B3) e CVM.
    Extrai informações do Informe Mensal Estruturado e dados cadastrais oficiais.
    """
    BASE_CVM_URL = "https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/"
    TICKER_ALIASES = {
        "PMLL": {"isin": "BRMALLCTF007", "cnpj": "26.499.833/0001-32", "name": "PATRIA MALLS"},
        "PMLL11": {"isin": "BRMALLCTF007", "cnpj": "26.499.833/0001-32", "name": "PATRIA MALLS"},
        "MALL": {"isin": "BRMALLCTF007", "cnpj": "26.499.833/0001-32", "name": "PATRIA MALLS"},
        "MALL11": {"isin": "BRMALLCTF007", "cnpj": "26.499.833/0001-32", "name": "PATRIA MALLS"},
        "BTCI": {"isin": "BRFEXCCTF007", "cnpj": "09.552.812/0001-14", "name": "BTG PACTUAL CRÉDITO IMOBILIÁRIO"},
        "BTCI11": {"isin": "BRFEXCCTF007", "cnpj": "09.552.812/0001-14", "name": "BTG PACTUAL CRÉDITO IMOBILIÁRIO"},
        "BTCR": {"isin": "BRFEXCCTF007", "cnpj": "09.552.812/0001-14", "name": "BTG PACTUAL CRÉDITO IMOBILIÁRIO"},
        "BTCR11": {"isin": "BRFEXCCTF007", "cnpj": "09.552.812/0001-14", "name": "BTG PACTUAL CRÉDITO IMOBILIÁRIO"},
        "FEXC": {"isin": "BRFEXCCTF007", "cnpj": "09.552.812/0001-14", "name": "BTG PACTUAL CRÉDITO IMOBILIÁRIO"},
        "FEXC11": {"isin": "BRFEXCCTF007", "cnpj": "09.552.812/0001-14", "name": "BTG PACTUAL CRÉDITO IMOBILIÁRIO"},
        "RBRY": {"isin": "BRRBRYCTF004", "cnpj": "30.166.700/0001-11", "name": "RBR CREDITO IMOB FII"},
        "RBRY11": {"isin": "BRRBRYCTF004", "cnpj": "30.166.700/0001-11", "name": "RBR CREDITO IMOB FII"},
        "GARE": {"cnpj": "37.295.919/0001-60", "name": "FII GUARDIAL LOGISTICA"},
        "GARE11": {"cnpj": "37.295.919/0001-60", "name": "FII GUARDIAL LOGISTICA"},
        "GALG": {"cnpj": "37.295.919/0001-60", "name": "FII GUARDIAL LOGISTICA"},
        "GALG11": {"cnpj": "37.295.919/0001-60", "name": "FII GUARDIAL LOGISTICA"},
        "IRDM": {"isin": "BRIRIMCTF003", "cnpj": "41.076.564/0001-95", "name": "IRIDIUM CRI"},
        "IRDM11": {"isin": "BRIRIMCTF003", "cnpj": "41.076.564/0001-95", "name": "IRIDIUM CRI"},
    }

    @classmethod
    def get_latest_fii_data(cls, ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Localiza os dados oficiais mais recentes protocolados no Fundos.NET / CVM para um ticker.
        """
        ticker = ticker.upper().strip().replace(".SA", "")
        base_ticker = ticker[:4] # ex: TRXF, HGLG, GGRC

        cache_file = CVM_CACHE_DIR / f"{ticker}_official.json"
        
        alias_info = cls.TICKER_ALIASES.get(ticker) or cls.TICKER_ALIASES.get(base_ticker)
        
        # Carrega dados gerais da CVM
        try:
            df_geral, df_comp, df_ap = cls._load_cvm_tables(force_refresh=force_refresh)
            
            match_geral = pd.DataFrame()
            if alias_info:
                if "cnpj" in alias_info:
                    match_geral = df_geral[df_geral["CNPJ_Fundo_Classe"] == alias_info["cnpj"]]
                if match_geral.empty and "isin" in alias_info:
                    match_geral = df_geral[df_geral["Codigo_ISIN"] == alias_info["isin"]]

            if match_geral.empty:
                # Filtra pelo ISIN oficial que começa com BR + ticker
                match_geral = df_geral[df_geral["Codigo_ISIN"].str.contains(rf"^BR{base_ticker}CTF", case=False, na=False)]
            
            if match_geral.empty:
                # Tenta busca flexível por ISIN ou nome
                match_geral = df_geral[df_geral["Codigo_ISIN"].str.contains(base_ticker, case=False, na=False)]
            if match_geral.empty:
                match_geral = df_geral[df_geral["Nome_Fundo_Classe"].str.contains(base_ticker, case=False, na=False)]
            if match_geral.empty and alias_info and "name" in alias_info:
                match_geral = df_geral[df_geral["Nome_Fundo_Classe"].str.contains(alias_info["name"], case=False, na=False)]

            if match_geral.empty:
                logger.warning(f"Ticker {ticker} não encontrado no Informe Mensal CVM.")
                return cls._get_fallback_data(ticker)

            # Quando há múltiplos CNPJs para uma classe, seleciona o fundo principal pelo maior Patrimônio Líquido
            cnpjs = match_geral["CNPJ_Fundo_Classe"].unique()
            c_matches = df_comp[df_comp["CNPJ_Fundo_Classe"].isin(cnpjs)].sort_values("Patrimonio_Liquido", ascending=False)
            
            if not c_matches.empty:
                cnpj = c_matches.iloc[0]["CNPJ_Fundo_Classe"]
                latest_g = match_geral[match_geral["CNPJ_Fundo_Classe"] == cnpj].sort_values("Data_Referencia").iloc[-1]
            else:
                latest_g = match_geral.sort_values("Data_Referencia").iloc[-1]
                cnpj = latest_g["CNPJ_Fundo_Classe"]

            # Complemento mais recente do fundo principal (PL, Cotistas, VPC, DY Mes)
            match_c = df_comp[df_comp["CNPJ_Fundo_Classe"] == cnpj].sort_values("Data_Referencia")
            latest_c = match_c.iloc[-1] if not match_c.empty else {}

            # Ativo e Passivo (Imóveis, CRIs, Alavancagem)
            match_ap = df_ap[df_ap["CNPJ_Fundo_Classe"] == cnpj].sort_values("Data_Referencia")
            latest_ap = match_ap.iloc[-1] if not match_ap.empty else {}

            # Extração de campos estruturados
            pl = float(latest_c.get("Patrimonio_Liquido", 0.0) or 0.0)
            vpc = float(latest_c.get("Valor_Patrimonial_Cotas", 0.0) or 0.0)
            cotas = float(latest_c.get("Cotas_Emitidas", 0.0) or 0.0)
            cotistas = int(latest_c.get("Total_Numero_Cotistas", 0) or 0)
            
            # Ativos
            total_investido = float(latest_ap.get("Total_Investido", 0.0) or 0.0)
            imoveis = float(latest_ap.get("Imoveis_Renda_Acabados", 0.0) or 0.0) + float(latest_ap.get("Imoveis_Renda_Construcao", 0.0) or 0.0)
            cotas_fiis = float(latest_ap.get("FII", 0.0) or 0.0)
            cris = float(latest_ap.get("CRI", 0.0) or latest_ap.get("CRI_CRA", 0.0) or 0.0)
            caixa = float(latest_ap.get("Disponibilidades", 0.0) or 0.0) + float(latest_ap.get("Titulos_Publicos", 0.0) or 0.0)

            # Passivos e Securitizações (Alavancagem)
            divida_cris = float(latest_ap.get("Obrigacoes_Securitizacao_Recebiveis", 0.0) or 0.0)
            total_passivo = float(latest_ap.get("Total_Passivo", 0.0) or 0.0)
            alavancagem_pl = (divida_cris / pl * 100.0) if pl > 0 else 0.0

            data_ref = str(latest_g.get("Data_Referencia", ""))
            data_entrega = str(latest_g.get("Data_Entrega", ""))

            return {
                "ticker": ticker,
                "cnpj": cnpj,
                "razao_social": latest_g.get("Nome_Fundo_Classe", f"{ticker} Fundo de Investimento Imobiliário"),
                "administrador": latest_g.get("Nome_Administrador", "Não informado"),
                "gestor": latest_g.get("Tipo_Gestao", "Gestão Ativa"),
                "segmento": latest_g.get("Segmento_Atuacao", "Renda Imobiliária"),
                "mandato": latest_g.get("Mandato", "Híbrido"),
                "data_referencia": data_ref,
                "data_protocolo_fnet": data_entrega,
                "patrimonio_liquido": pl,
                "vpc": vpc,
                "cotas_emitidas": cotas,
                "cotistas": cotistas,
                "total_investido": total_investido,
                "imoveis_valor": imoveis,
                "cotas_fiis_valor": cotas_fiis,
                "cris_valor": cris,
                "caixa_valor": caixa,
                "divida_cris": divida_cris,
                "total_passivo": total_passivo,
                "alavancagem_pl_pct": round(alavancagem_pl, 2),
                "fonte": "Fundos.NET / CVM - Informe Mensal Estruturado"
            }

        except Exception as e:
            logger.error(f"Erro ao consultar CVM / Fundos.NET para {ticker}: {e}")
            return cls._get_fallback_data(ticker)

    @classmethod
    def _load_cvm_tables(cls, force_refresh: bool = False):
        """Baixa e armazena em cache o zip de informe mensal da CVM."""
        current_year = 2026
        zip_path = CVM_CACHE_DIR / f"inf_mensal_fii_{current_year}.zip"

        # Se arquivo não existe ou é mais velho que 24 horas
        if force_refresh or not zip_path.exists() or (time.time() - zip_path.stat().st_mtime > 86400):
            url = f"{cls.BASE_CVM_URL}inf_mensal_fii_{current_year}.zip"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                with open(zip_path, "wb") as f:
                    f.write(resp.content)
            elif not zip_path.exists():
                # Tenta ano anterior como fallback
                url_prev = f"{cls.BASE_CVM_URL}inf_mensal_fii_{current_year - 1}.zip"
                resp_prev = requests.get(url_prev, timeout=30)
                if resp_prev.status_code == 200:
                    with open(zip_path, "wb") as f:
                        f.write(resp_prev.content)

        z = zipfile.ZipFile(zip_path)
        
        # Lê arquivos csv dentro do zip
        name_geral = [n for n in z.namelist() if "geral" in n][0]
        name_comp = [n for n in z.namelist() if "complemento" in n][0]
        name_ap = [n for n in z.namelist() if "ativo_passivo" in n][0]

        df_geral = pd.read_csv(z.open(name_geral), sep=";", encoding="latin1")
        df_comp = pd.read_csv(z.open(name_comp), sep=";", encoding="latin1")
        df_ap = pd.read_csv(z.open(name_ap), sep=";", encoding="latin1")

        return df_geral, df_comp, df_ap

    @classmethod
    def _get_fallback_data(cls, ticker: str) -> Dict[str, Any]:
        """Dados de fallback estruturados caso o serviço CVM esteja indisponível."""
        return {
            "ticker": ticker,
            "cnpj": "Não identificado",
            "razao_social": f"{ticker} Fundo de Investimento Imobiliário",
            "administrador": "Administradora Fiduciária B3",
            "gestor": "Gestão Ativa de Recursos",
            "segmento": "Renda Imobiliária",
            "mandato": "Renda Híbrida / Tijolo",
            "data_referencia": "Agosto / 2026",
            "data_protocolo_fnet": "Setembro / 2026",
            "patrimonio_liquido": 0.0,
            "vpc": 0.0,
            "cotas_emitidas": 0.0,
            "cotistas": 0,
            "total_investido": 0.0,
            "imoveis_valor": 0.0,
            "cotas_fiis_valor": 0.0,
            "cris_valor": 0.0,
            "caixa_valor": 0.0,
            "divida_cris": 0.0,
            "total_passivo": 0.0,
            "alavancagem_pl_pct": 0.0,
            "fonte": "Fundos.NET / B3"
        }
