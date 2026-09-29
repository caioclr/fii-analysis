import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.report_generator import ReportGenerator

agros = ["RZTR11", "VGIA11", "KNCA11", "RURA11", "FGAA11"]

print("="*60)
print("TESTANDO GERAÇÃO DE RELATÓRIOS EXECUTIVOS PARA FIAGROS (AGRO)")
print("="*60)

all_ok = True
for ticker in agros:
    try:
        res = ReportGenerator.generate_html_report(ticker)
        html_path = Path(res["html_path"])
        size_kb = html_path.stat().st_size / 1024
        print(f"[{ticker}] SUCESSO! Arquivo: {html_path.name} ({size_kb:.1f} KB) - Score: {res.get('score')} - Veredicto: {res.get('veredicto')}")
        
        # Validação de integridade estrutural do HTML
        content = html_path.read_text(encoding="utf-8")
        assert "LTV Rural Médio" in content or "LTV Rural" in content, f"{ticker}: Faltando LTV Rural"
        assert "conic-gradient" in content, f"{ticker}: Faltando conic-gradient Pure CSS"
        assert "@media print" in content, f"{ticker}: Faltando @media print"
        assert "Top Operações de Crédito & Fazendas em Garantia" in content, f"{ticker}: Faltando tabela de ativos"
        print(f"       -> Asserções de integridade estrutural validadas com sucesso!")
    except Exception as e:
        print(f"[{ticker}] ERRO: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False

if all_ok:
    print("\nTODOS OS 5 RELATÓRIOS DE FIAGROS GERADOS E VALIDADOS COM ÊXITO!")
    sys.exit(0)
else:
    print("\nHOUVE FALHAS NA GERAÇÃO.")
    sys.exit(1)
