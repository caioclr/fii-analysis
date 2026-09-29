# 📊 Analisys - Plataforma de Inteligência e Auditoria Fundamentalista de FIIs & Investimentos

Plataforma institucional de alta performance para auditoria fundamentalista, valuation rigoroso (sem Bazin), comparação setorial e gestão inteligente de ativos na B3, com foco central em **Fundos Imobiliários (FIIs)**, **Fiagros**, **Ações** e **Asset Allocation com Aportes Inteligentes**.

O sistema opera com uma **Arquitetura Dual Stack**:
1. **Frontend Moderno (SPA):** Desenvolvido em **React 18 + TypeScript + Vite + Tailwind CSS** (Dark Mode corporativo).
2. **Backend de Alta Performance:** API REST construída em **Python + FastAPI**, com validação cruzada regulatória e cache SQLite.
3. **Dashboard Legado:** Interface interativa em **Streamlit** preservada para consultas rápidas e prototipagem local.

---

## 🚀 Como Executar

### 1. Inicialização Completa da Plataforma Moderna (FastAPI + React SPA)

#### Passo A: Iniciar o Backend (FastAPI)
Abra um terminal no diretório raiz do projeto:
```powershell
# Ativar o ambiente virtual e iniciar a API FastAPI
.\venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
* **API REST:** `http://127.0.0.1:8000`
* **Documentação Interativa Swagger:** `http://127.0.0.1:8000/docs`

#### Passo B: Iniciar o Frontend (React + Vite)
Abra outro terminal na pasta `frontend/`:
```powershell
cd frontend
npm install
npm run dev
```
* **Aplicação Web SPA:** **`http://127.0.0.1:5533`**

---

### 2. Inicialização do Dashboard Legado (Streamlit)

Caso deseje utilizar o painel legado em Streamlit:
```powershell
.\run.bat
# Ou manualmente:
.\venv\Scripts\streamlit.exe run app.py
```
* **Streamlit UI:** `http://localhost:8501`

---

## 🎯 Módulos e Funcionalidades Principais

### 1. 🔍 Screener Quantitativo & Instantâneo (396 Ativos B3)
* **Catálogo Universal:** Cobertura de 396 FIIs e Fiagros listados na B3.
* **Abas Rápidas por Segmento:** Filtros imediatos com contagem em tempo real para Logística, Papel (CRIs), Shoppings, Lajes Corporativas, Fundos de Fundos (FOFs), Híbridos e Fiagros / Agro.
* **Filtros Paramétricos Avançados:** P/VP máximo, DY 12M mínimo, liquidez média diária (ADTV) mínima e vacância física máxima.
* **Ordenação Instantânea:** Ordenação no cliente por múltiplos, dividendos, volume e scores, com paginação fluida.

### 2. 📑 Dossiê Executivo & Auditoria Regulatória
Dossiê institucional completo sem dados genéricos ou tabelas vazias, estruturado em 5 abas integradas:
* **Header Oficial:** Ticker, razão social, CNPJ, gestor, administrador, base de cotistas, PL contábil, cotação atual, preço-teto institucional, margem de segurança e **Score de Qualidade unificado (0,0 a 10,0)**.
* **8 KPIs Analíticos:** P/VP com indicação de desconto/ágio s/ VPC, DY anualizado, Liquidez diária (ADTV), DY mensal, Vacância física, Vacância financeira, Alavancagem onerosa sobre PL e Score.
* **DRE Gerencial Linha a Linha:** FFO/cota, índice de cobertura percentual e demonstrativo contábil com mês anterior, mês atual, variação % e impacto em R$/cota.
* **Distribuição de dividendos e projeção de resultados:** Posicionado logo após a DRE, exibe 4 KPI cards em destaque (*Dividendo Recorrente*, *Saldo de Reserva* com meses de autonomia, *Não Recorrente Legal* sob o Art. 10 da Lei 8.668/93 e *Dividendo Estimado Guidance*) + gráfico interativo ECharts em barras empilhadas com média dos últimos 12 meses e seletor de visualização (*Últimos 12M*, *Projeção Futura* e *Visão Integrada*).
* **Portfólio de Ativos & Propriedades:** Lista de galpões, shoppings, lajes corporativas, ativos de crédito ou portfólio de fazendas agrícolas rurais (AGRO) com localização, tipologia, garantias reais e vencimentos.
* **Raio-X da carteira: culturas, estratégia e indexadores:** Gráficos duplos de rosca em Pure CSS (`conic-gradient`) com miolo temático setorial (`CADEIA/AGRO`, `TAXA/INDEX`, `ABL/PRÓPRIA`, `ATIVO/TOTAL`, `CRIs/SUBORD`) e legendas com percentuais auditados.
* **Concentração de Inquilinos & Tomadores de Crédito:** Maiores parceiros locatários e grupos produtores rurais, participação na receita, modelo de contrato (SLB/BTL/Atípico) e rating.
* **Indexadores dos Contratos:** Distribuição de indexadores com barras dinâmicas para IPCA, IGP-M, CDI/DI e Outros/Pré.
* **Estrutura de capital, securitizações e alavancagem financeira:** 4 KPI cards em destaque (*Saldo Devedor de CRIs*, *Alavancagem Financeira Bruta* com trava <25%, *Dívida/Ativo Total LTV* com Ativo Total consolidado e *Caixa Livre & Liquidez Imediata*) + tabela com ativos vinculados, custo médio ponderado e cronogramas de amortização.
* **Semáforo de Riscos & Parecer Conclusivo:** Green Flags, Red Flags com destaques tipográficos em negrito e Parecer do Analista com alocação recomendada e diretrizes de execução.
* **Simulador de Valuation:** Ferramenta interativa de sensibilidade macroeconômica recalculando o Preço-Teto em tempo real via Spread NTN-B, Gordon DCF e Balanço Patrimonial.
* **Gráficos B3 TradingView:** Candlesticks diários/semanais com médias móveis, volume de negociação e histórico real de proventos pagos.
* **HTML Clássico:** Visualizador dos relatórios oficiais compilados com suporte a impressão em PDF corporativo (`@media print` / `Ctrl + P`).

### 3. ⚔️ Comparador Setorial Multi-Métrica & Radiografia Visual
* **Pódio 5 Selos de Liderança:** *Melhor Oportunidade de Preço*, *Maior Retorno Real Líquido (IPCA+)*, *Mais Seguro & Conservador*, *Campeão de Reserva & Extraordinário* e *Líder Geral do Setor*.
* **Radar Multidimensional Normalizado 5D:** Comparação entre até 4 ativos em Desconto, Retorno Real, Solvência, Qualidade Operacional e Reserva.
* **Matriz de Dispersão 2x2 Valuation vs Qualidade:** Eixo X (P/VP) vs Eixo Y (Score Técnico 0 a 10), com quadrantes de Oportunidade, Qualidade com Ágio, Armadilha e Evitar.
* **Matriz Comparativa de Pares:** Tabela com indicadores completos e trajetória operacional mês a mês (`▲ Melhorando`, `— Estável`, `▼ Piorando`).

### 4. 📈 Análise de Ações, Asset Allocation & Aportes Inteligentes
* **Controle de Carteira de Ações:** Posições acionárias na B3, dividendos/JCP e exposição setorial.
* **Metas de Alocação (Asset Allocation):** Diagnóstico automático de desvios (*Underweight* / *Overweight*).
* **Calculadora de Aporte Inteligente:** Algoritmo que calcula a distribuição de novos aportes para reequilibrar a carteira **sem necessidade de giro ou venda de posições**.

---

## 📁 Estrutura do Repositório

```
analisys/
├── frontend/                         # Interface Web Moderna (React 18 + Vite SPA)
│   ├── src/
│   │   ├── api/client.ts             # Cliente Axios tipado para consumo da API FastAPI
│   │   ├── components/               # Header, Sidebar retrátil, Dossiês, Gráficos TradingView
│   │   ├── types/index.ts            # Schemas e interfaces TypeScript completas
│   │   └── views/                    # Screener, Dossiê Detalhado, Comparador e Parâmetros
│   ├── package.json
│   └── vite.config.ts
│
├── src/
│   ├── api/                          # Camada Backend REST API (FastAPI)
│   │   ├── main.py                   # Ponto de entrada FastAPI, CORS e rotas
│   │   └── routes_fii.py             # Endpoints /screener, /details, /market-series, /comparator
│   ├── services/                     # Motores Analíticos de Negócio
│   │   ├── cross_validation_service.py # Reconciliação contábil CVM vs BolsaAI
│   │   ├── bolsai_service.py         # Integração com API BolsaAI (MCP)
│   │   ├── fundos_net_service.py     # Parser de informes mensais CVM / Fundos.NET
│   │   ├── market_data.py            # Coleta de cotações B3 e séries de mercado
│   │   ├── fii_analyzer.py           # Análise quantitativa de FIIs e Número Mágico
│   │   ├── fii_comparator_service.py # Pódio 5 Selos, Radar e Matriz de Pares
│   │   ├── valuation_pricing_service.py # Precificação por Spread NTN-B, DCF e Retorno Real
│   │   ├── dividend_projection_service.py # FFO, cobertura, reservas e Lei 8.668/93
│   │   ├── trend_analysis_service.py # Diagnóstico de trajetória operacional MoM
│   │   ├── report_generator.py       # Orquestrador multi-segmento de relatórios
│   │   └── *_report_renderer.py      # Renderizadores especializados (Agro, Logística, Shoppings, etc.)
│   ├── database/                     # Persistência SQLite local (portfolio.db)
│   └── config.py                     # Configurações globais e taxonomia setorial
│
├── docs/                             # Documentação Técnica e Arquitetural
│   ├── README.md                     # Índice geral da documentação
│   ├── 01_visao_funcional.md         # Módulos funcionais e especificações de tela
│   ├── 02_fluxos_de_informacao.md    # Pipelines de dados, integração e caching
│   ├── 03_setores_e_metricas.md      # Metodologia por segmento e limites prudenciais
│   ├── 04_guia_de_uso.md             # Manual operacional do usuário
│   └── 05_governanca_e_validacao_de_dados.md # Governança contábil, reconciliações e testes
│
├── tests/                            # Bateria de Testes Automatizada
│   └── test_data_validation.py       # Validação de cotações B3, ADTV, laudos e regras de dados
│
├── data/                             # Armazenamento local SQLite e caches
│   └── portfolio.db
│
├── app.py                            # Dashboard legado em Streamlit
├── requirements.txt                  # Dependências Python
└── README.md                         # Documento principal
```

---

## 🧪 Baterias de Testes e Validação

### 1. Testes de Dados e Backend (Python)
Para validar a reconciliação oficial CVM vs. BolsaAI, apuração de ADTV e integridade dos dossiês:
```powershell
.\venv\Scripts\python.exe -m unittest tests/test_data_validation.py -v
```

### 2. Validação e Compilação do Frontend (TypeScript / Vite)
Para verificar a consistência estrita de tipos TypeScript e o bundle de produção:
```powershell
cd frontend
npm run build
```

---

## 📖 Documentação Detalhada

Para aprofundar nas regras de cálculo, fórmulas matemáticas, governança e manuais de uso, consulte a pasta [`docs/`](docs/README.md).
