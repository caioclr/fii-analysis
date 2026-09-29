import sys
import os
import re

with open('data/reports/BTCI11_auditoria.html', 'r', encoding='utf-8') as f:
    c = f.read()

print('1. Fund Name:', re.search(r'fund-name">(.*?)</', c).group(1))
print('2. BTG Pactual mentioned:', c.count('BTG Pactual'))
print('3. DRE rows found:', len(re.findall(r'Receitas de Juros|Resultado Operacional|Rendimento Declarado', c)))
print('4. Indexadores found:', len(re.findall(r'Atrelado ao IPCA|Atrelado ao CDI', c)))
print('5. Top devedores found:', len(re.findall(r'Beach Park|Direcional|BRK Ambiental|Vitacon', c)))
print('6. Green Flags found:', len(re.findall(r'Taxa m.*?dia excepcional|Desconto patrimonial expressivo|Super.*?vit operacional', c)))
print('7. Red Flags found:', len(re.findall(r'Concentra.*?o em IPCA|Exposi.*?o a cr.*?dito', c)))
print('8. Teto in HTML:', re.search(r'teto-val">(.*?)</', c).group(1))
print('9. Total length of HTML:', len(c))
