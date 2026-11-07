# CartoGeo 0.5.3 — correções (07/11/2026)

Atualização de manutenção sobre a 0.5.2. A base de dados entregue é a mesma de 06/10/2026, sem alteração.

- **Painel com a contagem certa de ações atrasadas.** Na Central de operação, o número "Ações vencendo hoje ou atrasadas" parava em 12 (o tamanho da lista exibida). Agora mostra o total real: na base entregue, 24.
- **Varredura do PNCP sem bloqueio por excesso de pedidos (HTTP 429).** A varredura pedia as páginas sem intervalo, desistia na primeira recusa e já passava para a UF seguinte, que também era recusada. Por isso as coletas de 30/09 e 02/10 ficaram parciais. Agora há uma pausa de 1,5 s entre páginas, até três tentativas por página respeitando o tempo de espera pedido pela fonte e, se a fonte continuar recusando, a rodada para e a próxima execução retoma da página em que parou.
- **Retorno seguro ao conferir contato.** Depois de marcar um contato como conferido, o app só volta para telas do próprio app.
- **Rótulo do acumulado do ano.** O período de comparação dos royalties sempre mostra o nome do mês (ex.: "mar–ago"), e não mais um número quando o ano não começa em janeiro.
- **Mensagens com nomes de arquivos atuais.** Diagnóstico, restauração, agenda do Windows, rotina local e importação de cartórios citavam `INICIAR.bat`, `INSTALAR.bat` e `ATUALIZAR.bat`, que não existem mais. Agora citam `01_INSTALAR.bat` e `02_ABRIR.bat`. A mensagem de coleta em andamento não fala mais em um botão inexistente.
- Testes: 46, todos passando (4 novos para estas correções).

## Como atualizar uma instalação que já está em uso

1. Feche o app (Ctrl+C na janela preta).
2. Faça um backup (tela Backup, antes de fechar, ou copie a pasta `aplicativo\dados` para fora do computador).
3. Copie por cima, na pasta `aplicativo` instalada, os arquivos deste pacote **exceto** a pasta `dados`.
4. Abra `02_ABRIR.bat`. Não há migração de banco nesta versão.

Em computador novo, siga o guia normal: `01_INSTALAR.bat`.
