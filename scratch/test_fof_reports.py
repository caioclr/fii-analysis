import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.report_generator import ReportGenerator

fofs = ["HFOF11", "BCFF11", "RBRF11", "KFOF11", "CXCI11"]

print("="*60)
print("TESTANDO GERAÇÃO DE RELATÓRIOS EXECUTIVOS PARA FOFS")
print("="*60)

all_ok = True
for ticker in fofs:
    try:
        res = ReportGenerator.generate_html_report(ticker)
        html_path = Path(res["html_path"])
        size_kb = html_path.stat().st_size / 1024
        print(f"[{ticker}] SUCESSO! Arquivo: {html_path.name} ({size_kb:.1f} KB) - Score: {res.get('score')} - Veredicto: {res.get('veredicto')}")
        
        # Validação básica de integridade do HTML
        content = html_path.read_text(encoding="utf-8")
        assert "Duplo Desconto Real Composto" in content, f"{ticker}: Faltando Duplo Desconto"
        assert "conic-gradient" in content, f"{ticker}: Faltando conic-gradient Pure CSS"
        assert "@media print" in content, f"{ticker}: Faltando @media print"
        assert "Top 5 FIIs em Custódia" in content or "Top Ativos em Custódia" in content or "Top FIIs Investidos" in content, f"{ticker}: Faltando tabela de ativos"
        print(f"       -> Asserções de integridade estrutural validadas com sucesso!")
    except Exception as e:
        print(f"[{ticker}] ERRO: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False

if all_ok:
    print("\nTODOS OS 5 RELATÓRIOS DE FOFS GERADOS E VALIDADOS COM ÊXITO!")
    sys.exit(0)
else:
    print("\nHOUVE FALHAS NA GERAÇÃO.")
    sys.exit(1)
