import React, { useState, useEffect } from 'react';
import { fiiApi } from '../api/client';
import type {
  SectorComparisonResponse,
  ScreenerFiiItem,
  SectorPodiumBadge,
  SectorRadarItem,
  RadarData,
} from '../types';
import { Radar5DChart } from '../components/charts/Radar5DChart';
import { ScatterValuationChart } from '../components/charts/ScatterValuationChart';
import {
  Trophy,
  Award,
  ShieldCheck,
  TrendingUp,
  Flame,
  ArrowUpDown,
  ExternalLink,
  Layers,
} from 'lucide-react';

interface FiiSectorComparatorViewProps {
  initialSegment?: string;
  initialTicker?: string;
  onSelectFii: (ticker: string) => void;
}

const fmt = (val?: number | null, decimals = 2): string => {
  if (val == null || isNaN(val)) return '-';
  return val.toFixed(decimals);
};

const BADGE_THEMES: Record<string, { border: string; bg: string; text: string; icon: any }> = {
  lider_geral: { border: 'border-amber-500/80', bg: 'bg-amber-950/20', text: 'text-amber-400', icon: Trophy },
  melhor_preco: { border: 'border-emerald-500/80', bg: 'bg-emerald-950/20', text: 'text-emerald-400', icon: Award },
  maior_renda: { border: 'border-sky-500/80', bg: 'bg-sky-950/20', text: 'text-sky-400', icon: TrendingUp },
  mais_seguro: { border: 'border-indigo-500/80', bg: 'bg-indigo-950/20', text: 'text-indigo-400', icon: ShieldCheck },
  maior_extraordinario: { border: 'border-purple-500/80', bg: 'bg-purple-950/20', text: 'text-purple-400', icon: Flame },
};

export const FiiSectorComparatorView: React.FC<FiiSectorComparatorViewProps> = ({
  initialSegment = 'LOGISTICA',
  initialTicker = '',
  onSelectFii,
}) => {
  const [selectedSegment, setSelectedSegment] = useState<string>(initialSegment || 'LOGISTICA');
  const [activeTicker, setActiveTicker] = useState<string>(initialTicker || '');
  const [data, setData] = useState<SectorComparisonResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Ordenação da Matriz de Pares
  const [sortField, setSortField] = useState<keyof ScreenerFiiItem>('score_geral');
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const segments = [
    { id: 'LOGISTICA', label: 'Logística' },
    { id: 'PAPEL', label: 'Papel (CRIs)' },
    { id: 'SHOPPING', label: 'Shoppings' },
    { id: 'LAJES', label: 'Lajes Corporativas' },
    { id: 'FOF', label: 'Fundos de Fundos (FOFs)' },
    { id: 'HIBRIDO', label: 'Híbridos' },
    { id: 'AGRO', label: 'Fiagros / Agro' },
  ];

  const loadComparison = async (seg: string, tick: string) => {
    try {
      setLoading(true);
      const res = await fiiApi.getSectorComparison(seg, tick);
      setData(res);
      if (!tick && res.matrix.length > 0) {
        setActiveTicker(res.matrix[0].ticker);
      }
    } catch (err) {
      console.error('Erro ao carregar comparador setorial:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComparison(selectedSegment, activeTicker);
  }, [selectedSegment]);

  const handleSelectTicker = (ticker: string) => {
    setActiveTicker(ticker);
    loadComparison(selectedSegment, ticker);
  };

  const handleSort = (field: keyof ScreenerFiiItem) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const podiumBadges = React.useMemo<SectorPodiumBadge[]>(() => {
    if (!data?.podium) return [];
    if (Array.isArray(data.podium)) return data.podium;
    const badges: SectorPodiumBadge[] = [];
    const p = data.podium as any;
    for (const [key, val] of Object.entries(p)) {
      if (val && typeof val === 'object') {
        const v = val as any;
        badges.push({
          id: key,
          title: v.titulo || key,
          icon: '⭐',
          ticker: v.ticker || '',
          destaque_label: v.titulo || '',
          valor_label: v.ticker || '',
          descricao: v.motivo || '',
        });
      }
    }
    return badges;
  }, [data?.podium]);

  const formattedRadarData = React.useMemo<RadarData>(() => {
    const indicators = [
      'Desconto (P/VP)',
      'Retorno Real',
      'Solvência',
      'Qualidade',
      'Reserva Lucros',
    ];

    if (!data?.radar || !Array.isArray(data.radar) || data.radar.length === 0) {
      return {
        indicators,
        active_fii: { ticker: activeTicker || 'FII', values: [50, 50, 50, 50, 50] },
        sector_benchmark: { name: 'Média do Setor', values: [50, 50, 50, 50, 50] },
      };
    }

    const items = data.radar as SectorRadarItem[];
    const activeItem = items.find((r) => r.ticker === activeTicker) || items[0];

    const avg = (fn: (r: SectorRadarItem) => number) => {
      const sum = items.reduce((acc, cur) => acc + (fn(cur) || 0), 0);
      return Math.round((sum / items.length) * 10) / 10;
    };

    const benchmarkValues = [
      avg((r) => r.desconto),
      avg((r) => r.retorno_real),
      avg((r) => r.solvencia),
      avg((r) => r.qualidade),
      avg((r) => r.reserva),
    ];

    const activeValues = [
      activeItem.desconto,
      activeItem.retorno_real,
      activeItem.solvencia,
      activeItem.qualidade,
      activeItem.reserva,
    ];

    return {
      indicators,
      active_fii: { ticker: activeItem.ticker, values: activeValues },
      sector_benchmark: { name: 'Média do Setor', values: benchmarkValues },
    };
  }, [data?.radar, activeTicker]);

  const sortedMatrix = React.useMemo(() => {
    if (!data?.matrix) return [];
    return [...data.matrix].sort((a, b) => {
      let valA: any = (a as any)[sortField];
      let valB: any = (b as any)[sortField];

      if (sortField === 'preco_atual') {
        valA = a.preco_atual ?? a.preco ?? a.close_price ?? 0;
        valB = b.preco_atual ?? b.preco ?? b.close_price ?? 0;
      } else if (sortField === 'score_geral') {
        valA = a.score_geral ?? a.score ?? 0;
        valB = b.score_geral ?? b.score ?? 0;
      }

      if (typeof valA === 'string') {
        valA = valA.toLowerCase();
        valB = (valB || '').toLowerCase();
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }

      valA = valA || 0;
      valB = valB || 0;
      return sortAsc ? valA - valB : valB - valA;
    });
  }, [data?.matrix, sortField, sortAsc]);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Top Segment Selector Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-blue-400" />
              Comparador Setorial de Fundos Imobiliários
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Análise cruzada de pares homogêneos, pódio de liderança e fronteira de eficiência.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Setor Atual:</span>
            <span className="px-3 py-1 rounded-lg text-xs font-bold bg-blue-600/20 text-blue-300 border border-blue-500/40">
              {segments.find((s) => s.id === selectedSegment)?.label || selectedSegment}
            </span>
          </div>
        </div>

        {/* Segment Tabs */}
        <div className="flex overflow-x-auto gap-2 pb-1 scrollbar-none">
          {segments.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setSelectedSegment(s.id);
                setActiveTicker('');
              }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer ${
                selectedSegment === s.id
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                  : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {loading || !data ? (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-3 text-slate-400">
          <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs font-medium">
            Calculando métricas setoriais e pódios de liderança...
          </span>
        </div>
      ) : (
        <>
          {/* PÓDIO DE 5 SELOS DE LIDERANÇA */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Trophy className="w-4 h-4 text-amber-400" />
                Pódio de Liderança Setorial (5 Selos Institucionais)
              </h3>
              <span className="text-xs text-slate-400">
                Pares analisados: <b className="text-white font-mono">{data.tickers?.length || data.matrix?.length || 0}</b>
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
              {podiumBadges.map((badge) => {
                const theme = BADGE_THEMES[badge.id] || BADGE_THEMES.lider_geral;
                const IconComp = theme.icon;
                const isSelected = activeTicker === badge.ticker;

                return (
                  <div
                    key={badge.id}
                    onClick={() => handleSelectTicker(badge.ticker)}
                    className={`bg-slate-900 border rounded-xl p-4 flex flex-col justify-between cursor-pointer transition hover:scale-[1.02] ${
                      isSelected ? `${theme.border} ${theme.bg}` : 'border-slate-800'
                    }`}
                  >
                    <div>
                      <div className={`flex items-center justify-between ${theme.text}`}>
                        <span className="text-[11px] font-bold uppercase tracking-wider">
                          {badge.title.replace(/^[^\w\s]+/, '').trim() || badge.title}
                        </span>
                        <IconComp className="w-4 h-4" />
                      </div>
                      <div className="my-2">
                        <span className="text-xl font-black text-white font-mono">
                          {badge.ticker}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-[11px] text-slate-400 line-clamp-3">
                        {badge.descricao}
                      </p>
                      <span className={`text-[10px] font-bold block mt-2 ${theme.text}`}>
                        {badge.destaque_label || badge.valor_label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* CHARTS DUAIS: RADAR 5D + SCATTER 2X2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Radar5DChart radarData={formattedRadarData} />
            <ScatterValuationChart
              scatterData={data.scatter}
              onSelectTicker={handleSelectTicker}
              activeTicker={activeTicker}
            />
          </div>

          {/* MATRIZ DE PARES SETORIAIS */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden flex flex-col">
            <div className="px-5 py-4 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">
                  Matriz Comparativa de Pares ({segments.find((s) => s.id === selectedSegment)?.label})
                </h3>
                <p className="text-xs text-slate-400">
                  FII selecionado para o Radar 5D:{' '}
                  <span className="text-cyan-400 font-bold font-mono">{activeTicker}</span>
                </p>
              </div>

              <span className="text-xs text-slate-500">
                Clique em um fundo para focar ou ver Dossiê
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/40">
                    <th
                      onClick={() => handleSort('ticker')}
                      className="py-3 px-4 font-semibold cursor-pointer hover:text-white"
                    >
                      <div className="flex items-center gap-1.5">
                        <span>Ticker</span>
                        <ArrowUpDown className="w-3 h-3 text-slate-500" />
                      </div>
                    </th>
                    <th
                      onClick={() => handleSort('nome')}
                      className="py-3 px-4 font-semibold cursor-pointer hover:text-white"
                    >
                      Fundo
                    </th>
                    <th
                      onClick={() => handleSort('preco_atual')}
                      className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white"
                    >
                      Cotação
                    </th>
                    <th
                      onClick={() => handleSort('pvp')}
                      className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white"
                    >
                      P/VP
                    </th>
                    <th
                      onClick={() => handleSort('dy_anual')}
                      className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white"
                    >
                      DY 12M
                    </th>
                    <th
                      onClick={() => handleSort('liquidez_diaria')}
                      className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white"
                    >
                      ADTV
                    </th>
                    <th
                      onClick={() => handleSort('vacancia_fisica')}
                      className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white"
                    >
                      Vacância
                    </th>
                    <th
                      onClick={() => handleSort('score_geral')}
                      className="py-3 px-3 font-semibold text-center cursor-pointer hover:text-white"
                    >
                      Score (0-10)
                    </th>
                    <th className="py-3 px-3 font-semibold text-center">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {sortedMatrix.map((peer) => {
                    const isActive = peer.ticker === activeTicker;
                    return (
                      <tr
                        key={peer.ticker}
                        onClick={() => handleSelectTicker(peer.ticker)}
                        className={`cursor-pointer transition ${
                          isActive
                            ? 'bg-blue-600/15 border-l-4 border-l-blue-500 text-white font-bold'
                            : 'hover:bg-slate-800/40 text-slate-300'
                        }`}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            {isActive && <div className="w-1.5 h-1.5 rounded-full bg-cyan-400"></div>}
                            <span className={isActive ? 'text-cyan-300' : 'text-white'}>
                              {peer.ticker}
                            </span>
                          </div>
                        </td>

                        <td className="py-3 px-4 font-sans text-slate-300 max-w-[200px] truncate">
                          {peer.nome}
                        </td>

                        <td className="py-3 px-3 text-right">
                          R$ {fmt(peer.preco_atual ?? peer.close_price)}
                        </td>

                        <td
                          className={`py-3 px-3 text-right ${
                            (peer.pvp ?? 1.0) <= 1.0 ? 'text-emerald-400' : 'text-amber-400'
                          }`}
                        >
                          {(peer.pvp ?? 0) > 0 ? fmt(peer.pvp) : '-'}
                        </td>

                        <td className="py-3 px-3 text-right text-emerald-400">
                          {(peer.dy_anual ?? peer.dy_12m ?? 0) > 0 ? `${fmt(peer.dy_anual ?? peer.dy_12m)}%` : '-'}
                        </td>

                        <td className="py-3 px-3 text-right text-sky-300">
                          {(peer.liquidez_diaria ?? 0) > 0
                            ? `R$ ${fmt((peer.liquidez_diaria ?? 0) / 1000, 0)}k`
                            : peer.adtv_milhoes
                            ? `R$ ${fmt(peer.adtv_milhoes, 1)}M`
                            : '-'}
                        </td>

                        <td className="py-3 px-3 text-right text-slate-300">
                          {peer.vacancia_fisica != null
                            ? `${fmt(peer.vacancia_fisica, 1)}%`
                            : peer.vacancy_pct != null
                            ? `${fmt(peer.vacancy_pct, 1)}%`
                            : '-'}
                        </td>

                        <td className="py-3 px-3 text-center">
                          {(() => {
                            const raw = peer.score_geral ?? peer.score ?? 7.0;
                            const score = raw > 10 ? raw / 10 : raw;
                            const colorClass =
                              score >= 8.0
                                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                                : score >= 7.0
                                ? 'bg-sky-950 text-sky-300 border border-sky-800'
                                : 'bg-amber-950 text-amber-300 border border-amber-800';
                            return (
                              <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${colorClass}`}>
                                {score.toFixed(1)}
                              </span>
                            );
                          })()}
                        </td>

                        <td
                          className="py-3 px-3 text-center"
                          onClick={(e) => {
                            e.stopPropagation();
                          }}
                        >
                          <button
                            onClick={() => onSelectFii(peer.ticker)}
                            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-blue-600 text-slate-300 hover:text-white transition text-[11px] font-sans flex items-center gap-1 mx-auto cursor-pointer"
                            title="Ver Dossiê Completo"
                          >
                            <span>Dossiê</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
