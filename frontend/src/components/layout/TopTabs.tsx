import React from 'react';
import { FileText, Sliders, TrendingUp, Scale, Code } from 'lucide-react';

export type DetailsTab = 'dossier' | 'valuation' | 'charts' | 'compare' | 'raw_html';

interface TopTabsProps {
  activeTab: DetailsTab;
  onTabChange: (tab: DetailsTab) => void;
}

export const TopTabs: React.FC<TopTabsProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    {
      id: 'dossier' as DetailsTab,
      label: 'Dossiê Executivo',
      icon: FileText,
      description: 'KPIs, DRE, Portfólio, Inquilinos e Parecer',
    },
    {
      id: 'valuation' as DetailsTab,
      label: 'Simulador de Valuation',
      icon: Sliders,
      description: 'Preço-Teto & Sliders em Tempo Real',
    },
    {
      id: 'charts' as DetailsTab,
      label: 'Gráficos B3 & Volume',
      icon: TrendingUp,
      description: 'Candles TradingView & Histórico',
    },
    {
      id: 'compare' as DetailsTab,
      label: 'Pares & Setor',
      icon: Scale,
      description: 'Comparativo Setorial & Radar 5D',
    },
    {
      id: 'raw_html' as DetailsTab,
      label: 'HTML Clássico',
      icon: Code,
      description: 'Visualização Original do Sistema',
    },
  ];

  return (
    <div className="no-print border-b border-slate-800 bg-slate-950/60 sticky top-[57px] z-10 backdrop-blur-md">
      <div className="flex overflow-x-auto gap-2 px-6 pt-2 pb-0 scrollbar-none">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2.5 px-4 py-3 border-b-2 text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? 'border-blue-500 text-blue-400 bg-blue-500/10 rounded-t-lg'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
