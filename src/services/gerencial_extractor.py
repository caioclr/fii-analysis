import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import io
from pypdf import PdfReader
from src.config import DATA_DIR

logger = logging.getLogger(__name__)

GERENCIAL_CACHE_DIR = DATA_DIR / "gerencial_cache"
GERENCIAL_CACHE_DIR.mkdir(exist_ok=True)

class GerencialExtractor:
    """
    Serviço especializado na extração e estruturação de dados de Relatórios Gerenciais (PDFs)
    de Fundos Imobiliários, com foco prioritário em Shopping Centers (HSML11, XPML11, VISC11, HGBS11, PMLL11).
    """

    @classmethod
    def extract_from_pdf(cls, file_or_path: Union[str, Path, io.BytesIO, bytes], ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Lê e extrai os dados estruturados de um PDF de relatório gerencial.
        """
        try:
            reader = PdfReader(file_or_path)
            full_text = ""
            pages_text = []
            for i, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                pages_text.append(txt)
                full_text += f"\n--- PÁGINA {i+1} ---\n" + txt

            # Se ticker não foi informado, tenta inferir do texto
            if not ticker:
                ticker = cls._infer_ticker(full_text)

            detected_ticker = ticker.upper().strip().replace(".SA", "") if ticker else "DESCONHECIDO"

            # Extração de métricas de Shopping Centers
            data = cls._parse_shopping_metrics(full_text, pages_text, detected_ticker)

            # Salva no cache estruturado
            cls.save_to_cache(detected_ticker, data)

            return data

        except Exception as e:
            logger.error(f"Erro ao extrair dados do relatório gerencial: {e}")
            return {"error": str(e), "success": False}

    @classmethod
    def _infer_ticker(cls, text: str) -> Optional[str]:
        known = ["HSML11", "XPML11", "VISC11", "HGBS11", "PMLL11", "MALL11", "TRXF11", "HGLG11", "GGRC11", "PVBI11", "KNCR11"]
        for t in known:
            if re.search(rf"\b{t}\b", text, re.IGNORECASE):
                return t
        return None

    @classmethod
    def _parse_shopping_metrics(cls, text: str, pages: List[str], ticker: str) -> Dict[str, Any]:
        """
        Analisa o texto completo e as páginas em busca dos padrões da ABRASCE e das gestoras
        (HSI, XP Asset, Vinci, Hedge, Pátria/Genial).
        """
        result = {
            "ticker": ticker,
            "success": True,
            "raw_text_length": len(text),
            "pages_count": len(pages),
            "metricas_operacionais": {},
            "dre_caixa": {},
            "alocacao_geografica": [],
            "composicao_ativo": [],
            "empreendimentos": [],
            "locatarios_ancoras": [],
            "indexadores": {},
            "estrutura_capital": {}
        }

        # 1. Vendas Mesmas Lojas (SSS) e Aluguel Mesmas Lojas (SSR)
        # Padrões comuns: "SSS: 7,8%", "Same Store Sales: +8.2%", "Vendas Mesmas Lojas de 7,8%"
        sss_match = re.search(r"(?:SSS|Same\s*Store\s*Sales|Vendas\s*Mesmas\s*Lojas)[^\d\+\-]*([\+\-]?\s*\d+[\.,]\d+)%", text, re.IGNORECASE)
        if sss_match:
            try:
                result["metricas_operacionais"]["sss_pct"] = float(sss_match.group(1).replace(" ", "").replace(",", "."))
            except Exception:
                pass

        ssr_match = re.search(r"(?:SSR|Same\s*Store\s*Rent|Alugue(?:l|is)\s*Mesmas\s*Lojas)[^\d\+\-]*([\+\-]?\s*\d+[\.,]\d+)%", text, re.IGNORECASE)
        if ssr_match:
            try:
                result["metricas_operacionais"]["ssr_pct"] = float(ssr_match.group(1).replace(" ", "").replace(",", "."))
            except Exception:
                pass

        # 2. Ocupação e Vacâncias
        # Padrão: "Ocupação: 95,5%", "Vacância Física: 4,5%", "Vacância Financeira: 3,5%"
        vac_fis_match = re.search(r"Vac[âa]ncia\s*F[íi]sica[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if vac_fis_match:
            try:
                result["metricas_operacionais"]["vacancia_fisica"] = float(vac_fis_match.group(1).replace(",", "."))
            except Exception:
                pass

        vac_fin_match = re.search(r"Vac[âa]ncia\s*Financeira[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if vac_fin_match:
            try:
                result["metricas_operacionais"]["vacancia_financeira"] = float(vac_fin_match.group(1).replace(",", "."))
            except Exception:
                pass

        ocup_match = re.search(r"(?:Taxa\s*de\s*)?Ocupa[çc][ãa]o\s*(?:M[ée]dia)?[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if ocup_match:
            try:
                ocup_val = float(ocup_match.group(1).replace(",", "."))
                result["metricas_operacionais"]["ocupacao_pct"] = ocup_val
                if "vacancia_fisica" not in result["metricas_operacionais"] and ocup_val <= 100:
                    result["metricas_operacionais"]["vacancia_fisica"] = round(100.0 - ocup_val, 2)
            except Exception:
                pass

        # Custo de Ocupação (OCR)
        ocr_match = re.search(r"(?:Custo\s*de\s*Ocupa[çc][ãa]o|OCR)[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if ocr_match:
            try:
                result["metricas_operacionais"]["ocr_pct"] = float(ocr_match.group(1).replace(",", "."))
            except Exception:
                pass

        # Inadimplência Líquida
        inad_match = re.search(r"(?:Inadimpl[êe]ncia|Inadimpl[êe]ncia\s*L[íi]quida)[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if inad_match:
            try:
                result["metricas_operacionais"]["inadimplencia_pct"] = float(inad_match.group(1).replace(",", "."))
            except Exception:
                pass

        # 3. FFO e Cobertura
        # Padrões: "FFO por cota: R$ 0,64", "FFO Operacional: 0,64", "Cobertura: 85,3%" ou "0,85"
        ffo_cota_match = re.search(r"(?:FFO(?:\s*Operacional)?(?:\s*Recorrente)?(?:\s*por|\s*/)?\s*Cota)[^\d]*R?\$?\s*(\d+[\.,]\d+)", text, re.IGNORECASE)
        if ffo_cota_match:
            try:
                result["dre_caixa"]["ffo_cota"] = float(ffo_cota_match.group(1).replace(",", "."))
            except Exception:
                pass

        cobertura_match = re.search(r"(?:[ÍI]ndice\s*de\s*Cobertura(?:\s*do\s*FFO)?|Cobertura(?:\s*do\s*FFO)?)[^\d]*(\d+[\.,]\d+)\s*(%?)", text, re.IGNORECASE)
        if cobertura_match:
            try:
                val = float(cobertura_match.group(1).replace(",", "."))
                is_pct = cobertura_match.group(2) == "%" or val > 5.0
                result["dre_caixa"]["cobertura_ffo"] = round(val / 100.0, 2) if is_pct else round(val, 2)
            except Exception:
                pass

        # NOI Caixa
        noi_match = re.search(r"(?:NOI\s*Caixa|NOI\s*Operacional)[^\d]*R?\$?\s*(\d+[\.,]\d+)\s*(?:mi|milh[õo]es|bi)?", text, re.IGNORECASE)
        if noi_match:
            try:
                result["dre_caixa"]["noi_caixa"] = float(noi_match.group(1).replace(",", "."))
            except Exception:
                pass

        # 4. Alavancagem e CRIs
        alav_match = re.search(r"(?:Alavancagem|Passivo\s*(?:Oneroso)?\s*/\s*PL)[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if alav_match:
            try:
                result["estrutura_capital"]["alavancagem_pl_pct"] = float(alav_match.group(1).replace(",", "."))
            except Exception:
                pass

        ltv_match = re.search(r"(?:LTV|D[íi]vida\s*/\s*Ativo)[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if ltv_match:
            try:
                result["estrutura_capital"]["ltv_pct"] = float(ltv_match.group(1).replace(",", "."))
            except Exception:
                pass

        # 5. Indexadores (IPCA vs IGP-M)
        ipca_match = re.search(r"IPCA[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        igpm_match = re.search(r"IGP-?M[^\d]*(\d+[\.,]\d+)%", text, re.IGNORECASE)
        if ipca_match:
            try:
                result["indexadores"]["IPCA"] = float(ipca_match.group(1).replace(",", "."))
            except Exception:
                pass
        if igpm_match:
            try:
                result["indexadores"]["IGP-M"] = float(igpm_match.group(1).replace(",", "."))
            except Exception:
                pass

        return result

    @classmethod
    def save_to_cache(cls, ticker: str, data: Dict[str, Any]) -> None:
        """Salva os dados extraídos em cache JSON estruturado."""
        cache_file = GERENCIAL_CACHE_DIR / f"{ticker.upper()}_gerencial.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados gerenciais salvos em cache: {cache_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar cache gerencial para {ticker}: {e}")

    @classmethod
    def get_cached_data(cls, ticker: str) -> Optional[Dict[str, Any]]:
        """Lê os dados extraídos previamente do cache se disponíveis."""
        cache_file = GERENCIAL_CACHE_DIR / f"{ticker.upper()}_gerencial.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao ler cache gerencial para {ticker}: {e}")
        return None
