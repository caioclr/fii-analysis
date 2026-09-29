# 01. Visão Funcional do Sistema

O **Analisys** é uma plataforma institucional de inteligência, auditoria documental e gestão de investimentos focada em Fundos Imobiliários (FIIs), Fiagros e Ações listados na B3.

Este documento detalha cada módulo funcional, telas da interface de usuário, componentes analíticos e regras de negócio da plataforma.

---

## 🖥️ Arquitetura de Interface

A plataforma é disponibilizada através de uma interface **Single Page Application (SPA)** de alta reatividade desenvolvida em **React 18 + TypeScript + Tailwind CSS**, conectada a uma API REST em **FastAPI**, com persistência local em SQLite e suporte ao dashboard complementar em Streamlit.

A interface moderna é dividida em **4 grandes visões de trabalho**:
1. **🔍 Screener & Busca Instantânea (396 FIIs e Fiagros)**
2. **📑 Dossiê Executivo & Valuation** (com 5 abas integradas)
3. **⚔️ Comparador Setorial de Pares** (Pódio 5 Selos, Radar 5D e Dispersão 2x2)
4. **⚙️ Parâmetros Macroeconômicos** (Calibração em tempo real de NTN-B, IPCA e Spreads)

---

## 1. 🔍 Screener & Busca Instantânea (`FiiScreenerView`)

### Objetivo
Permitir a triagem rápida de todo o universo negociável da B3 (**396 FIIs e Fiagros**), com respostas instantâneas no cliente e filtros por múltiplos, proventos e qualidade.

### Componentes Funcionais
1. **Barra de Busca e Ação Rápida:**
   * Campo de busca universal por código (ticker) ou razão social com busca por prefixo em tempo real.
   * Atalho de teclado rápido na barra lateral para digitar qualquer ticker e pressionar `Enter` para saltar direto ao Dossiê.
2. **Abas Setoriais com Contadores Vivos:**
   * *Todos os FIIs (396 ativos)*
   * *Logística e Renda Urbana*
   * *Papel (Recebíveis Imobiliários - CRIs)*
   * *Shopping Centers*
   * *Lajes Corporativas*
   * *Fundos de Fundos (FOFs)*
   * *Híbridos / Multiestratégia*
   * *Fiagros / Agro (Terras e CRAs)*
3. **Filtros Quantitativos Avançados:**
   * **P/VP Máximo:** Identificação de ativos com desconto sobre o valor patrimonial contábil oficial da CVM.
   * **Dividend Yield Anualizado Mínimo (% a.a.):** Filtro por taxa de retorno nominal.
   * **Liquidez Diária Mínima (ADTV em R$ mil):** Eliminação de ativos ilíquidos ou de difícil saída no pregão.
   * **Vacância Física Máxima (%):** Seleção de portfólios com alta taxa de ocupação.
4. **Tabela Analítica Reativa:**
   * Colunas: *Ticker*, *Segmento*, *Cotação Atual*, *VPC Oficial*, *P/VP*, *DY 12M*, *ADTV Médio*, *Vacância Física*, *Score de Qualidade (0 a 10)* e *Ações*.
   * Ordenação bidirecional por qualquer parâmetro e paginação rápida.

---

## 2. 📑 Dossiê Executivo & Valuation (`FiiDetailsView`)

O Dossiê Executivo oferece um raio-x profundo e auditado do fundo selecionado, organizado em **5 abas estruturadas**:

### Aba A: Dossiê Executivo (Relatório Completo)
Estruturado de forma lógica e sequencial:

1. **Header Institucional Oficial:**
   * Ticker em destaque, nome empresarial, gestora responsável, administrador fiduciário, base oficial de cotistas e Patrimônio Líquido (PL) consolidado.
   * Cartão de Cotação de Fechamento B3 vs. Preço-Teto Estimado institucional com Margem de Segurança percentual.
   * **Score de Qualidade Unificado:** Pontuação técnica rigorosa em escala uniforme de **0,0 a 10,0**, com selo de veredito institucional (*Aprovado*, *Neutro* ou *Atenção*).
2. **Grade de 8 KPIs Analíticos:**
   * *P/VP:* Relação com status automático de *Desconto s/ VPC* ou *Ágio s/ VPC*.
   * *DY 12M:* Rendimento anualizado dos últimos 12 meses.
   * *Liquidez Diária:* Volume médio diário negociado na B3 (ADTV em R$ mi).
   * *DY Mensal:* Rentabilidade pontual do último provento declarado.
   * *Vacância Física:* Percentual de ABL desocupada com alerta se $> 10\%$.
   * *Vacância Financeira:* Impacto financeiro de desocupação e carências.
   * *Alavancagem (PL):* Proporção de dívida securitizada frente ao PL contábil.
   * *Score Qualidade:* Nota técnica global do ativo.
3. **Metadados Cadastrais Regulatórios:**
   * Razão Social oficial CVM, CNPJ do fundo, quantidade de cotas emitidas e data-base do balancete contábil mais recente com data de protocolo no Fundos.NET.
4. **Demonstrativo de Resultados do Exercício (DRE Gerencial):**
   * Cobertura do FFO (Funds From Operations) em percentual e geração por cota em R$.
   * Diagnóstico auditorial de sustentabilidade do provento.
   * Tabela comparativa mês a mês: rubricas de receitas operacionais, juros/arrendamentos, correções inflacionárias, despesas de gestão/administração, despesas financeiras e resultado líquido distribuível aos cotistas.
5. **Distribuição de dividendos e projeção de resultados:**
   * Posicionado imediatamente após a Demonstração de Resultados (DRE Gerencial).
   * Título padronizado sem numeração e apenas com a primeira letra maiúscula (*Distribuição de dividendos e projeção de resultados*).
   * **4 KPI Cards em Destaque:**
     1. *Dividendo Recorrente:* Último provento declarado por cota, FFO operacional por cota, índice de cobertura percentual e badge de sustentabilidade (Superávit Operacional, Neutro ou Déficit).
     2. *Saldo de Reserva:* Lucros acumulados e retidos por cota (R$/cota), autonomia em meses de cobertura e badge de integridade do colchão (Colchão Confortável, Moderado ou Comprimido).
     3. *Não Recorrente Legal (Lei 8.668/93):* Estimativa de distribuição extraordinária obrigatória no fechamento do semestre (regra de 95% do lucro caixa), meses restantes até o encerramento e provento total de pico esperado.
     4. *Dividendo Estimado (Guidance):* Provento mensal projetado regular para os próximos meses e faixa de guidance (mínimo e máximo).
   * **Gráfico Interativo ECharts:**
     * Visualização em barras empilhadas segregando proventos recorrentes (azul) e proventos não recorrentes/extraordinários (âmbar).
     * Linha tracejada de referência com a média recorrente dos últimos 12 meses.
     * Seletor de visualização rápida: *Últimos 12M*, *Projeção Futura (6 Meses)* e *Visão Integrada (12M + Projeção)*.
   * **Banner de Regulamentação Legal:** Base normativa sob o Art. 10 da Lei nº 8.668/1993 e Resolução CVM nº 175.
6. **Portfólio de Propriedades e Imóveis Físicos:**
   * Lista completa de galpões, shopping centers, lajes corporativas, ativos de crédito ou fazendas rurais (para Fiagros).
   * Colunas detalhadas: Nome do Ativo, Localização / Polo Produtivo, ABL Total / Volume, ABL Própria, Participação na Carteira (%), Ocupação / Vencimento e Garantias Reais / Especificações técnicas.
7. **Raio-X da carteira: culturas, estratégia e indexadores:**
   * Posicionado imediatamente após a tabela de propriedades.
   * Título padronizado sem numeração e em caixa mista (*Raio-X da carteira: culturas, estratégia e indexadores* no Agro, *Raio-X da carteira: geografia e composição do ativo* em Logística/Shoppings, etc.).
   * Gráficos duplos de rosca (Pure CSS Conic-Gradient) de alta resolução, com miolos centrais temáticos (`CADEIA/AGRO`, `TAXA/INDEX`, `ABL/PRÓPRIA`, `ATIVO/TOTAL`) e legendas com os percentuais auditados.
8. **Concentração de Inquilinos e Risco de Crédito dos Locatários:**
   * Principais contrapartes locatárias ou grupos produtores parceiros, percentual de representatividade nas receitas, modalidade contratual (Atípico BTS/SLB ou Típico) e rating de crédito.
9. **Indexadores dos Contratos e Proteção Inflacionária:**
   * Barras de distribuição visual para proteção em IPCA, IGP-M, CDI/DI e Outros/Pré.
10. **Estrutura de capital, securitizações e alavancagem financeira:**
   * **4 KPI Cards em Destaque:**
     1. *Saldo Devedor de CRIs (Passivo Oneroso):* Volume total de dívida securitizada em R$ Milhões (âmbar).
     2. *Alavancagem Financeira Bruta (Passivo / PL):* Percentual de endividamento sobre o PL com indicação de conforto institucional (trava prudencial de 25,00%).
     3. *Dívida / Ativo Total (LTV Contábil):* Percentual LTV e exibição do **Ativo Total** consolidado em R$ Bilhões.
     4. *Caixa & Liquidez Imediata:* Saldo em tesouraria líquida e proporção percentual do PL.
   * **Tabela de Securitizações (5 Colunas):** Relação das emissões de CRIs, ativo imobiliário vinculado em garantia, % do passivo total, custo médio ponderado e cronograma de vencimento/amortização.
10. **Semáforo de Flags & Parecer Conclusivo:**
    * *Green Flags (Pontos Fortes):* Tese fundamentalista, vantagens competitivas e destaques operacionais com marcação visual em negrito.
    * *Red Flags (Pontos de Atenção):* Fatores de risco, concentração de inquilinos e pontos de monitoramento contínuo.
    * *Parecer Institucional:* Conclusão da auditoria, justificativa técnica, recomendação de alocação sugerida na carteira (ex: *7,5% a 10,0%*) e diretriz de execução.

---

### Aba B: Simulador Interativo de Valuation
* **Simulador de Sensibilidade Macroeconômica:**
  * Sliders interativos de calibração para a taxa da NTN-B 2035 de referência, expectativa de inflação (IPCA) e Spread Real mínimo exigido.
  * Recálculo instantâneo do Preço-Teto Recomendado, Retorno Real Líquido (`IPCA + X% a.a.`) e Margem de Segurança (%) frente à cotação de mercado.
  * Decomposição transparente dos métodos de valuation: Modelo de Spread NTN-B, Fluxo de Caixa Descontado (DCF Gordon) e Método Patrimonial (VPC).

---

### Aba C: Gráficos B3 TradingView & Histórico de Proventos
* **TradingView Candlestick Chart:**
  * Gráfico interativo com seleção de períodos (1 Mês, 3 Meses, 6 Meses, 1 Ano, 5 Anos).
  * Candlesticks diários e semanais, médias móveis ponderadas e barras de volume de negociação.
* **Histórico de Rendimentos Distribuídos:**
  * Grade com os últimos 12 meses de proventos pagos por cota, data de pagamento e rentabilidade pontual.

---

### Aba D: Pares & Setor
* Acesso imediato ao comparador setorial com o segmento do ativo pré-selecionado para análise competitiva lado a lado.

---

### Aba E: HTML Clássico & Exportação PDF
* Exibição do relatório corporativo compilado com formatação institucional e suporte nativo a impressão em PDF profissional através de `@media print` (`Ctrl + P`).

---

## 3. ⚔️ Comparador Setorial Multi-Métrica (`FiiSectorComparatorView`)

### Objetivo
Permitir a seleção de qualquer segmento da B3 e avaliar a liderança técnica entre os fundos através de métricas padronizadas e radiografias visuais.

### Componentes
1. **Pódio com 5 Selos de Liderança Setorial:**
   * 🏷️ *Melhor Oportunidade de Preço:* Maior Margem de Segurança frente ao Preço-Teto e menor P/VP.
   * 💰 *Maior Retorno Real Líquido:* Top rendimento real isento (`IPCA + X% a.a.`) com cobertura FFO saudável ($\ge 98\%$).
   * 🛡️ *Mais Seguro & Conservador:* Menor endividamento de CRIs e vacância física controlada.
   * 🎁 *Campeão de Reserva & Extraordinário:* Maior colchão de lucros acumulados retidos por cota (meses de autonomia).
   * ⭐ *Líder Geral do Setor:* Maior pontuação técnica global (Score de 0 a 10).
2. **Radar Multidimensional Normalizado (0 a 100):**
   * Gráfico de radar comparando até 4 fundos simultaneamente em 5 dimensões: *Desconto*, *Retorno Real*, *Solvência*, *Qualidade Operacional* e *Reserva*.
3. **Dispersão 2x2 Valuation vs. Qualidade:**
   * Eixo X (P/VP) vs Eixo Y (Score Técnico 0 a 10), com 4 quadrantes analíticos (*Oportunidade Clara*, *Qualidade com Ágio*, *Armadilha/Risco* e *Evitar/Caro*).
4. **Matriz Analítica Completa:**
   * Tabela multi-indicador completa com trajetória operacional mês a mês (`▲ Melhorando`, `— Estável`, `▼ Piorando`).

---

## 4. ⚙️ Parâmetros Macroeconômicos (`SettingsView`)

* Ajuste das variáveis macroeconômicas de base: taxa anual da NTN-B 2035 (padrão: 6,50%), projeção do IPCA (padrão: 4,00%) e spreads de risco exigidos por classe de FII.
* Os parâmetros são persistidos na tabela `pricing_parameters` do SQLite e propagados dinamicamente para o backend e frontend.
