# 02. Fluxos de Informações e Dados

Este documento descreve detalhadamente os pipelines de dados, os fluxos de integração e o ciclo de vida da informação dentro do **Analisys**, demonstrando como cada componente interage com fontes externas e locais.

---

## 🌐 Visão Geral da Arquitetura de Dados

O sistema opera com um **modelo de camadas integradas e blindadas**, garantindo que nenhuma informação seja apresentada sem respaldo documental e que as operações sejam resilientes a indisponibilidades parciais de rede.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FONTES DE DADOS                                      │
├─────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│    1. CVM / B3          │       2. Mercado / BolsaAI   │    3. Gestoras de FIIs        │
│    (Fundos.NET)         │       (APIs / Yahoo Fin.)    │    (Relatórios Gerenciais)    │
│    • Dados Contábeis    │       • Cotações & Proventos │    • Métricas Operacionais    │
│    • Fé Pública Oficial │       • Liquidez & Múltiplos │    • FFO & Engenharia         │
└────────────┬────────────┴──────────────┬───────────────┴───────────────┬───────────────┘
             │                           │                               │
             ▼                           ▼                               ▼
┌─────────────────────────┬──────────────────────────────┬───────────────────────────────┐
│ src/services/           │ src/services/                │ src/services/                 │
│ fundos_net_service.py   │ bolsai_service.py            │ gerencial_extractor.py        │
│ market_data.py          │                              │                               │
└────────────┬────────────┴──────────────┬───────────────┴───────────────┬───────────────┘
             │                           │                               │
             ▼                           ▼                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MOTOR DE RECONCILIAÇÃO E AUDITORIA                              │
│                        src/services/cross_validation_service.py                        │
│                        • Validação Cruzada CVM vs. Mercado                             │
│                        • Detecção Oficial de Segmento                                  │
│                        • Correção de Múltiplos Divergentes                             │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      RENDERIZADORES SETORIAIS ESPECIALIZADOS                           │
│                      src/services/report_generator.py                                  │
│                      ├── src/services/shopping_report_renderer.py (Shoppings)          │
│                      ├── src/services/logistica_report_renderer.py (Galpões)           │
│                      ├── src/services/papel_report_renderer.py (CRIs / Papel)          │
│                      ├── src/services/lajes_report_renderer.py (Corporativo)           │
│                      ├── src/services/fof_report_renderer.py (Fundos de Fundos)        │
│                      ├── src/services/agro_report_renderer.py (Fiagros / Terras)       │
│                      ├── src/services/hibrido_report_renderer.py (Multi-Ativos)        │
│                      └── Mecanismo Antifalha hasattr / _ensure_complete_sections       │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CAMADA DE API REST (FASTAPI)                              │
│                              src/api/main.py & src/api/routes_fii.py                   │
│                              • GET /api/fii/screener                                   │
│                              • GET /api/fii/{ticker}/details                           │
│                              • GET /api/fii/{ticker}/market-series                     │
│                              • GET /api/fii/comparator/{segment}                       │
│                              • GET/POST /api/fii/settings/pricing                      │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                     ┌───────────────────┴───────────────────┐
                     ▼                                       ▼
┌────────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│       FRONTEND SPA (REACT 18 + VITE)   │ │       DASHBOARD LEGADO (STREAMLIT)        │
│       • Screener com 396 FIIs          │ │       • Painel de Posições e Carteira     │
│       • Dossiê Executivo (5 abas)      │ │       • Comparador Setorial Básico        │
│       • TradingView Charts B3          │ │       • Rebalanceamento por Metas         │
│       • Simulador de Valuation         │ │       • Upload de Planilhas B3            │
└────────────────────────────────────────┘ └───────────────────────────────────────────┘
```

---

## 📡 1. Endpoints da API REST (FastAPI)

A camada de API expõe endpoints em conformidade OpenAPI/Swagger (`/docs`):

### `GET /api/fii/screener`
* **Finalidade:** Retornar o catálogo unificado de FIIs e Fiagros para alimentação do Screener da interface.
* **Parâmetros de Consulta:**
  * `search` (opcional): Filtro textual de ticker ou nome.
  * `segment` (opcional): Código do segmento (`LOGISTICA`, `PAPEL`, `SHOPPING`, `LAJES`, `FOF`, `HIBRIDO`, `AGRO`).
  * `max_pvp` (opcional): Teto de P/VP.
  * `min_dy` (opcional): Piso de Dividend Yield anualizado (%).
  * `min_liquidez` (opcional): Piso de ADTV em R$.
  * `max_vacancia` (opcional): Teto de vacância física (%).
  * `page` / `page_size`: Controle de paginação.
* **Payload de Resposta:** `total`, `count`, `items` (lista de ativos com cotação, VPC, P/VP, DY, ADTV, vacância e score unificado 0 a 10), `segments` e `segment_counts`.

### `GET /api/fii/{ticker}/details`
* **Finalidade:** Fornecer o payload analítico completo para renderização do Dossiê Executivo.
* **Estrutura dos Dados:**
  * `header`: Ticker, nome, razão social, CNPJ, gestor, administrador, cotistas, PL, score (0 a 10), veredito.
  * `kpis`: 8 KPIs analíticos consolidados com validação cruzada.
  * `dre`: Linhas contábeis gerenciais com FFO/cota e cobertura percentual.
  * `dividendos`: Analytics de proventos, colchão de liquidez e projeções:
    * `provento_atual`, `ffo_cota`, `cobertura_ffo_pct` e `status_sustentabilidade`.
    * `reserva_acumulada_cota`, `meses_reserva_cobertura` e `status_colchao`.
    * `extraordinario_estimado_fim_semestre`, `provento_pico_fim_semestre` e `meses_para_fechamento_semestre` (Art. 10 da Lei nº 8.668/93 - Mínimo obrigatório de 95% do lucro caixa semestral).
    * `provento_projetado_mes`, `guidance_min`, `guidance_max` e `guidance_faixa`.
    * `historico_12m`: 12 meses cronológicos de pagamentos com segregação de provento recorrente vs extraordinário pago.
    * `projecao_futura`: 6 meses futuros projetados com pico no fechamento semestral.
    * `media_recorrente_12m`: Média aritmética de referência dos proventos regulares dos últimos 12 meses.
    * `base_legal`: Dispositivos normativos da Lei 8.668/93 e Resolução CVM 175.
  * `ativos`: Propriedades imobiliárias, operações de CRIs ou fazendas rurais em Fiagros.
  * `donut_geografia`: Distribuição geográfica (ou cultura agrícola no caso AGRO) para renderização do gráfico de rosca Pure CSS.
  * `donut_composicao`: Composição patrimonial do ativo ou estratégia de investimento (SLB/BTL/Land Equity).
  * `inquilinos`: Maiores locatários ou grupos produtores rurais, percentual de receita e rating.
  * `indexadores`: Distribuição da carteira em IPCA, IGP-M, CDI/DI e Outros/Pré.
  * `dividas`: Operações de securitização (CRIs), ativos vinculados, custos médios ponderados e cronogramas de amortização.
  * `green_flags` / `red_flags`: Pontos fortes e pontos de atenção com formatação tipográfica em negrito.
  * `parecer`: Preço-teto recomendado, margem de segurança, alocação recomendada e diretrizes de execução.
  * `raw_html`: Código HTML executivo completo compilado para impressão em PDF corporativo.

### `GET /api/fii/{ticker}/market-series`
* **Finalidade:** Retornar os dados históricos de mercado da B3 para os gráficos TradingView e histórico de dividendos.
* **Parâmetros:** `period` (`1m`, `3m`, `6m`, `1y`, `5y`).
* **Payload:** Séries temporais em formato OHLCV (Open, High, Low, Close, Volume) e histórico dos últimos proventos distribuídos por cota.

### `GET /api/fii/comparator/{segment}`
* **Finalidade:** Alimentar o Comparador Setorial de Pares.
* **Payload:** Pódio com 5 Selos analíticos de liderança, coordenadas para a Matriz de Dispersão 2x2 (P/VP vs Score), dados normalizados para o Radar Multidimensional 5D e tabela com trajetórias MoM.

### `GET /api/fii/settings/pricing` & `POST /api/fii/settings/pricing`
* **Finalidade:** Consultar e persistir os parâmetros macroeconômicos de referência (NTN-B 2035, IPCA e Spreads).

---

## 🔄 2. Pipeline de Reconciliação CVM vs. Mercado

1. **Consulta Primária CVM / Fundos.NET:**
   * O sistema busca o último Informe Mensal Estruturado oficial.
   * Extrai o Valor Patrimonial da Cota (VPC), Patrimônio Líquido Contábil, Base de Cotistas e Passivo Oneroso (saldo devedor de CRIs).
2. **Consulta Secundária de Mercado (BolsaAI / B3):**
   * O sistema obtém cotação ao vivo, volume médio negociado (ADTV), dividendos acumulados e múltiplos.
3. **Reconciliação e Blindagem:**
   * O `CrossValidationService` compara as fontes:
     * O VPC da CVM tem **prevalência absoluta** sobre qualquer estimativa externa.
     * O P/VP é recalculado rigorosamente como $\frac{\text{Preço de Mercado B3}}{\text{VPC CVM}}$.
     * Casos de inconsistência em APIs externas (como P/VP distorcido) são corrigidos automaticamente.
4. **Mecanismo Antifalha Setorial:**
   * Os renderizadores contam com verificações seguras de atributos (`hasattr`) e sintetizadores de DRE e ativos rurais, garantindo que fundos de qualquer segmento (Agro, Papel, Lajes, FOF, Híbrido, Shopping, Logística) carreguem sem exceções de execução.