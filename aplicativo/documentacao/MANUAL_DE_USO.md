# Manual de uso — App Automac_Royalties 0.5.1

30/09/2026 · Uendry Maia

## Como usar este manual

Este manual ensina a operar o App Automac_Royalties 0.5.1 tela por tela e tarefa por tarefa. Ele complementa o **Guia de uso** que fica dentro do app. Consulte a parte que responde à sua dúvida; não é preciso ler tudo em ordem.

| Parte | Consulte quando precisar de… |
| --- | --- |
| 1. Instalar, abrir, entrar e fechar | ligar o app, criar ou trocar senha, encerrar sem perder dados |
| 2. Mapa do app | saber para que serve cada item do menu e em que ordem usar |
| 3. Rotinas | saber o que fazer hoje, nesta semana, neste mês e no trimestre |
| 4A a 4D. Tela a tela | entender cada campo, botão, filtro e aviso de uma tela |
| 5. Procedimentos completos | executar uma tarefa inteira, do primeiro clique ao registro final |
| 6. Regras comerciais | saber o que o app faz sozinho, o que nunca faz e por quê |
| 7. Problemas e soluções | resolver uma mensagem de erro ou um comportamento estranho |
| Glossário, arquivos e pastas | entender um termo ou achar um arquivo no computador |

**Convenções de escrita**

- **Negrito** é o texto exato de um botão, menu, campo ou aviso, como aparece na tela. Exemplo: **Registrar atividade**.
- A seta indica um caminho de cliques. Exemplo: **Poços e produção** → **Importar produção mensal**.
- `Texto em código` é um arquivo, pasta ou endereço. Exemplo: `02_ABRIR.bat`, `http://127.0.0.1:8766`.
- Os caminhos de pasta partem da pasta principal do app. A recomendada é `C:\Automac_Royalties\`. A versão instalada aparece no pé do menu lateral.
- **Atenção:** marca uma ação que pode perder dados, travar uma coleta ou gerar retrabalho.

**Três ideias que explicam o app inteiro**

1. Tudo termina em uma próxima ação com data. Oportunidade sem data some da sua rotina diária.
2. O que não foi registrado não existe para as metas nem para os relatórios.
3. O app não envia nada sozinho. Ele coleta, organiza, calcula e prepara rascunhos; quem decide e envia é você.

## Parte 1 — Instalar, abrir, entrar e fechar

O app roda no seu computador e abre no navegador pelo endereço `http://127.0.0.1:8766`. Enquanto a janela preta estiver aberta, o app e a agenda de coletas funcionam.

### 1.1 O que há na pasta principal

| Item | Para que serve |
| --- | --- |
| `01_INSTALAR.bat` | Instala do zero: cria o ambiente Python, baixa as dependências e cria sua conta |
| `02_ABRIR.bat` | Abre o app. É o único arquivo que você usa no dia a dia |
| `COMECE_AQUI.txt` | Instruções curtas de instalação (o texto ainda diz 0.4.1) |
| `aplicativo\` | O programa, o ambiente Python (`.venv`) e todos os seus dados (`dados\`) |
| `aplicativo\dados\` | Banco de dados, documentos anexados, arquivos das fontes, backups e a pasta `importar` |
| `aplicativo\RESTAURAR.bat` | Volta um backup (ver Procedimento 12) |
| `aplicativo\DIAGNOSTICO.bat` | Gera um resumo técnico sem contatos nem senhas, para pedir ajuda |

**Atenção:** a pasta está dentro do OneDrive. A sincronização pode corromper o banco enquanto o app está aberto. Mova para `C:\Automac_Royalties\` assim que puder (Procedimento 13).

### 1.2 Instalar em um computador novo

Você só faz isto uma vez por computador.

**Antes de começar**

- Windows 10 ou 11 com internet.
- Python 3.12, 3.13 ou 3.14 instalado (python.org). Na instalação do Python, marque **Add python.exe to PATH**.

**Passo a passo**

1. Copie a pasta principal para `C:\Automac_Royalties\`, **sem** a pasta `aplicativo\.venv`: o ambiente Python é refeito na instalação.
   - Para levar os dados junto, mantenha `aplicativo\dados`. As contas existentes continuam valendo, e o instalador não pede conta nova.
   - Para começar sem dados, deixe de fora também `aplicativo\dados`.
2. Dê dois cliques em `01_INSTALAR.bat`.
   - Se o Windows mostrar um aviso de proteção, clique em **Mais informações** e depois em **Executar assim mesmo**.
3. Acompanhe as três etapas na janela preta:
   - **\[1/3\]** cria o ambiente `aplicativo\.venv`;
   - **\[2/3\]** baixa Django, waitress, openpyxl e as demais dependências (precisa de internet);
   - **\[3/3\]** prepara o banco de dados.
4. Sem dados anteriores, o instalador pede para criar sua conta. As perguntas saem parte em inglês:
   - **Usuário**: um nome curto, sem espaço (exemplo: `uendry`);
   - **Endereço de email**: pode deixar em branco e apertar Enter;
   - **Password** e **Password (again)**: a senha não aparece enquanto você digita. Use 10 caracteres ou mais, sem ser só números nem senha comum.
5. Se aparecer **Bypass password validation and create user anyway? \[y/N\]**, a senha foi recusada. Digite `N`, aperte Enter e escolha outra.
6. Espere **INSTALAÇÃO CONCLUÍDA**. Feche a janela.

Se o Python não estiver instalado, a janela avisa e para. Nos demais erros, o instalador grava `ERRO_INSTALACAO.txt` na pasta principal. As causas mais comuns são versão errada do Python e falta de internet.

### 1.3 Abrir o app (todo dia)

1. Dê dois cliques em `02_ABRIR.bat`.
2. A janela preta executa, nesta ordem:
   - backup automático, só quando há atualização pendente do banco (**Backup antes da atualizacao: …**);
   - verificações do banco;
   - preparação dos cadastros (municípios, cartórios, agenda, lista quente e pesquisas);
   - importação da pasta `dados\importar` (**Pasta importar: … Concluída** ou **nenhum arquivo novo**).
3. Quando aparecer **Automac_Royalties: http://127.0.0.1:8766 / Mantenha esta janela aberta**, o navegador abre sozinho.
4. Se o navegador não abrir, digite `http://127.0.0.1:8766` na barra de endereço. Vale salvar esse endereço nos favoritos.
5. Minimize a janela preta. Não feche: fechar desliga o app e a agenda.

**Mensagens normais na janela preta**

- **Backup antes da atualizacao: …** aparece depois de uma atualização do app. É o backup automático; nada a fazer.
- **A aplicacao ou a restauracao ja esta em execucao. Feche-a primeiro.** O app já está aberto em outra janela, ou uma coleta ainda roda em segundo plano. Procure a aba do navegador já aberta; se não houver, espere alguns minutos e abra de novo.
- **Uma coleta anterior ainda esta ativa; aguarde sua conclusao.** Espere a coleta terminar antes de iniciar outra.

### 1.4 Entrar

1. Na tela **Acesse sua operação**, preencha **Usuário** e **Senha**.
2. Clique em **Entrar**. Você cai na **Central de operação**.
3. Se aparecer **Por favor, entre com um usuário e senha corretos**, confira maiúsculas e minúsculas: os dois campos diferenciam.

A sessão dura até duas semanas no mesmo navegador, mesmo fechando a aba.

### 1.5 Sair e fechar

- **Sair · usuário**, no pé do menu, encerra só a sessão. O app continua ligado.
- **Fechar o app:** na janela preta, aperte `Ctrl+C` ou feche a janela no X.
- Antes de fechar, confira na **Central de operação** → **Coletas recentes** que nenhuma coleta está **Coletando**.

**Atenção:** feche o app antes de atualizar, restaurar backup, mover a pasta ou trocar senha. Não desligue o computador durante uma coleta.

### 1.6 Trocar senha e criar outro usuário

Ainda não há tela para isso: é feito por comando. O plano da equipe prevê uma tela de usuários.

1. Feche o app.
2. Abra a pasta `aplicativo` no Explorador de Arquivos.
3. Clique na barra de endereço da pasta, digite `cmd` e aperte Enter. Abre um prompt já nessa pasta.
4. Digite um dos comandos e aperte Enter:
   - trocar senha: `.venv\Scripts\python.exe manage.py changepassword uendry` (troque `uendry` pelo seu usuário);
   - criar usuário: `.venv\Scripts\python.exe manage.py createsuperuser`.
5. Digite a nova senha duas vezes. Feche o prompt e abra o app.

Hoje todo usuário vê e altera tudo. Não existe perfil só de leitura.

### 1.7 Celular e outros computadores

Hoje o app só abre no computador onde está rodando: o endereço `127.0.0.1` significa "este computador". O acesso do Gilberto e da equipe está no documento **App Automac_Royalties para a equipe**.

## Parte 2 — Mapa do app

O menu lateral tem 21 itens. Aqui eles aparecem em sete grupos para facilitar; o menu não mostra os grupos. O nome no menu nem sempre é igual ao título da tela; a tabela mostra os dois para você se localizar.

| Grupo | Menu | Título da tela | Para que serve | Quando usar |
| --- | --- | --- | --- | --- |
| Prospecção | **Central de operação** | Sua central de inteligência. | Resumo do dia: metas da semana, ações vencendo, sinais novos, coletas | Todo dia, ao abrir |
| Prospecção | **Lista quente — Frente 1** | Lista quente — Frente 1 (royalties) | Os 20 municípios-alvo de royalties por círculo, com excedentes e produção marítima | Ao escolher quem abordar |
| Prospecção | **Lista quente — Paraíba** | Lista quente — Paraíba | Planos diretores, oportunidades e sinais na Paraíba | Ao escolher quem abordar na PB |
| Prospecção | **Metas e relatório** | Metas do trimestre — set. a nov. 2026 | Metas da semana e do trimestre, atrasadas, relatórios para baixar | Toda sexta |
| Prospecção | **Funil comercial** | Oportunidades | Lista de todas as oportunidades e a ficha de cada uma | Sempre que for trabalhar um alvo |
| Sinais | **Radar de oportunidades** | Radar de oportunidades | Sinais coletados (PNCP, páginas, diários, registros manuais) para revisar | Todo dia |
| Sinais | **Central de cartórios** | Central de cartórios | 78 cartórios da PB com contatos, cópia de e-mails e CSV | Ao prospectar SIGEF e REURB |
| Organização | **Tarefas e decisões** | Planejamento interno | Ações internas que não são de um cliente (cursos, cadastros de fornecedor) | Semanal |
| Organização | **Agenda e automações** | Agenda e automações | Rotinas de coleta automática e compromissos | Ao criar ou pausar rotinas |
| Coletas | **Fontes e coletas** | Fontes e coletas | Rodar uma coleta na hora e ver o histórico de execuções | Quando precisar de dado novo já |
| Coletas | **Fontes e cobertura** | Fontes e cobertura | Saúde de cada fonte e cadastro de páginas monitoradas | Semanal ou quando algo falhar |
| Dados | **Inteligência territorial** | Municípios | Ficha de cada um dos 751 municípios: royalties por mês e relacionamentos | Ao estudar um município |
| Dados | **Poços e produção** | Poços e cartografia | Cadastro de poços da ANP, mapa, planilha Excel, produção mensal | Ao preparar abordagem de royalties |
| Dados | **Royalties** | Inteligência de royalties | Ranking de royalties por ano, UF e município | Ao preparar abordagem de royalties |
| Dados | **Planos diretores** | Planos diretores | Lei, data-base e marco de revisão de 10 anos por município | Frente de planejamento urbano |
| Cadastros | **Organizações** | Organizações | Prefeituras, órgãos, empresas, escritórios, cartórios, parceiros | Antes de criar oportunidade |
| Cadastros | **Todos os contatos** | Contatos | Pessoas e setores, com conferência por telefone | Ao pesquisar e conferir contatos |
| Cadastros | **Financeiro** | Recebimentos e despesas | Parcelas previstas, recebidas e despesas | Ao fechar proposta ou receber |
| Segurança | **Continuidade e evidências** | Acompanhamento e editais | Varredura de editais por capacidade, pacote de acompanhamento, dossiê de fontes | Semanal ou sob demanda |
| Segurança | **Backup** | Backup e exportação | Backup completo e CSV de oportunidades | Toda sexta |
| Ajuda | **Guia de uso** | Guia de uso do Automac_Royalties | O guia resumido dentro do app | Na dúvida rápida |

**Elementos que aparecem em todas as telas**

- **↓ Briefing do dia**, no topo: baixa um resumo com os 30 sinais a revisar, as tarefas abertas e as 10 últimas coletas.
- **Etiqueta de estado**, no canto superior direito. Ela se atualiza a cada 30 segundos:
  - **Operação local**: acabou de carregar;
  - **Agenda ativa**: as coletas automáticas estão funcionando;
  - **Agenda sem sinal**: a agenda não dá sinal há mais de 6 minutos;
  - **Conexão local interrompida**: a janela preta foi fechada.
- **Sair · usuário** e a versão (**Automac_Royalties 0.5.1**), no pé do menu.
- **Guia de uso**, no rodapé da página.
- Listas longas têm **← Anterior**, **Página X de Y** e **Próxima →**.
- O item do menu só fica destacado na tela principal da seção. Numa subtela (a ficha de uma oportunidade, por exemplo), nenhum item fica destacado.

**A ordem natural de uso**

1. **Os dados entram:** coletas automáticas da agenda, arquivos da pasta `importar` e seus cadastros.
2. **Os alvos aparecem:** sinais no **Radar**, municípios nas **Listas quentes**.
3. **Você qualifica:** converte o sinal em oportunidade ou abre a ficha de um alvo da lista quente.
4. **Você aborda:** confere o contato por telefone, gera a mensagem, envia do seu e-mail e registra a atividade.
5. **O app agenda o retorno:** follow-up em 4 dias (D+4) ou 10 dias (D+10). A **Central** mostra o que vence.
6. **Você presta contas:** **Metas e relatório** mede a semana e o trimestre; na sexta, o relatório vai para o Gilberto.

## Parte 3 — Rotinas

A rotina diária leva cerca de 20 minutos e garante a meta de 10 abordagens por semana. As demais rotinas mantêm os dados atualizados e o Gilberto informado.

### 3.1 Todo dia (manhã)

1. **Abra o app** (`02_ABRIR.bat`) e confira a etiqueta **Agenda ativa** no canto superior direito.
2. Na **Central de operação**, leia o cartão **Prospecção desta semana**:
   - **N de 10 — Abordagens na semana**: quantas faltam para a meta;
   - **Ações vencendo hoje ou atrasadas**: o que não pode passar de hoje.
3. Em **Seu próximo passo**, trate cada item com ponto laranja (oportunidade vencida ou do dia):
   1. clique no item para abrir a ficha;
   2. faça a ação (ligação, e-mail, follow-up);
   3. registre em **Histórico de relacionamento** → **Registrar atividade**. O app agenda o próximo passo.
4. Se sobrar tempo para a meta, abra a **Lista quente — Frente 1** e aborde o próximo município do círculo em aberto (Procedimento 1).
5. No **Radar de oportunidades**, com **Revisão: A revisar** e **Primeira coleta: Novos em 24h**, decida cada sinal:
   - não serve: **Revisar e decidir →** → **Motivo do descarte** → **Descartar sinal**;
   - serve: **Revisar e decidir →** → **Criar oportunidade acompanhável** (Procedimento 2).
6. Antes de desligar o computador, confira em **Coletas recentes** que nada está **Coletando**.

### 3.2 Toda sexta-feira

1. **Metas e relatório**: confira **Abordagens nesta semana** (meta 10) e os **Indicadores do trimestre**.
2. Em **Atrasadas**, replaneje cada item: abra a ficha → **Editar oportunidade** → **Prazo da próxima ação** → **Salvar registro**.
3. Clique em **↓ Relatório da semana** e envie o arquivo ao Gilberto (Procedimento 6).
4. Na **Lista quente — Frente 1**, veja se o círculo da semana está todo abordado. Os prazos do plano são 1º círculo até 02/10, 2º até 09/10 e 3º até 16/10.
5. Em **Fontes e cobertura**, procure fontes com erro em vermelho ou rotinas **Não executada**.
6. Em **Backup**, clique em **Gerar e baixar backup completo** e copie o arquivo para fora do computador (pendrive ou Drive).

### 3.3 Todo mês

| Quando | O que fazer | Onde |
| --- | --- | --- |
| Dia 20 em diante | Conferir se os royalties do ano atualizaram (a agenda coleta no dia 20, às 9h) | **Royalties** → escolha o ano → linha **Meses incluídos** |
| Quando a ANP publicar o mês | Baixar a produção por poço do mês novo e importar | Procedimento 8 |
| Último dia útil | Baixar o relatório do mês | Endereço `http://127.0.0.1:8766/metas/relatorio.md?de=2026-10-01&ate=2026-10-31` (troque as datas) |
| Último dia útil | Conferir planos diretores com **Data a conferir** | **Planos diretores** |
| Último dia útil | Backup com cópia fora do computador | **Backup** |

### 3.4 Todo trimestre

1. Compare os **Indicadores do trimestre** com as metas: 3 contratos, 15 propostas, 120 contatos qualificados, 20 reuniões e 200 editais triados.
2. Encerre as oportunidades paradas: **Editar oportunidade** → **Etapa** **Suspensa** ou **Perdida** → preencha **Justificativa de suspensão, perda ou conclusão**.
3. Revise as rotinas em **Agenda e automações**: pause as que não trazem nada.
4. **Atenção:** o trimestre está fixo no app de 01/09/2026 a 30/11/2026. Antes de 01/12, peça a atualização do período e das metas. Sem isso, as abordagens da semana ficam em 0 de 10 e as reuniões param de contar. Contratos, propostas, contatos qualificados e editais triados já contam desde o início, não por trimestre.

## Parte 4A — Tela a tela: prospecção

Estas são as telas de trabalho diário. A ficha da oportunidade (4A.6) é onde a abordagem acontece e fica registrada.

### 4A.1 Central de operação

**Menu:** **Central de operação**. É a tela que abre depois do login. De cima para baixo:

1. **Faixa de abertura:** botões **Explorar o radar ↗** (vai ao Radar) e **Organizar minha semana** (vai à Agenda).
2. **Quatro cartões de números.** Cada um é clicável:

| Cartão | O que conta | Clique leva a |
| --- | --- | --- |
| **RADAR** | Sinais aguardando revisão | Radar |
| **ÚLTIMAS 24 HORAS** | Sinais novos na base | Radar filtrado por novos em 24h |
| **PRAZOS** | Sinais com prazo que encerra em até 7 dias | Radar filtrado por prazo da semana |
| **RELACIONAMENTO** | Cartórios no cadastro | Central de cartórios |

3. **Prospecção desta semana** (link **Metas e relatório →**):
   - **N de 10 — Abordagens na semana**: registros do tipo **Contato realizado** desde segunda-feira;
   - **Alvos da Frente 1 a abordar**: municípios de royalties ainda na etapa **Identificada**;
   - **Oportunidades ativas no funil**: tudo que não está Perdida, Concluída ou Suspensa;
   - **Ações vencendo hoje ou atrasadas**: conta no máximo 12. Se aparecer 12, pode haver mais; confira em **Metas e relatório** → **Atrasadas**.
4. **Atalhos:** **★ Lista quente — Frente 1**, **★ Lista quente — Paraíba**, **↓ Relatório da semana**, **◎ E-mails e telefones dos cartórios**, **＋ Agendar uma coleta**, **＋ Registrar oportunidade privada** e **◷ Conferir cobertura das fontes**.
5. **O que merece sua atenção** (link **Ver radar →**): os 5 sinais mais novos a revisar, com tipo, município e data. **Prazo encerrado** avisa que a licitação já fechou.
6. **Seu próximo passo** (link **Tarefas →**):
   - ponto laranja: oportunidade com ação vencida ou do dia;
   - ponto azul: até 5 tarefas internas abertas (**Definir prazo** quando não há data);
   - rodapé **N oportunidades ativas ainda sem data**: abra cada uma e dê um prazo.
7. **Agenda de atualização** (link **Gerenciar →**): as próximas 4 rotinas com dia e hora.
8. **Coletas recentes** (link **Saúde das fontes →**): as 5 últimas coletas com o resultado.
9. **CONTROLE FINANCEIRO:** receitas recebidas no mês menos despesas registradas. Não é lucro. Botão **Abrir financeiro →**.

### 4A.2 Lista quente — Frente 1 (royalties)

**Menu:** **Lista quente — Frente 1**. Mostra os 20 municípios do Plano Comercial de 31/08/2026.

**Cartões do topo:** **ALVOS** (municípios na lista), **A ABORDAR** (ainda em Identificada), **EM CONTATO** (Contato realizado) e **DIAGNÓSTICO / PROPOSTA** (conversas avançadas).

**Tabela Lista quente**, agrupada em **1º círculo — RN**, **2º círculo — SE** e **3º círculo — CE e AL**:

| Coluna | Como ler |
| --- | --- |
| **Município** | Clique para abrir a ficha da oportunidade |
| **Excedentes 2021–2025** | Soma da parcela acima de 5% em 2021–2025 e o percentual sobre o total. **coleta ANP no app** = dado coletado; **plano comercial** = número do plano, ainda sem coleta; **Aguardando coleta ANP** = rode a série de royalties |
| **Excedentes 2026 (jan–ago) vs 2025** | Parcela acima de 5% no ano corrente e a variação sobre os mesmos meses do ano anterior. **sem base anterior** = o ano anterior não tem esses meses |
| **Costa** | Extensão de litoral, quando conhecida |
| **Etapa** | Onde a conversa está |
| **Próxima ação** | O que fazer e a data. Data em vermelho = atrasada |
| **Contatos** | **N cadastrados · M abordagens** e o link **+ contato** |

**Como usar a tabela**

1. Trabalhe de cima para baixo dentro do círculo da semana.
2. Prefira municípios com excedentes altos e variação forte no ano. Exemplos de 2026: Macau +22%, Areia Branca −44%.
3. Município com excedente perto de zero (Grossos e Tibau, por exemplo) tem tese fraca pelo critério do plano. Decida antes de abordar.
4. **+ contato** abre o cadastro de contato. Depois de salvar, o app volta para a lista de contatos, não para a lista quente: use o menu para voltar.

**Outros municípios com excedentes (RN, SE, CE, AL):** os 25 maiores fora da lista, com **Excedentes** e **% do total**. O botão **Investigar** cria um sinal "Investigar oportunidade de royalties — Município / UF" e abre esse sinal para você decidir.

**Produção marítima por campo — dados mensais da ANP** (só aparece depois de importar produção):

- colunas **UF**, **Campo**, **Operador**, **Último mês**, **Poços**, **Petróleo (bbl/dia)**, **Gás (mil m³/dia)** e **Petróleo desde …**;
- **sem produção nos meses seguintes** marca campo que parou (Arabaiana depois de junho de 2026, por exemplo);
- produção de um campo não diz, sozinha, qual município é confrontante.

**Produção marítima ativa — cadastro ANP atualizado:** poços marítimos com situação "produzindo" no cadastro, por campo. O link **Ver poços →** abre a lista filtrada.

### 4A.3 Lista quente — Paraíba

**Menu:** **Lista quente — Paraíba**. Reúne as frentes de planejamento urbano e fundiária na PB.

- **Botões:** **+ Cadastrar plano diretor**, **+ Registrar evidência** e **Lista quente — Frente 1**.
- **Planos diretores monitorados:** **Município**, **Lei**, **Idade** (em anos), **Situação** com o **Marco** de revisão, e os links **Fonte** e **Editar**. **Data a conferir** quer dizer que a data da lei ainda não foi conferida no ato original.
- **Oportunidades na Paraíba:** oportunidades ativas na PB fora de royalties (hoje Lucena, Santa Rita, João Pessoa e Cabedelo), com **Frente**, etapa, **Próxima ação** e o link **Mensagem**, que abre o gerador de mensagem direto.
- **Sinais de demanda:** até 20 sinais da PB não descartados (Ponte do Futuro, recomendação do MPPB, decisão do TJPB e outros).

### 4A.4 Metas e relatório

**Menu:** **Metas e relatório**. Tudo aqui é contado a partir do que você registrou.

- **Botões:** **↓ Relatório da semana**, **↓ Relatório de setembro** e **Lista quente**.
- **Abordagens nesta semana:** **N de 10**, com barra de progresso, desde segunda-feira.
- **Indicadores do trimestre** (01/09 a 30/11/2026):

| Indicador | Meta | Como o app conta |
| --- | --- | --- |
| **Contratos assinados** | 3 | Oportunidades em Contratada, Em execução ou Concluída |
| **Propostas enviadas** | 15 | Oportunidades com registro de Proposta ou etapa a partir de Proposta enviada |
| **Contatos qualificados na base** | 120 | Contatos com data de conferência, exceto cartórios e marcados **Não contatar** |
| **Reuniões realizadas** | 20 | Registros do tipo Reunião no histórico |
| **Editais triados por você** | 200 | Sinais do PNCP revisados, descartados ou convertidos. Inclui os descartes automáticos do filtro de exclusão |

- Abaixo da tabela, três metas que o app não mede e você acompanha à mão: cadastros de fornecedor ativos (3), processos de inexigibilidade estruturados (1) e assinaturas recorrentes ativas (1).
- **Atrasadas** e **Próximos 7 dias:** a lista de ligações e follow-ups. Clique para abrir a ficha.
- **Funil por frente e etapa:** quantas oportunidades há em cada frente e etapa. Link **Abrir funil →**.

**Relatórios:** o arquivo baixado (`relatorio-prospeccao-AAAAMMDD-AAAAMMDD.md`) tem os indicadores, as atividades do período, o funil, as próximas ações (atrasadas marcadas) e os sinais do período. O botão de setembro é fixo; para outro período, use o endereço com datas (Procedimento 6).

### 4A.5 Funil comercial (lista de oportunidades)

**Menu:** **Funil comercial** (título **Oportunidades**).

- **Buscar registros** + **Buscar**: procura no título e no nome da organização.
- **Cadastrar oportunidade**: abre o formulário em branco.
- Colunas **Registro** (título e organização), **Contexto** (frente e etapa), **Acompanhamento** (próxima ação, data ou **Sem prazo**, responsável) e o link **Editar**.
- Não há filtro por frente ou etapa na tela. Use a busca, ou **Metas e relatório** → **Funil por frente e etapa** para ver as contagens.

**Formulário da oportunidade** (**Cadastrar oportunidade** ou **Editar oportunidade**):

| Campo | Obrigatório | Como preencher |
| --- | --- | --- |
| **Oportunidade** | Sim | Título curto: "Royalties — Macau/RN", "Plano diretor — Lucena/PB" |
| **Organização** | Sim | Escolha na lista. Se não existir, cadastre antes em **Organizações** |
| **Frente** | Sim | Royalties e águas territoriais; Inteligência territorial e risco; Georreferenciamento rural e SIGEF; REURB e cadastro urbano; Capacitação; Terrenos de marinha; Apoio técnico a empresas e escritórios |
| **Etapa** | Sim | Começa em Identificada. As atividades mudam a etapa sozinhas (4A.7) |
| **Rota** | Não | A definir, Direta ou Via NUPEC |
| **Prioridade definida por você** | Não | Alta, Normal ou Baixa. A lista ordena por prioridade e depois por data |
| **Justificativa da prioridade** | Não | Uma frase: "excedentes de R$ 12 mi e queda de 44% em 2026" |
| **Problema e evidências** | Não | O problema do cliente com dado público e a fonte. Nunca o método |
| **Escopo e entregas possíveis** | Não | O que o Automac_Royalties entregaria |
| **Responsável** | Não | Padrão: Uendry |
| **Decisor ou setor** | Não | Quem decide. Não aparece na ficha, só no formulário |
| **Capacidade técnica confirmada para este escopo** | Não | Marque só depois de confirmar com a equipe técnica |
| **Valor estimado da proposta (R$)** | Não | Valor que será proposto |
| **Custo estimado de execução (R$)** | Não | Custo interno |
| **Primeiro recebimento esperado** | Não | Data |
| **Próxima ação** | Sim | Verbo + objeto: "Ligar para a Procuradoria e confirmar e-mail" |
| **Prazo da próxima ação** | Não, mas sempre preencha | Sem data, a oportunidade some da rotina |
| **O que falta para avançar** | Não | Pendências |
| **Justificativa de suspensão, perda ou conclusão** | Só nas etapas Suspensa, Perdida e Concluída | Motivo ou evidência do resultado |

Clique em **Salvar registro**. O app mostra **Registro salvo.**, abre a ficha e grava no histórico quais campos mudaram.

### 4A.6 A ficha da oportunidade

Abra clicando no título em qualquer lista, na lista quente ou em **Seu próximo passo**.

**Topo:** etiqueta da etapa, **Organização · Frente**, botão **Editar oportunidade** e o aviso **Próxima ação** com data e responsável (**Definir prazo** quando falta data).

**Cartão Diagnóstico:** o problema, o **Escopo** e as **Pendências**.

**Cartão Condições comerciais:**

- **Rota**, **Proposta estimada**, **Custo estimado**, **Primeiro recebimento** e **Prioridade** com a justificativa;
- **Adicionar parcela ou despesa**: abre o Financeiro já ligado a esta oportunidade;
- **Abrir briefing interno**: texto com os dados da ficha e 4 perguntas para a conversa;
- **✉ Gerar mensagem de abordagem**: abre o gerador (4A.9).

**Cartão Contatos de \[organização\]** (link **+ contato**):

- cada contato mostra nome, cargo, e-mail, telefone e o link da fonte;
- à direita, uma de três situações: **Não contatar**, **Conferido dd/mm** ou o botão **Conferi por telefone**;
- sem contatos, o app sugere cadastrar o procurador, o secretário de Fazenda ou o setor responsável.

**Cartão Histórico de relacionamento:** campos **Tipo** e **Registro** e o botão **Registrar atividade**. Os registros aparecem do mais novo para o mais antigo, com tipo, data e autor.

**Cartão Documentos e versões:** **Nome e versão do documento**, **Arquivo** e **Adicionar documento**. Limite de 25 MB por arquivo. Guarde propostas, ofícios e atas; deixe ortofotos e rasters fora do app.

### 4A.7 Registrar atividade e a cadência automática

1. Na ficha, em **Histórico de relacionamento**, escolha o **Tipo**.
2. Em **Registro**, escreva o que aconteceu: com quem falou, o que ficou combinado, o próximo passo.
3. Clique em **Registrar atividade**. Aparece **Histórico atualizado.** e, quando a cadência age, **Cadência: …** com o que mudou.

| Tipo | Etapa passa para | Próxima ação e data |
| --- | --- | --- |
| **Contato realizado** | Contato realizado, se estava em Identificada ou Qualificada | Primeiro contato em 10 dias: "Follow-up D+4", hoje + 4. Segundo contato dentro de 10 dias: "Follow-up D+10", 10 dias após o primeiro |
| **Proposta** | Proposta enviada, se estava antes dessa etapa (ou em Suspensa ou Perdida). Nas etapas seguintes, registrar Proposta não muda etapa nem prazo | "Follow-up D+4 da proposta enviada", hoje + 4 |
| **Reunião** | Diagnóstico, se estava em Identificada, Qualificada ou Contato realizado | Não muda |
| **Nota** | Não muda | Não muda |
| **Decisão** | Não muda | Não muda |
| **Alteração de cadastro** | Não muda | Não muda. É o tipo que o próprio app usa; evite escolher |

**Cuidados com a cadência**

- **Contato realizado** sempre reescreve a **Próxima ação**, mesmo numa oportunidade avançada. Numa negociação, prefira **Nota** e ajuste a data em **Editar oportunidade**.
- **Proposta** numa oportunidade Suspensa ou Perdida a traz de volta para Proposta enviada. É o esperado quando a conversa reabre.
- Cada mudança automática gera um registro "Cadência automática: …" no histórico. Ele não conta como abordagem.
- Só **Contato realizado** conta para a meta de 10 abordagens por semana.

**As 11 etapas e quando usar cada uma**

| Etapa | Use quando |
| --- | --- |
| Identificada | O alvo está mapeado, sem contato ainda |
| Qualificada | Tese e interlocutor confirmados, antes do primeiro contato |
| Contato realizado | Houve contato de ida (e-mail, ligação, visita) |
| Diagnóstico | Houve reunião e você está entendendo o problema |
| Proposta enviada | A proposta saiu |
| Negociação | O cliente discute preço, escopo ou forma de contratação |
| Contratada | Contrato assinado |
| Em execução | Trabalho em andamento |
| Concluída | Entregue. Exige justificativa |
| Suspensa | Parada por decisão de alguém. Exige justificativa |
| Perdida | O cliente recusou ou contratou outro. Exige justificativa |

### 4A.8 Conferir um contato por telefone

Contato pesquisado entra como **não conferido**. Só depois de conferido ele conta como contato qualificado.

1. Ligue para o número do contato (ou o geral da prefeitura).
2. Confirme nome, cargo, e-mail e telefone direto.
3. Se algum dado mudou, clique em **Editar** ao lado do contato, corrija e salve.
4. Volte à ficha e clique em **Conferi por telefone**. Aparece **Contato conferido em dd/mm/aaaa. Agora conta como contato qualificado.**
5. Registre a ligação no histórico como **Nota** (só confirmou dados) ou **Contato realizado** (já apresentou o Automac_Royalties).

Não há botão de desfazer. Para desfazer, **Editar** o contato e apague a data em **Conferido em**.

### 4A.9 Gerar mensagem de abordagem

1. Na ficha, clique em **✉ Gerar mensagem de abordagem** (ou em **Mensagem** na lista quente da Paraíba).
2. Leia os avisos em vermelho antes de tudo:
   - **Sem royalties 2021–2025 carregados para este município**: o texto sai com \[valor\] e \[x\]. Rode a série de royalties antes de enviar (Procedimento 7);
   - **Excedentes abaixo de 1% do total**: pelo critério do plano, a tese é fraca. Decida antes de abordar.
3. Confira o cartão **E-mail**:
   - **Para:** até 3 e-mails, escolhidos pelo cargo (procurador, tributos, finanças, fazenda em royalties; planejamento, urbanismo, meio ambiente, procurador nas demais frentes). **cadastre um contato com e-mail** = não há destinatário;
   - **Assunto:** pronto, editável no seu e-mail;
   - **Texto:** usa os dados do app. Em royalties, traz o total e os excedentes de 2021–2025 e, quando há ano novo, a frase "De janeiro a agosto de 2026, a parcela acima de 5% somou …, X% acima/abaixo do mesmo período de 2025". Nos planos diretores, traz a lei e a idade do plano.
4. Ajuste o tom direto na caixa de texto.
5. Envie de um destes jeitos:
   - **Abrir no e-mail**: abre seu programa de e-mail com destinatários, assunto e texto. Confira se o texto veio inteiro; alguns programas cortam textos longos;
   - **Copiar texto**: cola no Gmail ou Outlook web.
6. Use o **Roteiro de ligação** (**Copiar roteiro**) para telefonar: 5 passos e as regras "não falar de método, mapas ou traçados; não prometer receita".
7. **Volte à ficha e registre Contato realizado.** Gerar a mensagem não registra nada.

### 4A.10 Briefing interno

**Abrir briefing interno** mostra um texto simples com organização, frente, etapa, responsável, problema, escopo, pendências, próxima ação, 4 perguntas para a conversa e as regras de abordagem. Leia antes de cada ligação ou reunião. Para imprimir, use `Ctrl+P` no navegador.

## Parte 4B — Tela a tela: sinais, coletas e automações

Estas telas trazem as pistas para dentro do app e mostram se as fontes estão respondendo. Só uma coleta roda por vez.

### 4B.1 Radar de oportunidades

**Menu:** **Radar de oportunidades**. Linha de topo: **N resultados no filtro · N novos na base em 24h · N prazos nos próximos 7 dias**. Botões **↓ Briefing** e **＋ Registrar pista**.

**Filtros** (depois de escolher, clique em **Aplicar filtros**; **Limpar** zera tudo):

| Filtro | Opções |
| --- | --- |
| Busca | Objeto, município ou palavra |
| **Frente** | Todas as frentes; REURB e fundiário; Planos diretores; Cadastro e geodados; Levantamentos; Ambiental e risco; Royalties; Expansão e obras |
| **Origem** | Todas as origens; PNCP; Diários indexados; Fontes públicas; Fontes privadas; Registro manual |
| **UF** | Todas as UFs; PB; RN; CE; SE; AL |
| **Revisão** | A revisar (padrão); Em acompanhamento; Descartados; Todos |
| **Prazo** | Qualquer prazo; Prazo futuro informado; Até 7 dias; Sem prazo informado |
| **Primeira coleta** | Todas as coletas; Novos em 24h; Novos em 7 dias; Novos em 30 dias |
| **Ordenação** | Mais recentes na base; Maior aderência textual |

**Cartão de cada sinal:**

- etiqueta com o tipo e a origem (em código: `pncp`, `pagina`, `diario`, `manual`);
- **N aderência**: 20 pontos de base, 12 por tema identificado e 20 se vier do PNCP, até 95. Mede palavras, não chance de contrato;
- localização (**Localização a conferir** quando o app não identificou), motivo e trecho;
- **Publicado**, **Coletado** e **Prazo informado** (ou **Sem prazo de contratação identificado**);
- botões **Revisar e decidir →** e **Fonte ↗**.

Lista vazia não prova que não há oportunidades; pode ser só o filtro ou uma fonte fora do ar.

**Tela Revisar sinal** (botão **Revisar e decidir →**):

1. Leia o título, o motivo e o **Prazo na fonte** (**ENCERRADO** quando passou).
2. Clique em **Conferir na fonte** e leia o original. Os dados brutos ficam em **Dados de origem**.
3. Decida:
   - **Serve:** no cartão **Qualificar para acompanhamento**, o formulário da oportunidade vem preenchido (título, problema com a fonte, frente, próxima ação "Conferir demanda, interlocutor e capacidade de entrega" para daqui a 2 dias). Escolha a **Organização** (se não existir, use o link **Cadastre a organização** e volte), ajuste e clique em **Criar oportunidade acompanhável**. O sinal passa para **Em acompanhamento**;
   - **Não serve:** em **Motivo do descarte**, escreva o porquê ("compra de equipamento", "fora do escopo", "prazo encerrado") e clique em **Descartar sinal**. O descarte de sinais do PNCP conta como edital triado;
   - **Mudou de ideia:** **Reabrir revisão** volta o sinal para A revisar.
4. Sinal já convertido mostra **Abrir oportunidade vinculada**.

**Registrar pista** (botão **＋ Registrar pista**, tela **Registrar evidência de consulta pública**): use para o que você achou fora das coletas (cartório, lei municipal, notícia).

1. **Título ou nome da instituição**.
2. **Tipo**: Contato institucional, Plano diretor, Edital ou Outro gatilho.
3. **Fonte pública consultada**: cole o endereço.
4. **Trecho e evidências encontrados**: cole o trecho.
5. **Salvar registro**. O sinal entra em A revisar. Se já existir, o app avisa e mantém o anterior.

### 4B.2 Central de cartórios

**Menu:** **Central de cartórios**. 78 cartórios ativos da Paraíba (fonte CNJ, 18/09/2026). Cartório é canal de indicação para SIGEF e REURB, não comprador.

1. Filtre: busca por nome, município, CNS ou e-mail; **UF**; marque **Registro de imóveis** e **Com e-mail utilizável**; clique em **Filtrar**.
2. Para copiar e-mails de uma vez: abra **Lista de e-mails do filtro** → **Copiar e-mails**. Os marcados **Não contatar** ficam de fora.
3. Para um contato: use **Copiar** ao lado do e-mail ou do telefone.
4. Para planilha: **↓ Exportar lista completa** baixa `cartorios.csv` com o filtro atual.
5. Para corrigir: **Editar contato** ou **Editar cadastro**. Para bloquear, marque **Não contatar** no contato.

O cadastro é histórico do CNJ, não confirmação de atendimento: confira antes de usar. Os contatos dos cartórios vêm com Conferido em 18/09/2026, a data da consulta ao CNJ; isso não significa que alguém ligou.

### 4B.3 Fontes e coletas (coleta na hora)

**Menu:** **Fontes e coletas**. Use quando precisar de dado novo agora, sem esperar a agenda.

1. No cartão **Iniciar coleta**, escolha a **Fonte**:

| Fonte | O que traz | Campos que importam |
| --- | --- | --- |
| IBGE — municípios dos cinco estados | Cadastro de municípios de PB, RN, CE, SE e AL | Nenhum |
| ANP — royalties anuais | Tabela de royalties de um ano | **Ano da tabela ANP** |
| ANP — série de royalties 2021 até hoje (todos os anos) | Todos os anos de 2021 até o atual | Nenhum |
| ANP — poços: primeira carga, base verificada 18/09/2026 | Carga inicial de poços. Recusa se já houver poços | Nenhum |
| ANP — poços: atualização online | Cadastro atual de poços dos 5 estados | Nenhum |
| PNCP — oportunidades por objeto | Licitações de uma UF | **UF para o PNCP**, **Consulta PNCP**, **Limite de páginas PNCP**, **Especialidades no objeto do edital** |
| Páginas oficiais monitoradas | Novidades das páginas cadastradas (até 20 por rodada) | Nenhum |

2. Clique em **Buscar na fonte oficial**. Abre a página da coleta.
3. A página se atualiza a cada 5 segundos. Não desligue o computador.
4. Leia o resultado: **Na fila**, **Coletando**, **Concluída**, **Parcial** (parte veio; o resumo diz o quê) ou **Falhou** (o motivo aparece).
5. Em **Arquivos de origem preservados** ficam os arquivos originais com a impressão digital SHA-256.

**Consultas assistidas:** **Consultar TJPB** abre o site do tribunal; **Registrar resultado da consulta** registra o que você achou; **Páginas monitoradas (N)** lista as páginas cadastradas.

**Histórico de execução:** todas as coletas com data, estado e resumo. Clique para abrir.

Se aparecer **Já há uma coleta em andamento**, espere terminar. Coleta presa há mais de 5 minutos é marcada como falha pela agenda; se continuar, feche e abra o app.

### 4B.4 Fontes e cobertura

**Menu:** **Fontes e cobertura**. Mostra o que foi consultado, o que falhou e onde a cobertura é parcial. Botões **Coleta avulsa** (vai a Fontes e coletas) e **＋ Adicionar fonte pública ou privada**.

- **Rotinas e últimas respostas:** **Coleta**, **Última execução**, **Resultado** e **Próximo horário**.
- **Fontes monitoradas:** cada página com **Última tentativa**, **Último sucesso** e o último erro em vermelho. **Consultar agora** coleta só aquela fonte; **Editar** muda termos ou pausa.

**Adicionar uma fonte** (**＋ Adicionar fonte pública ou privada**):

1. **Nome da fonte**: "Prefeitura de Lucena — Publicações".
2. **Página pública a acompanhar**: o endereço da página de publicações ou do feed. Evite a página inicial: os links de menu viram ruído.
3. **Formato**: Página HTML, Feed RSS/Atom ou PDF com texto. PDF escaneado não funciona.
4. **Origem**: Pública/institucional ou Empresa / oportunidade privada.
5. **Município** e **Finalidade** (tipo de sinal gerado).
6. **Termos separados por vírgula**: as palavras que geram sinal (padrão: plano diretor, regularização fundiária, georreferenciamento).
7. Marque **Ativa** e clique em **Salvar registro**. Depois, em Fontes e cobertura, teste com **Consultar agora**.

### 4B.5 Agenda e automações

**Menu:** **Agenda e automações**. O aviso do topo diz **Executor local ativo** (a agenda deu sinal nos últimos 6 minutos) ou **Executor sem sinal recente**.

**Rotinas que já vêm configuradas** (horário de Brasília/Fortaleza):

| Rotina | Frequência |
| --- | --- |
| PNCP · radar a cada 12 horas | A cada 720 minutos, nos 5 estados |
| Diários · checagem diária | A cada 1.440 minutos |
| Fontes públicas e privadas · a cada 2 horas | A cada 120 minutos |
| Cadastro de poços · segunda às 08h | Toda segunda, 8h |
| Royalties · dia 20 às 09h | Todo dia 20, 9h. Atualiza só o ano corrente. Em janeiro e fevereiro, rode o ano anterior à mão (Procedimento 7) |

**Cartão de cada rotina:** etiqueta **Ativa** ou **Pausada**, repetição, **PRÓXIMA EXECUÇÃO** e a última coleta. Botões:

- **Executar agora**: roda já e abre a página da coleta;
- **Pausar** / **Ativar**: ao ativar, a rotina roda na próxima verificação;
- **Editar**: abre o formulário.

**Criar ou editar uma rotina** (**＋ Nova rotina**):

1. **Nome da rotina**.
2. **Coleta**: PNCP — propostas abertas; Diários municipais — Querido Diário; Páginas e feeds monitorados; ANP — cadastro e localização de poços; ANP — royalties do ano atual; ANP — produção via URL pública de CSV.
3. **Ativa**.
4. **Repetição**: A cada intervalo, Todo dia, Dia da semana ou Dia do mês. Preencha só o campo correspondente:
   - **Intervalo em minutos** (mínimo 15);
   - **Horário — Brasília/Fortaleza**;
   - **Dia da semana**;
   - **Dia do mês** (mês sem esse dia usa o último dia).
5. **UFs do radar**: marque ao menos uma.
6. Os campos de CSV só valem para a coleta de produção por URL.
7. **Salvar registro**.

**Como a agenda funciona:** com o app aberto, ela verifica a cada 30 segundos e roda uma coleta por vez. Se o computador ficou desligado, a rotina atrasada roda uma vez e segue para o próximo horário. Para coletar com o app fechado (computador ligado e sessão do Windows aberta), rode `aplicativo\ATIVAR_AGENDA_WINDOWS.bat`; para desligar, `DESATIVAR_AGENDA_WINDOWS.bat`. Depois de mover a pasta, rode o ATIVAR de novo.

**Cartão Tarefas e compromissos:** até 30 tarefas internas e 20 oportunidades ativas com data. **＋ Agendar tarefa** cria uma tarefa interna.

### 4B.6 Continuidade e evidências

**Menu:** **Continuidade e evidências** (título **Acompanhamento e editais**).

- **Gerar pacote de acompanhamento:** baixa um ZIP com tarefas, oportunidades, coletas e agenda, e guarda uma cópia em `dados\acompanhamento\`. Serve para retomar o trabalho com um assistente de IA.
- **Varrer editais por capacidades:** marque as **Capacidades a pesquisar** (estudos ambientais; regularização fundiária; levantamentos; geoprocessamento; planejamento territorial), os **Estados**, o **Máximo de páginas por UF nesta rodada** (padrão 20, máximo 40) e **Termos adicionais**. Clique em **Iniciar varredura**.
- **Cobertura e retomada:** as 10 últimas varreduras por UF, com examinados, correspondências e situação. **Retomar páginas pendentes** continua uma varredura parcial.
- **Sinais encontrados:** os editais achados pela varredura.
- **Gerar dossiê de evidências:** baixa um ZIP com todas as fontes coletadas, as impressões SHA-256 e um manifesto; guarda cópia em `dados\dossies\`. Mostra a origem dos dados; não é prova jurídica nem assinatura digital.

Os dois pacotes ficam bloqueados enquanto houver coleta rodando.

## Parte 4C — Tela a tela: dados

Estas telas guardam os números públicos que sustentam cada abordagem: royalties, poços, produção e planos diretores. Os dados só mudam por coleta, importação ou cadastro seu.

### 4C.1 Inteligência territorial (municípios)

**Menu:** **Inteligência territorial** (título **Municípios**). São 751 municípios de PB, RN, CE, SE e AL.

1. Filtre por **Nome ou código IBGE** e **UF**; clique em **Filtrar**.
2. **Abrir mapa interno** mostra os municípios no mapa; **Localizar** aproxima um município.
3. Clique no nome para abrir a ficha do município:
   - **Código IBGE** e a fonte cadastral;
   - **Investigar royalties neste município**: cria (ou abre) um sinal de royalties para você decidir no Radar;
   - **Cadastrar organização** e **Registrar plano diretor**;
   - **Série mensal importada**: **Período**, **Até 5%**, **Excedentes**, **Total** e o arquivo de origem;
   - **Relacionamentos**: organizações cadastradas, suas oportunidades e o plano diretor.

### 4C.2 Poços e produção

**Menu:** **Poços e produção** (título **Poços e cartografia**). Cadastro de poços da ANP nos 5 estados.

**Topo:** **Carregar ou atualizar cadastro** (vai a Fontes e coletas) e **Importar produção mensal**. A linha **Última execução** diz quando o cadastro foi atualizado; a agenda atualiza toda segunda, 8h.

**Filtrar a lista**

1. Busca por poço, cadastro, campo ou operador.
2. **UF**; ambiente (**Terra e mar**, **Terra** ou **Mar**); situação ANP.
3. Clique em **Filtrar**. A linha de contagem mostra o total e a divisão por UF.

**Exportar o que está filtrado** (todos respeitam o filtro):

| Botão | Você recebe | Uso típico |
| --- | --- | --- |
| **Abrir mapa** | Mapa com os poços do filtro | Ver onde estão |
| **↓ Planilha Excel deste filtro** | `pocos_anp_AAAAMMDD.xlsx`: aba **Resumo por UF** (total, marítimos, produzindo, injetando e produção marítima ativa por campo) e aba **Poços** (lista completa com coordenadas) | Levar números para o Gilberto ou para uma proposta |
| **Baixar mapa offline + dados QGIS** | `cartografia_pocos.zip` com mapa em HTML, camadas GeoJSON e LEIA\_ME | Uso técnico no QGIS |
| **GeoJSON** | `pocos_anp.geojson` | Uso técnico |

**Atenção:** o mapa e as camadas têm uso interno. Nenhum mapa vai para material comercial.

**Mapa dos poços** (**Abrir mapa**): os seletores **UF para aproximar**, **Município** e **Linha fornecida** só aproximam o mapa; não filtram nem ligam poços a municípios. Legenda: ponto de terra, ponto de mar e linhas LBR fornecidas. Clique num poço para ver os dados e **Abrir ficha e produção**.

**Ficha do poço:** cadastro ANP, localização, o arquivo original da ANP e a **Produção mensal importada** (**Referência**, **Petróleo (bbl/dia)**, **Gás (Mm³/dia)**, CSV de origem). Sem produção importada não quer dizer produção zero.

**Importar produção mensal pela tela** (**Importar produção mensal**, título **Produção mensal por poço**):

1. No cartão **1. Baixar na ANP**, clique em **Consultar produção no CDP** e siga os 4 passos. O site da ANP tem CAPTCHA: o download é manual.
2. No cartão **2. Alimentar o aplicativo**:
   - **CSV original exportado do CDP/ANP**: escolha o arquivo como baixou, sem abrir e salvar no Excel;
   - **Ambiente selecionado na consulta**: Terra, Mar ou Pré-sal — subconjunto de Mar;
   - clique em **Importar e conferir CSV**.
3. Acompanhe a coleta até **Concluída**.
4. Confira em **Períodos importados** (e o arquivo em **Histórico**).

Limite de 25 MB por CSV. Hoje há produção marítima de janeiro a agosto de 2026 (RN, SE e AL).

A situação "produzindo" vem do cadastro da ANP, não da produção mensal. Os nomes de operador no cadastro podem estar desatualizados; a produção mensal traz os nomes atuais.

### 4C.3 Royalties

**Menu:** **Royalties** (título **Inteligência de royalties**). Ranking das distribuições municipais por excedentes.

1. Filtre por **Município**, ano e UF; clique em **Consultar**. Sem escolha, o app mostra o ano mais recente.
2. Leia **Meses incluídos** antes de comparar anos: 2026 tem janeiro a agosto; 2021 a 2025 estão completos.
3. Colunas:
   - **Até 5%**: a parcela mínima (Lei 7.990/89);
   - **Excedentes**: a parcela acima de 5% (Lei 9.478/97), onde a confrontação atua;
   - **Total** e **Excedentes / total**.
4. **↻ Carregar/atualizar série 2021 até hoje (ANP)** baixa todos os anos de novo. Use quando a lista quente mostrar **Aguardando coleta ANP** ou depois de uma revisão da ANP.

A participação especial não está no app. Valor recebido não prova direito a revisão nem receita do Automac_Royalties. Não há botão de envio de planilha de royalties: a tabela entra pela coleta ou pela pasta `importar` (4C.5).

### 4C.4 Planos diretores

**Menu:** **Planos diretores**. Um plano por município. O app calcula o marco de revisão: o prazo local, se houver, ou a data-base + 10 anos (Estatuto da Cidade).

**Cadastrar um plano** (**Cadastrar plano diretor**):

| Campo | Como preencher |
| --- | --- |
| **Município** | Escolha na lista |
| **Lei e identificação** | "Lei Complementar 164/2024" |
| **Data da instituição ou última revisão integral comprovada** | A data do ato. Não pode ser futura |
| **Fonte oficial da lei** | Endereço do diário oficial ou do site da câmara |
| **Pesquisa de revisões posteriores realizada em** | A data em que você pesquisou. Obrigatório quando marcar a conferência |
| **Conferi a lei e pesquisei revisões integrais posteriores** | Marque só depois de ver o ato original |
| **Prazo local de revisão, se comprovado** | Quando a lei municipal fixa prazo próprio |
| **Evidências, alterações parciais e dúvidas** | Leis que alteraram partes, dúvidas em aberto |

**Situação calculada:**

- **Data a conferir**: a caixa de conferência não foi marcada;
- **Marco de revisão ultrapassado — verificar situação**: o prazo passou; é argumento de abordagem;
- **Revisão a verificar nos próximos 12 meses**: o prazo vence em até um ano;
- **Marco de revisão futuro**: plano recente.

Hoje há 4 planos: Lucena, Santa Rita, João Pessoa e Cabedelo. Só Cabedelo está conferido.

### 4C.5 Pasta de importação (`aplicativo\dados\importar`)

Coloque aqui os arquivos oficiais que você baixou. Ao abrir o app, cada arquivo novo é importado uma única vez e o original fica guardado.

| Arquivo | O nome precisa ter | Exemplo que funciona |
| --- | --- | --- |
| Tabela anual de royalties da ANP (.xlsx) | a palavra `royalties` e o ano (`2026`) | `royalties-tabelas-jan-dez-2026_03.xlsx` |
| Produção por poço do CDP (.csv) | a palavra `producao` (sem acento) e `_Mar` ou `_Terra` | `2026_09_producao_Mar.csv` |

**Passo a passo**

1. Baixe o arquivo no site oficial.
2. Renomeie seguindo a tabela, se preciso.
3. Copie para `aplicativo\dados\importar`.
4. Feche e abra o app. A janela preta mostra **Pasta importar: arquivo: Concluída** (ou Parcial, ou Falhou). O motivo de uma falha fica no resumo da coleta, em Fontes e coletas → Histórico de execução.
5. Confira: royalties em **Royalties** (escolha o ano); produção em **Poços e produção** → **Importar produção mensal** → **Períodos importados**.

**O que o app ignora ou recusa**

- Arquivo com mesmo conteúdo de um já importado é pulado, mesmo com outro nome.
- `produção` com acento, `.xls`, `.zip` e `.pdf` são ignorados sem aviso. Extraia o `.xlsx` de dentro do ZIP da ANP.
- CSV sem `_Mar` ou `_Terra` gera o aviso **informe \_Mar ou \_Terra no nome do arquivo** a cada abertura, até você renomear.
- Planilha de royalties sem ano no nome gera **ano não encontrado no nome**.
- Pré-sal só entra pela tela de importação, não pela pasta.
- Arquivo que falhou não é tentado de novo. Se a falha for do app, peça a reimportação na próxima atualização.

## Parte 4D — Tela a tela: cadastros e gestão

Os cadastros seguem o mesmo padrão: lista com busca, botão **Cadastrar …** e link **Editar** em cada linha. Todo salvamento mostra **Registro salvo.** O app não apaga registros: para tirar algo de circulação, use a etapa, a situação ou **Não contatar**.

### 4D.1 Organizações

**Menu:** **Organizações**. Cadastre a organização antes da oportunidade: toda oportunidade precisa de uma.

| Campo | Como preencher |
| --- | --- |
| **Nome da organização** | Nome oficial: "Prefeitura Municipal de Macau" |
| **Tipo** | Prefeitura, Cartório, Escritório de advocacia, Empresa, Órgão público, Parceiro ou Outro |
| **Papel no relacionamento** | A identificar, Possível comprador, Interlocutor institucional ou Possível parceiro |
| **Município** | Obrigatório na prática para prefeituras: é por ele que o app acha os royalties |
| **CNPJ ou CNS** | CNPJ; CNS para cartórios |
| **Site oficial**, **Fonte do cadastro**, **Data de conferência** | De onde veio a informação e quando você conferiu |
| **Endereço publicado**, **Atribuições da serventia**, **Observações** | Opcionais |

Nome e tipo iguais a um cadastro existente são recusados com uma mensagem em inglês (**Organization com este Nome da organização e Tipo já existe**). Busque na lista antes de cadastrar.

**Atenção:** uma oportunidade da frente de royalties cuja organização não tem **Município** pode derrubar a Lista quente — Frente 1. Sempre preencha o município.

Na lista, o link **Adicionar contato** abre o cadastro de contato já ligado à organização.

### 4D.2 Todos os contatos

**Menu:** **Todos os contatos** (título **Contatos**). A busca procura em nome, organização e e-mail.

| Campo | Como preencher |
| --- | --- |
| **Organização** | Obrigatório |
| **Nome ou setor** | Pessoa ("João Silva") ou setor ("Procuradoria-Geral") |
| **Cargo ou função** | Importante: o gerador de mensagem escolhe os destinatários pelo cargo. Use palavras como procurador, secretário de finanças, tributação, fazenda, planejamento, urbanismo |
| **E-mail institucional**, **Telefone** | Como publicado |
| **Fonte** | Endereço de onde tirou o contato |
| **Conferido em** | Deixe vazio. O botão **Conferi por telefone** preenche |
| **Não contatar** | Marque se a pessoa pediu para não ser contatada ou o contato está errado |
| **Observações** | Melhor horário, quem atendeu, histórico curto |

A lista mostra **Conferido: data** ou **Pendente**. Hoje há 15 contatos pesquisados, nenhum conferido por telefone.

### 4D.3 Tarefas e decisões

**Menu:** **Tarefas e decisões** (título **Planejamento interno**). Ações internas que não são de um cliente: montar cursos, cadastros de fornecedor, dossiê de habilitação.

- **Fluxo de trabalho:** Evidência → verificação atual → diagnóstico interno → escopo → decisão.
- Filtro **Etapa**: Todas, Verificar evidência, Diagnóstico interno, Preparar escopo, Aguardar decisão de Uendry, Concluído, Suspenso.
- Cada cartão mostra frente, etapa, município, responsável, prazo, **Próxima ação** e **Pendências**.

**Criar uma tarefa** (**Nova ação interna**):

1. **Ação interna**: "Estruturar curso de GNSS".
2. **Município** (se houver) e **Frente de trabalho** (Regularização fundiária, Cadastro territorial, Cartografia ou Operação interna).
3. **Etapa interna**, **Responsável**, **Próxima ação** e **Prazo definido por você**.
4. **Pendências e condições** e **Notas e resultado**.
5. **Salvar ação interna**. Aparece **Planejamento salvo. Nenhuma ação externa foi executada.** Cada edição fica no **Histórico** da tarefa.

Os dois cursos (GNSS e QGIS municipal) já estão aqui. **Baixar resumo para continuar no chat** gera `CONTINUIDADE_AUTOMAC.md` para retomar o trabalho com um assistente de IA.

### 4D.4 Financeiro

**Menu:** **Financeiro** (título **Recebimentos e despesas**). Registre parcelas e despesas ligadas às oportunidades. O atalho mais prático é **Adicionar parcela ou despesa** na ficha da oportunidade.

| Campo | Como preencher |
| --- | --- |
| **Oportunidade** | A que gera a receita ou a despesa |
| **Descrição da parcela** | "Parcela 1/3 — diagnóstico" |
| **Natureza** | Honorários, Êxito condicionado, Outra receita ou Despesa |
| **Valor (R$)** | Valor da parcela |
| **Situação** | Prevista, Contratada, Faturada ou Recebida / paga |
| **Data prevista** | Quando deve entrar ou sair |
| **Recebido / pago em** | Só com situação Recebida / paga |
| **Condição contratual e evidência** | Cláusula, nota fiscal, comprovante. Obrigatório para marcar recebido |

O cartão **CONTROLE FINANCEIRO** da Central soma os recebidos do mês menos as despesas.

### 4D.5 Backup

**Menu:** **Backup** (título **Backup e exportação**).

- **Gerar e baixar backup completo**: cria e baixa um ZIP com o banco, os documentos, os arquivos das fontes, a pasta `importar`, os pacotes e a chave do app. Uma cópia fica em `dados\backups\`. Não funciona durante uma coleta (**Aguarde o fim da coleta antes de criar o backup.**).
- **Exportar oportunidades em CSV**: planilha `oportunidades.csv` (separada por ponto e vírgula) com todas as oportunidades, para abrir no Excel.
- **Restauração**: só pelo `RESTAURAR.bat`, com o app fechado (Procedimento 12).

**Atenção:** o backup contém todos os contatos e a chave do app. Guarde em lugar protegido. Os backups antigos não são apagados sozinhos; limpe `dados\backups\` de tempos em tempos, mantendo os 3 mais recentes.

### 4D.6 Guia de uso

**Menu:** **Guia de uso**. O guia resumido em 22 seções, dentro do app. Para o passo a passo completo, use este manual.

## Parte 5 — Procedimentos completos

Cada procedimento vai do primeiro clique ao registro final. Siga na ordem; os números das telas remetem à Parte 4.

| Nº | Procedimento | Frequência |
| --- | --- | --- |
| 1 | Abordar um município da Frente 1, do alvo ao follow-up | Várias vezes por semana |
| 2 | Transformar um sinal do Radar em oportunidade | Diária |
| 3 | Registrar uma oportunidade nova do zero | Sob demanda |
| 4 | Pesquisar, cadastrar e conferir um contato | Semanal |
| 5 | Da reunião à proposta e ao contrato | Sob demanda |
| 6 | Enviar o relatório da semana ou do mês ao Gilberto | Sexta e fim do mês |
| 7 | Atualizar os royalties | Mensal |
| 8 | Atualizar a produção mensal por poço | Mensal |
| 9 | Cadastrar e conferir um plano diretor | Sob demanda |
| 10 | Acompanhar uma nova fonte (página, feed, PDF) | Sob demanda |
| 11 | Criar ou ajustar uma rotina de coleta | Rara |
| 12 | Fazer backup e restaurar | Semanal / emergência |
| 13 | Tirar o app do OneDrive | Uma vez |
| 14 | Levar os números de um município para uma reunião | Sob demanda |
| 15 | Encerrar uma oportunidade | Sob demanda |
| 16 | Pedir ajuda técnica | Quando algo falhar |

### Procedimento 1 — Abordar um município da Frente 1

1. Abra **Lista quente — Frente 1** e escolha, no círculo da semana, um município em **Identificada**.
2. Leia **Excedentes 2021–2025** e a coluna de 2026. Se o excedente estiver perto de zero, decida se vale abordar (tese fraca).
3. Clique no nome do município para abrir a ficha.
4. No cartão **Contatos**:
   - sem contatos: faça o Procedimento 4 e volte;
   - com contato não conferido: ligue, confirme os dados e clique em **Conferi por telefone**.
5. Clique em **✉ Gerar mensagem de abordagem**. Resolva os avisos em vermelho antes de seguir.
6. Revise o texto, ajuste o tom e envie pelo **Abrir no e-mail** ou pelo **Copiar texto**, a partir do seu e-mail.
7. Volte à ficha (**← Voltar à oportunidade**). Em **Histórico de relacionamento**:
   - **Tipo:** Contato realizado;
   - **Registro:** "E-mail enviado a \[nome, cargo\] com a leitura dos royalties 2021–2025 e de 2026. Aguardando retorno.";
   - clique em **Registrar atividade**.
8. Confira a mensagem **Cadência:** a etapa passou para Contato realizado e o follow-up ficou em D+4.
9. Se ligar no mesmo dia para a mesma pessoa, registre a ligação como **Nota**. Guarde **Contato realizado** para cada nova tentativa de contato.
10. No D+4, o item aparece em **Seu próximo passo**. Ligue usando o **Roteiro de ligação** e registre **Contato realizado**: o app agenda o D+10.
11. No D+10 sem resposta, tente outro cargo da mesma organização. Sugestão: depois de três tentativas sem retorno, mude a etapa para **Suspensa** com a justificativa "sem resposta após 3 tentativas" (Procedimento 15).
12. Se houver resposta e reunião marcada, siga o Procedimento 5.

### Procedimento 2 — Transformar um sinal do Radar em oportunidade

1. **Radar de oportunidades** → filtro **Revisão: A revisar** → **Aplicar filtros**.
2. No sinal, clique em **Revisar e decidir →** e depois em **Conferir na fonte**. Leia o original.
3. Pergunte: é serviço que o Automac_Royalties entrega? O prazo ainda está aberto? Há comprador identificável?
4. Se a organização não existe no app, clique em **Cadastre a organização**, salve e volte ao sinal.
5. No cartão **Qualificar para acompanhamento**, escolha a **Organização**, confira **Frente**, **Próxima ação** e **Prazo da próxima ação**.
6. Clique em **Criar oportunidade acompanhável**. A ficha abre com a fonte registrada no histórico.
7. Se não serve: escreva o **Motivo do descarte** e clique em **Descartar sinal**.

### Procedimento 3 — Registrar uma oportunidade nova do zero

Use para indicações, contatos de eventos, empresas e escritórios (atalho **＋ Registrar oportunidade privada** na Central).

1. **Organizações** → busque a organização. Se não existir: **Cadastrar organização**, preencha nome, tipo, papel e **Município** → **Salvar registro**.
2. **Funil comercial** → **Cadastrar oportunidade**.
3. Preencha no mínimo: **Oportunidade**, **Organização**, **Frente**, **Problema e evidências**, **Próxima ação** e **Prazo da próxima ação**.
4. **Salvar registro**. A ficha abre.
5. Em **Contatos**, clique em **+ contato** e cadastre quem você conhece (Procedimento 4).
6. Registre no histórico como a oportunidade surgiu (**Nota**: "Indicação de Fulano em 30/09").

### Procedimento 4 — Pesquisar, cadastrar e conferir um contato

1. Pesquise em fontes públicas: site da prefeitura (secretarias, organograma, fale conosco), portal da transparência, diário oficial (nomeações), site da câmara.
2. Priorize o cargo certo para a frente:
   - royalties: procurador-geral, secretário de Finanças, Fazenda ou Tributação;
   - planos diretores e REURB: secretário de Planejamento, Urbanismo ou Meio Ambiente, e a Procuradoria.
3. Cadastre: ficha da oportunidade → **+ contato** (ou **Todos os contatos** → **Cadastrar contato**). Preencha **Organização**, **Nome ou setor**, **Cargo ou função**, **E-mail institucional**, **Telefone** e **Fonte** (o endereço de onde tirou). Deixe **Conferido em** vazio.
4. **Salvar registro**. O app volta à lista de contatos; volte à ficha pelo **Funil comercial**.
5. Ligue e confirme nome, cargo e e-mail. Corrija em **Editar** se preciso.
6. Na ficha, clique em **Conferi por telefone**. O contato passa a contar na meta de 120 contatos qualificados.
7. Se a pessoa pedir para não ser contatada: **Editar** → marque **Não contatar** → salve.

### Procedimento 5 — Da reunião à proposta e ao contrato

1. **Antes da reunião:** abra a ficha → **Abrir briefing interno**. Leia as perguntas.
2. **Depois da reunião:** registre **Reunião** no histórico (quem participou, o problema relatado, o que pediram). A etapa passa para **Diagnóstico**.
3. **Editar oportunidade** e atualize **Problema e evidências**, **Escopo e entregas possíveis**, **Decisor ou setor**, **O que falta para avançar**, **Próxima ação** e prazo.
4. Confirme com a equipe técnica que o Automac_Royalties entrega o escopo. Só então marque **Capacidade técnica confirmada para este escopo**.
5. Preencha os três campos de valores e datas:
   - valor estimado da proposta;
   - custo estimado de execução;
   - **Primeiro recebimento esperado**.
6. Escreva a proposta fora do app. Em **Documentos e versões**, anexe o PDF com nome e versão ("Proposta Macau v1").
7. Envie a proposta e registre **Proposta** no histórico. A etapa passa para **Proposta enviada** e o follow-up fica em D+4.
8. Em **Adicionar parcela ou despesa**, lance as parcelas como **Prevista**.
9. Se o cliente negociar: **Editar oportunidade** → **Etapa: Negociação**. Anexe cada nova versão da proposta (v2, v3) e ajuste o prazo em Editar oportunidade: nessa etapa, registrar Proposta não agenda follow-up.
10. Contrato assinado: **Etapa: Contratada**; mude as parcelas para **Contratada**; registre **Decisão** no histórico com a data da assinatura.
11. Início do trabalho: **Em execução**. A cada recebimento: parcela → **Recebida / paga**, data e evidência.
12. Entrega final: **Concluída**, com a justificativa ("Entregue em dd/mm, termo de recebimento anexo").

### Procedimento 6 — Enviar o relatório ao Gilberto

**Relatório da semana (toda sexta)**

1. Confira se todas as abordagens da semana foram registradas. O que não está no app não aparece.
2. **Metas e relatório** → **↓ Relatório da semana** (também na Central).
3. O arquivo `relatorio-prospeccao-AAAAMMDD-AAAAMMDD.md` vai para a pasta Downloads. Abra com o Bloco de Notas para conferir.
4. Envie ao Gilberto: anexe o arquivo ao e-mail, ou copie o texto e cole no corpo.
5. No e-mail, acrescente em duas ou três linhas o destaque da semana e o que precisa de decisão dele.

**Relatório de outro período**

1. Na barra de endereço do navegador, digite `http://127.0.0.1:8766/metas/relatorio.md?de=2026-10-01&ate=2026-10-31`.
2. Troque as datas pelo período (formato ano-mês-dia). Data inválida volta ao padrão (semana atual) sem aviso.
3. Aperte Enter: o arquivo baixa.

### Procedimento 7 — Atualizar os royalties

A agenda coleta o ano corrente todo dia 20, às 9h, com o app aberto. Você só age quando a coleta automática falhar ou precisar de outro ano.

1. **Conferir:** **Royalties** → escolha o ano → **Consultar** → leia **Meses incluídos**.
2. **Forçar a série completa:** **Royalties** → **↻ Carregar/atualizar série 2021 até hoje (ANP)**. Acompanhe até **Concluída**.
3. **Um ano específico:** **Fontes e coletas** → **Fonte: ANP — royalties anuais** → **Ano da tabela ANP** → **Buscar na fonte oficial**.
4. **Se o site da ANP não responder:** baixe a planilha no site da ANP, deixe `royalties` e o ano no nome, coloque em `dados\importar` e reabra o app (4C.5).
5. Confira o resultado na **Lista quente — Frente 1**: a coluna do ano corrente deve mostrar os novos meses.

### Procedimento 8 — Atualizar a produção mensal por poço

1. **Poços e produção** → **Importar produção mensal** → **Consultar produção no CDP**.
2. No site da ANP, siga os 4 passos do cartão **1. Baixar na ANP**: escolha o mês novo e o ambiente Mar (e depois Terra, se quiser), resolva o CAPTCHA e exporte o CSV.
3. Não abra o CSV no Excel antes de importar.
4. Escolha um caminho:
   - **pela tela:** no cartão **2. Alimentar o aplicativo**, escolha o arquivo e o ambiente → **Importar e conferir CSV**;
   - **pela pasta:** renomeie para `2026_09_producao_Mar.csv` (ano, mês, `producao`, ambiente), copie para `dados\importar` e reabra o app.
5. Confira em **Períodos importados** e na **Lista quente — Frente 1** → **Produção marítima por campo** (coluna **Último mês**).

### Procedimento 9 — Cadastrar e conferir um plano diretor

1. Ache a lei do plano diretor: site da Câmara Municipal, diário oficial do município ou portal de leis municipais.
2. Pesquise revisões posteriores: "plano diretor" + nome do município + "revisão" ou "lei complementar".
3. **Lista quente — Paraíba** → **+ Cadastrar plano diretor** (ou **Planos diretores** → **Cadastrar plano diretor**).
4. Preencha **Município**, **Lei e identificação**, a data da instituição ou da última revisão integral, **Fonte oficial da lei** e **Pesquisa de revisões posteriores realizada em** (a data de hoje).
5. Só marque **Conferi a lei e pesquisei revisões integrais posteriores** se leu o ato original (PDF do diário ou da câmara), não uma notícia.
6. Anote em **Evidências, alterações parciais e dúvidas** as leis que mudaram partes do plano.
7. **Salvar registro**. Confira a **Situação** calculada.
8. Se o marco passou ou vence em 12 meses, crie a oportunidade (Procedimento 3), frente **Inteligência territorial e risco** ou **REURB e cadastro urbano**. O gerador de mensagem usará a lei e a idade do plano.

### Procedimento 10 — Acompanhar uma nova fonte

1. Ache a página de publicações, notícias ou licitações do órgão. Se houver feed RSS, prefira o feed.
2. **Fontes e cobertura** → **＋ Adicionar fonte pública ou privada**.
3. Preencha como em 4B.4, com termos específicos ("REURB, regularização fundiária, georreferenciamento").
4. **Salvar registro**. O app mostra a lista de páginas monitoradas.
5. Volte a **Fontes e cobertura** e clique em **Consultar agora** na nova fonte.
6. Veja o resultado na coleta e os sinais no **Radar** (**Origem: Fontes públicas** ou **Fontes privadas**).
7. Se vier ruído demais, **Editar** e restrinja os termos. Se não vier nada por semanas, pause a fonte.

### Procedimento 11 — Criar ou ajustar uma rotina de coleta

1. **Agenda e automações** → **＋ Nova rotina** (ou **Editar** numa rotina).
2. Preencha nome, **Coleta**, **Repetição** e o campo de tempo correspondente (4B.5). Marque as **UFs do radar**.
3. **Salvar registro**. A mensagem lembra que a agenda só roda com o app aberto ou com o Agendador do Windows ativo.
4. Para testar, clique em **Executar agora**.
5. Para parar sem apagar, clique em **Pausar**.

Evite intervalos curtos: as fontes publicam com atraso e o PNCP pode pedir pausa (erro 429).

### Procedimento 12 — Fazer backup e restaurar

**Fazer backup (toda sexta)**

1. Confira que não há coleta **Coletando**.
2. **Backup** → **Gerar e baixar backup completo**.
3. O arquivo `automac-AAAAMMDD-HHMMSS-….zip` baixa. Copie para um pendrive ou pasta do Drive da empresa.
4. Guarde os 3 backups mais recentes fora do computador.

**Restaurar (só em emergência)**

1. Feche o app (feche a janela preta). Se a agenda do Windows estiver ativa, rode antes DESATIVAR\_AGENDA\_WINDOWS.bat e, no fim, o ATIVAR de novo.
2. Localize o ZIP do backup. Segure Shift, clique nele com o botão direito e escolha **Copiar como caminho**.
3. Abra `aplicativo\RESTAURAR.bat`.
4. Em **Caminho completo do backup ZIP:**, cole o caminho e aperte Enter.
5. Em **Substituir a base atual pelo backup? Digite RESTAURAR:**, digite `RESTAURAR` em maiúsculas e aperte Enter. Qualquer outra resposta cancela.
6. Espere **Restaurado. Cópia anterior preservada em: …**. A base atual fica guardada antes de ser trocada.
7. Abra o app e confira a Central e o Funil.

| Mensagem | Significado |
| --- | --- |
| **A aplicacao ou a restauracao ja esta em execucao. Feche-a primeiro.** | O app está aberto, ou uma coleta roda em segundo plano (inclusive pela agenda do Windows). Feche, espere alguns minutos e repita |
| **Backup incompleto.** | O ZIP não tem o banco ou a chave. Use outro backup |
| **Banco corrompido.** ou **Banco incompatível.** | Corrompido: o backup está danificado. Incompatível: o arquivo não é um backup do Automac_Royalties. Use outro backup e peça ajuda. Backups de versões anteriores são aceitos e atualizados ao abrir o app |
| **Backup excede o limite de 5 GB.** | Arquivo grande demais. Peça ajuda |

### Procedimento 13 — Tirar o app do OneDrive

Faça num dia sem pressa. O app fica fora do ar por alguns minutos.

1. Com o app aberto, faça um backup (Procedimento 12) e guarde o ZIP fora do OneDrive.
2. Feche o app.
3. Crie a pasta `C:\Automac_Royalties\`.
4. **Copie** (não recorte) a pasta principal `Automac_Royalties_0.4.1` para dentro de `C:\Automac_Royalties\`.
5. Na nova pasta, abra `02_ABRIR.bat`. Confira a Central, o Funil (o mesmo número de oportunidades da pasta antiga) e os Royalties.
6. Se usava a agenda do Windows, rode DESATIVAR\_AGENDA\_WINDOWS.bat na pasta antiga e depois `aplicativo\ATIVAR_AGENDA_WINDOWS.bat` na nova pasta.
7. Atualize o atalho e os favoritos para a nova pasta.
8. Trabalhe uma semana pela nova pasta. Só então apague a cópia antiga do OneDrive.

Se a nova pasta não abrir, não apague nada na pasta antiga. Na nova, apague só a pasta aplicativo\\.venv e rode 01\_INSTALAR.bat nela; persistindo, continue na pasta antiga e peça ajuda (Procedimento 16).

### Procedimento 14 — Levar os números de um município para uma reunião

1. **Royalties** → digite o município → consulte ano a ano (2021 a 2026). Anote até 5%, excedentes e total.
2. **Inteligência territorial** → abra o município → **Série mensal importada** para ver mês a mês.
3. **Lista quente — Frente 1** → linha do município: excedentes 2021–2025 e a variação de 2026.
4. **Poços e produção** → filtre UF e ambiente Mar → **↓ Planilha Excel deste filtro** (produção marítima ativa por campo).
5. Na ficha: **✉ Gerar mensagem de abordagem** dá o texto-base; **Abrir briefing interno** dá as perguntas.
6. Monte a peça com tabela e texto. **Atenção:** nenhum mapa, nenhuma linha, nenhum método, nenhuma promessa de receita.

### Procedimento 15 — Encerrar uma oportunidade

1. Abra a ficha → **Editar oportunidade**.
2. **Etapa**: **Perdida** (cliente recusou ou contratou outro), **Suspensa** (parada, pode voltar) ou **Concluída** (entregue).
3. Preencha **Justificativa de suspensão, perda ou conclusão**. Sem ela, o app recusa com **Registre o motivo ou a evidência do resultado.**
4. **Salvar registro**.
5. Registre **Decisão** no histórico com o motivo em uma frase. A oportunidade sai do funil ativo e das ações vencendo.

### Procedimento 16 — Pedir ajuda técnica

1. Anote o que fez, o que esperava e o que apareceu. Tire um print da tela (`Win+Shift+S`).
2. Feche o app e rode `aplicativo\DIAGNOSTICO.bat`. Ele gera `DIAGNOSTICO_AUTOMAC.txt` com versão, contagens e últimas coletas, sem contatos nem senhas.
3. Se a dúvida for de contexto de trabalho, gere também o pacote em **Continuidade e evidências** → **Gerar pacote de acompanhamento**.
4. Envie o print, o diagnóstico e o pacote para quem dá suporte ao app.

O texto do diagnóstico ainda cita `INICIAR.bat` e `INSTALAR.bat`: os nomes corretos hoje são `02_ABRIR.bat` e `01_INSTALAR.bat`.

## Parte 6 — Regras comerciais que o app aplica

O app foi montado sobre seis regras de ouro do Plano Comercial. Algumas ele aplica sozinho; outras dependem de você.

### 6.1 As seis regras de ouro

1. **Mostre o problema com dado público; nunca o método.** O método é o que o Automac_Royalties vende. Explicado antes do contrato, o cliente pode contratar outro para executá-lo.
2. **Nenhum mapa indicativo em material comercial.** Um mapa entrega a tese e pode ser lido como promessa.
3. **PMRR de Bayeux fora de qualquer peça comercial.**
4. **Não prometa receita nem resultado administrativo ou judicial.** A decisão é da ANP, do IBGE ou da Justiça.
5. **Registre tudo.** O que não está no app não aparece nas metas nem no relatório ao Gilberto.
6. **Contato só é qualificado depois de conferido por telefone.** Contato pesquisado pode estar desatualizado.

### 6.2 O que o app faz sozinho

| Regra automática | Onde age | Por quê |
| --- | --- | --- |
| Nada é enviado automaticamente | Mensagens, cartórios, relatórios | Toda comunicação externa passa pela sua revisão |
| Follow-up em D+4 e D+10 | Ao registrar Contato realizado, ou Proposta antes da etapa Proposta enviada | Ninguém fica sem retorno por esquecimento |
| Etapa avança com a atividade | Contato realizado, Reunião, Proposta | O funil reflete o que aconteceu, não o que você lembrou de atualizar |
| Filtro de exclusão no PNCP | Coletas e toda abertura do app | Compra de equipamentos, aparelhos, software e frota não é serviço do Automac_Royalties |
| Aviso de tese fraca | Gerador de mensagem | Excedente abaixo de 1% do total não sustenta a tese de confrontação |
| Aviso de dado faltando | Gerador de mensagem | Mensagem com \[valor\] não pode sair |
| Destinatário escolhido pelo cargo | Gerador de mensagem | Royalties vai para Procuradoria e Fazenda; planos diretores para Planejamento e Urbanismo |
| Contatos "Não contatar" excluídos | Mensagens e cópia de e-mails dos cartórios | Respeitar quem pediu para não ser procurado |
| Justificativa obrigatória | Etapas Suspensa, Perdida e Concluída | Explicar ao Gilberto por que a oportunidade saiu |
| Recebimento exige data e evidência | Financeiro | O saldo do mês só conta o que entrou de fato |
| Arquivos das fontes guardados com SHA-256 | Toda coleta | Provar de onde veio cada número |
| Backup antes de atualizar o banco | Abertura do app | Uma atualização com problema não apaga seu trabalho |

### 6.3 O que o app não sabe e você precisa lembrar

- **Aderência não é probabilidade.** A nota do Radar conta palavras. Um sinal com 95 pode não servir; um com 40 pode ser o melhor da semana.
- **Produção de um campo não diz qual município é confrontante.** Não associe poço a município em material comercial.
- **"Produzindo" é a situação do cadastro**, não a produção do mês.
- **Excedentes recebidos não provam direito a revisão** nem receita para o Automac_Royalties.
- **A participação especial ainda não está no app.** Não afirme valores dela com base no app.
- **Cartório é canal de indicação**, não comprador. Contatos de cartório não contam na meta de contatos qualificados.
- **Lista vazia no Radar não prova ausência de oportunidade.** Pode ser o filtro ou uma fonte fora do ar: confira **Fontes e cobertura**.

## Parte 7 — Problemas e soluções

Procure a mensagem ou o sintoma na primeira coluna. Se nada resolver, siga o Procedimento 16.

### 7.1 Abrir, entrar e navegar

| Sintoma ou mensagem | Causa provável | O que fazer |
| --- | --- | --- |
| Navegador diz "Não é possível acessar esse site" | A janela preta está fechada | Abra `02_ABRIR.bat` |
| **Conexão local interrompida** no topo | A janela preta foi fechada com a aba aberta | Abra `02_ABRIR.bat` e atualize a página (F5) |
| **Volte para a pasta principal e execute 01\_INSTALAR.bat primeiro.** | O ambiente `.venv` não existe (pasta nova ou copiada pela metade) | Rode `01_INSTALAR.bat` |
| A janela preta avisa "A aplicacao ou a restauracao ja esta em execucao" | O app já está aberto, ou uma coleta roda em segundo plano | Procure a aba já aberta. Se não houver, espere alguns minutos e abra de novo; persistindo, rode `DIAGNOSTICO.bat` |
| **Por favor, entre com um usuário e senha corretos** | Usuário ou senha errados | Confira maiúsculas. Esqueceu a senha: troque pelo comando (1.6) |
| Tela branca ou erro ao abrir uma página | Falha interna | Atualize (F5). Persistindo, anote a página e rode `DIAGNOSTICO.bat` |
| **Lista quente — Frente 1** dá erro | Oportunidade de royalties ligada a organização sem município | Edite a organização do alvo afetado e preencha **Município** |
| Toast **Selecione o texto e use Ctrl+C.** | O navegador bloqueou a cópia automática | Selecione o texto e copie com `Ctrl+C` |

### 7.2 Agenda e coletas

| Sintoma ou mensagem | Causa provável | O que fazer |
| --- | --- | --- |
| **Agenda sem sinal** ou **Executor sem sinal recente** | O app ficou suspenso ou a agenda travou | Feche e abra o app. A rotina atrasada roda uma vez |
| **Já há uma coleta em andamento** | Só uma coleta roda por vez | Espere terminar. Presa há mais de 5 minutos: a agenda marca como falha; se não marcar, feche e abra o app |
| Coleta **Falhou** | A fonte não respondeu ou mudou | Leia o motivo na página da coleta e tente mais tarde |
| Coleta **Parcial** | Parte das páginas não veio (nas varreduras do PNCP, dá para retomar) | Em **Continuidade e evidências**, use **Retomar páginas pendentes** |
| PNCP com HTTP 429 | A fonte pediu pausa | Nada: a próxima rotina tenta de novo |
| Diários com erro de SSL | Problema conhecido da fonte Querido Diário | Use as páginas monitoradas; o conserto está no plano de melhorias |
| **Execucao interrompida. Inicie uma nova coleta.** | Aparece no resumo da coleta (Fontes e coletas → Histórico de execução): o app foi fechado durante a coleta | Normal. A agenda roda de novo no próximo horário |
| A mensagem de erro fala em "marcar a execução interrompida" | Texto antigo; esse botão não existe | Feche e abra o app: ele marca sozinho |

### 7.3 Dados e importação

| Sintoma ou mensagem | Causa provável | O que fazer |
| --- | --- | --- |
| **Aguardando coleta ANP** na lista quente | Royalties ainda não coletados | Procedimento 7, passo 2 |
| Coluna de 2026 não aparece | O ano corrente não foi carregado | Procedimento 7 |
| **informe \_Mar ou \_Terra no nome do arquivo** | CSV sem o ambiente no nome | Renomeie o arquivo na pasta `importar` e reabra o app |
| **ano não encontrado no nome** | Planilha de royalties sem o ano | Renomeie com o ano (`…2026….xlsx`) e reabra o app |
| Arquivo na pasta `importar` não foi lido e não há aviso | Nome sem `royalties` ou `producao`, acento em "produção", ou arquivo `.zip`, `.xls` ou `.pdf` | Corrija o nome ou extraia o `.xlsx` do ZIP |
| Arquivo já importado não é lido de novo | O app reconhece o conteúdo, mesmo com outro nome | Normal. Para reprocessar um arquivo que falhou, peça na próxima atualização |
| **Envie CSV de até 25 MB, sem converter no Excel.** | CSV grande ou salvo pelo Excel | Baixe de novo no CDP e importe sem abrir |
| Poço sem produção na ficha | Produção do período não importada | Procedimento 8. Ausência de dado não é produção zero |
| Operador com nome antigo | O cadastro da ANP está desatualizado | Confie no nome da produção mensal |

### 7.4 Formulários

| Mensagem | O que fazer |
| --- | --- |
| **Este campo é obrigatório.** | Preencha o campo marcado |
| **Registre o motivo ou a evidência do resultado.** | Preencha **Justificativa de suspensão, perda ou conclusão** |
| **Organization com este Nome da organização e Tipo já existe.** | A organização já está cadastrada: busque na lista |
| **Para registrar recebimento ou pagamento, informe a data e a evidência.** | Preencha **Recebido / pago em** e **Condição contratual e evidência** |
| **Data de realização exige situação Recebida / paga.** | Mude a **Situação** ou apague a data |
| **Informe quando pesquisou revisões posteriores.** | Preencha a data da pesquisa no plano diretor |
| **A data da lei não pode ser futura.** | Corrija a data do plano diretor |
| **Informe o motivo do descarte.** | Escreva o motivo antes de **Descartar sinal** |
| **Informe o tipo e o texto do registro.** | Escolha o **Tipo** e escreva o **Registro** |
| **Limite de 25 MB.** | Anexe um arquivo menor ou um link |
| **Selecione pelo menos uma UF.** | Marque uma UF na rotina |
| **Aguarde o fim da coleta antes de criar o backup.** | Espere a coleta terminar |

### 7.5 Limites conhecidos da versão 0.5.1

- Não há botão de excluir registros. Use etapa, situação ou **Não contatar**.
- Não há tela de usuários nem de troca de senha.
- O trimestre e o botão **Relatório de setembro** estão fixos em 2026.
- O Funil não tem filtro por frente ou etapa na tela.
- A pasta `importar` só é lida ao abrir o app.
- **Abrir no e-mail** pode cortar textos longos em alguns programas; use **Copiar texto**.
- O app só abre no computador em que roda.

Quase todos estes itens estão no plano de melhorias do documento **App Automac_Royalties para a equipe**.

## Glossário, arquivos e pastas

### Glossário

| Termo | Significado no app |
| --- | --- |
| Abordagem | Um registro do tipo **Contato realizado**. A meta é 10 por semana |
| Aderência | Nota de 20 a 95 dada pelas palavras do sinal; registros manuais ficam com 0. Não é chance de contrato |
| Até 5% (mínimos) | Parcela dos royalties até 5% da produção, pela Lei 7.990/89 |
| bbl/dia | Barris de petróleo por dia |
| CDP | Consulta de dados de produção da ANP, de onde vem o CSV por poço |
| Círculo | Grupo de municípios da Frente 1 por prazo: 1º RN (02/10), 2º SE (09/10), 3º CE e AL (16/10) |
| CNS | Código Nacional de Serventia, identifica cada cartório |
| Confrontação | Critério que define quais municípios recebem royalties de produção no mar |
| Contato qualificado | Contato com data de conferência, não bloqueado e que não é de cartório |
| Coleta | Uma consulta a uma fonte oficial. Tem estado: Na fila, Coletando, Concluída, Parcial ou Falhou |
| D+4, D+10 | Follow-up 4 dias depois do contato, ou 10 dias depois do primeiro contato quando houve um segundo |
| Dossiê | ZIP com as fontes coletadas, as impressões SHA-256 e um manifesto |
| Etapa | Posição da oportunidade no funil (11 etapas, de Identificada a Perdida) |
| Excedentes | Parcela dos royalties acima de 5%, pela Lei 9.478/97. É onde a confrontação atua |
| Executor / agenda | A parte do app que roda as coletas nos horários marcados |
| Frente | Linha de serviço do Automac_Royalties (royalties, REURB, SIGEF, capacitação e outras) |
| Lista quente | Alvos priorizados pelo Plano Comercial |
| Marco de revisão | Data em que o plano diretor deve ser revisto: prazo local ou data-base + 10 anos |
| Mil m³/dia (Mm³/dia) | Milhares de metros cúbicos de gás por dia |
| NUPEC | Rota de contratação por meio do NUPEC, alternativa à contratação direta do Automac_Royalties |
| Oportunidade | Um alvo trabalhado no funil, ligado a uma organização |
| Participação especial | Compensação paga por campos de grande produção. Ainda não está no app |
| PNCP | Portal Nacional de Contratações Públicas, fonte das licitações |
| Querido Diário | Base de diários oficiais municipais |
| REURB | Regularização fundiária urbana |
| SHA-256 | Impressão digital de um arquivo: prova que ele não mudou desde a coleta |
| SIGEF | Sistema de Gestão Fundiária do INCRA, para georreferenciamento rural |
| Sinal | Uma pista coletada ou registrada, que você revisa no Radar |

### Arquivos e pastas

| Caminho (a partir da pasta principal) | O que é | Pode mexer? |
| --- | --- | --- |
| `01_INSTALAR.bat` | Instalador | Só em computador novo |
| `02_ABRIR.bat` | Abre o app | Sim, todo dia |
| `aplicativo\RESTAURAR.bat` | Restaura um backup | Só em emergência, com o app fechado |
| `aplicativo\DIAGNOSTICO.bat` | Gera `DIAGNOSTICO_AUTOMAC.txt` | Sim |
| `aplicativo\ATIVAR_AGENDA_WINDOWS.bat` e `DESATIVAR_AGENDA_WINDOWS.bat` | Ligam e desligam a agenda com o app fechado | Sim |
| `aplicativo\dados\automac.sqlite3` | O banco de dados com todo o seu trabalho | Não. Nunca abra, copie ou apague com o app aberto |
| `aplicativo\dados\secret.key` | Chave do app | Não |
| `aplicativo\dados\importar\` | Pasta para arquivos oficiais baixados por você | Sim: coloque arquivos aqui |
| `aplicativo\dados\backups\` | Backups gerados | Sim: copie para fora e limpe os antigos |
| `aplicativo\dados\documentos\` | Anexos das oportunidades | Não: use a ficha |
| `aplicativo\dados\fontes\` | Arquivos originais de cada coleta | Não |
| `aplicativo\dados\acompanhamento\` e `dossies\` | Pacotes gerados | Sim: são cópias |
| `aplicativo\dados\logs\` | Registros técnicos das coletas | Só para suporte |
| `aplicativo\.venv\` | Ambiente Python | Não |
| `aplicativo\documentacao\` | Guias e notas de versão | Sim: leitura |

### Endereços úteis

| Endereço | Abre |
| --- | --- |
| `http://127.0.0.1:8766/` | Central de operação |
| `http://127.0.0.1:8766/lista-quente/` | Lista quente — Frente 1 |
| `http://127.0.0.1:8766/metas/` | Metas e relatório |
| `http://127.0.0.1:8766/metas/relatorio.md?de=AAAA-MM-DD&ate=AAAA-MM-DD` | Relatório de qualquer período |
| `http://127.0.0.1:8766/radar/` | Radar de oportunidades |
| `http://127.0.0.1:8766/pocos/producao/` | Importar produção mensal |
| `http://127.0.0.1:8766/ajuda/` | Guia de uso |
