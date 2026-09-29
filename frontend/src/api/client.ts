import axios from 'axios';
import type {
  FiiScreenerResponse,
  FiiDetailsResponse,
  FiiMarketSeriesResponse,
  ValuationSimulateRequest,
  ValuationSimulateResponse,
  SectorCompareResponse,
  PricingSettings,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 45000,
});

export const fiiApi = {
  getScreener: async (params?: {
    search?: string;
    segment?: string;
    min_dy?: number;
    max_pvp?: number;
    min_liquidez?: number;
    max_vacancia?: number;
    page?: number;
    page_size?: number;
  }): Promise<FiiScreenerResponse> => {
    const { data } = await api.get('/fii/screener', { params });
    return data;
  },

  getDetails: async (ticker: string): Promise<FiiDetailsResponse> => {
    const { data } = await api.get(`/fii/${ticker.toUpperCase()}/details`);
    return data;
  },

  getMarketSeries: async (ticker: string, period = '1y'): Promise<FiiMarketSeriesResponse> => {
    const { data } = await api.get(`/fii/${ticker.toUpperCase()}/market-series`, {
      params: { period },
    });
    return data;
  },

  simulateValuation: async (
    ticker: string,
    params: ValuationSimulateRequest
  ): Promise<ValuationSimulateResponse> => {
    const { data } = await api.post(`/fii/${ticker.toUpperCase()}/valuation-simulate`, params);
    return data;
  },

  getSectorComparison: async (
    segment: string,
    activeTicker?: string
  ): Promise<SectorCompareResponse> => {
    const { data } = await api.get(`/fii/compare-sector/${encodeURIComponent(segment)}`, {
      params: { active_ticker: activeTicker },
    });
    return data;
  },

  getPricingSettings: async (): Promise<PricingSettings> => {
    const { data } = await api.get('/settings/pricing-parameters');
    return data;
  },

  updatePricingSettings: async (settings: Partial<PricingSettings>): Promise<PricingSettings> => {
    const { data } = await api.post('/settings/pricing-parameters', settings);
    return data;
  },
};
