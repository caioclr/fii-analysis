# 03. Guia de Setores e Métricas Especializadas

A análise fundamentalista institucional de Fundos de Investimento Imobiliário (FIIs) e Fiagros exige réguas e métricas especializadas para cada tipologia de ativo. Um condomínio logístico não pode ser avaliado pelos mesmos parâmetros de uma carteira de crédito (CRI), de um shopping center ou de um portfólio de fazendas agrícolas.

Este documento consolida os parâmetros analíticos, fórmulas de cálculo e limites prudenciais adotados no motor de inteligência do **Analisys**.

---

## 🏛️ Métricas Transversais de Governança, Dívida & Risco

### 1. FFO (Funds From Operations) & Sustentabilidade de Proventos
* **Definição:** Mede a verdadeira geração de caixa operacional líquido das atividades recorrentes, expurgando ganhos de capital não-recorrentes com venda de imóveis, receitas voláteis de aplicações financeiras temporárias e efeitos contábeis sem impacto de caixa.
* **Índice de Cobertura do FFO:**
  $$\text{Índice de Cobertura} = \frac{\text{FFO Recorrente por Cota}}{\text{Dividendo Declarado por Cota}} \times 100$$
* **Diagnóstico da Auditoria:**
  * **Cobertura $\ge 100\%$:** **Superávit Operacional.** O dividendo é 100% suportado pela renda operacional dos contratos vigentes, permitindo a formação de colchão de reserva.
  * **Cobertura $< 100\%$:** **Déficit Operacional.** O fundo está pagando rendimentos acima do seu resultado caixa do mês, consumindo caixa acumulado, amortizando capital ou utilizando reservas passadas.

### 2. Estrutura de Capital, Securitizações e Alavancagem Financeira
A seção dedicada de estrutura de capital analisa 4 grandezas fundamentais:
1. **Saldo Devedor de CRIs (Passivo Oneroso):** Montante consolidado em R$ Milhões devido pelo fundo referente a emissões de Certificados de Recebíveis Imobiliários estruturados para aquisição e expansão de ativos.
2. **Alavancagem Financeira Bruta (Passivo / PL):**
   $$\text{Alavancagem} = \frac{\text{Saldo Devedor Oneroso de CRIs}}{\text{Patrimônio Líquido Contábil (CVM)}} \times 100$$
   * **Faixa Segura:** $\le 25,00\%$ do PL (zona de conforto prudencial).
   * **Faixa de Alerta:** $> 25,00\%$ do PL (risco de rolagem, compressão do FFO com juros altos e dependência de novas emissões de cotas).
3. **Dívida / Ativo Total (LTV Contábil):**
   $$\text{LTV Contábil} = \frac{\text{Passivo Oneroso}}{\text{Ativo Total Contábil}} \times 100$$
   Exibe também o valor nominal do **Ativo Total** consolidado em R$ Bilhões, demonstrando o tamanho real do balanço do fundo.
4. **Caixa Livre & Liquidez Imediata:** Saldo em tesouraria e aplicações de liquidez diária disponível para honrar amortizações contratuais e aproveitar oportunidades de aquisição sem necessidade de alavancagem adicional.

### 3. Escala Unificada de Score de Qualidade (0,0 a 10,0)
Para garantir consistência absoluta entre o Screener, o Comparador Setorial e o Dossiê Executivo, **todos os scores da plataforma são padronizados rigorosamente na escala de 0,0 a 10,0**:
* **8,5 a 10,0:** **Grau de Excelência / Aprovado.** Ativo de altíssima qualidade de governança, portfólio defensivo, cobertura FFO robusta e alavancagem equilibrada.
* **7,0 a 8,4:** **Grau Regular / Neutro.** Fundos operacionais saudáveis com pontos pontuais de atenção (ex: vacância localizada ou alavancagem moderada).
* **0,0 a 6,9:** **Grau de Atenção / Cautela.** Portfólio estressado, cobertura FFO deficitária ou risco de inadimplência/crédito elevado.

### 4. Gestão de Proventos, Colchão de Reserva e Distribuição Compulsória (Lei nº 8.668/93)
* **Saldo de Reserva Acumulada de Lucros (R$/cota) e Autonomia:**
  $$\text{Meses de Autonomia} = \frac{\text{Saldo de Reserva Acumulada por Cota}}{\text{Dividendo Recorrente por Cota}}$$
  * **$\ge 2,0$ meses:** **Colchão Confortável.** Amplo amortecedor financeiro contra sinistros, inadimplências pontuais ou obras de retrofits sem necessidade de redução de proventos.
  * **$1,0$ a $1,9$ meses:** **Colchão Moderado.** Margem prudencial adequada para sustentação temporária de rendimentos lineares.
  * **$< 1,0$ mês:** **Colchão Comprimido.** Baixa capacidade de amortecimento; qualquer choque operacional na receita de locação impactará diretamente a distribuição mensal.
* **Distribuição Compulsória Semestral (Art. 10 da Lei Federal nº 8.668/93 e Resolução CVM nº 175):**
  * O Fundo Imobiliário é legalmente obrigado a distribuir no mínimo **95% dos lucros auferidos apurados em regime de caixa**, calculados com base em balanço semestral encerrado em 30 de junho e 31 de dezembro.
  * Quando as distribuições lineares mensais retêm parcela do FFO para reserva, no último mês do semestre (junho e dezembro) o fundo deve obrigatoriamente distribuir todo o excedente legal, gerando o **Dividendo Extraordinário Não Recorrente Obrigatório**.
* **Guidance & Projeção Futura (6 Meses):**
  * O modelo projeta o dividendo mensal regular sustentável pelo FFO operacional e antecipa o salto no mês de fechamento do semestre civil, permitindo ao investidor precificar o rendimento total no ano.

---

## 🌾 Segmento Especializado: Fiagros & Terras Agrícolas (AGRO)

Fiagros com foco imobiliário rural (como o `RZTR11`) possuem dinâmicas específicas do agronegócio:

### 1. Estratégias de Aquisição e Arrendamento de Terras
* **Sale & Leaseback (SLB):** O fundo adquire a fazenda de um produtor rural consolidado e a arrenda de volta para o mesmo operador sob contrato atípico de longo prazo (geralmente 10 a 15 anos), muitas vezes com opção de recompra pré-fixada garantindo TIR real atrativa (`IPCA + 11% a 13% a.a.`).
* **Buy to Lease (BTL):** O fundo adquire terras estratégicas no mercado e as arrenda a terceiros produtores de grãos, cana ou fibras.
* **Land Equity:** Valorização do hectare agrícola decorrente de transformação e abertura de pastagens degradadas para lavouras de alta produtividade (soja, milho safrinha e algodão).

### 2. Raio-X da Carteira Agro (Donuts Pure CSS)
* **Donut 1 — Distribuição por Cultura Agrícola:**
  * Miolo: `CADEIA / AGRO`.
  * Grãos (Soja e Milho), Algodão & Fibras, Cana-de-Açúcar e Pecuária/Pastagens.
* **Donut 2 — Estratégia de Investimento & Indexadores:**
  * Miolo: `TAXA / INDEX`.
  * Sale & Leaseback (SLB), Buy to Lease (BTL), Land Equity / Desenvolvimento e Caixa & Liquidez.

### 3. Garantias Reais & Blindagem Jurídica no Campo
* **LTV Rural Conservador:** Em geral inferior a 45%, significando que o valor de mercado das terras dado em garantia supera em mais de 2x o capital investido pelo fundo.
* **Alienação Fiduciária da Terra:** A propriedade fiduciária fica registrada em nome do fundo até a quitação integral das obrigações do arrendamento.
* **Proteção pela Lei do Agro (Lei nº 13.986/20):** Confere regime especial às Cédulas de Produto Rural (CPRs) e alienações fiduciárias, preservando as garantias do fundo mesmo em processos de Recuperação Judicial do arrendatário.

---

## 🚛 Segmento: Logística e Renda Urbana

Centrado em condomínios logísticos modulares, centros de distribuição e *hubs* de e-commerce:
* **WAULT (*Weighted Average Unexpired Lease Term*):** Prazo médio ponderado de vencimento de todos os contratos vigentes ($> 5$ anos é excelente).
* **Contratos Atípicos (BTS / SLB):** Cláusulas de rescisão estipulando multa equivalente ao saldo integral devedor do contrato.
* **Especificações Técnicas de Engenharia:** Pé-direito livre $\ge 12$ metros, piso industrial de alta resistência com capacidade de carga $\ge 5$ a $6\text{ ton/m}^2$, proporção de docas com niveladores eletro-hidráulicos e certificação de sustentabilidade (LEED).

---

## 🛍️ Segmento: Shopping Centers

* **SSS (*Same Store Sales*):** Crescimento de vendas nas mesmas lojas frente ao ano anterior.
* **SSR (*Same Store Rent*):** Variação dos aluguéis reajustados para a mesma base de lojistas.
* **Custo de Ocupação (OCR):** Razão entre custo de ocupação do lojista (aluguel + condomínio + fundo de promoção) e seu faturamento (saudável entre 10% e 13,5%).
* **Mix de Receitas:** Equilíbrio entre Aluguel Mínimo, Aluguel Percentual de Vendas e Estacionamento.

---

## 📑 Segmento: Recebíveis Imobiliários (Papel / CRIs)

* **Nível de Subordinação:** Proporção de cotas Sênior (prioridade no recebimento do fluxo financeiro e garantias), Mezanino e Subordinada (que absorve os primeiros impactos de eventual inadimplência).
* **Indexadores:** Divisão da carteira entre títulos indexados à inflação (`IPCA + Spread% a.a.`) e à taxa de juros básica (`CDI + Spread% a.a.`).
* **LTV Médio Ponderado dos CRIs:** Relação média entre o valor do crédito concedido e o valor do laudo dos imóveis dados em garantia real imobiliária.
