import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { ScatterPoint } from '../../types';

interface ScatterValuationChartProps {
  scatterData: ScatterPoint[];
  onSelectTicker?: (ticker: string) => void;
  activeTicker?: string;
}

export const ScatterValuationChart: React.FC<ScatterValuationChartProps> = ({
  scatterData,
  onSelectTicker,
  activeTicker,
}) => {
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      formatter: (param: any) => {
        const item = param.data;
        if (!item) return '';
        const pvpStr = item.value?.[0] != null && !isNaN(item.value[0]) ? item.value[0].toFixed(2) : '-';
        const scoreStr = item.value?.[1] != null && !isNaN(item.value[1]) ? item.value[1].toFixed(1) : '-';
        const dyStr = item.dy != null && !isNaN(item.dy) ? item.dy.toFixed(2) : '-';
        return `
          <div style="font-family: sans-serif; font-size: 12px; color: #f8fafc; padding: 4px;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #38bdf8;">${item.ticker || ''}</div>
            <div>P/VP: <b>${pvpStr}</b></div>
            <div>Score Qualidade: <b>${scoreStr} / 100</b></div>
            <div>DY Anual: <b>${dyStr}%</b></div>
            <div style="color: #94a3b8; margin-top: 4px; font-size: 11px;">Quadrante: ${item.quadrante || '-'}</div>
          </div>
        `;
      },
      backgroundColor: '#0f172a',
      borderColor: '#334155',
    },
    grid: {
      left: '10%',
      right: '8%',
      top: '12%',
      bottom: '12%',
    },
    xAxis: {
      name: 'P/VP (Valuation)',
      nameLocation: 'middle',
      nameGap: 28,
      nameTextStyle: { color: '#94a3b8', fontSize: 11 },
      min: 0.6,
      max: 1.3,
      splitLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.4)',
          type: 'dashed',
        },
      },
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' },
    },
    yAxis: {
      name: 'Score de Qualidade Fundamentalista',
      nameLocation: 'middle',
      nameGap: 35,
      nameTextStyle: { color: '#94a3b8', fontSize: 11 },
      min: 30,
      max: 100,
      splitLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.4)',
          type: 'dashed',
        },
      },
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: any) => {
          return data.ticker === activeTicker ? 24 : 14;
        },
        data: (scatterData || []).map((d) => {
          const scoreVal = d.score_qualidade ?? (d.score != null ? (d.score <= 10 ? d.score * 10 : d.score) : 70);
          const dyVal = d.dy_anual ?? d.dy ?? 0;
          return {
            name: d.ticker,
            ticker: d.ticker,
            value: [d.pvp, scoreVal],
            dy: dyVal,
            quadrante: d.quadrante,
            itemStyle: {
              color:
                d.ticker === activeTicker
                  ? '#f59e0b'
                  : d.pvp <= 1.0 && scoreVal >= 70
                  ? '#10b981' // Oportunidade
                  : d.pvp > 1.0 && scoreVal >= 70
                  ? '#38bdf8' // Qualidade Premium
                  : d.pvp <= 1.0 && scoreVal < 70
                  ? '#eab308' // Armadilha de valor
                  : '#ef4444', // Risco
              borderColor: d.ticker === activeTicker ? '#ffffff' : 'transparent',
              borderWidth: d.ticker === activeTicker ? 3 : 0,
              shadowBlur: d.ticker === activeTicker ? 12 : 4,
              shadowColor: d.ticker === activeTicker ? '#f59e0b' : 'rgba(0,0,0,0.5)',
            },
            label: {
              show: true,
              formatter: '{b}',
              position: 'top',
              color: '#e2e8f0',
              fontSize: 10,
              fontWeight: d.ticker === activeTicker ? 'bold' : 'normal',
            },
          };
        }),
        markLine: {
          silent: true,
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.35)',
            type: 'solid',
            width: 1.5,
          },
          data: [{ xAxis: 1.0 }, { yAxis: 70 }],
        },
      },
    ],
  };

  const onChartClick = (params: any) => {
    if (params.data && params.data.ticker && onSelectTicker) {
      onSelectTicker(params.data.ticker);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          Matriz 2x2: Valuation (P/VP) vs Qualidade Fundamentalista
        </h3>
        <span className="text-[11px] text-slate-400">Clique em um ponto para inspecionar</span>
      </div>

      <ReactECharts
        option={option}
        style={{ height: '340px', width: '100%' }}
        onEvents={{ click: onChartClick }}
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-[11px]">
        <div className="flex items-center gap-1.5 text-emerald-400">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div>
          <span>Oportunidade (P/VP &le; 1, Qualidade &ge; 70)</span>
        </div>
        <div className="flex items-center gap-1.5 text-sky-400">
          <div className="w-2.5 h-2.5 rounded-full bg-sky-500"></div>
          <span>Qualidade Premium (P/VP &gt; 1, Qualidade &ge; 70)</span>
        </div>
        <div className="flex items-center gap-1.5 text-yellow-400">
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500"></div>
          <span>Armadilha de Valor (P/VP &le; 1, Qualidade &lt; 70)</span>
        </div>
        <div className="flex items-center gap-1.5 text-rose-400">
          <div className="w-2.5 h-2.5 rounded-full bg-rose-500"></div>
          <span>Risco Elevado (P/VP &gt; 1, Qualidade &lt; 70)</span>
        </div>
      </div>
    </div>
  );
};
