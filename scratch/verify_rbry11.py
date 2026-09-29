import sys
import re
from src.services.report_generator import ReportGenerator

def test_rbry11():
    res = ReportGenerator.generate_html_report('RBRY11')
    print("Report Data Dict:")
    for k in ['ticker', 'pvp', 'dy_anual', 'cotistas', 'pl']:
        print(f"  {k}: {res.get(k)}")

    with open(res['html_path'], 'r', encoding='utf-8') as f:
        html = f.read()

    # Find Price
    matches_price = re.findall(r'<div class="kpi-title">Cotação Atual</div>\s*<div class="kpi-value">([^<]+)</div>', html)
    matches_vpc = re.findall(r'VPC Contábil:\s*([^<]+)</div>', html)
    matches_pvp = re.findall(r'<div class="kpi-title">P/VP &[^<]*</div>\s*<div class="kpi-value[^"]*">([^<]+)</div>', html)
    
    print("\nExtracted from HTML:")
    print("  Preço de Mercado:", matches_price)
    print("  VPC Contábil:", matches_vpc)
    print("  P/VP:", matches_pvp)

if __name__ == '__main__':
    test_rbry11()
