import React, { useState } from 'react';
import {
  Search,
  FileText,
  Scale,
  Settings,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Zap,
  Building,
} from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string, ticker?: string) => void;
  activeTicker: string;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onNavigate,
  activeTicker,
  collapsed,
  onToggleCollapse,
}) => {
  const [tickerInput, setTickerInput] = useState('');

  const handleTickerSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (tickerInput.trim()) {
      onNavigate('details', tickerInput.trim().toUpperCase());
      setTickerInput('');
    }
  };

  const navItems = [
    {
      id: 'screener',
      label: 'Screener & Busca',
      sublabel: '396 FIIs da B3',
      icon: Search,
    },
    {
      id: 'details',
      label: 'Dossiê & Valuation',
      sublabel: activeTicker ? `Ativo: ${activeTicker}` : 'Raio-X Completo',
      icon: FileText,
    },
    {
      id: 'compare',
      label: 'Comparador Setorial',
      sublabel: 'Pódio 5 Selos & Radar',
      icon: Scale,
    },
    {
      id: 'settings',
      label: 'Parâmetros Macro',
      sublabel: 'NTN-B, IPCA & Spreads',
      icon: Settings,
    },
  ];

  return (
    <aside
      className={`no-print flex flex-col justify-between bg-slate-950 border-r border-slate-800 transition-all duration-300 z-30 shrink-0 select-none ${
        collapsed ? 'w-20' : 'w-64'
      }`}
      style={{ minHeight: '100vh' }}
    >
      {/* Top Part: Brand + Quick Search + Navigation Links */}
      <div className="flex flex-col gap-5 p-4">
        {/* Brand Header */}
        <div className="flex items-center justify-between">
          <div
            onClick={() => onNavigate('screener')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-extrabold text-white text-base tracking-wider flex items-center gap-1.5">
                  ANALISYS
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-900/80 text-indigo-300 border border-indigo-700/60 font-mono font-normal">
                    PRO
                  </span>
                </span>
                <span className="text-[11px] text-slate-400">Inteligência em FIIs</span>
              </div>
            )}
          </div>

          <button
            onClick={onToggleCollapse}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            title={collapsed ? 'Expandir Menu' : 'Recolher Menu'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Quick Ticker Search (when expanded) */}
        {!collapsed && (
          <form onSubmit={handleTickerSubmit} className="relative mt-1">
            <input
              type="text"
              placeholder="Ir direto p/ ticker (ex: HGLG11)"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value.toUpperCase())}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg py-2 pl-3 pr-8 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 uppercase font-mono tracking-wider"
            />
            <button
              type="submit"
              className="absolute right-2 top-2.5 text-slate-400 hover:text-white"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
            </button>
          </form>
        )}

        {/* Navigation Items */}
        <nav className="flex flex-col gap-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-left transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600/20 to-indigo-600/10 text-white border border-blue-500/30 shadow-md shadow-blue-500/5'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <div
                  className={`p-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white shadow'
                      : 'bg-slate-900 text-slate-400 group-hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {!collapsed && (
                  <div className="flex flex-col min-w-0">
                    <span className="text-xs font-semibold text-slate-200 truncate">
                      {item.label}
                    </span>
                    <span className="text-[10px] text-slate-500 truncate">{item.sublabel}</span>
                  </div>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Part: Quick FII Badge & Version Info */}
      <div className="p-4 border-t border-slate-800/80 flex flex-col gap-3">
        {!collapsed && activeTicker && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-2.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4 text-sky-400" />
              <div className="flex flex-col">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                  FII em Análise
                </span>
                <span className="font-bold text-xs text-white font-mono">{activeTicker}</span>
              </div>
            </div>
            <button
              onClick={() => onNavigate('details')}
              className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold"
            >
              Abrir
            </button>
          </div>
        )}

        {!collapsed && (
          <div className="flex items-center justify-between text-[10px] text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              BolsaAI API Online
            </span>
            <span>v2.0 SPA</span>
          </div>
        )}
      </div>
    </aside>
  );
};
