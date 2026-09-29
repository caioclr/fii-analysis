# 📚 Documentação do Projeto Analisys

Bem-vindo à documentação oficial e arquitetural do **Analisys** — plataforma de inteligência de investimentos, auditoria fundamentalista regulatória e gestão de ativos na B3 (com foco em Fundos Imobiliários, Fiagros e Ações).

---

## 🎯 Objetivo da Plataforma

O **Analisys** foi projetado para analistas e investidores que exigem rigor institucional e conciliação documental para suas tomadas de decisão. O sistema se destaca por:

1. **Catálogo & Screener Universal:** Acompanhamento de 396 FIIs e Fiagros listados na B3 com filtros quantitativos em tempo real e segmentação instantânea.
2. **Auditoria Regulatória Oficial (Fundos.NET / CVM):** Extração automatizada e validação contábil dos informes mensais estruturados protocolados na CVM.
3. **Valuation Institucional e Retorno Real (Sem Bazin):** Precificação técnica por Spread Real sobre NTN-B 2035, Gordon DCF e modelo patrimonial, apurando o rendimento real líquido isento (`IPCA + X% a.a.`).
4. **Sustentabilidade de Proventos e Projeções Semestrais:** FFO Caixa, índice de cobertura, colchão de reservas e estimativa de dividendos extraordinários sob o art. 10 da Lei nº 8.668/93.
5. **Dossiês Executivos de 7 Segmentos:** Relatórios com DRE gerencial, portfólio de ativos físicos e terras rurais, **Raio-X da carteira (donuts pure CSS)**, **Estrutura de capital e securitizações** e Semáforo de Flags de risco.
6. **Comparação Setorial Multi-Métrica:** Pódio com 5 selos analíticos de liderança, Radar 5D, Matriz de Dispersão 2x2 e tabela comparativa com trajetória operacional mês a mês (`▲`, `—`, `▼`).
7. **Arquitetura Dual Stack Moderna:** Backend de alto rendimento em **FastAPI** + Frontend reativo em **React 18 + TypeScript + Vite + Tailwind CSS**, além do dashboard analítico legado em **Streamlit**.

---

## 🧭 Mapa da Documentação

A documentação está estruturada em 5 guias especializados:

| Documento | Descrição e Foco |
| :--- | :--- |
| [**01. Visão Funcional do Sistema**](file:///c:/Users/caioc/projetos/analisys/docs/01_visao_funcional.md) | Especificação das telas, módulos da SPA moderna (Screener, Dossiê, Valuation, TradingView, Comparador) e interface legada. |
| [**02. Fluxos de Informações e Dados**](file:///c:/Users/caioc/projetos/analisys/docs/02_fluxos_de_informacao.md) | Pipelines de dados, integração CVM/BolsaAI/B3, rotas da API FastAPI, caching e reconciliação. |
| [**03. Guia de Setores e Métricas Especializadas**](file:///c:/Users/caioc/projetos/analisys/docs/03_setores_e_metricas.md) | Metodologia analítica por tipologia (Shoppings, Logística, Papel, Lajes, FOFs, Agro, Híbridos), fórmulas e governança de scores. |
| [**04. Guia Prático de Operação e Uso**](file:///c:/Users/caioc/projetos/analisys/docs/04_guia_de_uso.md) | Manual passo a passo para o usuário: inicialização do backend e frontend, navegação pela SPA, exportação para PDF e ajustes macro. |
| [**05. Governança e Validação de Dados**](file:///c:/Users/caioc/projetos/analisys/docs/05_governanca_e_validacao_de_dados.md) | Governança contábil, reconciliações de múltiplos, padronização de escalas de score (0 a 10) e baterias de testes automatizadas. |

---

## 🏗️ Arquitetura Funcional em Alto Nível

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FONTES DE DADOS                                      │
├─────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│    1. CVM / Fundos.NET  │       2. Mercado / BolsaAI   │    3. Gestoras / Relatórios   │
│    • Balancetes & VPC   │       • Cotações B3 ao Vivo  │    • DRE Gerencial & FFO      │
│    • Passivo de CRIs    │       • Liquidez & Múltiplos │    • Portfólio de Propriedades│
└────────────┬────────────┴──────────────┬───────────────┴───────────────┬───────────────┘
             │                           │                               │
             ▼                           ▼                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           MOTORES ANALÍTICOS DE NEGÓCIO (PYTHON)                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • CrossValidationService (Reconciliação CVM vs BolsaAI)                                │
│ • FIIComparatorService (Pódio 5 Selos, Radar 5D, Scatter 2x2)                          │
│ • ValuationPricingService (Preço-Teto NTN-B, Retorno Real IPCA+)                       │
│ • DividendProjectionService (FFO, Cobertura, Colchão de Reserva, Lei 8.668/93)         │
│ • 7 Renderizadores Especializados (Agro, Logística, Papel, Shoppings, Lajes, FOFs)    │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              API REST BACKEND (FASTAPI)                                │
│                              src/api/main.py & routes_fii.py                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • GET /api/fii/screener        (Catálogo de 396 FIIs, filtros e ordenação instantânea) │
│ • GET /api/fii/{ticker}/details (Dossiê completo, DRE, Dividendos 12M/Projeção, Ativos, Donuts, Dívidas, Flags) │
│ • GET /api/fii/{ticker}/market-series (Candlesticks OHLCV B3 e Histórico de Dividendos)│
│ • GET /api/fii/comparator/{seg} (Comparador setorial multi-métrica e trajetórias MoM)  │
│ • GET|POST /api/fii/settings/pricing (Sensibilidade de Parâmetros Macroeconômicos)    │
└──────────────────┬──────────────────────────────────────────────────┬──────────────────┘
                   │                                                  │
                   ▼                                                  ▼
┌──────────────────────────────────────┐            ┌────────────────────────────────────┐
│      FRONTEND SPA MODERNO            │            │     DASHBOARD LEGADO               │
│   (React 18 + Vite + Tailwind CSS)   │            │   (Streamlit - app.py)             │
├──────────────────────────────────────┤            ├────────────────────────────────────┤
│ • Screener Interativo (396 FIIs)     │            │ • Painel de Posições da Carteira   │
│ • Dossiê Executivo em 5 Abas         │            │ • Comparador Setorial Básico       │
│ • Simulador Interativo de Valuation  │            │ • Aporte Inteligente & Metas       │
│ • Gráficos B3 TradingView            │            │ • Upload de Planilhas B3 / Excel   │
│ • Impressão em PDF (@media print)    │            │ • Histórico Local em SQLite        │
└──────────────────────────────────────┘            └────────────────────────────────────┘
```

---

## ⚡ Inicialização Rápida

Para iniciar o ecossistema completo:
```powershell
# Terminal 1 - Backend FastAPI:
.\venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend React SPA:
cd frontend
npm run dev
```
Acesse o sistema pelo navegador em **`http://127.0.0.1:5533`**.
