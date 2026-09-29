import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { FiiScreenerView } from './views/FiiScreenerView';
import { FiiDetailsView } from './views/FiiDetailsView';
import { FiiSectorComparatorView } from './views/FiiSectorComparatorView';
import { SettingsView } from './views/SettingsView';
import { fiiApi } from './api/client';
import type { PricingSettings } from './types';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('screener');
  const [activeTicker, setActiveTicker] = useState<string>('HGLG11');
  const [activeSector, setActiveSector] = useState<string>('LOGISTICA');
  const [collapsedSidebar, setCollapsedSidebar] = useState<boolean>(false);
  const [pricingSettings, setPricingSettings] = useState<PricingSettings | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const loadSettings = () => {
    fiiApi
      .getPricingSettings()
      .then((data) => setPricingSettings(data))
      .catch((err) => console.error('Erro ao buscar configurações macro:', err));
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleNavigate = (view: string, ticker?: string) => {
    if (ticker) {
      setActiveTicker(ticker);
    }
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectFii = (ticker: string) => {
    setActiveTicker(ticker);
    setCurrentView('details');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCompareSector = (segment: string, ticker: string) => {
    setActiveSector(segment);
    if (ticker) setActiveTicker(ticker);
    setCurrentView('compare');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadSettings();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <div className="flex min-h-screen bg-[#0b0f19] text-slate-100 antialiased font-sans">
      {/* Expandable Sidebar Navigation */}
      <Sidebar
        currentView={currentView}
        onNavigate={handleNavigate}
        activeTicker={activeTicker}
        collapsed={collapsedSidebar}
        onToggleCollapse={() => setCollapsedSidebar(!collapsedSidebar)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Sticky Header with Breadcrumbs, Macro Indicators & PDF Export */}
        <Header
          currentView={currentView}
          activeTicker={activeTicker}
          pricingSettings={pricingSettings}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />

        {/* Dynamic Views */}
        <main className="flex-1 max-w-7xl w-full mx-auto pb-16">
          {currentView === 'screener' && (
            <FiiScreenerView
              onSelectFii={handleSelectFii}
              onCompareSector={handleCompareSector}
            />
          )}

          {currentView === 'details' && (
            <FiiDetailsView
              ticker={activeTicker}
              onNavigateToSector={handleCompareSector}
              onBackToScreener={() => setCurrentView('screener')}
            />
          )}

          {currentView === 'compare' && (
            <FiiSectorComparatorView
              initialSegment={activeSector}
              initialTicker={activeTicker}
              onSelectFii={handleSelectFii}
            />
          )}

          {currentView === 'settings' && (
            <SettingsView onSettingsSaved={loadSettings} />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
