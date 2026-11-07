# CartoGeo 0.5.2 — versão de passagem (06/10/2026)

Preparada para a instalação no computador do Gilberto.

- **Assinatura e nomes pela conta logada.** As mensagens de abordagem, o roteiro de ligação, a saudação da Central e o relatório de prospecção usam o nome completo da conta que está usando o app. Não há mais nome de pessoa fixo no código. Sem nome cadastrado, o texto sai com "[seu nome]" e um aviso.
- **Contas em português.** `03_CRIAR_USUARIO.bat` cria uma conta (nome completo, usuário e senha). `04_ALTERAR_USUARIO.bat` troca senha e nome e desativa ou reativa contas. O instalador pede a criação da conta no passo 4 de 4.
- **Trimestre automático.** As metas acompanham o trimestre corrente, avançando de três em três meses a partir de 01/09/2026 (set–nov, dez–fev, mar–mai, jun–ago).
- **Relatórios do mês.** A tela Metas tem botões para o mês atual e o mês anterior, no lugar do botão fixo de setembro.
- **Lista quente estável.** A lista não cai mais se um alvo for ligado a uma organização sem município.
- **Responsável "A definir".** O padrão do campo Responsável e a etapa "Aguardar decisão da direção" não citam mais nomes. Migração `0006`.
- **Base entregue.** A base de 06/10/2026 vem com a migração aplicada, as 24 oportunidades e as 5 ações internas com responsável "A definir" e a conta "comercial" desativada.
- Testes: 42, todos passando.
