import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import {
  Coins,
  ShieldCheck,
  Scale,
  TrendingUp,
  Info,
  Calendar,
  ArrowUpRight,
  Clock,
} from 'lucide-react';
import type { DossierDividendsAnalytics } from '../../types';

interface DossierDividendProjectionSectionProps {
  dividendos?: DossierDividendsAnalytics;
  ticker?: string;
}

const fmt = (v?: number | null, d = 2) =>
  v == null ? '-' : v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });

export const DossierDividendProjectionSection: React.FC<DossierDividendProjectionSectionProps> = ({
  dividendos,
  ticker = 'FII',
}) => {
  const [viewMode, setViewMode] = useState<'12m' | 'projecao' | 'integrada'>('integrada');

  if (!dividendos) {
    return null;
  }

  const historico = dividendos.historico_12m || [];
  const projecao = dividendos.projecao_futura || [];

  // Configuração dos dados de acordo com o modo selecionado
  let categories: string[] = [];
  let recorrenteData: number[] = [];
  let extraordinarioData: number[] = [];
  let markLineValue: number | undefined = undefined;

  if (viewMode === '12m') {
    categories = historico.map((h) => h.mes);
    recorrenteData = historico.map((h) => h.recorrente);
    extraordinarioData = historico.map((h) => h.nao_recorrente);
    markLineValue = dividendos.media_recorrente_12m;
  } else if (viewMode === 'projecao') {
    categories = projecao.map((p) => p.mes);
    recorrenteData = projecao.map((p) => p.recorrente_estimado);
    extraordinarioData = projecao.map((p) => p.nao_recorrente_estimado);
  } else {
    // Visão integrada: 12M Histórico + 6M Projeção
    categories = [
      ...historico.map((h) => h.mes),
      ...projecao.map((p) => `${p.mes}*`),
    ];
    recorrenteData = [
      ...historico.map((h) => h.recorrente),
      ...projecao.map((p) => p.recorrente_estimado),
    ];
    extraordinarioData = [
      ...historico.map((h) => h.nao_recorrente),
      ...projecao.map((p) => p.nao_recorrente_estimado),
    ];
    markLineValue = dividendos.media_recorrente_12m;
  }

  const chartOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 12 },
      formatter: (params: any) => {
        if (!params || !params.length) return '';
        const monthName = params[0].axisValue;
        let html = `<div class="font-bold text-slate-200 mb-1 border-b border-slate-700 pb-1">${monthName}</div>`;
        let total = 0;
        params.forEach((item: any) => {
          const val = Number(item.value || 0);
          total += val;
          const colorDot = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${item.color};margin-right:6px;"></span>`;
          html += `<div class="flex justify-between gap-4 text-xs py-0.5">
            <span class="text-slate-400">${colorDot}${item.seriesName}:</span>
            <span class="font-mono font-semibold text-slate-200">R$ ${val.toFixed(2)}</span>
          </div>`;
        });
        html += `<div class="flex justify-between gap-4 text-xs font-bold pt-1 border-t border-slate-700/60 mt-1">
          <span class="text-amber-300">Total Distribuído:</span>
          <span class="font-mono text-emerald-400">R$ ${total.toFixed(2)}</span>
        </div>`;
        return html;
      },
    },
    legend: {
      data: ['Dividendo Recorrente', 'Não Recorrente / Extraordinário'],
      bottom: 0,
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 14,
      itemHeight: 10,
    },
    grid: {
      left: '2%',
      right: '2%',
      bottom: '12%',
      top: '12%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        interval: 0,
        rotate: categories.length > 12 ? 35 : 0,
      },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.4)', type: 'dashed' } },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        formatter: 'R$ {value}',
      },
    },
    series: [
      {
        name: 'Dividendo Recorrente',
        type: 'bar',
        stack: 'total',
        data: recorrenteData,
        itemStyle: {
          color: '#0284c7', // Sky / Cyan institucional
          borderRadius: extraordinarioData.some((v) => v > 0) ? [0, 0, 2, 2] : [4, 4, 0, 0],
        },
        markLine:
          markLineValue != null
            ? {
                silent: true,
                symbol: 'none',
                lineStyle: { color: '#38bdf8', type: 'dashed', width: 1.5 },
                data: [
                  {
                    yAxis: markLineValue,
                    label: {
                      formatter: `Média 12M: R$ ${markLineValue.toFixed(2)}`,
                      position: 'insideEndTop',
                      color: '#38bdf8',
                      fontSize: 10,
                    },
                  },
                ],
              }
            : undefined,
      },
      {
        name: 'Não Recorrente / Extraordinário',
        type: 'bar',
        stack: 'total',
        data: extraordinarioData,
        itemStyle: {
          color: '#f59e0b', // Amber / Ouro
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  };

  const getColchaoBadgeColor = (cor: string) => {
    if (cor === 'success') return 'bg-emerald-950/70 border-emerald-700/60 text-emerald-400';
    if (cor === 'warning') return 'bg-amber-950/70 border-amber-700/60 text-amber-400';
    return 'bg-rose-950/70 border-rose-700/60 text-rose-400';
  };

  const getSustentabilidadeBadgeColor = (cor: string) => {
    if (cor === 'success') return 'bg-emerald-950/70 border-emerald-700/60 text-emerald-400';
    if (cor === 'warning') return 'bg-amber-950/70 border-amber-700/60 text-amber-400';
    return 'bg-rose-950/70 border-rose-700/60 text-rose-400';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      {/* 1. Header do Card - Padrão: sem numeração e só 1ª letra maiúscula */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Coins className="w-5 h-5 text-emerald-400" />
            Distribuição de dividendos e projeção de resultados
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Evolução dos proventos de {ticker} nos últimos 12 meses, capacidade do colchão de reservas e estimativa de dividendos obrigatórios (Lei 8.668/93).
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="bg-slate-950/80 border border-slate-800 px-2.5 py-1 rounded text-slate-300">
            Reserva: <b className="text-indigo-400">R$ {fmt(dividendos.reserva_acumulada_cota)}/cota</b>
          </span>
          <span className="bg-slate-950/80 border border-slate-800 px-2.5 py-1 rounded text-slate-300">
            Próximo Estimado: <b className="text-emerald-400">R$ {fmt(dividendos.provento_projetado_mes)}/cota</b>
          </span>
        </div>
      </div>

      {/* 2. Grid de 4 Métricas Principais (KPI Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {/* KPI 1: Dividendo Recorrente Atual */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 flex flex-col justify-between hover:border-slate-700 transition">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="font-semibold flex items-center gap-1.5 text-slate-300">
                <Coins className="w-3.5 h-3.5 text-sky-400" />
                Dividendo Recorrente
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Último Mês</span>
            </div>
            <div className="text-xl font-bold font-mono text-white">
              R$ {fmt(dividendos.provento_atual)}
              <span className="text-xs font-normal text-slate-400 ml-1">/cota</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              FFO Operacional: <b className="text-slate-200">R$ {fmt(dividendos.ffo_cota)}</b>
            </div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between">
            <span
              className={`text-[10px] px-2 py-0.5 rounded font-medium border ${getSustentabilidadeBadgeColor(
                dividendos.status_cor
              )}`}
            >
              {dividendos.status_sustentabilidade}
            </span>
            <span className="text-[11px] font-mono text-sky-400 font-semibold">
              {fmt(dividendos.cobertura_ffo_pct, 1)}% Cob.
            </span>
          </div>
        </div>

        {/* KPI 2: Saldo de Reserva de Lucros */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 flex flex-col justify-between hover:border-slate-700 transition">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="font-semibold flex items-center gap-1.5 text-slate-300">
                <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                Saldo de Reserva
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Colchão</span>
            </div>
            <div className="text-xl font-bold font-mono text-indigo-300">
              R$ {fmt(dividendos.reserva_acumulada_cota)}
              <span className="text-xs font-normal text-slate-400 ml-1">/cota</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Autonomia: <b className="text-slate-200">{dividendos.meses_reserva_cobertura} meses</b> de proventos
            </div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between">
            <span
              className={`text-[10px] px-2 py-0.5 rounded font-medium border ${getColchaoBadgeColor(
                dividendos.cor_colchao
              )}`}
            >
              {dividendos.status_colchao}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">Reserva Retida</span>
          </div>
        </div>

        {/* KPI 3: Dividendo Não Recorrente Obrigatório (Lei 8.668/93) */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 flex flex-col justify-between hover:border-slate-700 transition">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="font-semibold flex items-center gap-1.5 text-slate-300">
                <Scale className="w-3.5 h-3.5 text-amber-400" />
                Não Recorrente Legal
              </span>
              <span className="text-[10px] text-amber-500/90 font-mono">Lei 8.668/93</span>
            </div>
            <div className="text-xl font-bold font-mono text-amber-400">
              {dividendos.extraordinario_estimado_fim_semestre > 0
                ? `+ R$ ${fmt(dividendos.extraordinario_estimado_fim_semestre)}`
                : 'R$ 0,00'}
              <span className="text-xs font-normal text-slate-400 ml-1">/cota</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Pico semestral: <b className="text-emerald-400">R$ {fmt(dividendos.provento_pico_fim_semestre)}</b>
            </div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between">
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/60 text-amber-300 font-medium flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {dividendos.meses_para_fechamento_semestre}m para fechamento
            </span>
            <span className="text-[10px] text-slate-500">Mín. 95% Caixa</span>
          </div>
        </div>

        {/* KPI 4: Dividendos Estimados para Próximos Meses */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 flex flex-col justify-between hover:border-slate-700 transition">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="font-semibold flex items-center gap-1.5 text-slate-300">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                Dividendo Estimado
              </span>
              <span className="text-[10px] text-emerald-500/90 font-mono">Guidance</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400">
              R$ {fmt(dividendos.provento_projetado_mes)}
              <span className="text-xs font-normal text-slate-400 ml-1">/mês</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Faixa: <b className="text-slate-200">{dividendos.guidance_faixa}</b>
            </div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between">
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-medium">
              Run-Rate Estável
            </span>
            <span className="text-[10px] text-emerald-400 font-mono font-medium flex items-center">
              Projeção 6M <ArrowUpRight className="w-3 h-3 ml-0.5" />
            </span>
          </div>
        </div>
      </div>

      {/* 3. Seletor de visualização do Gráfico */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-sky-400" />
          <span className="text-xs font-semibold text-slate-300">
            {viewMode === '12m' && 'Histórico de Proventos dos Últimos 12 Meses'}
            {viewMode === 'projecao' && 'Projeção de Rendimentos Futuros (Próximos 6 Meses)'}
            {viewMode === 'integrada' && 'Visão Integrada: Últimos 12 Meses + Projeção Futura (6 Meses)'}
          </span>
        </div>
        <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg p-0.5">
          <button
            onClick={() => setViewMode('12m')}
            className={`px-2.5 py-1 text-xs rounded transition font-medium ${
              viewMode === '12m' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Últimos 12M
          </button>
          <button
            onClick={() => setViewMode('projecao')}
            className={`px-2.5 py-1 text-xs rounded transition font-medium ${
              viewMode === 'projecao' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Projeção Futura
          </button>
          <button
            onClick={() => setViewMode('integrada')}
            className={`px-2.5 py-1 text-xs rounded transition font-medium ${
              viewMode === 'integrada' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Visão Integrada
          </button>
        </div>
      </div>

      {/* 4. Gráfico ECharts */}
      <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 mb-4">
        <ReactECharts
          option={chartOption}
          notMerge={true}
          lazyUpdate={true}
          style={{ height: '310px', width: '100%' }}
        />
        {viewMode === 'integrada' && (
          <div className="text-[10px] text-slate-500 text-right pr-2">
            * Meses com asterisco representam estimativas projetadas de proventos regulares e extraordinários legais.
          </div>
        )}
      </div>

      {/* 5. Banner Institucional e Base Legal (Lei 8.668/93) */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 flex items-start gap-3 text-xs">
        <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-slate-200 flex items-center gap-2">
            <span>Regulamentação Legal de Distribuição e Reserva</span>
            <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-400">
              CVM / Lei nº 8.668/93
            </span>
          </div>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            {dividendos.base_legal}
          </p>
          <div className="pt-1 text-[11px] text-slate-300 flex items-center gap-2">
            <span className="text-slate-500">Diagnóstico:</span>
            <span>{dividendos.desc_sustentabilidade}</span>
            {dividendos.desc_extraordinario && (
              <span className="text-amber-400 font-medium"> • {dividendos.desc_extraordinario}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
