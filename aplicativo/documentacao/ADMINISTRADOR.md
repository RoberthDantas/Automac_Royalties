# Guia do administrador do Automac_Royalties

Administrador: Roberth Dantas Gomes, desde 07/11/2026 (versão 0.6.0). Este guia diz onde está cada coisa, como mudar o
app sem pôr os dados em risco e como publicar uma versão nova. O manual de uso de cada tela continua em
`MANUAL_DE_USO.md`.

## 1. Regras de ouro

1. **Nunca desenvolva em cima da base real.** A instalação de uso (ex.: `C:\Automac_Royalties`) só recebe versões prontas. Para
   mexer no código, use uma pasta de desenvolvimento com uma *cópia* da pasta `dados`.
2. **A pasta `dados` nunca vai para o Git nem para e-mail aberto.** Ela tem contatos de pessoas (dados pessoais),
   histórico comercial e a chave `secret.key` da máquina. O `.gitignore` já a exclui.
3. **Toda mudança passa nos testes** (`manage.py test core`) antes de virar versão.
4. **Toda versão tem notas** em `documentacao/NOTAS_X.Y.Z.md`: o que mudou e como atualizar.
5. **Backup toda sexta**, guardado fora do computador (tela Backup).

## 2. Mapa do código

O app é um projeto Django 6.0 com banco SQLite, servido localmente pelo Waitress em `127.0.0.1:8766`.

| Onde | O que tem |
| --- | --- |
| `01_INSTALAR.bat` → `aplicativo/instalar_do_zero.py` | Cria o `.venv`, instala `requirements.txt`, prepara a base e a primeira conta |
| `02_ABRIR.bat` → `aplicativo/launch.py` | Trava de instância única, backup antes de migrar, migrações, cargas, agenda e servidor |
| `05_ATUALIZAR.bat` → `aplicativo/atualizar_instalacao.py` | Aplica um pacote novo sobre uma instalação, sem tocar em `dados` |
| `aplicativo/automac/settings.py` | Configuração e o número `VERSION` |
| `aplicativo/automac/urls.py` | Todas as rotas (endereços das telas) |
| `core/models.py` | Tabelas: Organização, Contato, Oportunidade, Histórico, Sinal, Royalty, Poço, Coleta etc. |
| `core/views.py` | Painel, cadastros genéricos (`EDITORS` em `forms.py`), oportunidade, sinais, backup |
| `core/commercial.py` | Lista quente da Frente 1, metas do trimestre, relatório, cadência D+4/D+10 |
| `core/prospect.py` | Gerador de mensagens, lista quente PB, conferência de contatos, série ANP |
| `core/admin_views.py` | Exclusão com confirmação e tela Usuários |
| `core/collectors.py` | `fetch` (download com tentativas, TLS de compatibilidade, cópia com SHA-256), IBGE, ANP, PNCP |
| `core/bid_scans.py` | Varredura de editais por capacidade (`CAPABILITIES` = termos do filtro) |
| `core/intelligence.py` | Querido Diário, páginas monitoradas, produção por URL |
| `core/wells.py`, `well_views.py` | Cadastro de poços (WFS da ANP), CSV do CDP, mapa e exportações |
| `core/importer.py` | Arquivos colocados em `dados/importar` (royalties `.xlsx`, produção `.csv`) |
| `core/scheduling.py` | Agenda interna (verifica a cada 30 s, uma coleta por vez) |
| `core/templates/core/` | HTML das telas |
| `core/management/commands/` | Comandos: `criar_usuario`, `alterar_usuario`, `diagnostico`, `recuperar_exclusao`, `executar_agenda`, `varrer_editais` etc. |
| `core/test_*.py`, `core/tests.py` | Testes automáticos |
| `referencias/` | Cargas iniciais versionadas (municípios, poços de 18/09, pesquisa de contatos) |
| `staticfiles/` | CSS, JavaScript, Leaflet e GeoJSON dos mapas |

Onde mexer para as mudanças mais comuns:

- **Termos do filtro de editais:** `CAPABILITIES` em `core/bid_scans.py` (termos separados por vírgula, palavra inteira,
  sem acento importar). Teste contra os editais já baixados antes de publicar.
- **Lista de alvos da Frente 1:** `FRENTE1_TARGETS` em `core/commercial.py`.
- **Metas e valores-alvo:** `quarter_metrics` em `core/commercial.py`.
- **Texto das mensagens de abordagem:** `build_messages` em `core/prospect.py`.
- **Menu lateral:** `core/context.py`.

## 3. Montar o ambiente de desenvolvimento (Windows)

Uma vez só:

1. Instale o [Git para Windows](https://git-scm.com/download/win) e use o VS Code.
2. Pegue o código: `git clone <endereço do repositório> C:\dev\automac_royalties` (ou extraia o pacote de atualização ali).
3. Em `C:\dev\automac_royalties\aplicativo`:
   ```
   py -3.13 -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
4. Copie a pasta `dados` de uma instalação (com o app fechado) para `C:\dev\automac_royalties\aplicativo\dados`.
5. Para abrir a cópia de desenvolvimento numa porta diferente da instalação de uso:
   ```
   .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8766
   ```
   O `runserver` recarrega sozinho ao salvar um arquivo e não liga a agenda de coletas.

## 4. Fazer uma mudança

1. Crie um ramo: `git switch -c minha-melhoria`.
2. Altere o código. Se mudar `models.py`, gere a migração: `manage.py makemigrations core -n nome_curto` e aplique
   na cópia: `manage.py migrate`. O `02_ABRIR.bat` das instalações faz backup e aplica sozinho.
3. Escreva ou ajuste um teste em `core/test_*.py` que prove a mudança.
4. Rode tudo: `manage.py test core`. Todos precisam passar.
5. `git add -A` e `git commit -m "o que mudou"`; depois junte ao principal: `git switch main` e
   `git merge minha-melhoria`.

## 5. Publicar uma versão

Número X.Y.Z: aumente Z para correção, Y para melhoria, X para mudança grande.

1. Escreva `documentacao/NOTAS_X.Y.Z.md` (siga o modelo da 0.6.0).
2. Rode `aplicativo\GERAR_VERSAO.bat` e informe o número. Ele grava a versão, roda os testes e gera em `dist\`:
   - `Automac_Royalties_X.Y.Z_atualizacao.zip`: só o programa, para atualizar instalações com `05_ATUALIZAR.bat`;
   - `Automac_Royalties_X.Y.Z_completo.zip`: programa + base, só se você passar `--com-dados <pasta dados>`
     (`scripts\gerar_versao.py X.Y.Z --com-dados C:\Automac_Royalties\aplicativo\dados`). Leva dados pessoais: canal restrito.
3. Faça o commit e marque a versão, como o script mostra: `git tag vX.Y.Z` e `git push --follow-tags`.
4. Atualize cada computador: extraia o ZIP de atualização em outra pasta, feche o app, rode `05_ATUALIZAR.bat`.

## 6. Contas

- Tela **Usuários**: criar, renomear, trocar senha, desativar. Toda conta tem acesso completo (não há perfis).
- O nome completo da conta assina as mensagens de abordagem.
- Senha esquecida ou ninguém consegue entrar: `04_ALTERAR_USUARIO.bat` na pasta principal.

## 7. Dados, backup e recuperação

- **Backup:** tela Backup gera um ZIP com a base. Restaurar: `aplicativo\RESTAURAR.bat` com o app fechado.
- **Antes de migrar** a base, o `02_ABRIR.bat` grava um backup em `dados\backups`; o `05_ATUALIZAR.bat` também copia
  o banco para lá.
- **Registro apagado por engano:** com o app fechado, na pasta `aplicativo`:
  ```
  .venv\Scripts\python.exe manage.py recuperar_exclusao              (lista as exclusões)
  .venv\Scripts\python.exe manage.py recuperar_exclusao --numero 3   (recria a de número 3)
  ```
  Arquivos anexados apagados do disco não voltam; para eles, use o backup.
- **Diagnóstico rápido:** `aplicativo\DIAGNOSTICO.bat` (versão, migrações, contagens, últimas coletas).
- **Logs:** `dados\logs\coleta-N.log` (cada coleta), `agenda_windows.log` (agenda do Windows), `exclusoes.jsonl`.

## 8. Fontes de dados e quando conferir

| Fonte | Rotina | O que observar |
| --- | --- | --- |
| PNCP (editais) | a cada 12 h | Status "Parcial" com "pediu pausa (HTTP 429)" é normal; a próxima rodada retoma |
| Querido Diário | diária | Se falhar mesmo com o perfil de compatibilidade TLS, o erro aparece na coleta |
| Páginas monitoradas | diária | Tela Fontes e cobertura mostra a última consulta bem-sucedida de cada página |
| Poços ANP (WFS) | semanal | Mudança grande na contagem bloqueia a troca da base; conferir antes |
| Royalties ANP | dia 20, 9h | A ANP publica por volta do dia 20; conferir o mês novo na tela Royalties |
| Produção CDP | manual | Baixar o CSV no painel da ANP e importar em Poços e produção |

## 9. Repositório

O histórico começa em `v0.5.2` (versão recebida do Uendry Maia em 06/10/2026), seguido de `v0.5.3` (correções) e
`v0.6.0`. Para guardar no GitHub: crie um repositório **privado** vazio e, na pasta do código,
`git remote add origin <endereço>` e `git push -u origin main --follow-tags`.
