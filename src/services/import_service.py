import io
import pandas as pd
from typing import List, Dict, Any, Tuple
from src.database.repository import PortfolioRepository
from src.services.fii_analyzer import FII_DEFAULT_SEGMENTS

# ETFs conhecidos que terminam com 11 mas não são FIIs
KNOWN_ETFS = {"BOVA11", "SMAL11", "IVVB11", "HASH11", "BBOV11", "SPXI11", "XINA11", "GOLD11", "NASD11"}

class ImportService:
    @staticmethod
    def infer_asset_type(ticker: str) -> str:
        """Infere se o ticker é FII, Ação ou Outro."""
        ticker = ticker.upper().strip()
        if ticker in KNOWN_ETFS:
            return "OUTRO"
        if ticker in FII_DEFAULT_SEGMENTS:
            return "FII"
        if ticker.endswith("11"):
            return "FII"
        if any(ticker.endswith(digit) for digit in ["3", "4", "5", "6"]):
            return "ACAO"
        return "OUTRO"

    @classmethod
    def parse_file(cls, file_bytes: bytes, filename: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Lê arquivo CSV ou Excel e extrai posições de investimentos.
        Retorna (lista_de_ativos, lista_de_erros_ou_avisos).
        """
        errors = []
        try:
            if filename.lower().endswith(".csv"):
                # Tenta diferentes delimitadores e encodings comuns no Brasil
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), sep=";", encoding="utf-8")
                    if len(df.columns) <= 1:
                        df = pd.read_csv(io.BytesIO(file_bytes), sep=",", encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(file_bytes), sep=";", encoding="latin1")
                    if len(df.columns) <= 1:
                        df = pd.read_csv(io.BytesIO(file_bytes), sep=",", encoding="latin1")
            else:
                df = pd.read_excel(io.BytesIO(file_bytes))
        except Exception as e:
            return [], [f"Erro ao abrir o arquivo: {str(e)}"]

        # Normaliza nomes de colunas
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Mapeamento flexível de colunas
        ticker_col = None
        qty_col = None
        price_col = None
        type_col = None
        segment_col = None

        for col in df.columns:
            if any(term in col for term in ["código de negociação", "código", "codigo", "ticker", "papel", "ativo"]):
                if not ticker_col:
                    ticker_col = col
            if any(term in col for term in ["quantidade", "qtd", "qtde", "posição", "posicao"]):
                if not qty_col:
                    qty_col = col
            if any(term in col for term in ["preço médio", "preco medio", "preço medio", "custo médio", "preço", "preco"]):
                if not price_col:
                    price_col = col
            if any(term in col for term in ["tipo de ativo", "tipo", "classe"]):
                if not type_col:
                    type_col = col
            if any(term in col for term in ["segmento", "setor"]):
                if not segment_col:
                    segment_col = col

        if not ticker_col:
            return [], ["Não foi possível identificar a coluna de Ticker/Código do Ativo na planilha."]

        records = []
        for idx, row in df.iterrows():
            raw_ticker = str(row[ticker_col]).strip().upper()
            if not raw_ticker or raw_ticker == "NAN" or len(raw_ticker) < 4:
                continue

            # Extrai quantidade
            qty = 0.0
            if qty_col and pd.notna(row[qty_col]):
                try:
                    qty_val = str(row[qty_col]).replace(".", "").replace(",", ".")
                    qty = float(qty_val)
                except ValueError:
                    qty = 0.0

            # Extrai preço médio
            avg_price = 0.0
            if price_col and pd.notna(row[price_col]):
                try:
                    price_val = str(row[price_col]).replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                    avg_price = float(price_val)
                except ValueError:
                    avg_price = 0.0

            # Tipo de ativo
            asset_type = None
            if type_col and pd.notna(row[type_col]):
                val = str(row[type_col]).upper().strip()
                if "FII" in val or "IMOBILI" in val:
                    asset_type = "FII"
                elif "AÇÃO" in val or "ACAO" in val or "ACOES" in val:
                    asset_type = "ACAO"

            if not asset_type:
                asset_type = cls.infer_asset_type(raw_ticker)

            # Segmento
            segment = None
            if segment_col and pd.notna(row[segment_col]):
                segment = str(row[segment_col]).strip()
            elif asset_type == "FII":
                segment = FII_DEFAULT_SEGMENTS.get(raw_ticker, "Outros")

            if qty > 0:
                records.append({
                    "ticker": raw_ticker,
                    "asset_type": asset_type,
                    "quantity": qty,
                    "average_price": avg_price,
                    "segment": segment,
                    "target_percent": 0.0,
                    "notes": "Importado via planilha"
                })

        if not records:
            return [], ["Nenhuma posição válida encontrada no arquivo fornecido."]

        return records, errors

    @classmethod
    def import_to_database(cls, records: List[Dict[str, Any]]) -> int:
        """Salva a lista de ativos no banco de dados SQLite."""
        count = 0
        for item in records:
            PortfolioRepository.upsert_asset(
                ticker=item["ticker"],
                asset_type=item["asset_type"],
                quantity=item["quantity"],
                average_price=item["average_price"],
                target_percent=item.get("target_percent", 0.0),
                segment=item.get("segment"),
                notes=item.get("notes", "")
            )
            count += 1
        return count

    @staticmethod
    def get_template_df() -> pd.DataFrame:
        """Gera DataFrame de exemplo para download de template."""
        return pd.DataFrame([
            {"Ticker": "HGLG11", "Quantidade": 50, "Preco_Medio": 162.50, "Tipo": "FII", "Segmento": "Logística / Galpões"},
            {"Ticker": "XPML11", "Quantidade": 80, "Preco_Medio": 105.20, "Tipo": "FII", "Segmento": "Shoppings"},
            {"Ticker": "KNCR11", "Quantidade": 100, "Preco_Medio": 101.40, "Tipo": "FII", "Segmento": "Papel / CRI"},
            {"Ticker": "MXRF11", "Quantidade": 250, "Preco_Medio": 10.35, "Tipo": "FII", "Segmento": "Papel / Híbrido"},
            {"Ticker": "ITUB4",  "Quantidade": 100, "Preco_Medio": 32.80, "Tipo": "ACAO", "Segmento": "Financeiro / Bancos"},
            {"Ticker": "VALE3",  "Quantidade": 40,  "Preco_Medio": 64.20, "Tipo": "ACAO", "Segmento": "Materiais Básicos"},
            {"Ticker": "WEGE3",  "Quantidade": 60,  "Preco_Medio": 38.50, "Tipo": "ACAO", "Segmento": "Bens Industriais"}
        ])
