import React from 'react';
import type {
  FiiHeaderInfo,
  FiiKpis,
  DossierDre,
  DossierAssetItem,
  DossierTenantItem,
  DossierIndexers,
  DossierDebtItem,
  DossierVerdict,
  DossierDonutGroup,
  DossierDonutItem,
} from '../../types';
import {
  Building2,
  Users,
  PieChart,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  FileSpreadsheet,
} from 'lucide-react';

const fmt = (val?: number | null, decimals = 2): string => {
  if (val == null || isNaN(val)) return '-';
  return val.toFixed(decimals);
};

const curr = (val?: number | null): string => {
  if (val == null || isNaN(val)) return '0,00';
  return val.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

/* 1. SEÇÃO DE KPIs INSTITUCIONAIS */
export const DossierKPIsGrid: React.FC<{ kpis: FiiKpis; header: FiiHeaderInfo }> = ({
  kpis,
  header,
}) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      {/* P/VP */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">P/VP</span>
        <span className="text-xl font-bold font-mono text-white mt-1">
          {kpis?.pvp != null ? fmt(kpis.pvp) : '-'}
        </span>
        <span
          className={`text-[10px] mt-1 font-semibold ${
            (kpis?.pvp ?? 1.0) <= 1.0 ? 'text-emerald-400' : 'text-amber-400'
          }`}
        >
          {(kpis?.pvp ?? 1.0) <= 1.0 ? 'Desconto s/ VPC' : 'Ágio s/ VPC'}
        </span>
      </div>

      {/* DY 12M */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">DY 12M</span>
        <span className="text-xl font-bold font-mono text-emerald-400 mt-1">
          {kpis?.dy_anual != null ? `${fmt(kpis.dy_anual)}%` : '-'}
        </span>
        <span className="text-[10px] text-slate-500 mt-1">
          Mês: R$ {fmt(kpis?.provento_mes)}
        </span>
      </div>

      {/* ADTV Liquidez Diária */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">Liquidez Diária</span>
        <span className="text-xl font-bold font-mono text-sky-400 mt-1">
          R$ {fmt(kpis?.adtv_milhoes, 1)}M
        </span>
        <span className="text-[10px] text-slate-500 mt-1">ADTV Médio</span>
      </div>

      {/* DY Mensal */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">DY Mensal</span>
        <span className="text-xl font-bold font-mono text-indigo-400 mt-1">
          {kpis?.dy_mes_pct != null ? `${fmt(kpis.dy_mes_pct)}%` : '-'}
        </span>
        <span className="text-[10px] text-slate-500 mt-1">Último Provento</span>
      </div>

      {/* Vacância Física */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">Vacância Física</span>
        <span className="text-xl font-bold font-mono text-slate-200 mt-1">
          {fmt(kpis?.vacancia_fisica, 1)}%
        </span>
        <span
          className={`text-[10px] mt-1 ${
            (kpis?.vacancia_fisica ?? 0) > 10 ? 'text-amber-400' : 'text-emerald-400'
          }`}
        >
          {(kpis?.vacancia_fisica ?? 0) > 10 ? 'Atenção' : 'Saudável'}
        </span>
      </div>

      {/* Vacância Financeira */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">Vacância Fin.</span>
        <span className="text-xl font-bold font-mono text-slate-200 mt-1">
          {fmt(kpis?.vacancia_financeira, 1)}%
        </span>
        <span className="text-[10px] text-slate-500 mt-1">Impacto Renda</span>
      </div>

      {/* Alavancagem LTV */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">Alavancagem (PL)</span>
        <span className="text-xl font-bold font-mono text-slate-200 mt-1">
          {fmt(kpis?.alavancagem_pl, 1)}%
        </span>
        <span
          className={`text-[10px] mt-1 ${
            (kpis?.alavancagem_pl ?? 0) > 20 ? 'text-rose-400' : 'text-emerald-400'
          }`}
        >
          {(kpis?.alavancagem_pl ?? 0) > 20 ? 'Alavancado' : 'Equilibrado'}
        </span>
      </div>

      {/* Score Qualidade */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col justify-between dark-card">
        <span className="text-[11px] text-slate-400 font-medium">Score Qualidade</span>
        <span className="text-xl font-bold font-mono text-amber-400 mt-1">
          {fmt(header?.score, 1)}/10
        </span>
        <span className="text-[10px] text-slate-500 mt-1">{header?.veredicto || 'Audit Score'}</span>
      </div>
    </div>
  );
};

/* 2. DRE GERENCIAL LINHA A LINHA */
export const DossierDRESection: React.FC<{ dre: DossierDre }> = ({ dre }) => {
  const linhas = dre?.linhas || [];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-indigo-400" />
            Demonstrativo de Resultados do Exercício (DRE Gerencial)
          </h3>
          <p
            className="text-xs text-slate-400 mt-0.5"
            dangerouslySetInnerHTML={{ __html: dre?.diagnostico || '' }}
          />
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-slate-400">
            FFO/Cota: <b className="text-emerald-400">R$ {fmt(dre?.ffo_cota)}</b>
          </span>
          <span className="text-slate-400">
            Cobertura: <b className="text-sky-400">{fmt(dre?.cobertura_pct, 1)}%</b>
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2.5 px-3 font-semibold">Conta / Linha do DRE</th>
              <th className="py-2.5 px-3 font-semibold text-right">Mês Anterior</th>
              <th className="py-2.5 px-3 font-semibold text-right">Mês Atual</th>
              <th className="py-2.5 px-3 font-semibold text-right">Variação %</th>
              <th className="py-2.5 px-3 font-semibold text-right">R$/Cota</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {linhas.map((item, idx) => (
              <tr
                key={idx}
                className={`hover:bg-slate-800/40 transition ${
                  item.is_bold ? 'bg-slate-950/60 font-bold text-white' : 'text-slate-300'
                }`}
              >
                <td className="py-2.5 px-3 font-sans font-medium">{item.rubrica}</td>
                <td className="py-2.5 px-3 text-right text-slate-400">
                  {item.mes_ant != null ? `R$ ${curr(item.mes_ant)}` : '-'}
                </td>
                <td className="py-2.5 px-3 text-right">
                  {item.mes_atual != null ? `R$ ${curr(item.mes_atual)}` : '-'}
                </td>
                <td
                  className={`py-2.5 px-3 text-right ${
                    (item.var_pct ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {item.var_pct != null ? `${item.var_pct >= 0 ? '+' : ''}${fmt(item.var_pct, 1)}%` : '-'}
                </td>
                <td className="py-2.5 px-3 text-right text-slate-300">
                  {item.cota != null ? `R$ ${fmt(item.cota)}` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

/* 3. RAIO-X DA CARTEIRA (DONUTS PURA CSS CONIC-GRADIENT) */
const buildConicGradient = (items?: DossierDonutItem[]): string => {
  if (!items || items.length === 0) {
    return 'conic-gradient(#334155 0% 100%)';
  }
  let acc = 0;
  const slices: string[] = [];
  const validItems = items.filter((it) => it.pct > 0);
  if (validItems.length === 0) {
    return 'conic-gradient(#334155 0% 100%)';
  }
  const totalItems = validItems.length;
  validItems.forEach((it, idx) => {
    const start = idx === 0 ? 0 : acc;
    const end = idx === totalItems - 1 ? 100 : Math.min(acc + it.pct, 100);
    slices.push(`${it.cor} ${start.toFixed(1)}% ${end.toFixed(1)}%`);
    acc = end;
  });
  return `conic-gradient(${slices.join(', ')})`;
};

interface CenterLabel {
  top: string;
  bottom: string;
  bottomColor: string;
}

const getCenterLabels = (
  isDonut1: boolean,
  segmentCode?: string
): CenterLabel => {
  const code = (segmentCode || '').toUpperCase();
  if (isDonut1) {
    if (code === 'AGRO') {
      return { top: 'CADEIA', bottom: 'AGRO', bottomColor: '#4ade80' };
    }
    if (code === 'LOGISTICA' || code === 'SHOPPING' || code === 'LAJES') {
      return { top: 'ABL', bottom: 'PRÓPRIA', bottomColor: '#38bdf8' };
    }
    if (code === 'PAPEL') {
      return { top: 'TAXA', bottom: 'INDEX', bottomColor: '#38bdf8' };
    }
    if (code === 'FOF') {
      return { top: 'CLASSE', bottom: 'ATIVO', bottomColor: '#f59e0b' };
    }
    return { top: 'PORT', bottom: 'TIPO', bottomColor: '#38bdf8' };
  } else {
    if (code === 'AGRO') {
      return { top: 'TAXA', bottom: 'INDEX', bottomColor: '#38bdf8' };
    }
    if (code === 'LOGISTICA' || code === 'SHOPPING' || code === 'LAJES') {
      return { top: 'ATIVO', bottom: 'TOTAL', bottomColor: '#4ade80' };
    }
    if (code === 'PAPEL') {
      return { top: 'CRIs', bottom: 'SUBORD', bottomColor: '#a855f7' };
    }
    if (code === 'FOF') {
      return { top: 'GESTÃO', bottom: 'ESTRAT', bottomColor: '#10b981' };
    }
    return { top: 'ATIVO', bottom: 'TOTAL', bottomColor: '#4ade80' };
  }
};

const getSectionTitle = (segmentCode?: string): string => {
  const code = (segmentCode || '').toUpperCase();
  switch (code) {
    case 'AGRO':
      return 'Raio-X da carteira: culturas, estratégia e indexadores';
    case 'LOGISTICA':
      return 'Raio-X da carteira: geografia e composição do ativo';
    case 'SHOPPING':
      return 'Raio-X da carteira: distribuição geográfica e ativos';
    case 'PAPEL':
      return 'Raio-X da carteira de crédito: indexadores e subordinação';
    case 'LAJES':
      return 'Raio-X dos edifícios corporativos: eixos e padrão construtivo';
    case 'FOF':
      return 'Raio-X da carteira de FoFs: classes de ativos e estratégia';
    case 'HIBRIDO':
      return 'Raio-X da carteira híbrida: tipologia e contratos';
    default:
      return 'Raio-X da carteira: alocações e composição do ativo';
  }
};

export const DossierPortfolioDonutsSection: React.FC<{
  donutGeografia?: DossierDonutGroup;
  donutComposicao?: DossierDonutGroup;
  segmentCode?: string;
}> = ({ donutGeografia, donutComposicao, segmentCode }) => {
  if (!donutGeografia?.itens?.length && !donutComposicao?.itens?.length) {
    return null;
  }

  const title = getSectionTitle(segmentCode);
  const labels1 = getCenterLabels(true, segmentCode);
  const labels2 = getCenterLabels(false, segmentCode);

  const sub1 =
    (segmentCode || '').toUpperCase() === 'AGRO'
      ? 'Distribuição por Cultura'
      : donutGeografia?.titulo || 'Distribuição Geográfica (ABL)';

  const sub2 =
    (segmentCode || '').toUpperCase() === 'AGRO'
      ? 'Alocação por Indexador / Tipo'
      : donutComposicao?.titulo || 'Composição do Ativo Total';

  const conic1 = buildConicGradient(donutGeografia?.itens);
  const conic2 = buildConicGradient(donutComposicao?.itens);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      {/* Título padronizado sem numeração e com ícone */}
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <PieChart className="w-5 h-5 text-emerald-400" />
          <span>{title}</span>
        </h3>
        <span className="text-xs text-slate-400 font-mono hidden sm:inline">
          {donutComposicao?.total_str ? `Alocação Total: ${donutComposicao.total_str}` : '100% Alocado'}
        </span>
      </div>

      {/* Grid com os 2 painéis de donuts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Painel Donut 1 */}
        {donutGeografia?.itens && donutGeografia.itens.length > 0 && (
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-5 flex flex-col sm:flex-row items-center gap-6">
            {/* Donut Chart */}
            <div
              className="relative w-28 h-28 rounded-full flex items-center justify-center shrink-0 shadow-lg"
              style={{ background: conic1 }}
            >
              <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-center shadow-inner select-none">
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-bold leading-tight">
                  {labels1.top}
                </span>
                <span
                  className="text-[11px] font-extrabold font-mono leading-tight"
                  style={{ color: labels1.bottomColor }}
                >
                  {labels1.bottom}
                </span>
              </div>
            </div>

            {/* Legenda Lateral */}
            <div className="flex-1 w-full flex flex-col gap-2">
              <div className="text-[10.5px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">
                {sub1}
              </div>
              <div className="flex flex-col gap-1.5">
                {donutGeografia.itens.map((it, idx) => (
                  <div key={idx} className="flex items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span
                        className="w-2.5 h-2.5 rounded-[2px] shrink-0"
                        style={{ backgroundColor: it.cor }}
                      />
                      <span className="text-slate-300 font-medium text-xs truncate">
                        {it.nome}
                      </span>
                    </div>
                    <span className="text-white font-bold font-mono text-xs whitespace-nowrap">
                      {it.pct.toFixed(1).replace('.', ',')}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Painel Donut 2 */}
        {donutComposicao?.itens && donutComposicao.itens.length > 0 && (
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-5 flex flex-col sm:flex-row items-center gap-6">
            {/* Donut Chart */}
            <div
              className="relative w-28 h-28 rounded-full flex items-center justify-center shrink-0 shadow-lg"
              style={{ background: conic2 }}
            >
              <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-center shadow-inner select-none">
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-bold leading-tight">
                  {labels2.top}
                </span>
                <span
                  className="text-[11px] font-extrabold font-mono leading-tight"
                  style={{ color: labels2.bottomColor }}
                >
                  {labels2.bottom}
                </span>
              </div>
            </div>

            {/* Legenda Lateral */}
            <div className="flex-1 w-full flex flex-col gap-2">
              <div className="text-[10.5px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">
                {sub2}
              </div>
              <div className="flex flex-col gap-1.5">
                {donutComposicao.itens.map((it, idx) => (
                  <div key={idx} className="flex items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span
                        className="w-2.5 h-2.5 rounded-[2px] shrink-0"
                        style={{ backgroundColor: it.cor }}
                      />
                      <span className="text-slate-300 font-medium text-xs truncate">
                        {it.nome}
                      </span>
                    </div>
                    <span className="text-white font-bold font-mono text-xs whitespace-nowrap">
                      {it.pct.toFixed(1).replace('.', ',')}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* 4. PORTFÓLIO DE ATIVOS IMOBILIÁRIOS / OPERAÇÕES DE CRIs */
export const DossierAssetsSection: React.FC<{
  ativos: DossierAssetItem[];
  isCreditFund: boolean;
}> = ({ ativos = [], isCreditFund }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Building2 className="w-5 h-5 text-sky-400" />
          {isCreditFund
            ? 'Carteira de Ativos de Crédito (CRIs e Operações Compromissadas)'
            : 'Portfólio de Propriedades e Imóveis Físicos'}
        </h3>
        <span className="text-xs text-slate-400 font-medium">
          Total de Ativos Mapeados: {ativos.length}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2.5 px-3 font-semibold">
                {isCreditFund ? 'Devedor / Operação' : 'Imóvel / Empreendimento'}
              </th>
              <th className="py-2.5 px-3 font-semibold">Localização / Cidade</th>
              <th className="py-2.5 px-3 font-semibold text-right">ABL Total / Volume</th>
              <th className="py-2.5 px-3 font-semibold text-right">ABL Própria</th>
              <th className="py-2.5 px-3 font-semibold text-right">Participação %</th>
              <th className="py-2.5 px-3 font-semibold text-right">Ocupação / Status</th>
              <th className="py-2.5 px-3 font-semibold">Especificações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {ativos.map((a, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition">
                <td className="py-2.5 px-3 font-sans font-medium text-white">{a.nome}</td>
                <td className="py-2.5 px-3 font-sans text-slate-300">{a.cidade_uf || a.localizacao || '-'}</td>
                <td className="py-2.5 px-3 text-right text-slate-200">{a.abl_total || '-'}</td>
                <td className="py-2.5 px-3 text-right text-slate-300">{a.abl_propria || '-'}</td>
                <td className="py-2.5 px-3 text-right text-sky-400 font-bold">{a.participacao_pct || '-'}</td>
                <td className="py-2.5 px-3 text-right text-emerald-400 font-semibold">{a.ocupacao_pct || '-'}</td>
                <td className="py-2.5 px-3 font-sans text-slate-400 text-[11px] max-w-xs truncate">
                  {a.especificacoes || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

/* 4. PRINCIPAIS INQUILINOS / CONTRA-PARTES */
export const DossierTenantsSection: React.FC<{ tenants: DossierTenantItem[] }> = ({
  tenants = [],
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Users className="w-5 h-5 text-emerald-400" />
          Concentração de Inquilinos e Risco de Crédito dos Locatários
        </h3>
        <span className="text-xs text-slate-400">Total de Contra-partes: {tenants.length}</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2.5 px-3 font-semibold">Inquilino / Locatário</th>
              <th className="py-2.5 px-3 font-semibold">Setor de Atuação</th>
              <th className="py-2.5 px-3 font-semibold text-right">Part. na Receita (%)</th>
              <th className="py-2.5 px-3 font-semibold text-center">Tipo Contrato</th>
              <th className="py-2.5 px-3 font-semibold text-center">Vencimento</th>
              <th className="py-2.5 px-3 font-semibold text-center">Rating</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {tenants.map((t, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition">
                <td className="py-2.5 px-3 font-sans font-medium text-white">{t.nome}</td>
                <td className="py-2.5 px-3 font-sans text-slate-300">{t.segmento || '-'}</td>
                <td className="py-2.5 px-3 text-right font-bold text-emerald-400">
                  {t.receita_pct || '-'}
                </td>
                <td className="py-2.5 px-3 text-center font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] ${
                      t.tipo_contrato?.toLowerCase().includes('atípico')
                        ? 'bg-indigo-950 text-indigo-400 border border-indigo-800'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {t.tipo_contrato || 'Típico'}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-center text-slate-300">
                  {t.vencimento || '-'}
                </td>
                <td className="py-2.5 px-3 text-center font-sans">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                    {t.rating || 'N/A'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

/* 5. INDEXADORES DOS CONTRATOS */
export const DossierIndexersSection: React.FC<{ indexers?: DossierIndexers }> = ({ indexers }) => {
  const ipca = indexers?.ipca_pct ?? 0;
  const igpm = indexers?.igpm_pct ?? 0;
  const cdi = indexers?.cdi_pct ?? 0;
  const outros = indexers?.outros_pct ?? 0;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <PieChart className="w-5 h-5 text-indigo-400" />
          Indexadores dos Contratos e Proteção Inflacionária
        </h3>
        <span className="text-xs text-slate-400">Reajustes Anuais dos Aluguéis</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* IPCA */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3 space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-200">IPCA</span>
            <span className="font-mono font-bold text-indigo-400">{fmt(ipca, 1)}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(ipca, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* IGP-M */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3 space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-200">IGP-M</span>
            <span className="font-mono font-bold text-sky-400">{fmt(igpm, 1)}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className="bg-sky-500 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(igpm, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* CDI */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3 space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-200">CDI / DI</span>
            <span className="font-mono font-bold text-amber-400">{fmt(cdi, 1)}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className="bg-amber-500 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(cdi, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Outros / Pré */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3 space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-200">Outros / Pré</span>
            <span className="font-mono font-bold text-slate-400">{fmt(outros, 1)}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className="bg-slate-600 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(outros, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* 5. ESTRUTURA DE CAPITAL, SECURITIZAÇÕES E ALAVANCAGEM FINANCEIRA */
export const DossierCapitalStructureSection: React.FC<{
  debts?: DossierDebtItem[];
  kpis?: FiiKpis;
}> = ({ debts = [], kpis }) => {
  const saldoCris = kpis?.saldo_cris_mi ?? 0;
  const alav = kpis?.alavancagem_pl ?? 0;
  const ltv = kpis?.ltv ?? 0;
  const caixaMi = kpis?.caixa_mi ?? 0;
  const plBi = kpis?.pl_bi ?? 1.0;

  const ativoTotalBi = plBi * (1.0 + alav / 100.0);
  const caixaPlPct = plBi > 0 ? (caixaMi / (plBi * 1000.0)) * 100.0 : 0.0;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card print-avoid-break">
      {/* Título com barra vertical azul/sky idêntica ao design executivo */}
      <div className="flex items-center justify-between mb-5 border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white flex items-center gap-2.5">
          <span className="w-1.5 h-6 bg-sky-500 rounded-sm inline-block"></span>
          <span>Estrutura de capital, securitizações e alavancagem financeira</span>
        </h3>
        <span className="text-xs text-slate-400 font-mono">
          Total de Operações: {debts.length}
        </span>
      </div>

      {/* 4 Cards de Métricas Principais (KPIs) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Card 1: Saldo Devedor de CRIs */}
        <div className="bg-[#0b1322] border border-slate-800/90 rounded-lg p-4 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">
            Saldo Devedor de CRIs (Passivo Oneroso)
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-black font-mono text-amber-400">
              {saldoCris > 0 ? `R$ ${fmt(saldoCris, 1)} Milhões` : 'R$ 0,0 Milhões'}
            </span>
          </div>
          <span className="text-[11px] text-slate-400 font-sans">
            {saldoCris > 0
              ? 'Securitizações estruturadas para expansões'
              : 'Portfólio 100% desalavancado'}
          </span>
        </div>

        {/* Card 2: Alavancagem Financeira Bruta */}
        <div className="bg-[#0b1322] border border-slate-800/90 rounded-lg p-4 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">
            Alavancagem Financeira Bruta (Passivo / PL)
          </span>
          <div className="my-1.5">
            <span
              className={`text-2xl font-black font-mono ${
                alav <= 15 ? 'text-emerald-400' : alav <= 25 ? 'text-sky-400' : 'text-amber-400'
              }`}
            >
              {fmt(alav, 2)}%
            </span>
          </div>
          <span className="text-[11px] text-slate-400 font-sans">
            {alav <= 25
              ? 'Conservador: Bem abaixo da trava de 25,00%'
              : 'Alerta: Acima da trava prudencial de 25,00%'}
          </span>
        </div>

        {/* Card 3: Dívida / Ativo Total (LTV Contábil) */}
        <div className="bg-[#0b1322] border border-slate-800/90 rounded-lg p-4 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">
            Dívida / Ativo Total (LTV Contábil)
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-black font-mono text-sky-400">
              {fmt(ltv, 2)}%
            </span>
          </div>
          <span className="text-[11px] text-slate-400 font-sans">
            Ativo Total: R$ {fmt(ativoTotalBi, 2)} Bilhões
          </span>
        </div>

        {/* Card 4: Caixa & Liquidez Imediata */}
        <div className="bg-[#0b1322] border border-slate-800/90 rounded-lg p-4 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">
            Caixa & Liquidez Imediata
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-black font-mono text-emerald-400">
              R$ {fmt(caixaMi, 2)} mi
            </span>
          </div>
          <span className="text-[11px] text-slate-400 font-sans">
            {fmt(caixaPlPct, 2)}% do Patrimônio Líquido
          </span>
        </div>
      </div>

      {/* Tabela de Securitizações (CRIs) */}
      <div className="overflow-x-auto rounded-lg border border-slate-800/90">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="bg-[#090f1a] border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
              <th className="py-3 px-3.5 font-semibold">Operação / Securitização (CRI)</th>
              <th className="py-3 px-3.5 font-semibold">Ativo Vinculado</th>
              <th className="py-3 px-3.5 font-semibold text-center">% do Passivo</th>
              <th className="py-3 px-3.5 font-semibold text-center">Custo Médio Ponderado</th>
              <th className="py-3 px-3.5 font-semibold">Vencimento / Cronograma</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {debts.length === 0 ? (
              <tr>
                <td className="py-3.5 px-3.5 font-sans font-bold text-white">
                  Sem Emissões Onerosas de CRIs
                </td>
                <td className="py-3.5 px-3.5 font-sans text-slate-400">
                  Portfólio 100% Desalavancado
                </td>
                <td className="py-3.5 px-3.5 text-center text-emerald-400 font-bold">0,0%</td>
                <td className="py-3.5 px-3.5 text-center text-slate-400">N/A</td>
                <td className="py-3.5 px-3.5 font-sans text-slate-400">
                  O fundo opera com estrutura de capital limpa, sem passivos onerosos de securitização.
                </td>
              </tr>
            ) : (
              debts.map((d, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-3.5 font-sans font-bold text-white">
                    {d.operacao}
                  </td>
                  <td className="py-3.5 px-3.5 font-sans text-slate-300">
                    {d.ativo_vinculado}
                  </td>
                  <td className="py-3.5 px-3.5 text-center text-sky-400 font-bold font-mono">
                    {d.passivo_pct}
                  </td>
                  <td className="py-3.5 px-3.5 text-center text-slate-200 font-mono">
                    {d.taxa}
                  </td>
                  <td className="py-3.5 px-3.5 text-slate-300 font-sans">
                    {d.vencimento}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

/* Componente compatível legado */
export const DossierIndexersAndDebtSection: React.FC<{
  indexers: DossierIndexers;
  debts: DossierDebtItem[];
  kpis?: FiiKpis;
}> = ({ indexers, debts = [], kpis }) => {
  return (
    <div className="space-y-5">
      <DossierIndexersSection indexers={indexers} />
      <DossierCapitalStructureSection debts={debts} kpis={kpis} />
    </div>
  );
};

/* 6. PARECER FUNDAMENTALISTA E SEMÁFORO DE FLAGS */
export const DossierOpinionAndFlagsSection: React.FC<{
  parecer: DossierVerdict;
  greenFlags: string[];
  redFlags: string[];
}> = ({ parecer, greenFlags = [], redFlags = [] }) => {
  return (
    <div className="space-y-5 print-avoid-break">
      {/* Flags e Alertas */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card">
        <h3 className="text-base font-bold text-white flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
          <ShieldCheck className="w-5 h-5 text-indigo-400" />
          Semáforo de Flags e Auditoria de Riscos
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Green Flags */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              Pontos Fortes e Diferenciais (Green Flags)
            </h4>
            <div className="space-y-2">
              {greenFlags.map((flag, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/50 text-xs text-emerald-300 font-sans leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: flag }}
                />
              ))}
            </div>
          </div>

          {/* Red Flags / Atenção */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              Pontos de Atenção e Monitoramento (Red Flags)
            </h4>
            <div className="space-y-2">
              {redFlags.map((flag, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-rose-950/20 border border-rose-800/50 text-xs text-rose-300 font-sans leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: flag }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Parecer Fundamentalista e Diretrizes */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl dark-card space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            Tese de Investimento & Parecer Institucional
          </h3>
          <span className="text-xs text-slate-400">
            Alocação Sugerida: <b className="text-sky-300">{parecer?.alocacao_sugerida || '5% a 10%'}</b>
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs font-sans">
          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Conclusão da Tese
            </span>
            <p className="text-slate-300 leading-relaxed">{parecer?.conclusao}</p>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Justificativa Fundamentalista
            </span>
            <p className="text-slate-300 leading-relaxed">{parecer?.justificativa}</p>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-blue-950/20 border border-blue-800/50 text-xs text-blue-200 font-sans">
          <b>Diretriz de Execução:</b> {parecer?.diretriz}
        </div>
      </div>
    </div>
  );
};

export { DossierDividendProjectionSection } from './DossierDividendProjectionSection';

