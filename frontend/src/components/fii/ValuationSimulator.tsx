import React, { useState, useEffect } from 'react';
import { fiiApi } from '../../api/client';
import type {
  FiiKpis,
  DossierVerdict,
  ValuationSimulateResponse,
} from '../../types';
import { Sliders, TrendingUp, ShieldAlert, Award, RefreshCw } from 'lucide-react';

interface ValuationSimulatorProps {
  ticker: string;
  kpis: FiiKpis;
  parecer: DossierVerdict;
}

const fmt = (val?: number | null, decimals = 2): string => {
  if (val == null || isNaN(val)) return '-';
  return val.toFixed(decimals);
};

export const ValuationSimulator: React.FC<ValuationSimulatorProps> = ({
  ticker,
  kpis,
  parecer,
}) => {
  const [ntnbRate, setNtnbRate] = useState<number>(6.5);
  const [riskSpread, setRiskSpread] = useState<number>(2.0);
  const [projectedIpca, setProjectedIpca] = useState<number>(4.0);
  const [requiredMargin, setRequiredMargin] = useState<number>(10.0);

  const [simulation, setSimulation] = useState<ValuationSimulateResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Efeito para simular quando parâmetros mudam
  useEffect(() => {
    let isCancelled = false;
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        const res = await fiiApi.simulateValuation(ticker, {
          ntnb_reference_rate: ntnbRate,
          real_risk_spread: riskSpread,
          projected_ipca: projectedIpca,
        });
        if (!isCancelled) {
          setSimulation(res);
        }
      } catch (err) {
        console.error('Erro ao simular valuation:', err);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }, 150);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [ticker, ntnbRate, riskSpread, projectedIpca]);

  // Carregar configurações padrão na montagem
  useEffect(() => {
    fiiApi
      .getPricingSettings()
      .then((settings) => {
        setNtnbRate(settings.ntnb_reference_rate ?? settings.ntnb_2035_rate ?? 6.5);
        setRiskSpread(settings.real_risk_spread ?? settings.real_risk_spread_default ?? 2.0);
        setProjectedIpca(settings.projected_ipca ?? 4.0);
        setRequiredMargin(settings.default_discount_margin ?? 10.0);
      })
      .catch(() => {});
  }, []);

  const precoMercado = kpis?.preco_mercado ?? 100.0;
  const tetoRecomendado = simulation?.preco_teto_recomendado ?? parecer?.teto ?? precoMercado;
  const margemReal = simulation?.margem_seguranca_pct ?? parecer?.margem_seguranca_pct ?? 0.0;
  const statusRec = simulation?.status_atratividade ?? parecer?.conclusao ?? 'Aprovado';
  const taxaDescontoReal = fmt(ntnbRate + riskSpread);

  const tetoSpreadNtnb = simulation?.metodologias?.teto_spread_ntnb ?? tetoRecomendado;
  const tetoGordon = simulation?.metodologias?.teto_gordon_dcf ?? (tetoRecomendado * 0.9);
  const tetoPatrimonial = simulation?.metodologias?.teto_patrimonial ?? kpis?.vpc ?? precoMercado;

  const isBuyOpportunity = margemReal >= requiredMargin;
  const isFairPrice = margemReal >= 0 && margemReal < requiredMargin;

  const resetToInstitutional = () => {
    setNtnbRate(6.5);
    setRiskSpread(2.0);
    setProjectedIpca(4.0);
    setRequiredMargin(10.0);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col gap-6">
      {/* Header do Simulador */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-indigo-400" />
            Simulador de Valuation Institucional em Tempo Real
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Altere as premissas macroeconômicas e de risco para recalcular o Preço-Teto e a Margem
            de Segurança de <b>{ticker}</b> instantaneamente.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {loading && (
            <div className="flex items-center gap-1.5 text-xs text-indigo-400">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Recalculando...</span>
            </div>
          )}
          <button
            onClick={resetToInstitutional}
            className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 transition cursor-pointer"
          >
            Restaurar Premissas Padrão
          </button>
        </div>
      </div>

      {/* Grid de Sliders de Premissas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 bg-slate-950/70 p-5 rounded-xl border border-slate-800/80">
        {/* Slider 1: NTN-B */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">NTN-B 2035 (Juro Real Livre de Risco)</span>
            <span className="font-bold text-sky-400 bg-sky-950 px-2 py-0.5 rounded border border-sky-800">
              {fmt(ntnbRate)}% a.a.
            </span>
          </div>
          <input
            type="range"
            min="4.5"
            max="9.0"
            step="0.1"
            value={ntnbRate}
            onChange={(e) => setNtnbRate(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>4.5%</span>
            <span>Ref: 6.5%</span>
            <span>9.0%</span>
          </div>
        </div>

        {/* Slider 2: Spread de Risco */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">Spread de Risco Real Exigido</span>
            <span className="font-bold text-indigo-400 bg-indigo-950 px-2 py-0.5 rounded border border-indigo-800">
              +{fmt(riskSpread)}% a.a.
            </span>
          </div>
          <input
            type="range"
            min="0.5"
            max="4.5"
            step="0.1"
            value={riskSpread}
            onChange={(e) => setRiskSpread(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0.5% (Baixo)</span>
            <span>2.0% (Padrão)</span>
            <span>4.5% (Alto)</span>
          </div>
        </div>

        {/* Slider 3: IPCA Projetado */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">IPCA Projetado Médio</span>
            <span className="font-bold text-amber-400 bg-amber-950 px-2 py-0.5 rounded border border-amber-800">
              {fmt(projectedIpca)}% a.a.
            </span>
          </div>
          <input
            type="range"
            min="2.5"
            max="7.5"
            step="0.1"
            value={projectedIpca}
            onChange={(e) => setProjectedIpca(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>2.5%</span>
            <span>Ref: 4.0%</span>
            <span>7.5%</span>
          </div>
        </div>

        {/* Slider 4: Margem de Segurança Exigida */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">Margem de Segurança Mínima</span>
            <span className="font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
              {fmt(requiredMargin, 0)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="25"
            step="1"
            value={requiredMargin}
            onChange={(e) => setRequiredMargin(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-400"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0% (Sem folga)</span>
            <span>10% (Padrão)</span>
            <span>25% (Ultraconservador)</span>
          </div>
        </div>
      </div>

      {/* Taxa de Desconto Consolidada */}
      <div className="flex items-center justify-between px-4 py-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300">
        <div>
          Taxa de Capitalização Real Exigida (NTN-B + Spread):{' '}
          <span className="font-bold text-white font-mono">{taxaDescontoReal}% ao ano</span>
        </div>
        <div>
          Custo de Capital Nominal Implícito (Ke Gordon):{' '}
          <span className="font-bold text-amber-300 font-mono">
            {fmt(parseFloat(taxaDescontoReal) + projectedIpca)}% ao ano
          </span>
        </div>
      </div>

      {/* Cards de Resultados do Valuation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Preço Atual de Mercado */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">Cotação de Mercado</span>
          <div className="my-2">
            <span className="text-2xl font-black text-white font-mono">
              R$ {fmt(precoMercado)}
            </span>
          </div>
          <span className="text-[11px] text-slate-500">Base B3 em tempo real</span>
        </div>

        {/* Card 2: Preço-Teto Recomendado */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-indigo-300 font-medium">Preço-Teto Recomendado</span>
            <Award className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="my-2">
            <span className="text-2xl font-black text-indigo-300 font-mono">
              R$ {fmt(tetoRecomendado)}
            </span>
          </div>
          <span className="text-[11px] text-slate-400 truncate">
            {parecer?.diretriz || 'Modelo Fundamentalista Integrado'}
          </span>
        </div>

        {/* Card 3: Margem de Segurança */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Margem de Segurança Real</span>
            <TrendingUp
              className={`w-4 h-4 ${margemReal >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}
            />
          </div>
          <div className="my-2">
            <span
              className={`text-2xl font-black font-mono ${
                margemReal >= requiredMargin
                  ? 'text-emerald-400'
                  : margemReal >= 0
                  ? 'text-amber-400'
                  : 'text-rose-400'
              }`}
            >
              {margemReal >= 0 ? `+${fmt(margemReal, 1)}%` : `${fmt(margemReal, 1)}%`}
            </span>
          </div>
          <span className="text-[11px] text-slate-500">
            Exigida pelo usuário: &ge; {fmt(requiredMargin, 0)}%
          </span>
        </div>

        {/* Card 4: Parecer de Decisão */}
        <div
          className={`p-4 rounded-xl border flex flex-col justify-between ${
            isBuyOpportunity
              ? 'bg-emerald-950/40 border-emerald-800/80 text-emerald-300'
              : isFairPrice
              ? 'bg-amber-950/40 border-amber-800/80 text-amber-300'
              : 'bg-rose-950/40 border-rose-800/80 text-rose-300'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider">Recomendação</span>
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div className="my-2">
            <span className="text-lg font-bold">
              {isBuyOpportunity
                ? 'COMPRA / DESCONTO'
                : isFairPrice
                ? 'PREÇO JUSTO'
                : 'AGUARDAR / CARO'}
            </span>
          </div>
          <span className="text-[11px] opacity-90 line-clamp-2">{statusRec}</span>
        </div>
      </div>

      {/* Comparativo das 3 Metodologias Individuais */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2.5 px-3 font-semibold">Metodologia</th>
              <th className="py-2.5 px-3 font-semibold">Racional Fundamentalista</th>
              <th className="py-2.5 px-3 font-semibold text-right">Preço-Teto</th>
              <th className="py-2.5 px-3 font-semibold text-right">Margem s/ Mercado</th>
              <th className="py-2.5 px-3 font-semibold text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {/* 1. Spread NTN-B */}
            <tr className="hover:bg-slate-800/40 transition">
              <td className="py-3 px-3 font-sans font-medium text-slate-200">
                1. Spread Real s/ NTN-B
              </td>
              <td className="py-3 px-3 font-sans text-slate-400">
                FFO anualizado capitalizado à taxa real exigida de {taxaDescontoReal}% a.a.
              </td>
              <td className="py-3 px-3 text-right font-bold text-slate-200">
                R$ {fmt(tetoSpreadNtnb)}
              </td>
              <td
                className={`py-3 px-3 text-right font-bold ${
                  tetoSpreadNtnb >= precoMercado ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {precoMercado > 0 ? fmt(((tetoSpreadNtnb - precoMercado) / precoMercado) * 100, 1) : '0.0'}%
              </td>
              <td className="py-3 px-3 text-center font-sans">
                <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                  Fluxo Operacional
                </span>
              </td>
            </tr>

            {/* 2. Gordon DCF */}
            <tr className="hover:bg-slate-800/40 transition">
              <td className="py-3 px-3 font-sans font-medium text-slate-200">
                2. Dividendos Gordon (DCF)
              </td>
              <td className="py-3 px-3 font-sans text-slate-400">
                Fluxo perpétuo com correção pelo IPCA projetado ({fmt(projectedIpca)}% a.a.)
              </td>
              <td className="py-3 px-3 text-right font-bold text-slate-200">
                R$ {fmt(tetoGordon)}
              </td>
              <td
                className={`py-3 px-3 text-right font-bold ${
                  tetoGordon >= precoMercado ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {precoMercado > 0 ? fmt(((tetoGordon - precoMercado) / precoMercado) * 100, 1) : '0.0'}%
              </td>
              <td className="py-3 px-3 text-center font-sans">
                <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                  Proventos
                </span>
              </td>
            </tr>

            {/* 3. Patrimonial Prudencial */}
            <tr className="hover:bg-slate-800/40 transition">
              <td className="py-3 px-3 font-sans font-medium text-slate-200">
                3. Patrimonial Prudencial
              </td>
              <td className="py-3 px-3 font-sans text-slate-400">
                Valor Patrimonial da Cota (VPC R$ {fmt(kpis?.vpc)}) com travas regulatórias
              </td>
              <td className="py-3 px-3 text-right font-bold text-slate-200">
                R$ {fmt(tetoPatrimonial)}
              </td>
              <td
                className={`py-3 px-3 text-right font-bold ${
                  tetoPatrimonial >= precoMercado ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {precoMercado > 0 ? fmt(((tetoPatrimonial - precoMercado) / precoMercado) * 100, 1) : '0.0'}%
              </td>
              <td className="py-3 px-3 text-center font-sans">
                <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                  Garantia Real
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
