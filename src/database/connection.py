import sqlite3
from src.config import DB_PATH

def get_connection():
    """Retorna uma conexão ativa com o banco SQLite."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados caso não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de Ativos da Carteira
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            asset_type TEXT NOT NULL, -- 'FII', 'ACAO', etc.
            quantity REAL NOT NULL DEFAULT 0,
            average_price REAL NOT NULL DEFAULT 0,
            target_percent REAL DEFAULT 0,
            segment TEXT,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de Histórico de Transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            transaction_type TEXT NOT NULL, -- 'COMPRA', 'VENDA', 'PROVENTO'
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            total_value REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de Metas de Alocação Macro (Ex: 40% FIIs, 40% Ações, 20% Renda Fixa)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_allocation (
            asset_type TEXT PRIMARY KEY,
            target_percent REAL NOT NULL DEFAULT 0
        )
    """)

    # Tabela de Cache de Cotações e Indicadores de Mercado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_cache (
            ticker TEXT PRIMARY KEY,
            current_price REAL,
            pvp REAL,
            dy_12m REAL,
            last_dividend REAL,
            vp_per_share REAL,
            segment TEXT,
            data_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de Histórico de Auditorias Fundamentalistas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            audit_date TEXT NOT NULL,
            score REAL,
            veredicto TEXT,
            preco_mercado REAL,
            vpc REAL,
            pvp REAL,
            dy_anual REAL,
            preco_teto REAL,
            alocacao_sugerida TEXT,
            ffo_cota REAL,
            cobertura_ffo REAL,
            alavancagem_pct REAL,
            vacancia_fisica REAL,
            trend_status TEXT,
            reserva_cota REAL,
            guidance_proximo_mes REAL,
            extraordinario_estimado REAL,
            real_yield_pct REAL,
            custom_params_json TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de Séries Temporais Gerenciais (Multi-Mês)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gerencial_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            periodo TEXT NOT NULL,
            ano INTEGER,
            mes INTEGER,
            vacancia_fisica REAL,
            vacancia_financeira REAL,
            ocupacao_pct REAL,
            sss_pct REAL,
            ssr_pct REAL,
            aluguel_medio_m2 REAL,
            ocr_pct REAL,
            inadimplencia_pct REAL,
            ffo_cota REAL,
            provento_cota REAL,
            cobertura_ffo REAL,
            alavancagem_pl_pct REAL,
            ltv_pct REAL,
            reserva_acumulada_cota REAL,
            raw_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, periodo)
        )
    """)

    # Tabela de Parâmetros de Precificação e Macro
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pricing_parameters (
            param_name TEXT PRIMARY KEY,
            param_value REAL NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Inserção de metas macro padrão se vazio
    cursor.execute("SELECT COUNT(*) FROM macro_allocation")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO macro_allocation (asset_type, target_percent) VALUES (?, ?)",
            [
                ("FII", 50.0),
                ("ACAO", 40.0),
                ("RENDA_FIXA", 10.0),
                ("OUTRO", 0.0)
            ]
        )

    # Parâmetros de precificação padrão se vazio
    cursor.execute("SELECT COUNT(*) FROM pricing_parameters")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO pricing_parameters (param_name, param_value, description) VALUES (?, ?, ?)",
            [
                ("ntnb_reference_rate", 6.50, "Taxa de juro real do Tesouro IPCA+ longo (NTN-B 2035) em % a.a."),
                ("projected_ipca", 4.00, "Inflação projetada para 12 meses (Boletim Focus) em % a.a."),
                ("real_risk_spread", 2.00, "Spread de risco imobiliário exigido acima do Tesouro IPCA+ em % a.a.")
            ]
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")
