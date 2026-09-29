import React from 'react';
import { Printer, RefreshCw } from 'lucide-react';
import type { PricingSettings } from '../../types';

interface HeaderProps {
  currentView: string;
  activeTicker: string;
  pricingSettings: PricingSettings | null;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentView,
  activeTicker,
  pricingSettings,
  onRefresh,
  isRefreshing,
}) => {
  const getTitle = () => {
    switch (currentView) {
      case 'screener':
        return {
          title: 'Screener & Varredura de FIIs',
          subtitle: 'Filtros em tempo real sobre os 396 Fundos Imobiliários da B3',
        };
      case 'details':
        return {
          title: activeTicker ? `Dossiê Fundamentalista: ${activeTicker}` : 'Dossiê do FII',
          subtitle: 'Raio-X financeiro, portfólio físico/crédito e simulador de valuation',
        };
      case 'compare':
        return {
          title: 'Comparador Setorial & Pares',
          subtitle: 'Pódio de 5 Selos, Radar 5D Multidimensional e Matriz 2x2',
        };
      case 'settings':
        return {
          title: 'Configuração de Parâmetros Macroeconômicos',
          subtitle: 'Taxas de referência NTN-B 2035, IPCA e spreads institucionais',
        };
      default:
        return {
          title: 'Analisys Pro - Inteligência de FIIs',
          subtitle: 'Plataforma Quantitativa e Fundamentalista',
        };
    }
  };

  const info = getTitle();

  const handlePrint = () => {
    window.print();
  };

  return (
    <header className="no-print bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-20">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
          {info.title}
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">{info.subtitle}</p>
      </div>

      {/* Right Controls: Macro Indicators + Print Button + Refresh */}
      <div className="flex items-center gap-3">
        {/* Macro Indicators Pills */}
        <div className="hidden lg:flex items-center gap-2 text-xs font-mono">
          <div className="bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg flex items-center gap-1.5">
            <span className="text-slate-500 font-sans text-[11px]">NTN-B 2035:</span>
            <span className="font-bold text-sky-400">
              {(pricingSettings?.ntnb_reference_rate ?? pricingSettings?.ntnb_2035_rate ?? 6.5).toFixed(2)}%
            </span>
          </div>
          <div className="bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg flex items-center gap-1.5">
            <span className="text-slate-500 font-sans text-[11px]">IPCA Proj:</span>
            <span className="font-bold text-amber-400">
              {(pricingSettings?.projected_ipca ?? 4.0).toFixed(2)}%
            </span>
          </div>
          <div className="bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg flex items-center gap-1.5">
            <span className="text-slate-500 font-sans text-[11px]">Spread Real:</span>
            <span className="font-bold text-indigo-400">
              +{(pricingSettings?.real_risk_spread ?? pricingSettings?.real_risk_spread_default ?? 2.0).toFixed(2)}%
            </span>
          </div>
        </div>

        {/* Print Button (active on details view) */}
        {currentView === 'details' && (
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition cursor-pointer"
            title="Exportar Dossiê em PDF ou Imprimir (Ctrl+P)"
          >
            <Printer className="w-4 h-4" />
            <span className="hidden sm:inline">Exportar / Imprimir</span>
          </button>
        )}

        {/* Refresh Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition disabled:opacity-50 cursor-pointer"
            title="Atualizar Dados"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        )}
      </div>
    </header>
  );
};
