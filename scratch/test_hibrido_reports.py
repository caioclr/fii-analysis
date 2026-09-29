import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.report_generator import ReportGenerator

hibridos = ["HGRU11", "ALZR11", "TGAR11", "RBVA11", "VGHF11"]

print("="*60)
print("TESTANDO GERAÇÃO DE RELATÓRIOS EXECUTIVOS PARA HÍBRIDOS (HIBRIDO)")
print("="*60)

all_ok = True
for ticker in hibridos:
    try:
        res = ReportGenerator.generate_html_report(ticker)
        html_path = Path(res["html_path"])
        size_kb = html_path.stat().st_size / 1024
        print(f"[{ticker}] SUCESSO! Arquivo: {html_path.name} ({size_kb:.1f} KB) - Score: {res.get('score')} - Veredicto: {res.get('veredicto')}")
        
        # Validação de integridade estrutural do HTML
        content = html_path.read_text(encoding="utf-8")
        assert "Fundos Híbridos e Renda Urbana Mista" in content, f"{ticker}: Faltando segmento oficial"
        assert "conic-gradient" in content, f"{ticker}: Faltando conic-gradient Pure CSS"
        assert "@media print" in content, f"{ticker}: Faltando @media print"
        assert "Portfólio de Imóveis & Principais Locatários" in content or "Portfólio de Imóveis" in content, f"{ticker}: Faltando tabela de ativos"
        print(f"       -> Asserções de integridade estrutural validadas com sucesso!")
    except Exception as e:
        print(f"[{ticker}] ERRO: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False

if all_ok:
    print("\nTODOS OS 5 RELATÓRIOS DE FUNDOS HÍBRIDOS GERADOS E VALIDADOS COM ÊXITO!")
    sys.exit(0)
else:
    print("\nHOUVE FALHAS NA GERAÇÃO.")
    sys.exit(1)
