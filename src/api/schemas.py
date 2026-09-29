from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ==============================================================================
# 1. SCREENER & BUSCA DE FIIs
# ==============================================================================
class FiiScreenerItem(BaseModel):
    ticker: str
    name: str
    segment: Optional[str] = None
    segment_code: Optional[str] = None
    close_price: float = 0.0
    vpc: float = 0.0
    pvp: float = 1.0
    dy_12m: float = 0.0
    dy_monthly: float = 0.0
    last_dividend: float = 0.0
    adtv_milhoes: float = 0.0
    total_shareholders: int = 0
    vacancy_pct: Optional[float] = None
    net_asset_value: Optional[float] = None
    # Aliases para compatibilidade total
    nome: Optional[str] = None
    preco_atual: Optional[float] = None
    dy_anual: Optional[float] = None
    liquidez_diaria: Optional[float] = None
    vacancia_fisica: Optional[float] = None
    segmento: Optional[str] = None
    segmento_canonico: Optional[str] = None
    cotistas: Optional[int] = None
    score_geral: Optional[float] = 75.0

class FiiScreenerResponse(BaseModel):
    total: int
    count: int
    items: List[FiiScreenerItem]
    segments: List[str]
    segment_counts: Optional[Dict[str, int]] = None


# ==============================================================================
# 2. DETALHES DO FII (100% DOS DADOS PRESERVADOS)
# ==============================================================================
class FiiHeaderInfo(BaseModel):
    ticker: str
    name: str
    razao_social: str
    gestora: str
    administrador: str
    cnpj: str
    data_base: str
    data_protocolo: str
    score: float
    veredicto: str
    veredicto_tipo: str

class FiiKpis(BaseModel):
    preco_mercado: float
    vpc: float
    pvp: float
    dy_anual: float
    dy_mes_pct: float
    provento_mes: float
    vacancia_fisica: float
    vacancia_financeira: float
    ocupacao_media: float
    contratos_atipicos_pct: float
    wault_anos: float
    alavancagem_pl: float
    saldo_cris_mi: float
    ltv: float
    caixa_mi: float
    cotistas: int
    adtv_milhoes: float
    pl_bi: float
    cotas_emitidas: str

class DossierDreLine(BaseModel):
    rubrica: str
    mes_ant: Optional[float] = None
    mes_atual: Optional[float] = None
    var_pct: Optional[float] = None
    cota: Optional[float] = None
    var_class: str = ""
    is_bold: bool = False

class DossierDre(BaseModel):
    ffo_cota: float
    cobertura_ffo: float
    cobertura_pct: float
    receita_locacao_mi: Optional[float] = None
    desp_fin_mi: Optional[float] = None
    linhas: List[DossierDreLine]
    diagnostico: str

class DossierDonutItem(BaseModel):
    nome: str
    pct: float
    cor: str
    valor_str: Optional[str] = None

class DossierDonutGroup(BaseModel):
    titulo: str
    total_str: str
    itens: List[DossierDonutItem]

class DossierAssetItem(BaseModel):
    nome: str
    cidade_uf: str
    localizacao: str
    participacao_pct: str
    abl_total: str
    abl_propria: str
    ocupacao_pct: str
    tag_classe: str = "tag-aaa"
    especificacoes: str

class DossierTenantItem(BaseModel):
    nome: str
    segmento: str
    receita_pct: str
    tipo_contrato: str
    rating: str
    vencimento: str
    caracteristicas: str

class DossierIndexers(BaseModel):
    ipca_pct: float
    igpm_pct: float
    inpc_pct: float = 0.0
    cdi_pct: float = 0.0
    outros_pct: float = 0.0

class DossierDebtItem(BaseModel):
    operacao: str
    ativo_vinculado: str
    passivo_pct: str
    taxa: str
    vencimento: str

class DossierVerdict(BaseModel):
    teto: Optional[float] = None
    margem_seguranca_pct: Optional[float] = None
    alocacao_sugerida: str
    conclusao: str
    justificativa: str
    diretriz: str
    fontes: List[Dict[str, str]]

class HistoricalDividendPoint(BaseModel):
    mes: str
    data: str
    recorrente: float
    nao_recorrente: float
    total: float

class FutureDividendProjectionPoint(BaseModel):
    mes: str
    recorrente_estimado: float
    nao_recorrente_estimado: float
    total_estimado: float
    is_fechamento_semestre: bool

class DossierDividendsAnalytics(BaseModel):
    provento_atual: float
    ffo_cota: float
    cobertura_ffo_pct: float
    status_sustentabilidade: str
    status_cor: str
    desc_sustentabilidade: str
    capacidade_manutencao: str

    reserva_acumulada_cota: float
    meses_reserva_cobertura: float
    status_colchao: str
    cor_colchao: str
    desc_colchao: str

    extraordinario_estimado_fim_semestre: float
    provento_pico_fim_semestre: float
    tem_potencial_extraordinario: bool
    desc_extraordinario: str
    meses_para_fechamento_semestre: int
    base_legal: str

    provento_projetado_mes: float
    guidance_min: float
    guidance_max: float
    guidance_faixa: str

    historico_12m: List[HistoricalDividendPoint]
    projecao_futura: List[FutureDividendProjectionPoint]
    media_recorrente_12m: float

class FiiDetailsResponse(BaseModel):
    ticker: str
    segment_code: str
    segment_name: str
    header: FiiHeaderInfo
    kpis: FiiKpis
    dre: DossierDre
    dividendos: Optional[DossierDividendsAnalytics] = None
    donut_geografia: DossierDonutGroup
    donut_composicao: DossierDonutGroup
    ativos: List[DossierAssetItem]
    inquilinos: List[DossierTenantItem]
    indexadores: DossierIndexers
    dividas: List[DossierDebtItem]
    green_flags: List[str]
    red_flags: List[str]
    parecer: DossierVerdict
    raw_html: str

# ==============================================================================
# 3. TRADINGVIEW & SÉRIES DE MERCADO
# ==============================================================================
class MarketSeriesPoint(BaseModel):
    time: str # YYYY-MM-DD
    open: float
    high: float
    low: float
    close: float
    volume: float

class DividendHistoryItem(BaseModel):
    date: str
    rate: float

class FiiMarketSeriesResponse(BaseModel):
    ticker: str
    series: List[MarketSeriesPoint]
    dividend_history: List[DividendHistoryItem]

# ==============================================================================
# 4. SIMULADOR DE VALUATION
# ==============================================================================
class ValuationSimulateRequest(BaseModel):
    ntnb_reference_rate: float = 6.50
    projected_ipca: float = 4.00
    real_risk_spread: float = 2.00
    ke: Optional[float] = 0.115
    g_growth: Optional[float] = 0.04

class ValuationSimulateResponse(BaseModel):
    ticker: str
    preco_mercado: float
    preco_teto_recomendado: float
    margem_seguranca_pct: float
    status_atratividade: str
    real_yield: Dict[str, Any]
    metodologias: Dict[str, float]

# ==============================================================================
# 5. COMPARADOR SETORIAL
# ==============================================================================
class SectorPodiumBadge(BaseModel):
    id: str
    title: str
    icon: str
    ticker: str
    destaque_label: str
    valor_label: str
    descricao: str

class SectorRadarItem(BaseModel):
    ticker: str
    desconto: float
    retorno_real: float
    solvencia: float
    qualidade: float
    reserva: float

class SectorScatterItem(BaseModel):
    ticker: str
    pvp: float
    score: float
    preco: float
    dy: float
    margem: float
    quadrante: str

class SectorMatrixRow(BaseModel):
    ticker: str
    preco: float
    vpc: float
    pvp: float
    dy_anual: float
    real_yield_pct: float
    preco_teto: float
    margem_seguranca_pct: float
    ffo_cota: float
    cobertura_ffo: float
    alavancagem_pl: float
    vacancia_fisica: float
    score: float
    veredicto: str
    trajetoria: str

class SectorCompareResponse(BaseModel):
    segment_code: str
    segment_name: str
    tickers: List[str]
    podium: List[SectorPodiumBadge]
    radar: List[SectorRadarItem]
    scatter: List[SectorScatterItem]
    matrix: List[SectorMatrixRow]

# ==============================================================================
# 6. CONFIGURAÇÕES & PARÂMETROS
# ==============================================================================
class PricingParameters(BaseModel):
    ntnb_reference_rate: float = 6.50
    projected_ipca: float = 4.00
    real_risk_spread: float = 2.00
    default_discount_margin: float = 10.00
    ntnb_2035_rate: Optional[float] = None
    real_risk_spread_default: Optional[float] = None
    last_updated: Optional[str] = None

