# 04. Guia Prático de Operação e Uso

Este manual orienta o analista ou investidor em todas as rotinas operacionais do **Analisys**, desde a inicialização do ambiente até a emissão de dossiês executivos e exportação em PDF.

---

## 🚀 1. Inicialização do Sistema

### Opção A: Plataforma Moderna (FastAPI + React 18 SPA) — **Recomendada**

A arquitetura moderna opera com serviços desacoplados em dois terminais:

#### 1. Iniciar o Backend (FastAPI)
Abra o PowerShell na pasta raiz do projeto:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Status:** O backend iniciará na porta `8000`.
* **Swagger Docs:** Acesse `http://127.0.0.1:8000/docs` para inspecionar os endpoints e schemas.

#### 2. Iniciar o Frontend (Vite / React)
Abra um segundo terminal na pasta `frontend/`:
```powershell
cd frontend
npm run dev
```
* **Acesso:** Abra seu navegador em **`http://127.0.0.1:5533`**.

---

### Opção B: Dashboard Legado (Streamlit)
Caso deseje utilizar a interface legada em Streamlit:
```powershell
.\run.bat
# Ou manualmente:
.\venv\Scripts\streamlit.exe run app.py
```
* **Acesso:** Acesse pelo navegador em `http://localhost:8501`.

---

## 🔍 2. Como Utilizar o Screener Universal de FIIs e Fiagros

1. No menu lateral esquerdo, clique em **🔍 Screener & Busca**.
2. **Navegação por Abas Setoriais:**
   * Clique nos botões de segmento (*Todos os FIIs*, *Logística*, *Papel*, *Shoppings*, *Lajes*, *FOFs*, *Híbridos* ou *Fiagros*) para filtrar instantaneamente a listagem.
3. **Filtros Quantitativos:**
   * Clique em **Filtros Quantitativos** para abrir os seletores de:
     * *P/VP Máximo:* ex: filtrar fundos com P/VP $\le 0,95$.
     * *Dividend Yield Mínimo:* ex: buscar ativos com DY 12M $\ge 10,0\%$.
     * *Liquidez Diária Mínima:* ex: ativos com mais de R$ 1 milhão/dia de ADTV.
     * *Vacância Física Máxima:* ex: filtrar fundos com vacância $\le 5,0\%$.
4. **Ordenação Instantânea:**
   * Clique nos cabeçalhos da tabela (*P/VP*, *DY 12M*, *ADTV*, *Vacância*, *Score*) para alternar entre ordenação ascendente e descendente.
5. **Acesso ao Dossiê:**
   * Clique em qualquer linha de fundo para abrir instantaneamente o Dossiê Executivo detalhado daquele ativo.

---

## 📑 3. Como Explorar o Dossiê Executivo & Valuation

Na tela de **Dossiê & Valuation**, utilize as abas superiores:

### Aba 1: Dossiê Executivo
* **Leitura Sequencial do Laudo:**
  1. *Header Oficial:* Verifique a cotação B3 frente ao Preço-Teto institucional e a margem de segurança.
  2. *8 KPIs Analíticos:* Analise múltiplos e taxas de vacância.
  3. *DRE Gerencial:* Observe o FFO/cota e o índice de cobertura percentual mês a mês.
  4. *Distribuição de dividendos e projeção de resultados:* Avalie os 4 KPI cards em destaque (dividendo recorrente atual, saldo de reserva com autonomia em meses, estimativa de não recorrente obrigatório sob a Lei 8.668/93 e guidance regular para os próximos meses). Interaja com o gráfico ECharts alternando entre os modos *Últimos 12M* (com linha média pontilhada), *Projeção Futura (6M)* (com destaque para o salto extraordinário semestral) e *Visão Integrada*.
  5. *Portfólio de Propriedades:* Examine a lista de galpões, shoppings ou fazendas agrícolas rurais (AGRO) com colunas de ABL, garantias reais e vencimentos.
  6. *Raio-X da carteira: culturas, estratégia e indexadores:* Observe os gráficos duplos de rosca (Pure CSS Conic-Gradient) posicionados logo após o portfólio de ativos, inspecionando o miolo temático setorial e os percentuais de distribuição.
  7. *Concentração de Inquilinos:* Identifique os maiores tomadores de crédito ou locatários.
  8. *Indexadores de Contratos:* Veja o grau de blindagem inflacionária (IPCA vs CDI vs IGP-M).
  9. *Estrutura de capital, securitizações e alavancagem financeira:* Avalie os 4 KPI cards de endividamento (saldo devedor de CRIs, alavancagem passivo/PL com trava de 25%, LTV contábil e caixa de tesouraria) e a tabela de securitizações com custos e cronogramas.
  10. *Semáforo de Flags & Parecer Conclusivo:* Leia as Green Flags, Red Flags e a recomendação de alocação sugerida na carteira.

### Aba 2: Simulador de Valuation
* Ajuste os controles deslizantes da **NTN-B 2035**, **IPCA Projetado** e **Spread Real**.
* O sistema recalculará na hora o Preço-Teto Recomendado e a nova Margem de Segurança, detalhando o resultado pelos métodos de Spread NTN-B, Gordon DCF e Balanço Patrimonial.

### Aba 3: Gráficos B3 TradingView
* Selecione o período gráfico desejado (`1M`, `3M`, `6M`, `1A` ou `5A`).
* Analise o padrão de velas (candlesticks), médias móveis e volume financeiro.
* Confira a grade inferior com os rendimentos mensais distribuídos por cota ao longo do último ano.

### Aba 4: Pares & Setor
* Redirecionamento instantâneo para o Comparador Setorial trazendo o segmento em análise pré-selecionado.

### Aba 5: HTML Clássico & Impressão em PDF
* Clique no botão **Exportar / Imprimir** no topo superior direito da aplicação (ou aperte `Ctrl + P`).
* A folha de estilo de impressão (`@media print`) formatará automaticamente o laudo corporativo com fundo branco de alto contraste, sem barra lateral, pronto para ser salvo como arquivo PDF executivo.

---

## ⚔️ 4. Como Utilizar o Comparador Setorial de FIIs

1. Acesse **⚔️ Comparador Setorial** pelo menu lateral.
2. Selecione o segmento desejado (ex: *Logística e Renda Urbana*, *Shopping Centers*, *Fiagros*, etc.).
3. **Pódio de 5 Selos:** Verifique os ativos que conquistaram as premiações analíticas de *Melhor Oportunidade de Preço*, *Maior Retorno Real Líquido*, *Mais Seguro & Conservador*, *Campeão de Reserva* e *Líder Geral do Setor*.
4. **Radar 5D:** Compare até 4 fundos selecionados de forma visual.
5. **Matriz de Dispersão 2x2:** Identifique os ativos posicionados no quadrante de *Oportunidade Clara* (baixo P/VP e alto Score de Qualidade).
6. **Tabela de Pares:** Inspecione as métricas de cada concorrente e confira a trajetória operacional mês a mês (`▲`, `—`, `▼`).

---

## ⚙️ 5. Como Calibrar os Parâmetros Macroeconômicos

1. Acesse **⚙️ Parâmetros Macro** no menu lateral.
2. Ajuste a taxa de juros real da **NTN-B 2035** (padrão: 6,50% a.a.).
3. Ajuste a expectativa de inflação **IPCA** para o horizonte de 12 meses (padrão: 4,00% a.a.).
4. Ajuste os **Spreads Reais Mínimos Exigidos** por setor imobiliário.
5. Clique em **Salvar Parâmetros** para persistir as alterações no banco SQLite local. Todos os preços-teto da plataforma serão atualizados em tempo real.
