from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.api.schemas import PricingParameters
from src.database.repository import PricingParametersRepository
from src.services.bolsai_service import BolsaiService

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/pricing-parameters", response_model=PricingParameters)
def get_pricing_parameters():
    """Retorna os parâmetros macroeconômicos padrão de precificação."""
    params = PricingParametersRepository.get_parameters()
    ntnb = float(params.get("ntnb_reference_rate", 6.50))
    ipca = float(params.get("projected_ipca", 4.00))
    spread = float(params.get("real_risk_spread", 2.00))
    margin = float(params.get("default_discount_margin", 10.00))
    return PricingParameters(
        ntnb_reference_rate=ntnb,
        projected_ipca=ipca,
        real_risk_spread=spread,
        default_discount_margin=margin,
        ntnb_2035_rate=ntnb,
        real_risk_spread_default=spread,
        last_updated="2026-09-28T00:00:00"
    )

@router.post("/pricing-parameters", response_model=PricingParameters)
def update_pricing_parameters(params: PricingParameters):
    """Atualiza e persiste os parâmetros macroeconômicos padrão no SQLite."""
    ntnb = params.ntnb_2035_rate if params.ntnb_2035_rate is not None else params.ntnb_reference_rate
    ipca = params.projected_ipca
    spread = params.real_risk_spread_default if params.real_risk_spread_default is not None else params.real_risk_spread
    margin = params.default_discount_margin

    PricingParametersRepository.set_parameter("ntnb_reference_rate", ntnb)
    PricingParametersRepository.set_parameter("projected_ipca", ipca)
    PricingParametersRepository.set_parameter("real_risk_spread", spread)
    PricingParametersRepository.set_parameter("default_discount_margin", margin)

    return PricingParameters(
        ntnb_reference_rate=ntnb,
        projected_ipca=ipca,
        real_risk_spread=spread,
        default_discount_margin=margin,
        ntnb_2035_rate=ntnb,
        real_risk_spread_default=spread,
        last_updated="2026-09-28T00:00:00"
    )


@router.get("/bolsai-status")
def get_bolsai_status():
    """Retorna o status da chave da API BolsaAI."""
    key = BolsaiService.get_api_key()
    has_key = bool(key)
    masked_key = f"{key[:4]}...{key[-4:]}" if len(key) >= 8 else ("***" if key else "")
    return {
        "configured": has_key,
        "masked_key": masked_key
    }

@router.post("/bolsai-key")
def set_bolsai_key(payload: Dict[str, str]):
    """Salva e testa a chave da API BolsaAI."""
    key = payload.get("api_key", "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="Chave de API não informada")
    test_res = BolsaiService.test_connection(key)
    if not test_res.get("success"):
        raise HTTPException(status_code=400, detail=test_res.get("message", "Chave inválida"))
    BolsaiService.save_api_key(key)
    return {"success": True, "message": "Chave da BolsaAI salva e validada com sucesso!"}
