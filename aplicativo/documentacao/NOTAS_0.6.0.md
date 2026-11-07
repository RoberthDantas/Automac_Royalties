# CartoGeo 0.6.0 — melhorias (07/11/2026)

Primeira versão sob administração de Roberth Dantas Gomes. Inclui as correções da 0.5.3. A base de dados recebe uma
migração (datas de mudança de etapa e de revisão de sinais); o app faz backup sozinho antes de aplicá-la.

## Novidades

- **Tela Usuários** (menu lateral): criar conta, trocar nome ou senha, desativar e reativar. Não deixa você desativar a
  própria conta nem ficar sem nenhuma conta ativa. Os arquivos `03_` e `04_` continuam para emergências.
- **Excluir registros** em oportunidades, contatos, organizações, planos diretores, lançamentos financeiros, páginas
  monitoradas, ações internas e documentos anexados. Antes de excluir, o app mostra tudo o que sai junto (histórico,
  contatos, anexos) e pede confirmação. Registros com vínculo protegido (ex.: organização com oportunidades,
  oportunidade com lançamentos) não são apagados: o app diz o que precisa sair antes. Cada exclusão grava uma cópia em
  `dados\logs\exclusoes.jsonl`, recuperável com `manage.py recuperar_exclusao`.
- **Metas só do trimestre.** Contratos, propostas, contatos qualificados e editais triados agora contam apenas o
  trimestre corrente. Contatos qualificados mostra também o total da base na explicação.
- **Agenda do Windows sem janela.** `ATIVAR_AGENDA_WINDOWS.bat` passa a usar `pythonw.exe`; a saída fica em
  `dados\logs\agenda_windows.log`. Quem já tinha ativado a agenda precisa rodar `ATIVAR_AGENDA_WINDOWS.bat` de novo.
- **Querido Diário:** quando o servidor recusa o aperto de mão TLS padrão (erro `SSLV3_ALERT_HANDSHAKE_FAILURE`), o
  app tenta na hora um perfil de compatibilidade, ainda verificando o certificado. A origem do arquivo registra qual
  perfil foi usado.
- **Filtro de editais** com termos novos: diagnóstico socioambiental, estudo de viabilidade técnica ambiental,
  monitoramento e planos de gestão ambiental, controle/contenção de erosão, processos erosivos, SIG, WebGIS,
  geoportal e base cartográfica. Nos 2.700 editais guardados, entraram 2 a mais, ambos do perfil, sem ruído novo.
- **Ferramentas do administrador:** `05_ATUALIZAR.bat` (atualiza uma instalação sem tocar nos dados),
  `aplicativo\GERAR_VERSAO.bat` (testa e empacota uma versão), guia `documentacao\ADMINISTRADOR.md` e repositório Git.
- **Instalador no Windows** (encontrado na instalação real em 07/11): o `01_INSTALAR.bat` confiava no código de saída
  do `py`, e o gerenciador novo do Python devolve "sucesso" mesmo sem a versão pedida; agora confere pela saída e, se
  não achar Python, lista os que existem. E o backup automático antes de migrar a base falhava no Windows ao tentar ler
  as travas (`scheduler.lock`, `dispatch.lock`) que o próprio app mantém abertas; backup e restauração agora ignoram
  todos os arquivos `.lock`. Sem essa correção, qualquer atualização com migração parava no Windows.
- Testes: 56, todos passando.

## Como atualizar uma instalação em uso

1. Extraia `CartoGeo_0.6.0_atualizacao.zip` em uma pasta nova.
2. Feche o app e rode `05_ATUALIZAR.bat` dessa pasta nova, informando a pasta instalada.
3. Abra `02_ABRIR.bat` na pasta instalada.
4. Se usava a agenda do Windows, rode `aplicativo\ATIVAR_AGENDA_WINDOWS.bat` de novo.
