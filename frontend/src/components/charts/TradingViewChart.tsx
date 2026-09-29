import React, { useEffect, useRef, useState } from 'react';
import {
  createChart,
  ColorType,
  CrosshairMode,
  CandlestickSeries,
  HistogramSeries,
} from 'lightweight-charts';
import type { IChartApi, ISeriesApi } from 'lightweight-charts';
import type { MarketCandle } from '../../types';

interface TradingViewChartProps {
  candles: MarketCandle[];
  ticker: string;
  onPeriodChange?: (period: string) => void;
  currentPeriod?: string;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  candles,
  ticker,
  onPeriodChange,
  currentPeriod = '1y',
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [hoverData, setHoverData] = useState<MarketCandle | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Criar chart com tema dark refinado
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 420,
      layout: {
        background: { type: ColorType.Solid, color: '#0f172a' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(51, 65, 85, 0.4)' },
        horzLines: { color: 'rgba(51, 65, 85, 0.4)' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#334155',
        autoScale: true,
      },
      timeScale: {
        borderColor: '#334155',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Series de Candlestick
    const candleSeries: ISeriesApi<'Candlestick'> = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    // Series de Volume
    const volumeSeries: ISeriesApi<'Histogram'> = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
    });

    chart.priceScale('volume').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    // Formatar e ordenar dados
    const sortedCandles = [...candles].sort(
      (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime()
    );

    const candleData = sortedCandles.map((c) => ({
      time: c.time.split('T')[0],
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }));

    const volumeData = sortedCandles.map((c) => ({
      time: c.time.split('T')[0],
      value: c.volume,
      color: c.close >= c.open ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)',
    }));

    if (candleData.length > 0) {
      candleSeries.setData(candleData as any);
      volumeSeries.setData(volumeData as any);
      chart.timeScale().fitContent();
    }

    // Crosshair listener para tooltip HUD
    chart.subscribeCrosshairMove((param) => {
      if (
        param.point === undefined ||
        !param.time ||
        param.point.x < 0 ||
        param.point.x > chartContainerRef.current!.clientWidth ||
        param.point.y < 0 ||
        param.point.y > 420
      ) {
        setHoverData(null);
      } else {
        const dateStr = typeof param.time === 'string' ? param.time : '';
        const match = sortedCandles.find((c) => c.time.startsWith(dateStr));
        if (match) {
          setHoverData(match);
        }
      }
    });

    // Resize observer
    const resizeObserver = new ResizeObserver((entries) => {
      if (entries.length === 0 || !entries[0].target) return;
      const newRect = entries[0].contentRect;
      chart.applyOptions({ width: newRect.width });
    });

    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [candles]);

  const periods = [
    { label: '1 Mês', value: '1mo' },
    { label: '6 Meses', value: '6mo' },
    { label: '1 Ano', value: '1y' },
    { label: '2 Anos', value: '2y' },
    { label: '5 Anos', value: '5y' },
  ];

  const lastCandle = candles[candles.length - 1];
  const activeCandle = hoverData || lastCandle;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col gap-3">
      {/* Top Bar with HUD & Period Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-lg tracking-wide">{ticker}</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
              B3 • DIÁRIO
            </span>
          </div>

          {activeCandle && (
            <div className="hidden sm:flex items-center gap-3 text-xs font-mono text-slate-300">
              <div>
                <span className="text-slate-500">Data: </span>
                <span className="text-slate-200">{activeCandle.time.split('T')[0]}</span>
              </div>
              <div>
                <span className="text-slate-500">Abe: </span>
                <span className="text-slate-200">
                  R$ {activeCandle.open != null ? activeCandle.open.toFixed(2) : '-'}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Máx: </span>
                <span className="text-emerald-400">
                  R$ {activeCandle.high != null ? activeCandle.high.toFixed(2) : '-'}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Mín: </span>
                <span className="text-rose-400">
                  R$ {activeCandle.low != null ? activeCandle.low.toFixed(2) : '-'}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Fech: </span>
                <span
                  className={
                    (activeCandle.close ?? 0) >= (activeCandle.open ?? 0)
                      ? 'text-emerald-400'
                      : 'text-rose-400'
                  }
                >
                  R$ {activeCandle.close != null ? activeCandle.close.toFixed(2) : '-'}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Vol: </span>
                <span className="text-sky-300">
                  {activeCandle.volume ? activeCandle.volume.toLocaleString('pt-BR') : '-'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Period Selector */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          {periods.map((p) => (
            <button
              key={p.value}
              onClick={() => onPeriodChange?.(p.value)}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                currentPeriod === p.value
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Canvas */}
      <div ref={chartContainerRef} className="w-full relative rounded overflow-hidden" />
      <div className="text-[11px] text-slate-500 text-right">
        Fonte de Cotações: B3 Oficial via Yahoo Finance • Gráficos TradingView Engine
      </div>
    </div>
  );
};
