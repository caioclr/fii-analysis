# ⚛️ Analisys Frontend - Single Page Application (SPA)

Interface web moderna, reativa e de alta performance desenvolvida em **React 18**, **TypeScript**, **Vite** e **Tailwind CSS**, consumindo a API REST oficial do backend em FastAPI.

---

## 🚀 Como Executar

### Pré-requisitos
* Node.js 18+ instalado
* Backend FastAPI em execução na porta `8000` (`http://127.0.0.1:8000`)

### Modo Desenvolvimento
```bash
# Na pasta frontend/:
npm install
npm run dev
```
Acesse o sistema em: **`http://127.0.0.1:5533`**

### Build de Produção
```bash
npm run build
```
Executa a checagem estrita de tipos TypeScript (`tsc -b`) e compilação otimizada com Vite gerando os bundles finais na pasta `dist/`.

---

## 📁 Estrutura de Diretórios

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts             # Cliente Axios com métodos fortemente tipados para a API FastAPI
│   ├── components/
│   │   ├── charts/
│   │   │   └── TradingViewChart.tsx # Gráfico interativo estilo TradingView (Candlesticks, volume e médias)
│   │   ├── fii/
│   │   │   ├── DossierSections.tsx  # Componentes modulares do Dossiê Executivo (DRE, Ativos, Donuts, etc.)
│   │   │   ├── DossierDividendProjectionSection.tsx # Card de histórico 12M e projeção semestral de dividendos
│   │   │   └── ValuationSimulator.tsx # Simulador interativo com sensibilidade macroeconômica
│   │   └── layout/
│   │       ├── Header.tsx        # Topbar com breadcrumbs, indicadores macro e exportação para PDF
│   │       ├── Sidebar.tsx       # Barra lateral retrátil com busca instantânea por atalho de ticker
│   │       └── TopTabs.tsx       # Abas de navegação do Dossiê
│   ├── types/
│   │   └── index.ts              # Schemas e interfaces TypeScript para 100% dos dados da plataforma
│   ├── views/
│   │   ├── FiiScreenerView.tsx    # Screener quantitativo instantâneo de 396 FIIs e Fiagros da B3
│   │   ├── FiiDetailsView.tsx     # Raio-X completo, Dossiê Executivo, Valuation e Gráficos B3
│   │   ├── FiiSectorComparatorView.tsx # Pódio 5 Selos, Radar 5D, Scatter 2x2 e Matriz de Pares
│   │   └── SettingsView.tsx      # Calibração de parâmetros macroeconômicos (NTN-B, IPCA, Spreads)
│   ├── App.tsx                   # Roteador de estado global e layout mestre
│   ├── main.tsx                  # Ponto de entrada da aplicação
│   └── index.css                 # Estilos globais Tailwind, classes dark mode e regras de impressão
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🎯 Principais Visões da Interface

### 1. 🔍 Screener & Busca Instantânea (`FiiScreenerView`)
- Catálogo quantitativo completo com **396 FIIs e Fiagros listados na B3**.
- Abas instantâneas por segmento: *Todos*, *Logística*, *Papel (CRIs)*, *Shoppings*, *Lajes Corp.*, *Fundos de Fundos (FOFs)*, *Híbridos* e *Fiagros / Agro*.
- Filtros quantitativos em tempo real: P/VP máximo, Dividend Yield 12M mínimo, liquidez diária (ADTV) mínima e vacância física máxima.
- Ordenação instantânea no cliente por qualquer coluna com paginação dinâmica.

### 2. 📑 Dossiê Executivo & Valuation (`FiiDetailsView`)
Organizado em 5 abas integradas:
* **Dossiê Executivo:**
  - Header oficial com Score de Qualidade unificado (0 a 10), veredito institucional e 8 KPIs analíticos.
  - Metadados cadastrais e regulatórios oficiais (CVM / Fundos.NET).
  - *Demonstrativo de Resultados do Exercício (DRE Gerencial):* FFO/cota, cobertura percentual e tabela de rubricas contábeis mês a mês.
  - *Distribuição de dividendos e projeção de resultados:* 4 KPI cards em destaque (*Dividendo Recorrente*, *Saldo de Reserva* com meses de autonomia, *Não Recorrente Legal da Lei 8.668/93* e *Guidance Estimado*) + Gráfico ECharts de barras empilhadas com média dos últimos 12 meses e seletor com 3 modos de visualização (*Últimos 12M*, *Projeção Futura* e *Visão Integrada*).
  - *Portfólio de Propriedades e Imóveis Físicos:* Relação de ativos (galpões, shoppings, lajes, recebíveis de CRIs ou fazendas rurais em Fiagros).
  - *Raio-X da carteira: culturas, estratégia e indexadores:* Visualização com gráficos de rosca em Pure CSS (`conic-gradient`) com miolos dinâmicos e legendas com percentuais auditados.
  - *Concentração de Inquilinos e Risco de Crédito dos Locatários:* Principais parceiros locatários ou grupos produtores rurais parceiros.
  - *Indexadores dos Contratos e Proteção Inflacionária:* Barras de distribuição para IPCA, IGP-M, CDI/DI e Outros/Pré.
  - *Estrutura de capital, securitizações e alavancagem financeira:* 4 KPIs (Saldo Devedor de CRIs, Alavancagem Passivo/PL com trava <25%, LTV contábil com Ativo Total consolidado e Caixa Livre) + tabela detalhada de securitizações com custos e cronogramas.
  - *Semáforo de Flags e Auditoria de Riscos:* Green Flags e Red Flags com destaques tipográficos em negrito + Parecer Institucional com Preço-Teto e Alocação sugerida.
* **Simulador de Valuation:** Ajuste fino interativo de taxa da NTN-B, IPCA e Spreads, recalculando o Preço-Teto e Margem de Segurança instantaneamente.
* **Gráficos B3 & Volume:** Candlestick chart interativo com médias móveis, volume diário e histórico de rendimentos mensais distribuídos.
* **Pares & Setor:** Redirecionamento rápido para o comparador setorial com o ativo em foco.
* **HTML Clássico:** Visualizador do relatório original compilado com suporte nativo a impressão em PDF executivo (`Ctrl + P`).

### 3. ⚔️ Comparador Setorial (`FiiSectorComparatorView`)
- Pódio com 5 Selos de Liderança Setorial.
- Radar Multidimensional Normalizado 5D (Desconto, Retorno Real, Solvência, Qualidade Operacional e Reserva).
- Gráfico de Dispersão 2x2 Valuation vs Qualidade (P/VP vs Score).
- Matriz Analítica Completa com trajetória MoM (`▲`, `—`, `▼`).

### 4. ⚙️ Parâmetros Macroeconômicos (`SettingsView`)
- Calibração das taxas de referência da NTN-B 2035, inflação projetada (IPCA) e spreads reais exigidos por segmento imobiliário.
