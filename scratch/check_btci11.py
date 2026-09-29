import sys
import os
sys.path.insert(0, os.path.abspath("."))
import re
from src.services.report_generator import ReportGenerator, FII_KNOWLEDGE_BASE
from src.services.papel_report_renderer import PAPEL_KNOWLEDGE_BASE
from src.services.cross_validation_service import KNOWN_SEGMENTS, CrossValidationService

print("Is BTCI11 in KNOWN_SEGMENTS:", "BTCI11" in KNOWN_SEGMENTS)
print("Is BTCI11 in FII_KNOWLEDGE_BASE:", "BTCI11" in FII_KNOWLEDGE_BASE)
print("Is BTCI11 in PAPEL_KNOWLEDGE_BASE:", "BTCI11" in PAPEL_KNOWLEDGE_BASE)

res = ReportGenerator.generate_html_report('BTCI11')
print("Keys in result:", res.keys())
print("Result details:")
for k, v in res.items():
    if k != 'html_content':
        print(f"  {k}: {v}")

with open('data/reports/BTCI11_auditoria.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Check for placeholder '-' or None
dashes = html.count('>-<')
print(f"Number of '>-<' in HTML: {dashes}")

# Print sections 1, 2, 3, 4, 5
for line in html.split('\n'):
    if any(keyword in line for keyword in ['kpi-value', 'kpi-sub', 'metric-box-val', 'section-title', 'fund-name', 'header-meta']):
        print(line.strip()[:120])
