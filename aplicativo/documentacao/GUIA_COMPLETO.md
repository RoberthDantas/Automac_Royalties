# Guia completo da Automac_Royalties (0.5.1)

O app existe para uma coisa: transformar dado público em abordagem registrada. Tudo o que você faz nele deve terminar em uma próxima ação com data.

## 1. Rotina de uso

**Todo dia (15 minutos)**

1. Abra a **Central de operação** e veja "Prospecção desta semana" e "Seu próximo passo".
2. Faça as ações vencidas ou do dia (ligações, e-mails, follow-ups).
3. Registre cada contato no histórico da oportunidade. O app agenda o próximo passo sozinho.
4. Passe no **Radar**: descarte o que não serve (com motivo) e converta o que serve em oportunidade.

**Toda sexta (20 minutos)**

1. Abra **Metas e relatório** e confira as abordagens da semana (meta: 10).
2. Baixe o **Relatório da semana** e envie ao Dr. Gilberto.
3. Veja as ações atrasadas e replaneje as datas.

**Todo mês**

1. Gere o relatório do mês (botão "Relatório de setembro" ou endereço com as datas).
2. No dia 20 a agenda atualiza os royalties do ano; confira em **Royalties**.
3. Faça um **Backup** e guarde a cópia fora do computador.

## 2. Abrir, fechar e proteger

- **Abrir:** dois cliques em `02_ABRIR.bat`. O navegador abre em `http://127.0.0.1:8766`. Mantenha a janela preta aberta.
- **Fechar:** feche a janela preta (ou Ctrl+C nela). Feche o app antes de qualquer atualização.
- **Backup:** menu **Backup** → baixar. Para voltar um backup: `RESTAURAR.bat`, dentro da pasta `aplicativo`.
- **Diagnóstico:** `DIAGNOSTICO.bat` gera um resumo técnico sem contatos nem senhas, útil para pedir ajuda.
- **Onde guardar:** fora do OneDrive (por exemplo, `C:\Automac_Royalties`). Sincronização em nuvem com o banco aberto pode corromper os dados.

## 3. Central de operação

A tela inicial mostra, de cima para baixo:

- **Cartões do radar:** sinais a revisar, novos em 24 horas, prazos que vencem em 7 dias, cartórios cadastrados.
- **Prospecção desta semana:** abordagens feitas contra a meta de 10, alvos da Frente 1 ainda não abordados, oportunidades ativas e ações vencendo.
- **O que merece sua atenção:** últimos sinais do radar.
- **Seu próximo passo:** ações de oportunidades e tarefas internas por data.
- **Agenda de atualização e Coletas recentes:** o que roda sozinho e se deu certo.

"Agenda ativa", no alto à direita, indica que as coletas automáticas estão funcionando.

## 4. Lista quente — Frente 1 (royalties)

Os 20 municípios do Plano Comercial, organizados por círculo (1º RN, 2º SE, 3º CE e AL).

- **Excedentes 2021–2025:** o valor recebido na parcela acima de 5% e a proporção sobre o total, direto da coleta da ANP. É o número que abre a conversa.
- **Excedentes do ano corrente contra o ano anterior:** quando há um ano novo carregado (hoje, 2026 de janeiro a agosto), a coluna mostra o valor e a variação sobre os mesmos meses do ano anterior. Exemplos: Macau +22%, Areia Branca −44%.
- **Costa:** extensão de litoral, quando conhecida.
- **Etapa e próxima ação:** onde a conversa está e o que fazer, com data.
- **Contatos:** quantos cadastrados e quantas abordagens registradas.

Município com excedente zero (Grossos e Tibau, por exemplo) tem tese fraca pelo critério do plano: decida antes de abordar.

Abaixo da lista aparecem outros municípios com excedentes, a **produção marítima por campo** (último mês importado, poços, petróleo em barris/dia, gás em mil m³/dia e variação no ano) e o cadastro de poços marítimos produzindo. Em agosto de 2026: Macau 1.703 bbl/dia em 27 poços; Arabaiana sem produção depois de junho. Produção de um campo não indica, por si, qual município é confrontante.

## 5. Lista quente — Paraíba

As frentes 2 e 4 na Paraíba:

- **Planos diretores monitorados:** lei, idade, marco de revisão (10 anos) e situação. "Data a conferir" quer dizer que a lei ainda não foi conferida no ato original.
- **Oportunidades na Paraíba:** Lucena, Santa Rita, João Pessoa (orla após a anulação da LUOS) e Cabedelo, com link direto para gerar a mensagem.
- **Sinais de demanda:** Ponte do Futuro, recomendação do MPPB, decisão do TJPB e outros.

## 6. A ficha da oportunidade

Cada alvo tem uma ficha. Nela você:

1. **Vê o diagnóstico:** problema e evidências, escopo possível, pendências.
2. **Confere os contatos:** cada contato pesquisado vem como "não conferido". Depois de confirmar por telefone, clique em **Conferi por telefone**. Só então ele conta como contato qualificado nas metas.
3. **Gera a mensagem:** botão **Gerar mensagem de abordagem** (ver seção 7).
4. **Registra o histórico:** escolha o tipo e escreva o que aconteceu.
   - *Contato realizado* → etapa passa a "Contato realizado"; follow-up em 4 dias (D+4); um segundo contato na mesma janela agenda D+10.
   - *Reunião* → etapa passa a "Diagnóstico".
   - *Proposta* → etapa passa a "Proposta enviada"; follow-up em 4 dias.
   - *Nota* e *Decisão* → só registram.
5. **Anexa documentos:** propostas, ofícios, atas (até 25 MB por arquivo).
6. **Controla o financeiro:** parcelas previstas e recebidas. "Recebido" exige data e evidência.
7. **Abre o briefing interno:** perguntas para a reunião e regras de abordagem.

Para mudar etapa, prazo, rota (direta ou NUPEC), prioridade ou valores: **Editar oportunidade**.

## 7. Gerador de mensagens

Monta um rascunho de e-mail e um roteiro de ligação com os dados do app:

- **Royalties:** usa o total recebido de 2021 a 2025, a parcela de excedentes e, quando houver, a variação do ano corrente ("De janeiro a agosto de 2026, a parcela acima de 5% somou R$ 1,5 milhão, 44% abaixo do mesmo período de 2025").
- **Planos diretores e demais frentes:** usa a lei e a idade do plano, ou o problema registrado.

O botão **Abrir no e-mail** preenche destinatários, assunto e texto no seu programa de e-mail. Nada é enviado sem você. Avisos em vermelho indicam dado faltando ou tese fraca.

Regras que o texto já segue: mostrar o problema com dado público, nunca o método; nenhum mapa; nenhuma promessa de receita.

## 8. Metas e relatório

- **Abordagens nesta semana:** contatos registrados desde segunda-feira, contra a meta de 10.
- **Indicadores do trimestre:** contratos, propostas, contatos qualificados, reuniões e editais triados, contra as metas do plano.
- **Atrasadas e próximos 7 dias:** a lista de ligações e follow-ups.
- **Funil por frente e etapa.**
- **Relatórios:** "Relatório da semana" e "Relatório de setembro" baixam um arquivo pronto para enviar. Outro período: `/metas/relatorio.md?de=2026-10-01&ate=2026-10-31`.

Tudo é contado a partir do que foi registrado. O que não foi registrado não aparece.

## 9. Radar de oportunidades

Reúne sinais do PNCP, das páginas monitoradas, dos diários e das pesquisas registradas.

- Filtre por tema, UF, origem, prazo e data da coleta.
- Abra o sinal e leia a fonte original antes de decidir.
- **Descartar** exige um motivo (fica registrado e conta como edital triado).
- **Converter em oportunidade** cria a ficha no funil com a fonte anexada.
- O filtro de exclusão já descarta compra de equipamentos, aparelhos, software e frota.
- A relevância é uma regra de palavras (não é probabilidade de contrato).

## 10. Fontes e coletas

Tela para rodar uma coleta na hora:

- **ANP — série de royalties 2021 até hoje:** carrega todos os anos de uma vez. Também há um botão na tela **Royalties**.
- **ANP — royalties anuais:** um ano específico.
- **ANP — poços:** atualização do cadastro de poços.
- **IBGE:** municípios das cinco UFs.
- **PNCP:** licitações por palavras no objeto.
- **Páginas oficiais monitoradas.**

Só uma coleta roda por vez. A página da coleta se atualiza sozinha até "Concluída", "Parcial" ou "Falhou" (com o motivo).

**Pasta de importação (arquivos baixados por você).** Coloque arquivos oficiais em `aplicativo\dados\importar` e abra o app: cada um é importado uma única vez, e o original fica guardado.

| Arquivo | Regra do nome | Exemplo |
|---|---|---|
| Tabela anual de royalties da ANP (.xlsx) | o ano no nome | royalties-tabelas-jan-dez-2026_03.xlsx |
| Produção por poço do CDP (.csv) | _Mar ou _Terra no nome | 2026_08_producao_Mar.csv |

Confira o resultado em Royalties (escolha o ano) e em Poços e produção → Importar produção mensal → Períodos importados. Arquivo vazio ou fora do leiaute falha com o motivo, sem sobrescrever nada.

## 11. Fontes e cobertura

Mostra a saúde de cada fonte: última tentativa, último sucesso e erro.

- **Adicionar fonte pública ou privada:** cole a URL de uma página de publicações, feed RSS/Atom ou PDF com texto, escolha os termos e se é origem pública ou privada (empresa).
- Prefira páginas de publicações e feeds, não a página inicial: a página inicial traz links de menu que viram ruído.
- PDF escaneado precisa de OCR externo.

## 12. Agenda e automações

Rotinas que rodam sozinhas enquanto o app está aberto:

| Rotina | Frequência padrão |
|---|---|
| PNCP | a cada 12 horas |
| Páginas e feeds | a cada 2 horas |
| Diários (Querido Diário) | uma vez ao dia |
| Cadastro de poços | segunda, 8h |
| Royalties do ano | dia 20, 9h |

Você pode criar, editar, pausar e executar agora. Para rodar com o app fechado: `ATIVAR_AGENDA_WINDOWS.bat` (a cada 5 minutos, com o computador ligado e sua sessão aberta); para desligar, `DESATIVAR_AGENDA_WINDOWS.bat`.

## 13. Royalties

Ranking por excedentes, com filtros de ano, UF e município. Mínimos = parcela de 5% (Lei 7.990/89); excedentes = parcela acima de 5% (Lei 9.478/97), onde a confrontação atua. A participação especial ainda não entra no app. O botão **Carregar/atualizar série** traz todos os anos. Hoje há 2021 a 2025 completos e 2026 de janeiro a agosto.

## 14. Poços e produção

Cadastro da ANP para PB, RN, CE, SE e AL, com filtros de UF, ambiente (terra ou mar), situação e texto livre.

- **Abrir mapa:** os poços do filtro no mapa.
- **Planilha Excel deste filtro:** resumo por UF, produção marítima por campo e a lista completa.
- **GeoJSON e pacote cartográfico:** para o QGIS.
- **Importar produção mensal:** CSV do CDP enviado pela tela ou pela pasta de importação. Hoje há produção marítima de janeiro a agosto de 2026 (RN, SE e AL).

Situação "produzindo" é do cadastro, não da produção mensal.

## 15. Planos diretores

Cadastro por município: lei, data-base (instituição ou última revisão integral), fonte oficial, data da pesquisa e prazo local se houver. O app calcula o marco de 10 anos e mostra: "Data a conferir", "Revisão a verificar nos próximos 12 meses", "Marco de revisão ultrapassado" ou "Marco futuro". Marque "Conferi a lei" só depois de ver o ato original.

## 16. Inteligência territorial

Ficha de cada um dos 751 municípios: royalties por mês, organizações cadastradas e plano diretor. O botão **Investigar** cria um sinal de royalties para o município.

## 17. Central de cartórios

78 cartórios da Paraíba (CNJ, 18/09/2026), com endereço, atribuições e contatos. Filtre por município e Registro de Imóveis, copie e-mails e telefones de uma vez ou exporte CSV. "Não contatar" tira o cartório da cópia. Cartórios são canal de indicação para SIGEF e REURB, não compradores.

## 18. Organizações e contatos

- **Organizações:** prefeituras, órgãos, empresas, escritórios e parceiros, com papel (comprador, interlocutor, parceiro).
- **Contatos:** nome, cargo, e-mail, telefone, fonte e data de conferência.
- Contato qualificado = conferido e não bloqueado (cartórios não entram na meta).

## 19. Tarefas e decisões

Ações internas que não são de um cliente: estruturar cursos, dossiê de habilitação, cadastros de fornecedor. Etapas: verificar, diagnóstico, escopo, aguardar decisão, concluído. Cada alteração fica no histórico. Os dois primeiros cursos (GNSS e QGIS) já estão aqui.

## 20. Continuidade e evidências

- **Exportar acompanhamento:** pacote com tarefas, oportunidades, coletas e agenda para retomar o trabalho com o assistente.
- **Gerar dossiê:** pacote com todas as fontes coletadas, hashes SHA-256 e manifesto. Serve para rastrear a origem dos dados; não é prova jurídica nem assinatura digital.

## 21. Regras de ouro

1. Mostre o problema com dado público; nunca o método.
2. Nenhum mapa indicativo em material comercial.
3. PMRR de Bayeux fora de qualquer peça comercial.
4. Não prometa receita nem resultado administrativo ou judicial.
5. Registre tudo: o que não está no app não aparece nas metas.
6. Contato só é qualificado depois de conferido.

## 22. Problemas comuns

| Sintoma | O que fazer |
|---|---|
| "Agenda sem sinal" | O app não está aberto ou a agenda travou: feche e abra de novo. |
| Coleta "Falhou" | Leia o motivo na página da coleta; tente de novo mais tarde. |
| PNCP com HTTP 429 | A fonte pediu pausa; a próxima rotina tenta de novo. |
| Diários com erro de SSL | Problema conhecido da fonte; use as páginas monitoradas. |
| Tela com erro | Rode `DIAGNOSTICO.bat` e envie o arquivo gerado. |
