# CartoGeo 0.5.1 — 29/09/2026 (noite)

- **Pasta dados/importar**: arquivos oficiais colocados ali são importados ao abrir o app, uma única vez cada (royalties da ANP em .xlsx com o ano no nome; produção por poço do CDP em .csv com _Mar ou _Terra no nome). Originais preservados em dados/fontes.
- Carregados nesta versão: royalties 2026 (jan–ago, 6.008 valores) e produção marítima por poço de jan a ago de 2026 (288 registros de RN, SE e AL, todos vinculados ao cadastro). O arquivo de setembro veio vazio (ANP ainda não publicou).
- **Lista quente — Frente 1**: nova coluna com os excedentes do ano corrente contra os mesmos meses do ano anterior; nova tabela de produção marítima por campo (último mês, poços, petróleo, gás e variação no ano).
- **Mensagens de royalties**: incluem a variação recente ("De janeiro a agosto de 2026, a parcela acima de 5% somou…").
- Validação: 38 testes; importação simulada numa cópia do banco real.
