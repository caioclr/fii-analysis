import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import yfinance as yf

from src.services.bolsai_service import BolsaiService
from src.api.schemas import (
    HistoricalDividendPoint,
    FutureDividendProjectionPoint,
    DossierDividendsAnalytics
)

logger = logging.getLogger(__name__)

class DividendProjectionService:
    """
    Serviço de inteligência para Projeção de Dividendos Futuros, Avaliação de Sustentabilidade
    do Fluxo Caixa Operacional, Diagnóstico do Colchão de Reserva e Estimativa de Dividendos
    Extraordinários Semestrais sob a Lei nº 8.668/93 e regulamentação CVM.
    """

    @classmethod
    def project_and_analyze(cls, ticker: str, ffo_cota: float, provento_atual: float,
                            reserva_acumulada_cota: float, segment_code: str,
                            mes_corrente_semestre: int = 2) -> Dict[str, Any]:
        """
        Gera o diagnóstico completo de dividendos futuros, sustentabilidade e fechamento semestral.

        Parâmetros:
          - ticker: Código do FII
          - ffo_cota: FFO líquido operacional por cota no mês
          - provento_atual: Último dividendo distribuído por cota
          - reserva_acumulada_cota: Saldo atual de lucros acumulados e não distribuídos em R$/cota
          - segment_code: Código do setor
          - mes_corrente_semestre: Posição do mês dentro do semestre civil (1 a 6). Padrão = 2 (Agosto/Fevereiro).
        """
        ffo_cota = float(ffo_cota or provento_atual or 0.80)
        provento_atual = float(provento_atual or 0.80)
        reserva_cota = float(reserva_acumulada_cota or 0.0)

        # 1. Cobertura Operacional do FFO e Termômetro de Sustentabilidade
        cobertura_ffo = ffo_cota / provento_atual if provento_atual > 0 else 1.0
        cobertura_pct = round(cobertura_ffo * 100.0, 1)

        if cobertura_ffo >= 1.02:
            status_sustentabilidade = "Superávit Operacional"
            status_cor = "success"
            desc_sustentabilidade = f"O FII gera R$ {ffo_cota:.2f} de lucro operacional para pagar R$ {provento_atual:.2f}, retendo excedente para reserva."
            capacidade_manutencao = "Alta Capacidade de Manutenção com Geração de Reserva"
        elif cobertura_ffo >= 0.98:
            status_sustentabilidade = "Neutro no Limite"
            status_cor = "warning"
            desc_sustentabilidade = f"O dividendo (R$ {provento_atual:.2f}) é 100% financiado pelo FFO (R$ {ffo_cota:.2f}), sem sobras significativas."
            capacidade_manutencao = "Manutenção Neutra no Limite do Lucro Caixa"
        else:
            status_sustentabilidade = "Déficit Operacional"
            status_cor = "danger"
            desc_sustentabilidade = f"O dividendo (R$ {provento_atual:.2f}) supera o lucro caixa gerado (R$ {ffo_cota:.2f}), consumindo reservas acumuladas ou caixa."
            capacidade_manutencao = "Risco de Redução de Proventos se a Vacância/Inadimplência persistir"

        # 2. Análise do Colchão de Reserva (Autonomia em Meses)
        meses_reserva = round(reserva_cota / provento_atual, 1) if provento_atual > 0 else 0.0
        
        if meses_reserva >= 2.0:
            status_colchao = "Colchão Confortável"
            cor_colchao = "success"
            desc_colchao = f"A reserva de R$ {reserva_cota:.2f}/cota garante {meses_reserva:.1f} meses de proventos mesmo em caso de choque operacional."
        elif meses_reserva >= 1.0:
            status_colchao = "Colchão Moderado"
            cor_colchao = "warning"
            desc_colchao = f"Possui {meses_reserva:.1f} mês de dividendo em reserva (R$ {reserva_cota:.2f}/cota), protegendo contra vacância temporária."
        else:
            status_colchao = "Colchão Comprimido"
            cor_colchao = "danger"
            desc_colchao = f"Reserva baixa ({meses_reserva:.1f} meses, R$ {reserva_cota:.2f}/cota). Pouca margem para absorver sinistros sem corte de rendimentos."

        # 3. Estimativa de Proventos dos Próximos Meses (Run-Rate / Guidance 6M)
        # O dividendo projetado mensal regular baseia-se na sustentabilidade do FFO
        if cobertura_ffo >= 1.05:
            guidance_min = round(provento_atual, 2)
            guidance_max = round(ffo_cota, 2)
            provento_projetado_mes = round((guidance_min + guidance_max) / 2.0, 2)
        elif cobertura_ffo >= 0.98:
            guidance_min = round(provento_atual * 0.98, 2)
            guidance_max = round(provento_atual * 1.02, 2)
            provento_projetado_mes = round(provento_atual, 2)
        else:
            # Em déficit crônico, o provento tende a convergir para o FFO
            guidance_min = round(ffo_cota, 2)
            guidance_max = round(provento_atual, 2)
            provento_projetado_mes = round(ffo_cota, 2)

        # 4. Projeção de Dividendo Extraordinário de Fim de Semestre (Lei 8.668/93 - Mínimo 95%)
        # A Lei 8.668/93 obriga os FIIs a distribuírem pelo menos 95% do lucro caixa semestral apurado
        meses_restantes = max(1, 6 - mes_corrente_semestre)
        
        # Lucro estimado total no semestre = (lucro dos meses já ocorridos) + (ffo projetado dos meses restantes)
        lucro_semestre_projetado = (ffo_cota * mes_corrente_semestre) + (ffo_cota * meses_restantes)
        pago_meses_anteriores = provento_atual * (mes_corrente_semestre - 1)
        pagamentos_lineares_restantes = provento_projetado_mes * (meses_restantes - 1)
        
        total_pago_ordinario = pago_meses_anteriores + provento_atual + pagamentos_lineares_restantes
        minimo_obrigatorio_cvm = 0.95 * lucro_semestre_projetado

        # Se o fundo acumulou reservas e o total pago ordinariamente for menor que o mínimo legal:
        sobra_distribuivel = max(0.0, minimo_obrigatorio_cvm - total_pago_ordinario)
        # Também soma parcela da reserva pretérita acumulada liberada no encerramento
        parcela_reserva_liberada = min(reserva_cota * 0.40, reserva_cota)
        extraordinario_projetado_fim_semestre = round(sobra_distribuivel + (parcela_reserva_liberada if meses_reserva >= 1.5 else 0.0), 2)
        
        provento_pico_6_mes = round(provento_projetado_mes + extraordinario_projetado_fim_semestre, 2)

        tem_potencial_extraordinario = extraordinario_projetado_fim_semestre >= (provento_atual * 0.15)

        return {
            "ticker": ticker.upper(),
            "provento_atual": provento_atual,
            "ffo_cota": ffo_cota,
            "cobertura_ffo_pct": cobertura_pct,
            "status_sustentabilidade": status_sustentabilidade,
            "status_cor": status_cor,
            "desc_sustentabilidade": desc_sustentabilidade,
            "capacidade_manutencao": capacidade_manutencao,
            
            # Colchão de Reserva
            "reserva_acumulada_cota": reserva_cota,
            "meses_reserva_cobertura": meses_reserva,
            "status_colchao": status_colchao,
            "cor_colchao": cor_colchao,
            "desc_colchao": desc_colchao,

            # Projeção Futura Regular (Próximos Meses)
            "provento_projetado_mes": provento_projetado_mes,
            "guidance_faixa": f"R$ {guidance_min:.2f} a R$ {guidance_max:.2f}",
            "guidance_min": guidance_min,
            "guidance_max": guidance_max,

            # Fechamento Semestral (Lei 8.668/93)
            "mes_corrente_semestre": mes_corrente_semestre,
            "meses_para_fechamento_semestre": meses_restantes,
            "extraordinario_estimado_fim_semestre": extraordinario_projetado_fim_semestre,
            "provento_pico_fim_semestre": provento_pico_6_mes,
            "tem_potencial_extraordinario": tem_potencial_extraordinario,
            "desc_extraordinario": (
                f"Estimativa de distribuição extraordinária de R$ {extraordinario_projetado_fim_semestre:.2f}/cota no fechamento do semestre (levando a cota a R$ {provento_pico_6_mes:.2f} no mês)"
                if tem_potencial_extraordinario else
                "Distribuição semestral projetada de forma linear, sem expectativa de pico extraordinário relevante."
            )
        }

    @classmethod
    def build_dossier_dividend_analytics(
        cls,
        ticker: str,
        kb: Dict[str, Any],
        cross: Dict[str, Any],
        provento_atual: float,
        ffo_cota: float,
        reserva_cota: Optional[float] = None,
        segment_code: str = "LOGISTICA"
    ) -> DossierDividendsAnalytics:
        """
        Constrói a inteligência analítica completa de dividendos para o Dossiê:
        - Histórico de 12 meses (recorrentes vs extraordinários) com fallback yfinance/BolsaAI
        - Saldo de reserva de lucros acumulada e métrica de cobertura em meses
        - Estimativa de dividendo não recorrente obrigatório sob o Art. 10 da Lei 8.668/93
        - Guidance e projeção futura mês a mês para os próximos 6 meses
        """
        ticker = ticker.upper().strip().replace(".SA", "")
        provento_atual = float(provento_atual or kb.get("provento_mes") or 0.80)
        ffo_cota = float(ffo_cota or provento_atual)

        # 1. Resolve Reserva Acumulada de Lucros por Cota
        if reserva_cota is None or reserva_cota <= 0:
            dre_raw = kb.get("dre", {})
            reserva_cota = float(
                dre_raw.get("reserva_acumulada_cota") or
                kb.get("reserva_acumulada_cota") or
                kb.get("reserva_cota") or
                0.0
            )
            if reserva_cota <= 0:
                for l in dre_raw.get("linhas", []):
                    rub = str(l.get("rubrica", "")).lower()
                    if "reserva" in rub and l.get("cota") is not None:
                        val_c = abs(float(l["cota"]))
                        if val_c > 0:
                            reserva_cota = round(val_c * 6.0, 2)
                            break
            if reserva_cota <= 0 and ffo_cota > provento_atual:
                reserva_cota = round((ffo_cota - provento_atual) * 6.0 + 0.15, 2)
            elif reserva_cota <= 0:
                reserva_cota = round(provento_atual * 0.40, 2)

        # 2. Análise Semestral e Sustentabilidade
        now = datetime.now()
        mes_corrente_semestre = ((now.month - 1) % 6) + 1
        semestre_analysis = cls.project_and_analyze(
            ticker=ticker,
            ffo_cota=ffo_cota,
            provento_atual=provento_atual,
            reserva_acumulada_cota=reserva_cota,
            segment_code=segment_code,
            mes_corrente_semestre=mes_corrente_semestre
        )

        # 3. Coleta e consolidação dos últimos 12 meses de proventos
        by_month: Dict[str, List[float]] = {}
        try:
            dist = BolsaiService.get_fii_distributions_summary(ticker, years=1)
            for p in dist.get("history", []):
                d_str = str(p.get("reference_date") or p.get("payment_date") or p.get("date") or "")[:7]
                val = float(p.get("value_per_share") or p.get("rate") or p.get("amount") or 0.0)
                if d_str and val > 0:
                    by_month.setdefault(d_str, []).append(val)
        except Exception as e:
            logger.debug(f"Erro ao buscar proventos BolsaAI para {ticker}: {e}")

        # Se menos de 10 meses obtidos, complementa via yfinance
        if len(by_month) < 10:
            try:
                yf_sym = f"{ticker}.SA"
                t_obj = yf.Ticker(yf_sym)
                divs = t_obj.dividends
                if divs is not None and not divs.empty:
                    for dt, v in divs.tail(24).items():
                        ym = dt.strftime("%Y-%m")
                        val = round(float(v), 4)
                        if val > 0 and ym not in by_month:
                            by_month[ym] = [val]
            except Exception as e:
                logger.debug(f"Erro ao buscar histórico yfinance para {ticker}: {e}")

        months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        
        historico_12m: List[HistoricalDividendPoint] = []
        all_sorted_ym = sorted(by_month.keys())

        if len(all_sorted_ym) >= 12:
            target_yms = all_sorted_ym[-12:]
        else:
            target_yms = []
            for i in range(12, 0, -1):
                m_num = (now.month - i - 1) % 12 + 1
                y_num = now.year + (now.month - i - 1) // 12
                target_yms.append(f"{y_num:04d}-{m_num:02d}")

        for ym in target_yms:
            y, m = ym.split("-")
            label = f"{months_pt[int(m)-1]}/{y[2:]}"
            vals = by_month.get(ym, [])
            if not vals:
                rec = round(provento_atual, 3)
                nrec = 0.0
                tot = rec
            elif len(vals) == 1:
                v = round(vals[0], 3)
                if v > provento_atual * 1.35 and provento_atual > 0:
                    rec = round(provento_atual, 3)
                    nrec = round(v - provento_atual, 3)
                else:
                    rec = v
                    nrec = 0.0
                tot = round(rec + nrec, 3)
            else:
                rec_val = min(vals, key=lambda x: abs(x - provento_atual))
                rec = round(rec_val, 3)
                nrec = round(sum(vals) - rec_val, 3)
                tot = round(rec + nrec, 3)

            historico_12m.append(HistoricalDividendPoint(
                mes=label,
                data=f"{ym}-01",
                recorrente=rec,
                nao_recorrente=nrec,
                total=tot
            ))

        media_recorrente = round(
            sum(p.recorrente for p in historico_12m) / len(historico_12m), 3
        ) if historico_12m else provento_atual

        # 4. Projeção Futura dos Próximos 6 Meses
        projecao_futura: List[FutureDividendProjectionPoint] = []
        meses_restantes = semestre_analysis.get("meses_para_fechamento_semestre", 4)
        extraordinario_estimado = semestre_analysis.get("extraordinario_estimado_fim_semestre", 0.0)
        provento_proj_mes = semestre_analysis.get("provento_projetado_mes", provento_atual)

        for step in range(1, 7):
            proj_m_num = (now.month + step - 1) % 12 + 1
            proj_y_num = now.year + (now.month + step - 1) // 12
            base_label = f"{months_pt[proj_m_num-1]}/{str(proj_y_num)[2:]}"
            
            is_fechamento = (step == meses_restantes) or (proj_m_num in [6, 12] and step <= 6)
            if is_fechamento:
                label_proj = f"{base_label} (Semestral)"
                rec_est = provento_proj_mes
                nrec_est = extraordinario_estimado
                tot_est = round(rec_est + nrec_est, 2)
            else:
                label_proj = base_label
                rec_est = provento_proj_mes
                nrec_est = 0.0
                tot_est = rec_est

            projecao_futura.append(FutureDividendProjectionPoint(
                mes=label_proj,
                recorrente_estimado=rec_est,
                nao_recorrente_estimado=nrec_est,
                total_estimado=tot_est,
                is_fechamento_semestre=is_fechamento
            ))

        base_legal = (
            "Art. 10 da Lei nº 8.668/1993 e Resolução CVM nº 175: O FII deve distribuir no mínimo 95% do lucro caixa apurado "
            "semestralmente (fechamento em 30 de junho e 31 de dezembro). Eventuais superávits operacionais retidos durante o "
            "semestre devem ser compulsoriamente pagos no encerramento."
        )

        return DossierDividendsAnalytics(
            provento_atual=semestre_analysis["provento_atual"],
            ffo_cota=semestre_analysis["ffo_cota"],
            cobertura_ffo_pct=semestre_analysis["cobertura_ffo_pct"],
            status_sustentabilidade=semestre_analysis["status_sustentabilidade"],
            status_cor=semestre_analysis["status_cor"],
            desc_sustentabilidade=semestre_analysis["desc_sustentabilidade"],
            capacidade_manutencao=semestre_analysis["capacidade_manutencao"],
            
            reserva_acumulada_cota=semestre_analysis["reserva_acumulada_cota"],
            meses_reserva_cobertura=semestre_analysis["meses_reserva_cobertura"],
            status_colchao=semestre_analysis["status_colchao"],
            cor_colchao=semestre_analysis["cor_colchao"],
            desc_colchao=semestre_analysis["desc_colchao"],

            extraordinario_estimado_fim_semestre=semestre_analysis["extraordinario_estimado_fim_semestre"],
            provento_pico_fim_semestre=semestre_analysis["provento_pico_fim_semestre"],
            tem_potencial_extraordinario=semestre_analysis["tem_potencial_extraordinario"],
            desc_extraordinario=semestre_analysis["desc_extraordinario"],
            meses_para_fechamento_semestre=meses_restantes,
            base_legal=base_legal,

            provento_projetado_mes=semestre_analysis["provento_projetado_mes"],
            guidance_min=semestre_analysis["guidance_min"],
            guidance_max=semestre_analysis["guidance_max"],
            guidance_faixa=semestre_analysis["guidance_faixa"],

            historico_12m=historico_12m,
            projecao_futura=projecao_futura,
            media_recorrente_12m=media_recorrente
        )
