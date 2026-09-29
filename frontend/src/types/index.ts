// ==============================================================================
// 1. SCREENER & BUSCA DE FIIs
// ==============================================================================
export interface FiiScreenerItem {
  ticker: string;
  name: string;
  nome?: string;
  segment?: string;
  segmento?: string;
  segment_code?: string;
  segmento_canonico?: string;
  close_price: number;
  preco_atual?: number;
  vpc: number;
  pvp: number;
  dy_12m: number;
  dy_anual?: number;
  dy_monthly: number;
  last_dividend: number;
  adtv_milhoes: number;
  liquidez_diaria?: number;
  total_shareholders: number;
  cotistas?: number;
  vacancy_pct?: number;
  vacancia_fisica?: number;
  net_asset_value?: number;
  score_geral?: number;
}

export interface FiiScreenerResponse {
  total: number;
  count: number;
  items: FiiScreenerItem[];
  segments: string[];
  segment_counts?: Record<string, number>;
}

// ==============================================================================
// 2. DETALHES DO FII (DOSSIÊ COMPLETO)
// ==============================================================================
export interface FiiHeaderInfo {
  ticker: string;
  name: string;
  razao_social: string;
  gestora: string;
  administrador: string;
  cnpj: string;
  data_base: string;
  data_protocolo: string;
  score: number;
  veredicto: string;
  veredicto_tipo: string;
}

export interface FiiKpis {
  preco_mercado: number;
  vpc: number;
  pvp: number;
  dy_anual: number;
  dy_mes_pct: number;
  provento_mes: number;
  vacancia_fisica: number;
  vacancia_financeira: number;
  ocupacao_media: number;
  contratos_atipicos_pct: number;
  wault_anos: number;
  alavancagem_pl: number;
  saldo_cris_mi: number;
  ltv: number;
  caixa_mi: number;
  cotistas: number;
  adtv_milhoes: number;
  pl_bi: float;
  cotas_emitidas: string;
}

type float = number;

export interface DossierDreLine {
  rubrica: string;
  mes_ant?: number | null;
  mes_atual?: number | null;
  var_pct?: number | null;
  cota?: number | null;
  var_class?: string;
  is_bold?: boolean;
}

export interface DossierDre {
  ffo_cota: number;
  cobertura_ffo: number;
  cobertura_pct: number;
  receita_locacao_mi?: number | null;
  desp_fin_mi?: number | null;
  linhas: DossierDreLine[];
  diagnostico: string;
}

export interface DossierDonutItem {
  nome: string;
  pct: number;
  cor: string;
  valor_str?: string | null;
}

export interface DossierDonutGroup {
  titulo: string;
  total_str: string;
  itens: DossierDonutItem[];
}

export interface DossierAssetItem {
  nome: string;
  cidade_uf: string;
  localizacao: string;
  participacao_pct: string;
  abl_total: string;
  abl_propria: string;
  ocupacao_pct: string;
  tag_classe: string;
  especificacoes: string;
}

export interface DossierTenantItem {
  nome: string;
  segmento: string;
  receita_pct: string;
  tipo_contrato: string;
  rating: string;
  vencimento: string;
  caracteristicas: string;
}

export interface DossierIndexers {
  ipca_pct: number;
  igpm_pct: number;
  inpc_pct?: number;
  cdi_pct?: number;
  outros_pct?: number;
}

export interface DossierDebtItem {
  operacao: string;
  ativo_vinculado: string;
  passivo_pct: string;
  taxa: string;
  vencimento: string;
}

export interface DossierVerdict {
  teto?: number | null;
  margem_seguranca_pct?: number | null;
  alocacao_sugerida: string;
  conclusao: string;
  justificativa: string;
  diretriz: string;
  fontes: Array<{ nome: string; url: string }>;
}

export interface HistoricalDividendPoint {
  mes: string;
  data: string;
  recorrente: number;
  nao_recorrente: number;
  total: number;
}

export interface FutureDividendProjectionPoint {
  mes: string;
  recorrente_estimado: number;
  nao_recorrente_estimado: number;
  total_estimado: number;
  is_fechamento_semestre: boolean;
}

export interface DossierDividendsAnalytics {
  provento_atual: number;
  ffo_cota: number;
  cobertura_ffo_pct: number;
  status_sustentabilidade: string;
  status_cor: string;
  desc_sustentabilidade: string;
  capacidade_manutencao: string;

  reserva_acumulada_cota: number;
  meses_reserva_cobertura: number;
  status_colchao: string;
  cor_colchao: string;
  desc_colchao: string;

  extraordinario_estimado_fim_semestre: number;
  provento_pico_fim_semestre: number;
  tem_potencial_extraordinario: boolean;
  desc_extraordinario: string;
  meses_para_fechamento_semestre: number;
  base_legal: string;

  provento_projetado_mes: number;
  guidance_min: number;
  guidance_max: number;
  guidance_faixa: string;

  historico_12m: HistoricalDividendPoint[];
  projecao_futura: FutureDividendProjectionPoint[];
  media_recorrente_12m: number;
}

export interface FiiDetailsResponse {
  ticker: string;
  segment_code: string;
  segment_name: string;
  header: FiiHeaderInfo;
  kpis: FiiKpis;
  dre: DossierDre;
  dividendos?: DossierDividendsAnalytics;
  donut_geografia: DossierDonutGroup;
  donut_composicao: DossierDonutGroup;
  ativos: DossierAssetItem[];
  inquilinos: DossierTenantItem[];
  indexadores: DossierIndexers;
  dividas: DossierDebtItem[];
  green_flags: string[];
  red_flags: string[];
  parecer: DossierVerdict;
  raw_html: string;
}

// ==============================================================================
// 3. MERCADO & SÉRIES B3
// ==============================================================================
export interface MarketSeriesPoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface DividendHistoryItem {
  date: string;
  rate: number;
}

export interface FiiMarketSeriesResponse {
  ticker: string;
  series: MarketSeriesPoint[];
  dividend_history: DividendHistoryItem[];
}

// ==============================================================================
// 4. SIMULAÇÃO DE VALUATION
// ==============================================================================
export interface ValuationSimulateRequest {
  ntnb_reference_rate: number;
  projected_ipca: number;
  real_risk_spread: number;
  ke?: number;
  g_growth?: number;
}

export interface ValuationSimulateResponse {
  ticker: string;
  preco_mercado: number;
  preco_teto_recomendado: number;
  margem_seguranca_pct: number;
  status_atratividade: string;
  real_yield: {
    ticker?: string;
    real_yield_pct?: number;
    label_real?: string;
    ntnb_reference_rate?: number;
    spread_vs_ntnb?: number;
    spread_vs_ntnb_label?: string;
    cdi_gross_equivalent_pct?: number;
    cdi_gross_label?: string;
    metodologia_real?: string;
    is_isento_ir?: boolean;
  };
  metodologias: {
    teto_spread_ntnb?: number;
    teto_gordon_dcf?: number;
    teto_patrimonial?: number;
  };
}

// ==============================================================================
// 5. COMPARADOR SETORIAL
// ==============================================================================
export interface SectorPodiumBadge {
  id: string;
  title: string;
  icon: string;
  ticker: string;
  destaque_label: string;
  valor_label: string;
  descricao: string;
}

export interface SectorRadarItem {
  ticker: string;
  desconto: number;
  retorno_real: number;
  solvencia: number;
  qualidade: number;
  reserva: number;
}

export interface SectorScatterItem {
  ticker: string;
  pvp: number;
  score: number;
  preco: number;
  dy: number;
  margem: number;
  quadrante: string;
}

export interface SectorMatrixRow {
  ticker: string;
  nome?: string;
  preco: number;
  preco_atual?: number;
  close_price?: number;
  vpc: number;
  pvp: number;
  dy_anual: number;
  dy_12m?: number;
  liquidez_diaria?: number;
  adtv_milhoes?: number;
  real_yield_pct: number;
  preco_teto: number;
  margem_seguranca_pct: number;
  ffo_cota: number;
  cobertura_ffo: number;
  alavancagem_pl: number;
  vacancia_fisica: number;
  vacancy_pct?: number;
  score: number;
  score_geral?: number;
  veredicto: string;
  trajetoria: string;
}

export interface SectorCompareResponse {
  segment_code: string;
  segment_name: string;
  tickers: string[];
  podium: SectorPodiumBadge[];
  radar: SectorRadarItem[];
  scatter: SectorScatterItem[];
  matrix: SectorMatrixRow[];
}

export type MarketCandle = MarketSeriesPoint;

export interface RadarData {
  indicators: string[];
  active_fii: {
    ticker: string;
    values: number[];
  };
  sector_benchmark: {
    name: string;
    values: number[];
  };
}

export interface ScatterPoint {
  ticker: string;
  pvp: number;
  score?: number;
  score_qualidade?: number;
  dy?: number;
  dy_anual?: number;
  quadrante: string;
  preco?: number;
  margem?: number;
}

export type SectorComparisonResponse = SectorCompareResponse & {
  total_peers?: number;
};

export type ScreenerFiiItem = FiiScreenerItem;

// ==============================================================================
// 6. CONFIGURAÇÕES MACRO
// ==============================================================================
export interface PricingSettings {
  ntnb_reference_rate?: number;
  ntnb_2035_rate?: number;
  real_risk_spread?: number;
  real_risk_spread_default?: number;
  projected_ipca?: number;
  default_discount_margin?: number;
  source?: string;
  last_updated?: string;
}
