import re
from src.services.report_generator import ReportGenerator

res = ReportGenerator.generate_html_report('VILG11')
with open(res['html_path'], 'r', encoding='utf-8') as f:
    html = f.read()

m = re.findall(r'ADTV \(Mês\)</div>\s*<div class="kpi-value">([^<]+)</div>', html)
print("ADTV card encontrado no HTML:", m)
m_sub = re.findall(r'ADTV \(Mês\)</div>\s*<div class="kpi-value">[^<]+</div>\s*<div class="kpi-sub">([^<]+)</div>', html)
print("ADTV sub encontrado no HTML:", m_sub)
