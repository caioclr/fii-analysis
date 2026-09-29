import React, { useState, useEffect } from 'react';
import { fiiApi } from '../api/client';
import type { PricingSettings } from '../types';
import { Settings, Save, CheckCircle2, Shield, Info, RefreshCw } from 'lucide-react';

interface SettingsViewProps {
  onSettingsSaved?: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ onSettingsSaved }) => {
  const [ntnbRate, setNtnbRate] = useState<number>(6.5);
  const [spreadDefault, setSpreadDefault] = useState<number>(2.0);
  const [ipcaProj, setIpcaProj] = useState<number>(4.0);
  const [marginDefault, setMarginDefault] = useState<number>(10.0);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  useEffect(() => {
    fiiApi
      .getPricingSettings()
      .then((data: PricingSettings) => {
        setNtnbRate(data.ntnb_reference_rate ?? data.ntnb_2035_rate ?? 6.5);
        setSpreadDefault(data.real_risk_spread ?? data.real_risk_spread_default ?? 2.0);
        setIpcaProj(data.projected_ipca ?? 4.0);
        setMarginDefault(data.default_discount_margin ?? 10.0);
        setLastUpdated(data.last_updated || '');
      })
      .catch((err) => console.error('Erro ao buscar configurações:', err));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const updated = await fiiApi.updatePricingSettings({
        ntnb_reference_rate: ntnbRate,
        ntnb_2035_rate: ntnbRate,
        real_risk_spread: spreadDefault,
        real_risk_spread_default: spreadDefault,
        projected_ipca: ipcaProj,
        default_discount_margin: marginDefault,
      });
      setLastUpdated(updated.last_updated || new Date().toISOString());
      setSavedSuccess(true);
      onSettingsSaved?.();
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error('Erro ao salvar configurações:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-400" />
            Parâmetros Globais de Precificação e Macro
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            As taxas configuradas aqui servem de base para os cálculos padrão de Preço-Teto em toda
            a plataforma.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs font-semibold">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span>BolsaAI API Conectada</span>
        </div>
      </div>

      {/* Form Card */}
      <form
        onSubmit={handleSave}
        className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col gap-6"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* NTN-B */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-200">
              Taxa de Referência NTN-B 2035 (% ao ano)
            </label>
            <input
              type="number"
              step="0.1"
              value={ntnbRate}
              onChange={(e) => setNtnbRate(parseFloat(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white font-mono focus:outline-none focus:border-blue-500"
            />
            <p className="text-[11px] text-slate-500">
              Taxa real do título público indexado à inflação (juro real livre de risco).
            </p>
          </div>

          {/* Spread Real */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-200">
              Spread de Risco Real Padrão (% ao ano)
            </label>
            <input
              type="number"
              step="0.1"
              value={spreadDefault}
              onChange={(e) => setSpreadDefault(parseFloat(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white font-mono focus:outline-none focus:border-blue-500"
            />
            <p className="text-[11px] text-slate-500">
              Prêmio de risco imobiliário exigido acima do título público (padrão institucional: 2.0%).
            </p>
          </div>

          {/* IPCA Projetado */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-200">
              IPCA Projetado Médio (% ao ano)
            </label>
            <input
              type="number"
              step="0.1"
              value={ipcaProj}
              onChange={(e) => setIpcaProj(parseFloat(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white font-mono focus:outline-none focus:border-blue-500"
            />
            <p className="text-[11px] text-slate-500">
              Expectativa de inflação de longo prazo para correção de fluxo de caixa (Focus).
            </p>
          </div>

          {/* Margem de Segurança Padrão */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-200">
              Margem de Segurança Padrão Exigida (%)
            </label>
            <input
              type="number"
              step="1"
              value={marginDefault}
              onChange={(e) => setMarginDefault(parseFloat(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white font-mono focus:outline-none focus:border-blue-500"
            />
            <p className="text-[11px] text-slate-500">
              Desconto mínimo em relação ao Preço-Teto para sinalizar oportunidade de compra.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <div className="text-xs text-slate-500">
            {lastUpdated && <span>Última atualização: {new Date(lastUpdated).toLocaleString('pt-BR')}</span>}
            {savedSuccess && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold ml-2 inline-flex">
                <CheckCircle2 className="w-4 h-4" />
                Parâmetros salvos e persistidos com sucesso!
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 transition disabled:opacity-50 cursor-pointer"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span>{saving ? 'Gravando...' : 'Salvar Alterações'}</span>
          </button>
        </div>
      </form>

      {/* Racional Metodológico */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col gap-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Info className="w-4 h-4 text-sky-400" />
          Racional Metodológico Aplicado por Segmento
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="font-bold text-sky-400 block">Tijolo & Híbridos</span>
            <p className="text-slate-400">
              Método prioritário:{' '}
              <b className="text-slate-200">Spread Real s/ NTN-B 2035</b>. FFO anualizado é
              capitalizado à taxa exigida (NTN-B + Spread Real).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="font-bold text-amber-400 block">Papel (CRIs)</span>
            <p className="text-slate-400">
              Método prioritário:{' '}
              <b className="text-slate-200">Patrimonial Prudencial (VPC +2% máx)</b>. Impede
              pagamento de ágio excessivo sobre dívida que amortizará ao par.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="font-bold text-indigo-400 block">Fundos de Fundos (FOFs)</span>
            <p className="text-slate-400">
              Método prioritário:{' '}
              <b className="text-slate-200">Patrimonial com 5% de Desconto (VPC * 0,95)</b>.
              Compensa a sobreposição de custos e taxas de administração.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
