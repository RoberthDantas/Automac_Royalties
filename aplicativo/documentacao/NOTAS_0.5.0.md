# CartoGeo 0.5.0 — 29/09/2026 (noite)

Atualização sobre a 0.4.2, sem apagar dados. Backup prévio em `_backups`.

## Novo
- **Lista quente — Paraíba**: planos diretores monitorados (Lucena 2001, Santa Rita 2006, João Pessoa 2024, Cabedelo 2024), oportunidades no eixo da Ponte do Futuro e na orla de João Pessoa, sinais de demanda.
- **Contatos pesquisados** de 5 prefeituras do 1º círculo (Macau, Guamaré, Areia Branca, Porto do Mangue, Grossos), com fonte, marcados como não conferidos.
- **Botão "Conferi por telefone"** na ficha da oportunidade: marca a data de conferência; o contato passa a contar nas metas.
- **Gerador de mensagens**: e-mail e roteiro de ligação com os números do município (royalties 2021–2025 ou plano diretor), destinatários escolhidos pelo cargo, avisos quando a tese é fraca. Nada é enviado automaticamente.
- **Série de royalties** 2021 até o ano atual numa única coleta (botão em Royalties e opção em Fontes e coletas).
- **Tarefas dos dois primeiros cursos** (GNSS e QGIS) em Tarefas e decisões.
- **Guia de uso completo** no menu "Guia de uso" (texto-fonte: documentacao/GUIA_COMPLETO.md).
- Menu reorganizado: "Fontes e coletas" visível; listas quentes e metas no topo.

## Fontes da pesquisa (29/09/2026)
Pasta do Google Drive de Uendry (planos de Lucena, Cabedelo, Santa Rita, João Pessoa; LUOS JP; deliberação COPAM 5.652); SAPL Cabedelo (LC 87/2024); Câmara de João Pessoa; clickpb.com.br (recomendação MPPB a Santa Rita); polemicaparaiba.com.br (LUOS JP no TJPB); portaldacapital.com (embargo da Ponte do Futuro, 23/09/2026); sites e dados abertos das prefeituras de Macau, Guamaré, Areia Branca, Porto do Mangue e Grossos. Referência: referencias/prospeccao_20260929/prospeccao.json.

## Validação
37 testes automatizados; 127 telas conferidas numa cópia do banco com os royalties já carregados; carga idempotente (segunda execução não cria nada).

## Pendente
Tibau e Galinhos (sites bloquearam consulta automática); conferir por telefone todos os contatos; datas exatas das leis de Lucena, Santa Rita e João Pessoa; participação especial; tirar a pasta do OneDrive.
