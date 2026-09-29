import pandas as pd
from src.services.fii_comparator_service import FIIComparatorService

def test_comparator():
    res = FIIComparatorService.compare_sector("PAPEL", ["RBRY11", "BTCI11", "KNCR11", "KNSC11"])
    df = res["df"]
    print(df[["ticker", "preco_mercado", "vpc", "pvp", "dy_anual", "provento_mes", "real_yield_pct"]])

if __name__ == '__main__':
    test_comparator()
