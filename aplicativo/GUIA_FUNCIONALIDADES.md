# Funcionalidades da CartoGeo 0.5.0

Guia completo: menu "Guia de uso" ou documentacao/GUIA_COMPLETO.md. Novidades: documentacao/NOTAS_0.5.0.md e NOTAS_0.4.2.md.

Novidades da 0.4.2 (lista quente, metas, cadência de follow-up, filtros do radar, planilha de poços): ver documentacao/NOTAS_0.4.2.md.

Para instalar esta edição do zero, use COMECE_AQUI.txt na pasta principal.

## O que ficou pronto

| Área | Ação disponível | Resultado |
|---|---|---|
| Central de cartórios | Filtrar por município, UF e Registro de Imóveis; copiar e-mails/telefones; exportar CSV | Endereço, atribuições, fonte, data e contatos numa tela |
| Agenda e automações | Criar, editar, pausar e executar rotinas | Intervalo, dia da semana, dia do mês ou horário diário |
| Radar | Filtrar por tema, UF, origem, prazo e primeira coleta | REURB, planos diretores, cadastro, levantamentos, ambiental, royalties e expansão/obras |
| Fontes e cobertura | Cadastrar páginas públicas ou privadas, RSS/Atom e PDF textual | Última tentativa, último sucesso e erros visíveis |
| Briefing do dia | Baixar Markdown no topo da tela | Até 30 sinais priorizados, tarefas e resultado de coletas, sem geração por IA |
| Continuidade e evidências | Exportar acompanhamento e dossiê | Tarefas, etapas, pendências, agenda, falhas, fontes e métodos para retomar o trabalho |

A identidade visual usa a marca fornecida. Menu lateral, cartões de indicadores, ações rápidas, filtros, avisos de novos sinais e visual adaptado ao celular.

### Cartórios

Carga inicial: **78 cartórios ativos na consulta CNJ de 18/09/2026, da Paraíba**. Não representa todos os cartórios das cinco UFs nem confirma atendimento atual. Endereços e atribuições são complementados quando vazios; alterações de contatos e marcação “Não contatar” são preservadas. A lista copiável exclui bloqueados; o CSV mantém esses registros com a coluna de bloqueio explícita. Nenhum e-mail é enviado automaticamente.

### Rotinas iniciais

| Fonte | Frequência inicial | Observação |
|---|---|---|
| PNCP por capacidades | A cada 12 horas | PB/RN/CE/SE/AL; objeto da contratação; propostas no recorte de 30 dias; paginação retomável |
| Índice Querido Diário | Uma vez ao dia | Últimos 14 dias; depende das cidades indexadas e da disponibilidade do serviço |
| Páginas públicas/privadas | A cada 2 horas | Fontes ativas cadastradas; até 20 por execução, priorizando as menos recentemente consultadas |
| Cadastro de poços | Segunda-feira, 08h | Cadastro ANP; não equivale à produção mensal |
| Royalties | Dia 20, 09h | Atualiza a consulta do ano corrente; publicação da fonte pode atrasar |

Horário de Brasília/Fortaleza. Pode alterar todas essas configurações. Se escolher dia 31, um mês curto usa seu último dia. Após desligamento, a agenda executa uma ocorrência pendente, sem acumular todas as execuções perdidas. Coletas são serializadas; a duração e as filas podem atrasar o horário previsto.

**Produção por poço:** o exportador interativo do CDP continua com importação assistida. Há uma nova rotina de CSV por **URL pública direta**, se você possuir um endereço estável do arquivo. Selecione Terra/Mar corretamente. Não confundir a página do portal com o arquivo CSV; não há descoberta automática do arquivo mensal nem automação de login. Duplicidades ambíguas e divergências de ambiente são rejeitadas; o original recebido fica preservado.

### O que “praticamente em tempo real” significa aqui

O painel consulta seu banco a cada 30 segundos; o PNCP é consultado pela agenda inicialmente a cada 30 minutos. Isso não é um serviço de streaming nem garante descoberta em 30 minutos: dependemos da publicação, indexação, disponibilidade das fontes e conclusão das páginas. Sem aplicativo ou executor ativo, não há coleta.

O agendamento Windows verifica a fila a cada cinco minutos e exige computador ligado, internet e sessão do usuário iniciada. Não funciona com o computador desligado. `ROTINA_LOCAL.bat` é outra opção enquanto sua janela estiver aberta. Nenhuma dessas rotinas consome tokens de IA.

### Mais oportunidades públicas e privadas

Fontes iniciais: PNCP, integração ao índice Querido Diário e páginas oficiais de João Pessoa, Cabedelo, Ministério das Cidades e INCRA. Elas são pontos de entrada; não cobrem integralmente documentos, municípios, diários estaduais ou Diário Oficial da União.

Em **Fontes e cobertura → Adicionar fonte pública ou privada**, registre a URL pública de uma incorporadora, entidade setorial ou portal municipal; selecione HTML, RSS/Atom ou PDF e os termos relevantes. Para empresas, marque a origem privada. Essas fontes precisam ser escolhidas e cadastradas: não há carteira de leads privados verificados incluída.

Prefira feeds e páginas específicas de publicações. Uma página inicial HTML pode revelar apenas títulos e links, não o texto integral dos documentos. PDFs são lidos até 80 páginas; documentos digitalizados precisam de OCR externo. Conteúdo com login, bloqueio ou carregamento apenas por JavaScript pode exigir consulta manual.

A aderência é uma regra textual transparente: 20 pontos de base + 12 por tema + 20 para PNCP, teto 95. Não representa probabilidade de contratação, valor comercial, habilitação ou validação jurídica. Publique-se, coletou-se e encerra-se são datas diferentes.

## Fluxo de trabalho recomendado

1. Abra o briefing e os prazos de sete dias. Confira também as falhas em Fontes e cobertura.
2. Revise a fonte original e o escopo. Notícias de REURB, revisão de plano diretor, cadastro municipal ou empreendimento são indícios para investigação.
3. Promova sinais pertinentes para o funil, atribuindo responsável, próxima ação e prazo. Descarte ruídos sem apagá-los.
4. Use os contatos dos cartórios após conferir atendimento e eventual bloqueio de contato.
5. Exporte acompanhamento quando quiser retomar aqui. O chat não observa automaticamente o aplicativo no seu computador.
6. Gere o dossiê nas decisões relevantes e preserve uma cópia independente dos originais e hashes.

## Próximos avanços sugeridos — não implementados nesta versão

- Executor sempre ligado em equipamento dedicado, com monitoramento de falhas, para manter coleta contínua.
- Carteiras de municípios e empresas escolhidas por Uendry, com metas de cobertura e responsáveis pela verificação.
- Associação entre publicação, imóvel/território, organização e contato, após validação dos identificadores; evitar vínculos automáticos só por nomes parecidos.
- Alertas externos por canal escolhido e autorizado, após validar qualidade dos sinais e reduzir falsos positivos.

A versão entregue já prioriza rastreabilidade, agenda sem tokens e revisão comercial. Esses próximos avanços exigem fontes e operação definidas, não apenas mudança visual.
