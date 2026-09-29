import React, { useState, useEffect, useMemo } from 'react';
import { fiiApi } from '../api/client';
import type { FiiScreenerItem } from '../types';
import {
  Search,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  ArrowUpDown,
  ExternalLink,
  RotateCcw,
} from 'lucide-react';

interface FiiScreenerViewProps {
  onSelectFii: (ticker: string) => void;
  onCompareSector: (segment: string, ticker: string) => void;
}

type SortField =
  | 'ticker'
  | 'nome'
  | 'name'
  | 'segmento'
  | 'segment'
  | 'preco_atual'
  | 'close_price'
  | 'pvp'
  | 'dy_anual'
  | 'dy_12m'
  | 'liquidez_diaria'
  | 'adtv_milhoes'
  | 'cotistas'
  | 'total_shareholders'
  | 'vacancia_fisica'
  | 'vacancy_pct'
  | 'score_geral';

const fmt = (val?: number | null, decimals = 2): string => {
  if (val == null || isNaN(val)) return '-';
  return val.toFixed(decimals);
};

export const FiiScreenerView: React.FC<FiiScreenerViewProps> = ({
  onSelectFii,
  onCompareSector,
}) => {
  const [items, setItems] = useState<FiiScreenerItem[]>([]);

  const [segmentCounts, setSegmentCounts] = useState<Record<string, number>>({});
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  // Filtros
  const [search, setSearch] = useState<string>('');
  const [selectedSegment, setSelectedSegment] = useState<string>('');
  const [maxPvp, setMaxPvp] = useState<string>('');
  const [minDy, setMinDy] = useState<string>('');
  const [minLiquidez, setMinLiquidez] = useState<string>('');
  const [maxVacancia, setMaxVacancia] = useState<string>('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState<boolean>(false);

  // Ordenação
  const [sortField, setSortField] = useState<SortField>('liquidez_diaria');
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  // Paginação
  const [page, setPage] = useState<number>(1);
  const pageSize = 25;

  const fetchScreenerData = async () => {
    try {
      setLoading(true);
      const res = await fiiApi.getScreener({
        search: search.trim() || undefined,
        segment: selectedSegment || undefined,
        max_pvp: maxPvp ? parseFloat(maxPvp) : undefined,
        min_dy: minDy ? parseFloat(minDy) : undefined,
        min_liquidez: minLiquidez ? parseFloat(minLiquidez) * 1000 : undefined,
        max_vacancia: maxVacancia ? parseFloat(maxVacancia) : undefined,
        page: 1,
        page_size: 400, // Pegar catálogo completo para ordenação instantânea no cliente
      });

      setItems(res.items);
      setSegmentCounts(res.segment_counts || {});
      setTotal(res.total);
    } catch (err) {
      console.error('Erro ao buscar dados do screener:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchScreenerData();
    }, 200);
    return () => clearTimeout(timer);
  }, [search, selectedSegment, maxPvp, minDy, minLiquidez, maxVacancia]);

  // Lista ordenada
  const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => {
      let valA: any = (a as any)[sortField];
      let valB: any = (b as any)[sortField];

      if (sortField === 'preco_atual') {
        valA = a.preco_atual ?? a.close_price ?? 0;
        valB = b.preco_atual ?? b.close_price ?? 0;
      } else if (sortField === 'dy_anual') {
        valA = a.dy_anual ?? a.dy_12m ?? 0;
        valB = b.dy_anual ?? b.dy_12m ?? 0;
      } else if (sortField === 'liquidez_diaria') {
        valA = a.liquidez_diaria ?? ((a.adtv_milhoes ?? 0) * 1_000_000);
        valB = b.liquidez_diaria ?? ((b.adtv_milhoes ?? 0) * 1_000_000);
      } else if (sortField === 'vacancia_fisica') {
        valA = a.vacancia_fisica ?? a.vacancy_pct ?? 0;
        valB = b.vacancia_fisica ?? b.vacancy_pct ?? 0;
      } else if (sortField === 'nome') {
        valA = a.nome ?? a.name ?? '';
        valB = b.nome ?? b.name ?? '';
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
  }, [items, sortField, sortAsc]);

  const totalPages = Math.ceil(sortedItems.length / pageSize) || 1;
  const paginatedItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return sortedItems.slice(start, start + pageSize);
  }, [sortedItems, page, pageSize]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false); // default desc for financial metrics
    }
  };

  const resetFilters = () => {
    setSearch('');
    setSelectedSegment('');
    setMaxPvp('');
    setMinDy('');
    setMinLiquidez('');
    setMaxVacancia('');
    setPage(1);
  };

  const segments = [
    { id: '', label: 'Todos os FIIs', count: total },
    { id: 'LOGISTICA', label: 'Logística', count: segmentCounts['LOGISTICA'] || 0 },
    { id: 'PAPEL', label: 'Papel (CRIs)', count: segmentCounts['PAPEL'] || 0 },
    { id: 'SHOPPING', label: 'Shoppings', count: segmentCounts['SHOPPING'] || 0 },
    { id: 'LAJES', label: 'Lajes Corp.', count: segmentCounts['LAJES'] || 0 },
    { id: 'FOF', label: 'Fundos de Fundos', count: segmentCounts['FOF'] || 0 },
    { id: 'HIBRIDO', label: 'Híbridos', count: segmentCounts['HIBRIDO'] || 0 },
    { id: 'AGRO', label: 'Fiagros / Agro', count: segmentCounts['AGRO'] || 0 },
  ];

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Top Search & Filter Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Search Input */}
          <div className="relative flex-1 min-w-[280px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Buscar por ticker ou nome (ex: HGLG11, MXRF11, XPML11)..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className={`flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-semibold border transition cursor-pointer ${
                showAdvancedFilters
                  ? 'bg-blue-600/20 border-blue-500/50 text-blue-300'
                  : 'bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>Filtros Quantitativos</span>
              {showAdvancedFilters ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>

            {(search || selectedSegment || maxPvp || minDy || minLiquidez || maxVacancia) && (
              <button
                onClick={resetFilters}
                className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-slate-950 border border-slate-800 hover:bg-slate-800 transition cursor-pointer"
                title="Limpar todos os filtros"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Limpar</span>
              </button>
            )}
          </div>
        </div>

        {/* Segment Tabs */}
        <div className="flex overflow-x-auto gap-2 pb-1 scrollbar-none">
          {segments.map((seg) => (
            <button
              key={seg.id}
              onClick={() => {
                setSelectedSegment(seg.id);
                setPage(1);
              }}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition cursor-pointer ${
                selectedSegment === seg.id
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'bg-slate-950 border border-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <span>{seg.label}</span>
              {seg.count > 0 && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                    selectedSegment === seg.id
                      ? 'bg-blue-700 text-white'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {seg.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Collapsible Advanced Filters */}
        {showAdvancedFilters && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-3 border-t border-slate-800/80">
            <div>
              <label className="text-xs text-slate-400 block mb-1">P/VP Máximo</label>
              <input
                type="number"
                step="0.05"
                placeholder="Ex: 1.00 (Sem ágio)"
                value={maxPvp}
                onChange={(e) => {
                  setMaxPvp(e.target.value);
                  setPage(1);
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1">DY 12M Mínimo (%)</label>
              <input
                type="number"
                step="0.5"
                placeholder="Ex: 9.0"
                value={minDy}
                onChange={(e) => {
                  setMinDy(e.target.value);
                  setPage(1);
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1">
                Liquidez Mínima (Mil R$/dia)
              </label>
              <input
                type="number"
                step="100"
                placeholder="Ex: 500 (R$ 500 mil/dia)"
                value={minLiquidez}
                onChange={(e) => {
                  setMinLiquidez(e.target.value);
                  setPage(1);
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1">Vacância Máxima (%)</label>
              <input
                type="number"
                step="1"
                placeholder="Ex: 15"
                value={maxVacancia}
                onChange={(e) => {
                  setMaxVacancia(e.target.value);
                  setPage(1);
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* Main Results Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden flex flex-col">
        {/* Table Stats Header */}
        <div className="px-5 py-3.5 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Mostrando <span className="font-bold text-white font-mono">{sortedItems.length}</span>{' '}
            fundos imobiliários encontrados
          </div>
          <div className="text-[11px] text-slate-500">
            Dica: Clique na linha para abrir o Dossiê Completo
          </div>
        </div>

        {/* Table Element */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/40">
                <th
                  onClick={() => handleSort('ticker')}
                  className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Ticker</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('nome')}
                  className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Fundo Imobiliário</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('segmento')}
                  className="py-3 px-3 font-semibold cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Segmento</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('preco_atual')}
                  className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Cotação</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('pvp')}
                  className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>P/VP</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('dy_anual')}
                  className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>DY 12M</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('liquidez_diaria')}
                  className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>ADTV</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('vacancia_fisica')}
                  className="py-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Vacância</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('score_geral')}
                  className="py-3 px-3 font-semibold text-center cursor-pointer hover:text-white transition"
                >
                  <div className="flex items-center justify-center gap-1.5">
                    <span>Score (0-10)</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>
                <th className="py-3 px-3 font-semibold text-center">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400 font-sans">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <span>Consultando dados de 396 FIIs na BolsaAI...</span>
                    </div>
                  </td>
                </tr>
              ) : paginatedItems.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400 font-sans">
                    Nenhum fundo encontrado com os filtros selecionados.
                  </td>
                </tr>
              ) : (
                paginatedItems.map((fii) => (
                  <tr
                    key={fii.ticker}
                    onClick={() => onSelectFii(fii.ticker)}
                    className="hover:bg-slate-800/50 cursor-pointer transition group"
                  >
                    {/* Ticker */}
                    <td className="py-3 px-4 font-bold text-white group-hover:text-blue-400 transition">
                      <div className="flex items-center gap-2">
                        <span>{fii.ticker}</span>
                      </div>
                    </td>

                    {/* Nome */}
                    <td className="py-3 px-4 font-sans text-slate-300 max-w-[220px] truncate">
                      {fii.nome}
                    </td>

                    {/* Segmento */}
                    <td className="py-3 px-3 font-sans">
                      <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300 border border-slate-700">
                        {fii.segmento}
                      </span>
                    </td>

                    {/* Preço */}
                    <td className="py-3 px-3 text-right text-slate-200">
                      R$ {fmt(fii.preco_atual ?? fii.close_price)}
                    </td>

                    {/* P/VP */}
                    <td
                      className={`py-3 px-3 text-right font-bold ${
                        (fii.pvp ?? 0) <= 0
                          ? 'text-slate-500'
                          : (fii.pvp ?? 0) <= 1.0
                          ? 'text-emerald-400'
                          : 'text-amber-400'
                      }`}
                    >
                      {(fii.pvp ?? 0) > 0 ? fmt(fii.pvp) : '-'}
                    </td>

                    {/* DY 12M */}
                    <td className="py-3 px-3 text-right font-bold text-emerald-400">
                      {(fii.dy_anual ?? fii.dy_12m ?? 0) > 0
                        ? `${fmt(fii.dy_anual ?? fii.dy_12m)}%`
                        : '-'}
                    </td>

                    {/* ADTV */}
                    <td className="py-3 px-3 text-right text-sky-300">
                      {(fii.liquidez_diaria ?? 0) > 0
                        ? `R$ ${((fii.liquidez_diaria ?? 0) / 1000).toLocaleString('pt-BR', {
                            maximumFractionDigits: 0,
                          })}k`
                        : fii.adtv_milhoes
                        ? `R$ ${fmt(fii.adtv_milhoes, 1)}M`
                        : '-'}
                    </td>

                    {/* Vacância */}
                    <td className="py-3 px-3 text-right text-slate-300">
                      {fii.vacancia_fisica != null
                        ? `${fmt(fii.vacancia_fisica, 1)}%`
                        : fii.vacancy_pct != null
                        ? `${fmt(fii.vacancy_pct, 1)}%`
                        : '-'}
                    </td>

                    {/* Score (0 a 10) */}
                    <td className="py-3 px-3 text-center">
                      {(() => {
                        const raw = fii.score_geral ?? 7.0;
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

                    {/* Ações */}
                    <td
                      className="py-3 px-3 text-center"
                      onClick={(e) => {
                        e.stopPropagation();
                      }}
                    >
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => onSelectFii(fii.ticker)}
                          className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition cursor-pointer"
                          title="Ver Dossiê e Valuation"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => onCompareSector(fii.segment_code || fii.segmento_canonico || 'LOGISTICA', fii.ticker)}
                          className="px-2 py-0.5 rounded text-[10px] bg-slate-800 hover:bg-blue-600 text-slate-300 hover:text-white transition font-sans cursor-pointer"
                          title="Comparar com pares do mesmo setor"
                        >
                          Pares
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="px-5 py-3 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <div>
              Página <span className="font-bold text-white font-mono">{page}</span> de{' '}
              <span className="font-bold text-white font-mono">{totalPages}</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-3 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                Próxima
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
