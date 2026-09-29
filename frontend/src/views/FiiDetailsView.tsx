import React, { useState, useEffect } from 'react';
import { fiiApi } from '../api/client';
import type { FiiDetailsResponse, FiiMarketSeriesResponse } from '../types';
import { TopTabs } from '../components/layout/TopTabs';
import type { DetailsTab } from '../components/layout/TopTabs';
import {
  DossierKPIsGrid,
  DossierDRESection,
  DossierDividendProjectionSection,
  DossierPortfolioDonutsSection,
  DossierAssetsSection,
  DossierTenantsSection,
  DossierIndexersSection,
  DossierCapitalStructureSection,
  DossierOpinionAndFlagsSection,
} from '../components/fii/DossierSections';
import { ValuationSimulator } from '../components/fii/ValuationSimulator';
import { TradingViewChart } from '../components/charts/TradingViewChart';
import {
  Layers,
  DollarSign,
  AlertCircle,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';

interface FiiDetailsViewProps {
  ticker: string;
  onNavigateToSector: (segment: string, ticker: string) => void;
  onBackToScreener: () => void;
}

const fmt = (val?: number | null, decimals = 2): string => {
  if (val == null || isNaN(val)) return '-';
  return val.toFixed(decimals);
};

export const FiiDetailsView: React.FC<FiiDetailsViewProps> = ({
  ticker,
  onNavigateToSector,
  onBackToScreener,
}) => {
  const [activeTab, setActiveTab] = useState<DetailsTab>('dossier');
  const [details, setDetails] = useState<FiiDetailsResponse | null>(null);
  const [marketSeries, setMarketSeries] = useState<FiiMarketSeriesResponse | null>(null);
  const [chartPeriod, setChartPeriod] = useState<string>('1y');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Carregar dados de detalhes e séries B3
  useEffect(() => {
    let isCancelled = false;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [detailsRes, seriesRes] = await Promise.all([
          fiiApi.getDetails(ticker),
          fiiApi.getMarketSeries(ticker, chartPeriod).catch(() => null),
        ]);

        if (!isCancelled) {
          setDetails(detailsRes);
          setMarketSeries(seriesRes);
        }
      } catch (err: any) {
        console.error('Erro ao carregar detalhes:', err);
        if (!isCancelled) {
          setError(
            err.response?.data?.detail ||
              `Não foi possível carregar os dados para ${ticker}. Verifique o ticker e tente novamente.`
          );
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isCancelled = true;
    };
  }, [ticker]);

  // Carregar séries ao trocar período no gráfico
  const handlePeriodChange = async (newPeriod: string) => {
    setChartPeriod(newPeriod);
    try {
      const res = await fiiApi.getMarketSeries(ticker, newPeriod);
      setMarketSeries(res);
    } catch (err) {
      console.error('Erro ao buscar série do período:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-3 text-slate-400">
        <div className="w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-sm font-medium">
          Compilando Dossiê Fundamentalista de <b>{ticker}</b>...
        </span>
        <span className="text-xs text-slate-500">
          Cruzando DRE, ativos, inquilinos e valuations em tempo real
        </span>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="p-8 max-w-2xl mx-auto flex flex-col items-center gap-4 text-center">
        <div className="w-12 h-12 rounded-full bg-rose-950/80 border border-rose-800 flex items-center justify-center text-rose-400">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-white">Falha ao Carregar FII</h2>
        <p className="text-xs text-slate-400">{error || 'FII não encontrado na base de dados.'}</p>
        <button
          onClick={onBackToScreener}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition mt-2 cursor-pointer"
        >
          Voltar para o Screener
        </button>
      </div>
    );
  }

  const { header, kpis, parecer, segment_code, segment_name } = details;
  const isCreditFund = segment_code === 'PAPEL';

  const precoMercado = kpis?.preco_mercado ?? 100.0;
  const vpc = kpis?.vpc ?? 100.0;
  const teto = parecer?.teto ?? precoMercado;
  const margem = parecer?.margem_seguranca_pct ?? 0.0;

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Executive Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col gap-6 dark-card">
        {/* Top Breadcrumb & Actions */}
        <div className="no-print flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-slate-400">
            <button onClick={onBackToScreener} className="hover:text-white transition cursor-pointer">
              Screener
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
            <button
              onClick={() => onNavigateToSector(segment_code, ticker)}
              className="hover:text-white transition cursor-pointer"
            >
              {segment_name}
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
            <span className="text-white font-bold">{ticker}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigateToSector(segment_code, ticker)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-950 border border-slate-800 hover:bg-slate-800 hover:text-white transition cursor-pointer"
            >
              <ExternalLink className="w-3.5 h-3.5 text-sky-400" />
              <span>Ver Pares do Setor</span>
            </button>
          </div>
        </div>

        {/* Core Fund Identification */}
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-xl shadow-blue-500/20 text-white font-black text-xl tracking-wider">
              {ticker.slice(0, 4)}
            </div>

            <div className="flex flex-col">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-black text-white tracking-wide">{ticker}</h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-sky-300 border border-slate-700">
                  {segment_name}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800">
                  {parecer?.alocacao_sugerida || 'Alocação Moderada'}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800">
                  {header?.veredicto || 'Auditado'}
                </span>
              </div>
              <p className="text-sm text-slate-300 mt-1 font-medium">{header?.name}</p>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2">
                <span>
                  Gestão: <b className="text-slate-200">{header?.gestora || 'N/A'}</b>
                </span>
                <span>•</span>
                <span>
                  Admin: <b className="text-slate-200">{header?.administrador || 'N/A'}</b>
                </span>
                <span>•</span>
                <span>
                  Cotistas: <b className="text-slate-200">{kpis?.cotistas ? kpis.cotistas.toLocaleString('pt-BR') : '-'}</b>
                </span>
                <span>•</span>
                <span>
                  PL: <b className="text-slate-200">R$ {fmt(kpis?.pl_bi)} Bi</b>
                </span>
              </div>
            </div>
          </div>

          {/* Pricing Box */}
          <div className="flex items-center gap-6 bg-slate-950/80 p-4 rounded-xl border border-slate-800">
            <div className="flex flex-col">
              <span className="text-[11px] text-slate-400">Cotação Atual</span>
              <span className="text-2xl font-black text-white font-mono">
                R$ {fmt(precoMercado)}
              </span>
              <span className="text-[10px] text-slate-500">VPC: R$ {fmt(vpc)}</span>
            </div>

            <div className="h-10 w-px bg-slate-800"></div>

            <div className="flex flex-col">
              <span className="text-[11px] text-indigo-400 font-semibold">Preço-Teto Est.</span>
              <span className="text-2xl font-black text-indigo-300 font-mono">
                R$ {fmt(teto)}
              </span>
              <span
                className={`text-[10px] font-bold ${
                  margem >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                Margem: {margem >= 0 ? '+' : ''}{fmt(margem, 1)}%
              </span>
            </div>
          </div>
        </div>

        {/* 8 KPIs Institucionais */}
        <DossierKPIsGrid kpis={kpis} header={header} />
      </div>

      {/* Top Tabs Bar */}
      <TopTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Tab 1: Dossiê Executivo Completo */}
      {activeTab === 'dossier' && (
        <div className="flex flex-col gap-6">
          {/* Dados Cadastrais e Taxas */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs dark-card">
            <div>
              <span className="text-slate-500 block">Razão Social</span>
              <span className="font-semibold text-slate-200 truncate block">
                {header?.razao_social || 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block">CNPJ</span>
              <span className="font-semibold text-slate-200">{header?.cnpj || 'N/A'}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Cotas Emitidas</span>
              <span className="font-semibold text-slate-200">
                {kpis?.cotas_emitidas || 'Listadas B3'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block">Data-Base / Protocolo</span>
              <span className="font-semibold text-slate-200">
                {header?.data_base || 'Recente'} ({header?.data_protocolo || 'CVM'})
              </span>
            </div>
          </div>

          {/* DRE Gerencial */}
          <DossierDRESection dre={details.dre} />

          {/* Distribuição e Projeção de Dividendos */}
          <DossierDividendProjectionSection
            dividendos={details.dividendos}
            ticker={ticker}
          />

          {/* Portfólio de Imóveis ou CRIs */}
          <DossierAssetsSection ativos={details.ativos} isCreditFund={isCreditFund} />

          {/* Raio-X da Carteira: Culturas, Estratégia e Indexadores / Alocações (Donuts) */}
          <DossierPortfolioDonutsSection
            donutGeografia={details.donut_geografia}
            donutComposicao={details.donut_composicao}
            segmentCode={details.segment_code}
          />

          {/* Locatários / Devedores */}
          <DossierTenantsSection tenants={details.inquilinos} />

          {/* Indexadores dos Contratos e Receitas */}
          <DossierIndexersSection indexers={details.indexadores} />

          {/* 5. Estrutura de Capital, Securitizações e Alavancagem Financeira */}
          <DossierCapitalStructureSection debts={details.dividas} kpis={details.kpis} />

          {/* Parecer do Analista e Semáforo de Flags */}
          <DossierOpinionAndFlagsSection
            parecer={details.parecer}
            greenFlags={details.green_flags}
            redFlags={details.red_flags}
          />
        </div>
      )}

      {/* Tab 2: Simulador Interativo de Valuation */}
      {activeTab === 'valuation' && (
        <ValuationSimulator ticker={ticker} kpis={kpis} parecer={details.parecer} />
      )}

      {/* Tab 3: Gráficos B3 TradingView */}
      {activeTab === 'charts' && (
        <div className="flex flex-col gap-6">
          {marketSeries && marketSeries.series?.length > 0 ? (
            <TradingViewChart
              candles={marketSeries.series}
              ticker={ticker}
              onPeriodChange={handlePeriodChange}
              currentPeriod={chartPeriod}
            />
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
              Carregando cotações históricas da B3...
            </div>
          )}

          {/* Histórico de Proventos Mensais */}
          {marketSeries && marketSeries.dividend_history?.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
              <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-emerald-400" />
                Histórico de Rendimentos Distribuídos (Últimos Meses)
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                {marketSeries.dividend_history.slice(-12).map((div, i) => (
                  <div
                    key={i}
                    className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex flex-col justify-between"
                  >
                    <span className="text-[11px] text-slate-400">{div.date}</span>
                    <span className="text-lg font-bold font-mono text-emerald-400 mt-1">
                      R$ {fmt(div.rate)}
                    </span>
                    <span className="text-[10px] text-slate-500">Rendimento por cota</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Comparador Setorial Redirecionamento */}
      {activeTab === 'compare' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center flex flex-col items-center gap-4">
          <Layers className="w-12 h-12 text-blue-400" />
          <h3 className="text-lg font-bold text-white">Comparativo de Pares Setoriais</h3>
          <p className="text-xs text-slate-400 max-w-md">
            Compare o <b>{ticker}</b> contra todos os outros fundos do segmento{' '}
            <b>{segment_name}</b> através do Pódio de 5 Selos, Radar 5D e Matriz de Dispersão.
          </p>
          <button
            onClick={() => onNavigateToSector(segment_code, ticker)}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20 transition flex items-center gap-2 cursor-pointer"
          >
            <span>Abrir Comparador Completo ({segment_name})</span>
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Tab 5: HTML Clássico Original */}
      {activeTab === 'raw_html' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white">Visualização HTML Original do Relatório</h3>
            <span className="text-xs text-slate-500">Renderização em sandbox no DOM</span>
          </div>
          <div
            className="bg-white text-slate-900 p-6 rounded-xl overflow-x-auto shadow-inner"
            dangerouslySetInnerHTML={{ __html: details.raw_html }}
          />
        </div>
      )}
    </div>
  );
};
