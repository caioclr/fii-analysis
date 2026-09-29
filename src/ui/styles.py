import streamlit as st

def apply_custom_css():
    """Aplica estilos CSS customizados para uma interface moderna e profissional."""
    st.markdown("""
        <style>
        /* Tipografia e espaçamento */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }

        /* Cartões de métricas customizados */
        .metric-card {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border-radius: 12px;
            padding: 20px;
            color: #FFFFFF;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #334155;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .metric-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94A3B8;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 1.7rem;
            font-weight: 700;
            color: #F8FAFC;
        }
        .metric-delta-positive {
            color: #10B981;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .metric-delta-negative {
            color: #EF4444;
            font-weight: 600;
            font-size: 0.9rem;
        }

        /* Badges de Status P/VP */
        .badge-discount {
            background-color: #D1FAE5;
            color: #065F46;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .badge-fair {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .badge-agio {
            background-color: #FEE2E2;
            color: #991B1B;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.8rem;
        }

        /* Banner de destaque */
        .magic-box {
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            border-radius: 12px;
            padding: 20px;
            color: white;
            margin: 15px 0;
        }
        </style>
    """, unsafe_allow_html=True)
