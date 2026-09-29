# 🛡️ 05. Governança de Dados, Reconciliação e Bateria de Testes

Este documento estabelece as diretrizes institucionais de **Governança de Dados, Validação Cruzada, Reconciliação Contábil vs. Mercado e Bateria de Testes Automatizada** da plataforma **Analisys**.

---

## 1. Princípios Fundamentais de Governança

A integridade dos laudos de valuation e dossiês executivos depende da separação e conciliação estrita de grandezas analíticas. No mercado de Fundos de Investimento Imobiliário (FIIs) e Fiagros da B3, três distorções graves costumam afetar plataformas despreparadas:

1. **Confusão entre Preço de Mercado e Valor Patrimonial da Cota (VPC):** Tratar o valor contábil do informe da CVM como se fosse a cotação do pregão em bolsa de valores, mascarando ágios ou deságios de negociação.
2. **Inconsistência de Múltiplos em APIs Externas:** Provedores de mercado que calculam P/VP com bases de dados desatualizadas (como o caso do `GARE11`, onde APIs externas reportavam P/VP anômalo de 0,08 ao confundir cotas ou centavos, quando o valor correto oficial é 0,82 apurado via CVM).
3. **Escalas de Pontuação Desalinhadas:** Exibir notas em escalas diferentes (ex: alguns indicadores até 10 e outros até 100), confundindo a percepção de risco do investidor.
4. **Degradação de Interface por Falta de Dados Setoriais:** Erros de carregamento ao analisar classes distintas de ativos (ex: Fiagros, fundos de papel ou FOFs que não possuem galpão físico tradicional, causando falhas silenciosas de código).

O Analisys adota uma **Arquitetura de Dados em Camadas Blindadas**, garantindo que nenhum relatório seja emitido com inconsistências ou campos corrompidos.

---

## 2. Topologia das Fontes e Hierarquia de Prioridades

O pipeline do Analisys consome 4 camadas integradas de dados:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MATRIZ DE DADOS DO ANALISYS                       │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ Camada               │ Fonte Primária       │ Grandezas / Responsabilidade  │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 1. Regulatória Oficial│ CVM / Fundos.NET     │ • Valor Patrimonial da Cota   │
│                      │                      │ • Patrimônio Líquido (PL)     │
│                      │                      │ • Ativo Total & Alavancagem   │
│                      │                      │ • Número Oficial de Cotistas  │
│                      │                      │ • Contabilidade & Balancete   │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 2. Mercado B3 ao Vivo│ Yahoo Finance B3     │ • Cotação Atual de Tela       │
│                      │ & brapi.dev          │ • Último Fechamento           │
│                      │                      │ • ADTV (Média Móvel 30 Dias)  │
│                      │                      │ • Histórico de Pregão e DY    │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 3. Inteligência B3   │ BolsaAI API          │ • DY TTM vs. DY Recorrente    │
│                      │                      │ • Composição Operacional      │
│                      │                      │ • Vacância Física/Financeira  │
│                      │                      │ • Top Inquilinos / Imóveis    │
│                      │                      │ • Variáveis Macro (CDI, IPCA) │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 4. Gerencial & DRE   │ Relatórios em PDF    │ • DRE Caixa / FFO por cota    │
│                      │ (PyMuPDF Extractor)  │ • SSS, SSR, WAULT, LTV        │
│                      │                      │ • Vencimentos e Indexadores   │
│                      │                      │ • Colchão de Lucros Acumulados│
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

### Regras Estritas de Conciliação
* **Preço de Tela (`current_price`):** Yahoo Finance (`yfinance` com sufixo `.SA`) com fallback via `brapi.dev` ou cotação ao vivo BolsaAI. O valor contábil (`vpc`) **nunca** é atribuído como preço de tela.
* **Patrimônio e P/VP:** O valor patrimonial (`vpc`) tem prioridade absoluta da base oficial CVM/Fundos.NET. O P/VP é recalculado dinamicamente via $\frac{\text{Preço de Mercado}}{\text{VPC CVM}}$.
* **Resolução do Caso GARE11:** Quando a API externa retornar P/VP discrepante do cálculo CVM em mais de 15%, o motor de validação cruzada substitui o dado pelo quociente auditado oficial ($\text{Preço de Mercado} / \text{VPC}$).
* **Padronização dos Scores em Escala 0 a 10:** Todas as métricas de pontuação técnica, vereditos e notas de qualidade operam unificadas na escala de **0,0 a 10,0** (eliminando escalas até 100).
* **Blindagem de Renderizadores com `hasattr()`:** Todas as rotas da API executam verificações defensivas de métodos nos 7 renderizadores setoriais (`AgroReportRenderer`, `LajesReportRenderer`, `FofReportRenderer`, `HibridoReportRenderer`, `LogisticaReportRenderer`, `ShoppingReportRenderer`, `PapelReportRenderer`), impedindo quebras de execução em fundos atípicos (como Fiagros de terras).
* **Conciliação e Segregação de Dividendos (BolsaAI + yfinance):** A série histórica de 12 meses agrupa pagamentos mensais e segrega automaticamente o provento recorrente do provento não recorrente/extraordinário. A projeção futura modela o salto compulsório semestral estipulado pelo Art. 10 da **Lei nº 8.668/1993** (mínimo de 95% do lucro apurado em regime de caixa).

---

## 3. Bateria de Testes Automatizada

A plataforma dispõe de duas suites de testes automatizados para assegurar a confiabilidade do sistema:

### Suite 1: Testes de Dados e Reconciliação Contábil (Python / Unittest)
Arquivo: [`tests/test_data_validation.py`](file:///c:/Users/caioc/projetos/analisys/tests/test_data_validation.py)

Validações executadas:
1. **Consistência de Cotações da B3:** Garante que nenhum FII tenha cotação zerada ou nula e que o preço de fechamento represente o pregão real.
2. **Cálculo e Liquidez do ADTV:** Verifica se o cálculo da média móvel de volume financeiro diário de 30 dias está íntegro em R$ Milhões.
3. **Reconciliação Contábil CVM vs. Mercado:** Testa a conciliação do P/VP e proventos para fundos de múltiplos setores (Logística, Papel, Shoppings e Agro).
4. **Integridade de Dossiês HTML:** Garante que os laudos contenham todas as seções obrigatórias sem tags corrompidas ou tabelas vazias.

**Como executar:**
```powershell
.\venv\Scripts\python.exe -m unittest tests/test_data_validation.py -v
```

---

### Suite 2: Testes Visuais e E2E de Interface (Playwright)
Executa simulação de navegação real em navegadores Chromium/Edge headless:
1. **Navegação do Screener:** Busca instantânea por ticker e filtros setoriais.
2. **Carregamento de Dossiês Especializados:** Valida o dossiê de Fiagros (`RZTR11`) e fundos de tijolo (`BTLG11`), verificando DRE, novo card de **Distribuição de dividendos e projeção de resultados** (posicionado imediatamente após a DRE com 4 KPIs e alternância de abas 12M/Projeção/Integrada), Portfólio de Ativos, **Raio-X da carteira (donuts pure CSS)** posicionado após o portfólio de propriedades e **Estrutura de capital e securitizações**.
3. **Ausência de Erros no Console:** Monitoramento contínuo de exceções de JavaScript/React (`page.on('pageerror')`) e erros de renderização (`console.error`), garantindo zero erros de execução.

---

## 4. Matriz de Auditoria Contábil de Referência

Abaixo, a tabela de auditoria cruzada homologada para os principais fundos de referência da plataforma:

| Ticker | Segmento Oficial | Cotação B3 | VPC Oficial CVM | P/VP Auditado | DY 12M | Alavancagem (PL) | LTV Contábil | Score (0-10) | Veredito |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BTLG11** | Logística e Renda Urbana | R$ 98,20 | R$ 103,40 | **0,95** | 9,45% | 11,20% | 9,80% | **8,9** | Aprovado |
| **HGLG11** | Logística e Renda Urbana | R$ 162,50 | R$ 158,20 | **1,03** | 8,80% | 5,40% | 4,90% | **8,8** | Aprovado |
| **XPML11** | Shopping Centers | R$ 108,40 | R$ 114,80 | **0,94** | 9,15% | 14,80% | 12,50% | **8,8** | Aprovado |
| **VISC11** | Shopping Centers | R$ 115,20 | R$ 126,50 | **0,91** | 9,30% | 18,20% | 15,10% | **8,5** | Aprovado |
| **KNCR11** | Recebíveis Imobiliários (CRIs) | R$ 102,80 | R$ 101,50 | **1,01** | 12,40% | 0,00% | 0,00% | **9,1** | Aprovado |
| **MXRF11** | Recebíveis Imobiliários (CRIs) | R$ 10,25 | R$ 9,95 | **1,03** | 12,20% | 0,00% | 0,00% | **8,2** | Aprovado |
| **RZTR11** | Fiagros & Terras Agrícolas | R$ 88,50 | R$ 97,20 | **0,91** | 12,80% | 4,20% | 10,00% | **8,9** | Aprovado |
| **GARE11** | Logística e Renda Urbana | R$ 9,10 | R$ 11,10 | **0,82** | 11,50% | 18,50% | 15,40% | **8,2** | Aprovado |
| **HGRE11** | Lajes Corporativas | R$ 118,50 | R$ 148,00 | **0,80** | 8,20% | 8,10% | 7,20% | **8,0** | Neutro |
| **HFOF11** | Fundos de Fundos (FOFs) | R$ 74,20 | R$ 85,30 | **0,87** | 10,10% | 0,00% | 0,00% | **8,7** | Aprovado |
