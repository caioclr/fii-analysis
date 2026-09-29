import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { RadarData } from '../../types';

interface Radar5DChartProps {
  radarData: RadarData;
}

export const Radar5DChart: React.FC<Radar5DChartProps> = ({ radarData }) => {
  if (!radarData || !radarData.active_fii || !radarData.sector_benchmark) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex items-center justify-center min-h-[340px] text-slate-500 text-xs">
        Dados insuficientes para gerar o Radar 5D
      </div>
    );
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: {
        color: '#f8fafc',
      },
    },
    legend: {
      data: [radarData.active_fii.ticker, radarData.sector_benchmark.name],
      bottom: 0,
      textStyle: {
        color: '#94a3b8',
        fontSize: 12,
      },
    },
    radar: {
      indicator: (radarData.indicators || []).map((ind: string) => ({
        name: ind,
        max: 100,
      })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#38bdf8',
        fontWeight: 'bold',
        fontSize: 11,
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.6)',
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(15, 23, 42, 0.6)', 'rgba(30, 41, 59, 0.4)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(51, 65, 85, 0.8)',
        },
      },
    },
    series: [
      {
        name: 'Comparativo Multidimensional',
        type: 'radar',
        data: [
          {
            value: radarData.active_fii.values,
            name: radarData.active_fii.ticker,
            symbolSize: 6,
            lineStyle: {
              width: 3,
              color: '#38bdf8',
            },
            itemStyle: {
              color: '#38bdf8',
            },
            areaStyle: {
              color: 'rgba(56, 189, 248, 0.35)',
            },
          },
          {
            value: radarData.sector_benchmark.values,
            name: radarData.sector_benchmark.name,
            symbolSize: 4,
            lineStyle: {
              width: 2,
              type: 'dashed',
              color: '#a855f7',
            },
            itemStyle: {
              color: '#a855f7',
            },
            areaStyle: {
              color: 'rgba(168, 85, 247, 0.15)',
            },
          },
        ],
      },
    ],
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
      <h3 className="text-sm font-semibold text-slate-200 mb-2 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
        Radar 5D Institucional (FII vs Benchmark do Setor)
      </h3>
      <ReactECharts option={option} style={{ height: '340px', width: '100%' }} />
    </div>
  );
};
