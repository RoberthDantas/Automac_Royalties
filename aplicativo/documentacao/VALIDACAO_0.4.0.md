# Validação e limites — 0.4.0

Data da preparação: 28/09/2026.

## Verificação do aplicativo

- 28 testes Django passaram: fluxos anteriores, calendário mensal/semanal, autenticação, CSRF, exclusão de contatos bloqueados na cópia, proteção contra fórmulas no CSV, preservação de revisão, leitura RSS/Atom, falhas de fontes, edição/pausa, execução serial, retomada de paginação, cargas idempotentes, divergência de ambiente ANP e exportação de continuidade.
- `makemigrations --check --dry-run`: nenhuma alteração de modelo sem migração.
- Navegador Chromium: início, cartórios, agenda, radar e cobertura responderam HTTP 200; nenhum erro JavaScript observado. Verificação em 1440 px e 390 px sem transbordamento horizontal. Cartórios no celular usam blocos verticais.
- Windows, Python 3.14 e o Agendador de Tarefas não foram executados neste ambiente Linux/Python 3.12. Scripts entregues dependem de instalação e validação no PC do usuário.
- Não se verificou o banco atual do computador do usuário. O pacote exclui dados de desenvolvimento; não substitui sua base.

## Consulta real de preparação

Amostra PNCP em `referencias/pncp_20260928/`: 15 requisições previstas, três páginas para cada UF PB/RN/CE/SE/AL, tamanho 50, prazo final consultado 28/10/2026. Sete respostas válidas retornaram 350 publicações: RN páginas 2–3, CE páginas 1–2 e AL páginas 1–3. Oito requisições terminaram por timeout. Nenhuma das 350 descrições correspondeu aos termos dos perfis técnicos configurados na amostra. Isso não demonstra ausência de oportunidades, nem cobertura integral de qualquer UF.

O manifesto guarda URL exata, instante do pedido registrado pelo ambiente, cabeçalhos recebidos, estado e SHA-256 dos corpos JSON preservados. Os dados são uma referência histórica da entrega, não sinais comerciais inventados nem uma coleta atual realizada no PC do usuário. Os arquivos constam do dossiê de referências; não são importados como leads.

Uma requisição direta ao PNCP respondeu neste ambiente por seu mecanismo de rede. O coletor protegido do aplicativo encontrou falha de resolução DNS aqui. Sua validação de destinos públicos foi mantida; não foi removida para forçar um resultado. É necessário executar e conferir uma coleta na instalação local.

A API do índice Querido Diário apresentou bloqueio/indisponibilidade durante a preparação. A integração foi implementada com base no formato documentado, mas a cobertura ponta a ponta desse serviço não foi confirmada. Falhas são registradas; não equivalem a zero resultados. As páginas iniciais cadastradas também precisam de consulta local para medir cobertura útil.

## Fontes de referência

- PNCP: https://pncp.gov.br/ e API de consulta https://pncp.gov.br/api/consulta/v1/contratacoes/proposta
- Documentação Querido Diário: https://docs.queridodiario.ok.org.br/pt-br/latest/utilizando/api-publica.html
- Índice utilizado: https://api.queridodiario.ok.org.br/gazettes
- ANP, produção por poço: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/producao-de-petroleo-e-gas-natural-por-poco
- Contatos CNJ: conservar as URLs e arquivos originais individualizados em `cartorios_cnj_20260918`.

## Rastreabilidade e valor probatório

Aplicam-se também as orientações de `PROTOCOLO_FONTES.md`. O dossiê conserva fontes disponíveis, metadados, métodos e hashes. Hash prova correspondência entre bytes quando comparado com uma referência confiável; sozinho não comprova autoria, data original, veracidade, integridade anterior à captura ou validade jurídica. Relógio local e capturas automatizadas não equivalem a assinatura digital, ata notarial ou carimbo de tempo confiável.

Não há declaração de habilitação profissional, direito a royalties, existência de contratação aberta ou adequação ambiental produzida automaticamente. Documentos originais e análise técnica continuam necessários. Não foram enviadas mensagens, instaladas rotinas no computador do usuário nem publicados dados comerciais.
