import sys
sys.path.insert(0, ".")
import difflib
from pathlib import Path
from typing import Dict, Any, Optional, List

USER_FILE = Path(r"C:\Users\caioc\.gemini\antigravity\brain\bf1569ac-8813-46c8-b6df-a8962ee9991f\.user_uploaded\media_1790360662359.html")
user_html = USER_FILE.read_text(encoding="utf-8")

def fmt_br(val: Any, decimals: int = 2, prefix: str = "", suffix: str = "", force_sign: bool = False) -> str:
    if val is None or val == "":
        return "-"
    try:
        val_f = float(val)
    except (ValueError, TypeError):
        return str(val)
    
    if force_sign:
        sign = "+" if val_f > 0 else ("-" if val_f < 0 else "")
        abs_val = abs(val_f)
        formatted = f"{abs_val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{prefix}{sign}{formatted}{suffix}"
    else:
        if val_f < 0:
            formatted = f"{abs(val_f):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"-{prefix}{formatted}{suffix}"
        else:
            formatted = f"{val_f:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{prefix}{formatted}{suffix}"

def build_conic_gradient(items: List[Any]) -> str:
    if not items:
        return "background: #334155;"
    acc = 0.0
    slices = []
    total_items = len(items)
    for i, item in enumerate(items):
        pct = float(item[1])
        cor = str(item[2])
        start_str = "0%" if i == 0 else f"{acc:.1f}%"
        end_val = min(acc + pct, 100.0)
        end_str = "100%" if i == total_items - 1 else f"{end_val:.1f}%"
        slices.append(f"{cor} {start_str} {end_str}")
        acc = end_val
    joined = ",\n        ".join(slices)
    return f"background: conic-gradient(\n        {joined}\n      );"

from src.services.shopping_report_renderer import SHOPPING_KNOWLEDGE_BASE

kb = SHOPPING_KNOWLEDGE_BASE["HSML11"].copy()

# Add specific fields for HSML11 to match user example
kb["veredicto_badge_header"] = "Aprovado c/ Ressalva"
kb["veredicto_badge_s7"] = "APROVADO COM RESSALVA"
kb["col_ant_header"] = "Julho/2026 (R$ mi)"
kb["col_atual_header"] = "Agosto/2026 (R$ mi)"
kb["col_cota_header"] = "Agosto/2026 (R$/cota)"
kb["dre"]["ffo_sub"] = "Geração operacional orgânica (R$ 13,65 mi)"
kb["dre"]["cobertura_sub"] = "Déficit operacional de R$ 0,11/cota coberto"
kb["saldo_cris_sub"] = "Após amortização extraordinária de R$ 28,6 mi"
kb["alav_sub"] = "Alerta: Acima da trava de 25,00% do protocolo"
kb["alav_grid_sub"] = "Alerta: >25% (R$ 582,0 mi CRIs)"
kb["ltv_sub"] = "Ativo Total: R$ 2,75 Bilhões"
kb["caixa_sub"] = "5,82% do Patrimônio Líquido"
kb["cris"] = [
    ("CRI Shopping Paralela", "Shopping Paralela (Salvador/BA)", "42,0%", "IPCA + 6,80% a.a.", "Amortizações mensais com vencimento final em 2036.", "kpi-highlight-blue"),
    ("CRI SuperShopping Osasco", "SuperShopping (Osasco/SP)", "31,0%", "CDI + 2,10% a.a.", "Amortizações semestrais com vencimento final em 2035.", "kpi-highlight-amber"),
    ("CRI Shopping Granja Vianna", "Granja Vianna (Cotia/SP)", "27,0%", "CDI + 2,70% a.a.", "Alvo prioritário de pré-pagamentos com a reciclagem de ativos (vencimento 2037).", "kpi-highlight-amber")
]
kb["parecer"]["fonte_secundaria"] = "BTG Pactual Content Research & Informes Estruturados"
kb["parecer"]["fonte_secundaria_link"] = "https://content.btgpactual.com/research/ativo/HSML11"

# Generate complete HTML
ticker = "HSML11"
fund_name = kb["fund_name"]
gestora = kb["gestora"]
administrador = kb["administrador"]
data_base = kb["data_base"]
data_protocolo = kb["data_protocolo"]
score_html = f'{kb["score"]:.1f}<span style="font-size: 1rem; color: var(--text-muted); font-weight: 500;">/10</span>'
veredicto_badge_header = kb["veredicto_badge_header"]

pvp_str = fmt_br(kb["pvp"], 2)
preco_mercado_str = fmt_br(kb["preco_mercado"], 2, prefix="R$ ")
vpc_str = fmt_br(kb["vpc"], 2, prefix="R$ ")
dy_anual_str = fmt_br(kb["dy_anual"], 2, suffix="%")
dy_mes_str = fmt_br(kb["dy_mes_pct"], 2, suffix="%")
provento_mes_str = fmt_br(kb["provento_mes"], 2, prefix="R$ ")
vac_fis_str = fmt_br(kb["vacancia_fisica"], 1, suffix="%")
ocup_media_str = fmt_br(kb["ocupacao_media"], 1, suffix="%")
contratos_tipicos_str = fmt_br(kb["contratos_tipicos_pct"], 1, suffix="%")
contratos_desc = kb["contratos_tipo_desc"]
alav_pct_str = fmt_br(kb["alavancagem_pl"], 2, suffix="%")
alav_grid_sub = kb["alav_grid_sub"]
cotistas_str = fmt_br(kb["cotistas"], 0)
cotistas_desc = kb["cotistas_desc"]
adtv_str = fmt_br(kb["adtv_milhoes"], 2, prefix="R$ ", suffix=" mi")
adtv_sub = kb["adtv_ltm_desc"]
pl_str = fmt_br(kb["pl_bi"], 2, prefix="R$ ", suffix=" bi")
cotas_desc = kb["cotas_emitidas_desc"]

# DRE
dre_info = kb["dre"]
noi_val = fmt_br(dre_info["noi_caixa_mi"], 2, prefix="R$ ", suffix=" mi")
desp_fin_val = fmt_br(dre_info["desp_fin_mi"], 2, prefix="R$ ", suffix=" mi")
ffo_cota_val = fmt_br(dre_info["ffo_cota"], 2, prefix="R$ ")
ffo_sub = dre_info["ffo_sub"]
cobertura_val = f'{fmt_br(dre_info["cobertura_ffo"], 2)} ({fmt_br(dre_info["cobertura_pct"], 1, suffix="%")})'
cobertura_sub = dre_info["cobertura_sub"]
col_ant_h = kb["col_ant_header"]
col_atual_h = kb["col_atual_header"]
col_cota_h = kb["col_cota_header"]

dre_rows_html = ""
for i, row in enumerate(dre_info.get("linhas", [])):
    if i == 5:
        tr_tag = '<tr style="font-weight: 700; background-color: rgba(255,255,255,0.03);">'
    elif i == 7:
        tr_tag = '<tr style="font-weight: 700;">'
    elif row.get("is_bold"):
        tr_tag = '<tr style="font-weight: 700;">'
    else:
        tr_tag = '<tr>'
    
    var_class = f' {row["var_class"]}' if row.get("var_class") else ''
    if row.get("var_dash"):
        var_str = "-"
    else:
        var_val = row.get("var_pct", 0.0)
        var_str = fmt_br(var_val, 2, suffix="%", force_sign=True) if var_val != 0 else "0,00%"
    
    cota_val = row.get("cota", 0.0)
    decimals_cota = 2 if abs(cota_val) >= 0.05 or cota_val == 0 else 3
    cota_str = fmt_br(cota_val, decimals_cota, prefix="R$ ")

    dre_rows_html += f"""          {tr_tag}
            <td>{row.get("rubrica")}</td>
            <td class="text-right">{fmt_br(row.get("mes_ant", 0.0), 2)}</td>
            <td class="text-right">{fmt_br(row.get("mes_atual", 0.0), 2)}</td>
            <td class="text-right{var_class}">{var_str}</td>
            <td class="text-right">{cota_str}</td>
          </tr>
"""
dre_rows_html = dre_rows_html.rstrip("\n")

# Donuts
abl_info = kb["distribuicao_abl"]
abl_estados = abl_info["estados"]
donut_abl_style = build_conic_gradient(abl_estados)
abl_total_str = abl_info["total_str"]
donut_abl_legends = ""
for est_nome, est_pct, est_cor in abl_estados:
    donut_abl_legends += f"""          <li class="legend-item">
            <span><span class="legend-color" style="background: {est_cor};"></span>{est_nome}</span>
            <strong>{fmt_br(est_pct, 1, suffix="%")}</strong>
          </li>
"""
donut_abl_legends = donut_abl_legends.rstrip("\n")

ativo_info = kb["composicao_ativo"]
ativo_itens = ativo_info["itens"]
donut_pl_style = build_conic_gradient(ativo_itens)
ativo_total_str = ativo_info["total_str"]
donut_pl_legends = ""
for at_nome, at_pct, at_cor in ativo_itens:
    donut_pl_legends += f"""          <li class="legend-item">
            <span><span class="legend-color" style="background: {at_cor};"></span>{at_nome}</span>
            <strong>{fmt_br(at_pct, 1, suffix="%")}</strong>
          </li>
"""
donut_pl_legends = donut_pl_legends.rstrip("\n")

# Shoppings table
shoppings_rows_html = ""
for s in kb.get("shoppings", []):
    shoppings_rows_html += f"""          <tr>
            <td><strong>{s[0]}</strong></td>
            <td>{s[1]}</td>
            <td class="text-center">{s[2]}</td>
            <td class="text-right">{s[3]}</td>
            <td class="text-right">{s[4]}</td>
            <td class="text-center"><span class="badge-tag {s[6]}">{s[5]}</span></td>
            <td>{s[7]}</td>
          </tr>
"""
tot_s = kb.get("total_portfolio")
if tot_s:
    shoppings_rows_html += f"""          <tr style="font-weight: 700; background-color: rgba(255,255,255,0.03);">
            <td>{tot_s[0]}</td>
            <td>{tot_s[1]}</td>
            <td class="text-center">{tot_s[2]}</td>
            <td class="text-right">{tot_s[3]}</td>
            <td class="text-right">{tot_s[4]}</td>
            <td class="text-center"><span class="badge-tag {tot_s[6]}">{tot_s[5]}</span></td>
            <td>{tot_s[7]}</td>
          </tr>
"""
shoppings_rows_html = shoppings_rows_html.rstrip("\n")

# Ancoras table
ancoras_rows_html = ""
total_ancoras = len(kb.get("ancoras", []))
for i, a in enumerate(kb.get("ancoras", [])):
    h_class = " kpi-highlight-blue" if i < total_ancoras - 1 else ""
    ancoras_rows_html += f"""          <tr>
            <td><strong>{a[0]}</strong></td>
            <td>{a[1]}</td>
            <td class="text-center{h_class}">{a[2]}</td>
            <td class="text-center">{a[3]}</td>
            <td class="text-center"><span class="badge-tag {a[5]}">{a[4]}</span></td>
            <td>{a[6]}</td>
          </tr>
"""
ancoras_rows_html = ancoras_rows_html.rstrip("\n")

# Indexadores
idx = kb.get("indexadores", {"IPCA": 74.0, "IGP-M": 26.0})
ipca_str = fmt_br(idx.get("IPCA", 74.0), 1, suffix="%")
igpm_str = fmt_br(idx.get("IGP-M", 26.0), 1, suffix="%")

# Section 5
saldo_cris_str = fmt_br(kb["saldo_cris_mi"], 1, prefix="R$ ", suffix=" Milhões")
saldo_cris_sub = kb["saldo_cris_sub"]
alav_sub = kb["alav_sub"]
ltv_str = fmt_br(kb["ltv"], 2, suffix="%")
ltv_sub = kb["ltv_sub"]
caixa_str = fmt_br(kb["caixa_mi"], 2, prefix="R$ ", suffix=" mi")
caixa_sub = kb["caixa_sub"]

cris_rows_html = ""
for c in kb.get("cris", []):
    cris_rows_html += f"""          <tr>
            <td><strong>{c[0]}</strong></td>
            <td>{c[1]}</td>
            <td class="text-center {c[5]}">{c[2]}</td>
            <td class="text-center">{c[3]}</td>
            <td>{c[4]}</td>
          </tr>
"""
cris_rows_html = cris_rows_html.rstrip("\n")

green_flags_html = "\n".join([f"          <li>{f}</li>" for f in kb.get("green_flags", [])])
red_flags_html = "\n".join([f"          <li>{f}</li>" for f in kb.get("red_flags", [])])

parecer_info = kb["parecer"]
veredicto_badge_s7 = kb["veredicto_badge_s7"]
teto_str = fmt_br(kb["teto"], 2, prefix="R$ ")
conclusao_text = parecer_info["conclusao"]
justificativa_text = parecer_info["justificativa"]
diretriz_text = parecer_info["diretriz"]
fonte_primaria = parecer_info["fonte_primaria"]
fonte_link = parecer_info["fonte_link"]
fonte_sec_desc = parecer_info["fonte_secundaria"]
fonte_sec_link = parecer_info["fonte_secundaria_link"]
diagnostic_text = dre_info["diagnostico"]

assembled_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ticker} - Auditoria Documental e Diagnóstico Fundamentalista</title>
  <style>
    :root {{
      --bg-main: #0f172a;
      --bg-card: #1e293b;
      --bg-card-hover: #273549;
      --border: #334155;
      --border-accent: #475569;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-dim: rgba(56, 189, 248, 0.15);
      --success: #22c55e;
      --success-dim: rgba(34, 197, 94, 0.15);
      --warning: #f59e0b;
      --warning-dim: rgba(245, 158, 11, 0.15);
      --danger: #ef4444;
      --danger-dim: rgba(239, 68, 68, 0.15);
      --indigo: #818cf8;
      --purple: #a855f7;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      padding: 24px;
    }}

    .container {{
      max-width: 1240px;
      margin: 0 auto;
    }}

    /* HEADER */
    .header-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px 28px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
    }}

    .header-left {{
      flex: 1 1 500px;
    }}

    .ticker-badge {{
      display: inline-block;
      background: linear-gradient(135deg, #0284c7, #0369a1);
      color: #ffffff;
      font-size: 1.5rem;
      font-weight: 800;
      padding: 4px 14px;
      border-radius: 8px;
      letter-spacing: 0.5px;
      margin-right: 12px;
    }}

    .fund-name {{
      display: inline-block;
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-main);
      vertical-align: middle;
    }}

    .header-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-top: 12px;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .header-meta span strong {{
      color: var(--text-main);
    }}

    .audit-stamp {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background-color: var(--success-dim);
      border: 1px solid var(--success);
      color: var(--success);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .score-card {{
      background-color: #0b1329;
      border: 1px solid var(--border);
      padding: 14px 22px;
      border-radius: 10px;
      text-align: center;
      min-width: 140px;
    }}

    .score-label {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }}

    .score-value {{
      font-size: 2.1rem;
      font-weight: 800;
      color: var(--warning);
      line-height: 1.1;
      margin: 4px 0;
    }}

    .verdict-badge {{
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background-color: var(--warning-dim);
      color: var(--warning);
      border: 1px solid var(--warning);
      text-transform: uppercase;
    }}

    /* KPI GRID */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      transition: transform 0.15s ease;
    }}

    .kpi-title {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}

    .kpi-value {{
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.5px;
    }}

    .kpi-sub {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 4px;
    }}

    .kpi-highlight-green {{ color: var(--success); }}
    .kpi-highlight-blue {{ color: var(--primary); }}
    .kpi-highlight-amber {{ color: var(--warning); }}
    .kpi-highlight-red {{ color: var(--danger); }}

    /* SECTIONS */
    .section-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      border-left: 4px solid var(--primary);
      padding-left: 10px;
    }}

    .card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 24px;
    }}

    /* SUB-CARDS GRID */
    .metrics-subgrid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }}

    .metric-box {{
      background-color: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
    }}

    .metric-box-title {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .metric-box-val {{
      font-size: 1.2rem;
      font-weight: 700;
      margin-top: 4px;
    }}

    /* TABLES */
    .table-container {{
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 16px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }}

    th {{
      background-color: #0b1329;
      color: var(--text-muted);
      padding: 10px 14px;
      font-weight: 600;
      text-transform: uppercase;
      font-size: 0.72rem;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--border);
    }}

    td {{
      padding: 10px 14px;
      border-bottom: 1px solid #1e293b;
      color: var(--text-main);
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    tr:hover td {{
      background-color: rgba(255, 255, 255, 0.02);
    }}

    .text-right {{ text-align: right; }}
    .text-center {{ text-align: center; }}

    /* COVERAGE DIAGNOSTIC BOX */
    .diagnostic-box {{
      background-color: var(--warning-dim);
      border: 1px solid var(--warning);
      border-radius: 8px;
      padding: 14px 18px;
      font-size: 0.85rem;
      line-height: 1.5;
    }}

    .diagnostic-box strong {{
      color: var(--warning);
    }}

    /* CHARTS SECTION */
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }}

    .chart-panel {{
      background-color: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .chart-header {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 14px;
      text-align: center;
      text-transform: uppercase;
    }}

    .donut-container {{
      position: relative;
      width: 170px;
      height: 170px;
      margin: 10px 0 16px 0;
    }}

    /* CSS Pure Conic Gradient Donut Charts */
    .donut-abl {{
      width: 170px;
      height: 170px;
      border-radius: 50%;
      {donut_abl_style}
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .donut-pl {{
      width: 170px;
      height: 170px;
      border-radius: 50%;
      {donut_pl_style}
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .donut-hole {{
      width: 105px;
      height: 105px;
      border-radius: 50%;
      background-color: var(--bg-card);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }}

    .donut-hole-title {{
      font-size: 0.65rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .donut-hole-val {{
      font-size: 0.95rem;
      font-weight: 800;
      color: var(--text-main);
    }}

    .legend-list {{
      width: 100%;
      list-style: none;
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    .legend-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}

    .legend-color {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 2px;
      margin-right: 6px;
    }}

    /* TAGS */
    .badge-tag {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
    }}

    .tag-aaa {{ background-color: var(--success-dim); color: var(--success); border: 1px solid var(--success); }}
    .tag-aa {{ background-color: var(--primary-dim); color: var(--primary); border: 1px solid var(--primary); }}
    .tag-a {{ background-color: var(--warning-dim); color: var(--warning); border: 1px solid var(--warning); }}
    .tag-alert {{ background-color: var(--danger-dim); color: var(--danger); border: 1px solid var(--danger); }}

    /* MATRIX FLAGS */
    .matrix-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}

    .flag-card {{
      border-radius: 8px;
      padding: 16px 18px;
    }}

    .flag-card-green {{
      background-color: var(--success-dim);
      border: 1px solid rgba(34, 197, 94, 0.4);
    }}

    .flag-card-red {{
      background-color: var(--danger-dim);
      border: 1px solid rgba(239, 68, 68, 0.4);
    }}

    .flag-header {{
      font-size: 0.9rem;
      font-weight: 700;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .flag-header-green {{ color: var(--success); }}
    .flag-header-red {{ color: var(--danger); }}

    .flag-list {{
      list-style-type: none;
      font-size: 0.82rem;
      line-height: 1.5;
    }}

    .flag-list li {{
      margin-bottom: 8px;
      padding-left: 14px;
      position: relative;
    }}

    .flag-card-green li::before {{
      content: "✓";
      position: absolute;
      left: 0;
      color: var(--success);
      font-weight: 700;
    }}

    .flag-card-red li::before {{
      content: "✕";
      position: absolute;
      left: 0;
      color: var(--danger);
      font-weight: 700;
    }}

    /* VERDICT BOX */
    .verdict-box {{
      background: linear-gradient(145deg, #1e293b, #0f172a);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 22px;
    }}

    .verdict-summary-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 16px;
    }}

    .verdict-title {{
      font-size: 1.1rem;
      font-weight: 700;
    }}

    .teto-val {{
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--primary);
    }}

    .verdict-text {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.6;
    }}

    .verdict-text strong {{
      color: var(--text-main);
    }}

    .footer-stamp {{
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
      font-size: 0.72rem;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .footer-stamp a {{
      color: var(--primary);
      text-decoration: none;
    }}

    .footer-stamp a:hover {{
      text-decoration: underline;
    }}

    /* PRINT SPECIFIC STYLES */
    @media print {{
      body {{
        background-color: #ffffff !important;
        color: #0f172a !important;
        padding: 0;
        font-size: 9.5pt;
      }}

      .container {{
        max-width: 100%;
      }}

      .header-card, .card, .kpi-card, .metric-box, .chart-panel, .score-card, .verdict-box {{
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        box-shadow: none !important;
      }}

      .header-meta, .kpi-sub, .metric-box-title, .score-label, .chart-header, .legend-list, .verdict-text, .footer-stamp {{
        color: #475569 !important;
      }}

      .donut-hole {{
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: none !important;
      }}

      .donut-hole-val, .kpi-value, .metric-box-val, .fund-name, .section-title, .verdict-title {{
        color: #0f172a !important;
      }}

      .flag-card-green {{
        background-color: #f0fdf4 !important;
        border: 1px solid #86efac !important;
      }}

      .flag-card-red {{
        background-color: #fef2f2 !important;
        border: 1px solid #fca5a5 !important;
      }}

      .diagnostic-box {{
        background-color: #fffbeb !important;
        border: 1px solid #f59e0b !important;
      }}

      table th {{
        background-color: #f1f5f9 !important;
        color: #334155 !important;
        border-bottom: 1px solid #cbd5e1 !important;
      }}

      table td {{
        border-bottom: 1px solid #e2e8f0 !important;
        color: #0f172a !important;
      }}

      .avoid-break {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>

<div class="container">

  <!-- HEADER EXECUTIVO -->
  <header class="header-card avoid-break">
    <div class="header-left">
      <div>
        <span class="ticker-badge">{ticker}</span>
        <span class="fund-name">{fund_name}</span>
      </div>
      <div class="header-meta">
        <span><strong>Gestora:</strong> {gestora}</span>
        <span><strong>Administrador:</strong> {administrador}</span>
        <span><strong>Data-Base:</strong> {data_base}</span>
        <span><strong>Protocolo B3/Fundos.NET:</strong> {data_protocolo}</span>
        <span class="audit-stamp">Auditoria Independente</span>
      </div>
    </div>
    <div class="header-right">
      <div class="score-card">
        <div class="score-label">Score Técnico</div>
        <div class="score-value">{score_html}</div>
        <div class="verdict-badge">{veredicto_badge_header}</div>
      </div>
    </div>
  </header>

  <!-- PAINEL SUPERIOR: 8 CARDS DE KPIS -->
  <div class="kpi-grid avoid-break">
    <div class="kpi-card">
      <div class="kpi-title">P/VP</div>
      <div class="kpi-value kpi-highlight-green">{pvp_str}</div>
      <div class="kpi-sub">Mercado: {preco_mercado_str} | VPC: {vpc_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Dividend Yield</div>
      <div class="kpi-value kpi-highlight-blue">{dy_anual_str}</div>
      <div class="kpi-sub">{dy_mes_str} a.m. ({provento_mes_str}/cota)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Vacância Física</div>
      <div class="kpi-value kpi-highlight-green">{vac_fis_str}</div>
      <div class="kpi-sub">Ocupação Média: {ocup_media_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">% Contratos</div>
      <div class="kpi-value kpi-highlight-blue">{contratos_tipicos_str}</div>
      <div class="kpi-sub">{contratos_desc}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Alavancagem / PL</div>
      <div class="kpi-value kpi-highlight-amber">{alav_pct_str}</div>
      <div class="kpi-sub">{alav_grid_sub}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Cotistas</div>
      <div class="kpi-value">{cotistas_str}</div>
      <div class="kpi-sub">{cotistas_desc}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">ADTV (Mês)</div>
      <div class="kpi-value">{adtv_str}</div>
      <div class="kpi-sub">{adtv_sub}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Patrimônio Líquido</div>
      <div class="kpi-value">{pl_str}</div>
      <div class="kpi-sub">{cotas_desc}</div>
    </div>
  </div>

  <!-- SEÇÃO 1: DRE AUDITADA E SUSTENTABILIDADE -->
  <section class="card avoid-break">
    <h2 class="section-title">1. Demonstração de Resultados (DRE Auditada) & Sustentabilidade de Proventos</h2>

    <div class="metrics-subgrid">
      <div class="metric-box">
        <div class="metric-box-title">NOI Caixa Operacional Próprio</div>
        <div class="metric-box-val kpi-highlight-blue">{noi_val}</div>
        <div class="kpi-sub">Aluguéis mínimos, % sobre vendas e estacionamento</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Despesas Financeiras (Securitizações)</div>
        <div class="metric-box-val kpi-highlight-amber">{desp_fin_val}</div>
        <div class="kpi-sub">Encargos de juros e amortizações ordinárias</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">FFO Operacional Recorrente / Cota</div>
        <div class="metric-box-val kpi-highlight-amber">{ffo_cota_val}</div>
        <div class="kpi-sub">{ffo_sub}</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Índice de Cobertura do FFO Recorrente</div>
        <div class="metric-box-val kpi-highlight-amber">{cobertura_val}</div>
        <div class="kpi-sub">{cobertura_sub}</div>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Rubrica Financeira (Regime de Caixa)</th>
            <th class="text-right">{col_ant_h}</th>
            <th class="text-right">{col_atual_h}</th>
            <th class="text-right">Variação (%)</th>
            <th class="text-right">{col_cota_h}</th>
          </tr>
        </thead>
        <tbody>
{dre_rows_html}
        </tbody>
      </table>
    </div>

    <div class="diagnostic-box">
      <strong>Diagnóstico Auditorial de Cobertura:</strong> {diagnostic_text}
    </div>
  </section>

  <!-- SEÇÃO 2: PORTFÓLIO & COMPOSIÇÃO PATRIMONIAL -->
  <section class="card avoid-break">
    <h2 class="section-title">2. Alocação de Ativos e Segmentação do Portfólio</h2>
    
    <div class="charts-grid">
      <!-- Donut 1: ABL por Estado -->
      <div class="chart-panel">
        <div class="chart-header">Distribuição Geográfica (ABL Própria)</div>
        <div class="donut-container">
          <div class="donut-abl">
            <div class="donut-hole">
              <span class="donut-hole-title">ABL Própria</span>
              <span class="donut-hole-val">{abl_total_str}</span>
            </div>
          </div>
        </div>
        <ul class="legend-list">
{donut_abl_legends}
        </ul>
      </div>

      <!-- Donut 2: Composição do Ativo -->
      <div class="chart-panel">
        <div class="chart-header">Composição do Ativo Total</div>
        <div class="donut-container">
          <div class="donut-pl">
            <div class="donut-hole">
              <span class="donut-hole-title">Ativo Total</span>
              <span class="donut-hole-val">{ativo_total_str}</span>
            </div>
          </div>
        </div>
        <ul class="legend-list">
{donut_pl_legends}
        </ul>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 3: AUDITORIA TÉCNICA E GEOGRÁFICA -->
  <section class="card avoid-break">
    <h2 class="section-title">3. Engenharia, Localização Geográfica e Especificações dos Empreendimentos</h2>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Shopping Center / Ativo</th>
            <th>Cidade / UF</th>
            <th class="text-center">Participação</th>
            <th class="text-right">ABL Total (m²)</th>
            <th class="text-right">ABL Própria (m²)</th>
            <th class="text-center">Ocupação</th>
            <th>Características Construtivas & Urbanas</th>
          </tr>
        </thead>
        <tbody>
{shoppings_rows_html}
        </tbody>
      </table>
    </div>
  </section>

  <!-- SEÇÃO 4: INQUILINOS E RISCO DE CRÉDITO -->
  <section class="card avoid-break">
    <h2 class="section-title">4. Locatários, Risco de Crédito e Indexadores Contratuais</h2>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Lojista Âncora / Operador</th>
            <th>Segmento de Varejo</th>
            <th class="text-center">% Estimada do NOI</th>
            <th class="text-center">Tipo Contrato</th>
            <th class="text-center">Rating / Solvência</th>
            <th>Dinâmica de Repasse & Vendas</th>
          </tr>
        </thead>
        <tbody>
{ancoras_rows_html}
        </tbody>
      </table>
    </div>

    <!-- Indexadores Contratuais -->
    <div style="margin-top: 12px;">
      <h3 style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;">Indexadores de Reajuste dos Aluguéis Mínimos (Total: 100%)</h3>
      <div class="metrics-subgrid">
        <div class="metric-box">
          <div class="metric-box-title">IPCA (Inflação Oficial)</div>
          <div class="metric-box-val kpi-highlight-green">{ipca_str}</div>
          <div class="kpi-sub">Indexador predominante nas renovações recentes</div>
        </div>
        <div class="metric-box">
          <div class="metric-box-title">IGP-M</div>
          <div class="metric-box-val kpi-highlight-amber">{igpm_str}</div>
          <div class="kpi-sub">Contratos legados em transição gradual</div>
        </div>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 5: ENDIVIDAMENTO E ESTRUTURA DE CAPITAL -->
  <section class="card avoid-break">
    <h2 class="section-title">5. Estrutura de Capital, Securitizações e Alavancagem Financeira</h2>

    <div class="metrics-subgrid">
      <div class="metric-box">
        <div class="metric-box-title">Saldo Devedor de CRIs (Passivo Oneroso)</div>
        <div class="metric-box-val kpi-highlight-amber">{saldo_cris_str}</div>
        <div class="kpi-sub">{saldo_cris_sub}</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Alavancagem Financeira Bruta (Passivo / PL)</div>
        <div class="metric-box-val kpi-highlight-amber">{alav_pct_str}</div>
        <div class="kpi-sub">{alav_sub}</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Dívida / Ativo Total (LTV Contábil)</div>
        <div class="metric-box-val kpi-highlight-blue">{ltv_str}</div>
        <div class="kpi-sub">{ltv_sub}</div>
      </div>
      <div class="metric-box">
        <div class="metric-box-title">Caixa & Liquidez Imediata</div>
        <div class="metric-box-val kpi-highlight-green">{caixa_str}</div>
        <div class="kpi-sub">{caixa_sub}</div>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Operação / Securitização (CRI)</th>
            <th>Ativo Vinculado</th>
            <th class="text-center">% do Passivo</th>
            <th class="text-center">Custo Médio Ponderado</th>
            <th>Vencimento / Cronograma</th>
          </tr>
        </thead>
        <tbody>
{cris_rows_html}
        </tbody>
      </table>
    </div>
  </section>

  <!-- SEÇÃO 6: MATRIZ CRÍTICA (GREEN FLAGS & RED FLAGS) -->
  <section class="card avoid-break">
    <h2 class="section-title">6. Matriz Crítica de Riscos e Oportunidades</h2>

    <div class="matrix-grid">
      <!-- GREEN FLAGS -->
      <div class="flag-card flag-card-green">
        <div class="flag-header flag-header-green">
          <span>●</span> GREEN FLAGS (Pontos Fortes)
        </div>
        <ul class="flag-list">
{green_flags_html}
        </ul>
      </div>

      <!-- RED FLAGS -->
      <div class="flag-card flag-card-red">
        <div class="flag-header flag-header-red">
          <span>●</span> RED FLAGS (Pontos de Atenção)
        </div>
        <ul class="flag-list">
{red_flags_html}
        </ul>
      </div>
    </div>
  </section>

  <!-- SEÇÃO 7: VEREDITO E PARECER DE ALOCAÇÃO FUNDAMENTALISTA -->
  <section class="verdict-box avoid-break">
    <div class="verdict-summary-row">
      <div>
        <div class="verdict-title">7. Parecer Executivo de Auditoria & Recomendação Fundamentalista</div>
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Auditoria de Conformidade Regulatória e Financeira (v2.1 Pro)</div>
      </div>
      <div>
        <span class="verdict-badge" style="font-size: 0.9rem; padding: 6px 14px;">{veredicto_badge_s7}</span>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Preço-Teto de Segurança</div>
        <div class="teto-val">{teto_str}</div>
      </div>
    </div>

    <div class="verdict-text">
      <p style="margin-bottom: 10px;">
        <strong>Conclusão da Auditoria:</strong> {conclusao_text}
      </p>
      <p style="margin-bottom: 10px;">
        <strong>Justificativa da Ressalva Técnica:</strong> {justificativa_text}
      </p>
      <p style="margin-bottom: 10px;">
        <strong>Diretriz Prudencial de Alocação:</strong> {diretriz_text}
      </p>
    </div>

    <div class="footer-stamp">
      <span><strong>Fonte Primária:</strong> <a href="{fonte_link}" target="_blank" rel="noopener">{fonte_primaria}</a></span>
      <span><strong>Rastreabilidade Complementar:</strong> <a href="{fonte_sec_link}" target="_blank" rel="noopener">{fonte_sec_desc}</a></span>
      <span>Impressão: Ctrl + P (Otimizado via @media print)</span>
    </div>
  </section>

</div>

</body>
</html>"""

diff = list(difflib.unified_diff(
    user_html.splitlines(),
    assembled_html.splitlines(),
    fromfile="user_example",
    tofile="assembled",
    n=1
))
print("Diff lines between user_example and assembled:", len(diff))
if diff:
    print("\n".join(diff[:50]))
