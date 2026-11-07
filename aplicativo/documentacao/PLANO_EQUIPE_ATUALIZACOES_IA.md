# App CartoGeo para a equipe — acesso, atualizações e ajudante IA

30/09/2026 · Uendry Maia

## Resumo e recomendação

Minha recomendação é levar o app à equipe em duas fases:
- **Outubro:** um servidor local no escritório, a custo zero.
- **Novembro, se o uso pedir:** um servidor pago no Brasil, por R$ 30 a 70 por mês.

As atualizações passam a sair em pacotes numerados. Cada pacote se instala com um clique, faz backup antes e volta atrás sozinho se algo falhar. O ajudante IA é viável e custa pouco. No começo ele só lê e rascunha; nada é enviado sem uma pessoa.

| Pergunta                                  | Resposta curta                                                                                                                                                                                                                                                                                                             |
|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Como o Gilberto consulta o app?           | Pelo navegador, com login próprio. Na fase 1, o app roda num PC do escritório (o do Gilberto, se ficar ligado o dia todo) e os demais acessam pela rede. Na fase 2, o app roda num servidor pago e abre de qualquer lugar                                                                                                  |
| Quanto custa?                             | **Fase 1:** R$ 0. **Acesso de fora do escritório:** R$ 0 com Cloudflare (exige o DNS de cartogeo.org na Cloudflare ou um domínio novo de R$ 40 por ano), ou cerca de R$ 42 por usuário/mês com Tailscale. **Fase 2:** R$ 30 a 70 por mês. **Ajudante IA:** cerca de R$ 50 a 150 por mês, com teto definido por vocês |
| O que muda no app?                        | A versão 0.6.0, "modo equipe": contas e perfis por pessoa, acesso pela rede, nomes por usuário, trimestre configurável e o atualizador                                                                                                                                                                                     |
| Como o app continua evoluindo?            | Repositório privado, versões numeradas, `ATUALIZAR.bat` com backup e retorno automático, notas de versão e uma lista de pedidos priorizada todo mês                                                                                                                                                                        |
| Dá para ter um ajudante IA dentro do app? | Sim: um painel "Pergunte ao app" que usa a API da Claude para tirar dúvidas, consultar dados e rascunhar mensagens. Antes dele, um conector no Claude Desktop do Uendry, sem custo extra                                                                                                                                   |

*[Diagrama: como o app fica montado · fase 1 e fase 2 — ver o documento online ou o PDF]*

Da fase 1 para a fase 2, os dados passam por backup e restauração. Mudam o endereço e o lugar onde o app roda; o jeito de usar continua o mesmo.

As decisões que dependem do Gilberto estão na última seção. Os preços foram consultados em 30/09/2026, com o dólar a R$ 5,22; os links estão em **Fontes**, no fim do documento.

## Situação atual e o que impede o uso por mais pessoas

Hoje o app é de um usuário e um computador: ele só aceita conexões do próprio computador. A base já serve para equipe (login, banco único, agenda de coletas, backup). Faltam sete ajustes.

| Ponto             | Hoje                                                                                                | O que precisa para a equipe                                                                 |
|-------------------|-----------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| Endereço          | Só `127.0.0.1:8765`, o próprio PC                                                                   | Aceitar a rede do escritório ou um endereço na internet, com lista de endereços permitidos  |
| Contas            | Uma conta; novas contas só por comando; sem tela de senha                                           | Tela de usuários, troca de senha e perfis: administrador, comercial e consulta (só leitura) |
| Nomes fixos       | "Uendry" está escrito no código: saudação, responsável padrão, assinatura das mensagens e relatório | Nome, cargo e assinatura vindos do perfil de quem está logado                               |
| Período das metas | Trimestre fixo de 01/09 a 30/11/2026                                                                | Trimestre e metas configuráveis na tela                                                     |
| Pasta `importar`  | Só funciona no PC onde o app roda                                                                   | Tela de envio de arquivos (royalties e produção) pelo navegador                             |
| Local dos dados   | Pasta dentro do OneDrive; a sincronização pode corromper o banco                                    | Pasta local fora da nuvem, com backup diário e cópia fora do computador                     |
| Atualização       | Pacotes copiados à mão para a pasta                                                                 | Um atualizador com backup, testes e retorno automático (seção "Como o app será atualizado") |

**O que já ajuda:**
- O banco (SQLite) aguenta de 2 a 5 pessoas usando ao mesmo tempo, o tamanho desta equipe.
- As regras de segurança do app já estão no modo de produção.
- O histórico já grava o autor de cada atividade.
- A agenda de coletas roda dentro do app. Num servidor sempre ligado, as coletas deixam de depender do PC do Uendry.

## Opção A — Servidor local no PC do Gilberto

O app e o banco passam a morar no PC do Gilberto. Os demais acessam pelo navegador, na rede do escritório. Custa zero e fica pronto em cerca de duas semanas, com a versão 0.6.0. A condição é esse PC ficar ligado no horário de trabalho.

### Três formas de usar o PC do Gilberto

| Forma                                  | Como funciona                                                                                                                                 | Serve para                                                          | Limite                                                                                                                                                                                                            |
|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **A0. Cópia de consulta**              | Antes, o Uendry cria um login para o Gilberto (manual, seção 1.6). Depois gera um backup, e o Gilberto restaura no PC dele uma vez por semana | Gilberto explorar o app já nesta semana, sem nenhuma mudança no app | Dados com até uma semana de atraso. O que o Gilberto alterar se perde na próxima cópia. A cópia contém todos os contatos; pausar nela as rotinas de coleta                                                        |
| **A1. Servidor na rede do escritório** | O app roda no PC do Gilberto; o Uendry e os demais abrem `http://IP-do-PC:8765`                                                               | Uso diário da equipe no escritório                                  | Se o PC desligar, ninguém acessa. Sem cadeado HTTPS: usar só na rede protegida do escritório. Sem HTTPS, os botões Copiar só funcionam no próprio PC servidor; nos demais, copiar com Ctrl+C até a 0.6.0 corrigir |
| **A2. A1 + acesso de fora**            | A1 mais um túnel seguro para quem está fora do escritório                                                                                     | Trabalho em campo ou em casa                                        | Exige configurar Tailscale ou Cloudflare (abaixo)                                                                                                                                                                 |

Se o PC do Gilberto for um notebook que sai do escritório, o servidor deve ser outro computador que fique na mesa. Pode ser o PC do Uendry, com o Gilberto acessando pela rede: o passo a passo é o mesmo.

### Passo a passo da A1
1.  **Preparar o app:** instalar a versão 0.6.0, com contas por pessoa e o `03_ABRIR_EM_REDE.bat`.
2.  **Instalar no PC do Gilberto:** Python 3.13; copiar a pasta do app para `C:\CartoGeo\` sem `aplicativo\.venv` e sem `aplicativo\dados`; rodar `01_INSTALAR.bat`.
3.  **Levar os dados:** o Uendry cria o login do Gilberto, gera um backup, e o Gilberto restaura com `RESTAURAR.bat`. A partir daí, os dados oficiais ficam só no PC do Gilberto. A cópia do Uendry vira arquivo.
4.  **Fixar o endereço do PC:** no roteador, reservar um IP para o PC do Gilberto (exemplo: `192.168.0.50`).
5.  **Liberar o firewall:** conferir que a rede do escritório está marcada como **Privada** no Windows. Na primeira abertura, o Windows pergunta se libera a rede: marcar só **Redes privadas**.
6.  **Criar as contas:** Gilberto e Uendry (administradores) e os demais (consulta).
7.  **Agenda de coletas:** com o app aberto no PC do Gilberto, a agenda já roda. No PC do Uendry, rodar `DESATIVAR_AGENDA_WINDOWS.bat`, se estiver ativa, para a cópia antiga não coletar sozinha.
8.  **Nos outros computadores e celulares do escritório:** abrir `http://192.168.0.50:8765`, entrar com o próprio login e salvar nos favoritos.
9.  **Backup:** diário e automático no próprio PC (vem na 0.6.0); cópia semanal para o Drive da empresa.

### Acesso de fora do escritório (A2)

| Caminho                        | Como funciona                                                                                                                                                                          | Custo                                                                                                           | Observação                                                                                                                                                                                                 |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Tailscale**                  | Um programa em cada aparelho cria uma rede privada entre eles. O app continua invisível para a internet                                                                                | Plano Personal gratuito, mas só para uso não comercial. Plano Standard: US$ 8 por usuário/mês, cerca de R$ 42 | O mais simples de configurar. Para 2 pessoas, cerca de R$ 84 por mês                                                                                                                                      |
| **Cloudflare Tunnel + Access** | Um túnel publica o app num endereço como `app.cartogeo.org`, com HTTPS. Antes do login do app, a Cloudflare exige uma identificação extra, como um código enviado ao e-mail autorizado | Gratuito para até 50 usuários                                                                                   | Exige que o domínio use a Cloudflare. A CartoGeo já tem cartogeo.org; é preciso saber quem administra o DNS, porque a mudança afeta também o site e o e-mail. Um domínio novo .com.br custa R$ 40 por ano |

Não recomendo abrir a porta do roteador para a internet: expõe o PC sem HTTPS e sem uma segunda barreira.

### Prós e contras da opção A
- **Prós:** custo zero; dados dentro do escritório; fica pronto rápido; usa o que já existe.
- **Contras:**
  - depende de um PC ligado e sem reinicialização no meio do dia (o Windows Update reinicia sozinho se não for configurado);
  - os dados ficam num único aparelho, e o backup vira obrigatório;
  - o acesso de fora exige uma peça a mais (Tailscale ou Cloudflare);
  - a manutenção é feita no PC do Gilberto.

## Opção B — Hospedagem paga

O app passa a rodar 24 horas num servidor alugado no Brasil, com endereço próprio e HTTPS. Custa de R$ 30 a 70 por mês. É a opção certa quando houver uso fora do escritório, três ou mais usuários, ou quando as coletas não puderem parar à noite.

### Onde hospedar

Recomendo um servidor virtual (VPS) com data center em São Paulo. Os dados ficam no Brasil e a conexão com os portais públicos brasileiros fica curta.

| Provedor e plano       | Preço                                                     | Configuração            | Região              | Observação                                                                           |
|------------------------|-----------------------------------------------------------|-------------------------|---------------------|--------------------------------------------------------------------------------------|
| **Hostinger KVM 1**    | R$ 29,99/mês no contrato de 24 meses; renova a R$ 59,99 | 1 vCPU, 4 GB RAM, 50 GB | São Paulo           | Melhor custo, em reais, mas exige contrato de 24 meses (cerca de R$ 720 no período) |
| **Hostinger KVM 2**    | R$ 43,99/mês no contrato de 24 meses; renova a R$ 77,99 | 2 vCPU, 8 GB, 100 GB    | São Paulo           | Mais memória, se a equipe crescer. A renovação passa do teto de R$ 70               |
| **AWS Lightsail 2 GB** | US$ 12/mês, cerca de R$ 63                              | 2 vCPU, 2 GB, 60 GB     | São Paulo           | Pago em dólar, sem fidelidade: bom para o mês de teste                               |
| **Fly.io (1 GB)**      | cerca de US$ 5,70/mês mais disco, cerca de R$ 30        | Cobrança por uso        | São Paulo           | Mais técnico: exige empacotar o app                                                  |
| **Oracle Always Free** | Gratuito                                                  | Até 2 VMs pequenas      | São Paulo e Vinhedo | Pode faltar capacidade, e máquina ociosa pode ser recolhida. Só para testes          |
| **Magalu Cloud**       | Não verificado                                            | —                       | Sudeste e Nordeste  | Vale cotar: tem região no Nordeste                                                   |

Render, Railway e PythonAnywhere funcionam, mas não têm servidores no Brasil. DigitalOcean e Hetzner também não têm.

### Como fica montado
- **Sistema:** Ubuntu Linux, atualizado automaticamente.
- **Porta de entrada:** Caddy, que emite e renova o certificado HTTPS sozinho.
- **App:** o mesmo da versão 0.6.0, rodando como serviço que reinicia se cair.
- **Banco:** SQLite no início, suficiente para a equipe. Migrar para PostgreSQL só se passar de 5 pessoas simultâneas.
- **Endereço:** `app.cartogeo.org`, ou um .com.br novo por R$ 40 por ano.
- **Backup:** diário, com cópia automática fora do servidor (Drive da empresa), mais os backups do provedor, se contratados.
- **Segurança:**
  - só as portas 80 e 443 abertas, e acesso administrativo por chave;
  - limite de tentativas de login;
  - opcionalmente, a barreira da Cloudflare Access, que é gratuita.

### Passo a passo
1.  Aprovar o orçamento e o provedor.
2.  Contratar o VPS em nome da CartoGeo e criar o subdomínio no DNS.
3.  Rodar o script de implantação, preparado na versão 0.7.0: instala, configura HTTPS, serviço e backup.
4.  Levar os dados: backup do app atual e restauração no servidor.
5.  Criar as contas e testar por uma semana em paralelo com o app local.
6.  Virar a chave: o app local vira só leitura e depois arquivo.

### Prós e contras da opção B
- **Prós:**
  - acesso de qualquer lugar, inclusive celular;
  - coletas 24 horas;
  - nenhum PC precisa ficar ligado;
  - HTTPS e endereço profissional;
  - backup fora do escritório.
- **Contras:**
  - custo mensal;
  - os dados saem do escritório, embora fiquem no Brasil;
  - alguém precisa cuidar do servidor. Com os scripts e o atualizador, isso leva poucos minutos por mês.

## Contas, permissões, segurança e LGPD

Cada pessoa terá login próprio e um perfil. O app passará a registrar quem fez cada alteração. Vale para as duas opções.

### Perfis propostos

| Perfil            | Para quem                                                   | O que pode fazer                                                                                                                |
|-------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **Administrador** | Gilberto e Uendry (dois, para ninguém ficar trancado fora)  | Tudo, mais usuários, backup, restauração, rotinas de coleta e configurações de metas                                            |
| **Comercial**     | Quem prospecta                                              | Cadastrar e editar organizações, contatos e oportunidades; registrar atividades; revisar sinais; gerar mensagens; rodar coletas |
| **Consulta**      | Demais funcionários, ou o Gilberto no dia a dia se preferir | Ver todas as telas e baixar relatórios e planilhas; não altera nada                                                             |

### Regras de segurança
1.  Login individual; senha nunca compartilhada.
2.  Senha com 10 caracteres ou mais (o app já exige) e troca pela própria tela.
3.  Bloqueio temporário após tentativas de login erradas seguidas.
4.  Sessão que expira após 8 horas sem uso quando o acesso vem de fora do escritório.
5.  Trilha de auditoria: quem criou ou alterou oportunidades, contatos, organizações e planos, e quando.
6.  Nada é excluído por usuários comuns: registros são arquivados. Só o administrador exclui, e só para atender pedido de titular de dados.
7.  Backups guardados em pasta restrita, porque contêm contatos e a chave do app.

### LGPD

O app guarda dados pessoais: nome, cargo, e-mail e telefone institucionais de servidores públicos, cartórios e empresas. Isto é uma orientação geral de boas práticas, não um parecer jurídico; vale confirmar com a assessoria da CartoGeo.
- **Já existe no app:**
  - campo de fonte em cada contato;
  - marcação **Não contatar**, respeitada nas mensagens e cópias;
  - nenhum envio automático;
  - acesso só com login.
- **Entra nas versões 0.6.x:**
  - exclusão a pedido do titular, feita pelo administrador;
  - revisão anual dos contatos sem uso;
  - registro de quem acessou.
- **Na opção B:**
  - contrato com o provedor, que passa a ser operador dos dados;
  - servidor no Brasil, o que evita transferência internacional.
- **No ajudante IA:** enviar à API só o mínimo necessário. Telefone e e-mail de contatos não saem do app, a não ser no rascunho de mensagem para aquela pessoa.

## Como o app será atualizado

O app passa a evoluir em versões numeradas, uma pequena a cada duas semanas. Cada versão é um pacote instalado por um atualizador. O atualizador faz backup antes, testa depois e volta atrás sozinho se algo falhar. Os pedidos de melhoria entram numa lista única, priorizada uma vez por mês com o Gilberto.

### As peças

| Peça                                                                | O que é                                                                                                | Por quê                                                                  |
|---------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| **Repositório privado** (GitHub, gratuito para repositório privado) | O código-fonte oficial, com o histórico de cada mudança                                                | Nenhuma versão se perde; dá para voltar a qualquer ponto                 |
| **Versão numerada**                                                 | 0.6.0 traz novidades; 0.6.1 traz só correções. A 1.0.0 sai após um mês de uso em equipe sem incidentes | Todo mundo sabe o que está instalado; o número aparece no rodapé do menu |
| **Testes automáticos**                                              | Hoje são 38 testes; cada mudança nova ganha os seus                                                    | Um conserto não quebra outra tela sem ninguém ver                        |
| **Pacote de atualização**                                           | `CartoGeo_atualizacao_0.6.1.zip`, só com código, nunca com dados                                       | Instala igual no PC do escritório e no servidor pago                     |
| **`ATUALIZAR.bat`**                                                 | O atualizador de um clique                                                                             | Ninguém precisa copiar arquivos à mão                                    |
| **Notas de versão**                                                 | Uma página **Novidades** no app, com o que mudou em cada versão                                        | A equipe descobre as novidades sem manual novo                           |
| **Lista de pedidos**                                                | Botão **Sugerir melhoria** no app; cada pedido vira um item com autor e data                           | Nenhuma ideia se perde no WhatsApp                                       |

### O que o `ATUALIZAR.bat` faz
1.  Confere se o app está fechado; no servidor, pausa o serviço.
2.  Faz backup completo dos dados e guarda uma cópia do código atual em `_versoes\`.
3.  Confere a integridade e a versão do pacote.
4.  Troca só o código. Nunca toca em `dados\`, nas senhas ou nos anexos.
5.  Instala dependências novas, se houver.
6.  Atualiza a estrutura do banco e roda os testes rápidos.
7.  **Se qualquer passo falhar:** devolve o código e o banco da etapa 2 sozinho e mostra o motivo.
8.  **Se tudo passar:** mostra "Atualizado para 0.6.1" e abre o app na página **Novidades**.

No PC, o pacote é colocado na pasta `atualizacoes\` e o atualizador faz o resto. No servidor pago, o mesmo processo roda por comando, direto do repositório.

### O ciclo de melhorias
1.  **Pedido:** qualquer pessoa usa **Sugerir melhoria** ou manda ao Uendry. O pedido tem o que é, qual venda ajuda, um exemplo e o prazo desejado.
2.  **Priorização mensal:** 15 minutos com o Gilberto, junto do relatório do mês. A pergunta é quanto o item ajuda a vender e quanto custa fazer.
3.  **Desenvolvimento:** o Uendry com o Claude, no repositório, sempre com teste novo.
4.  **Ensaio:** o pacote é instalado antes numa cópia de teste, com dados reais restaurados de um backup.
5.  **Publicação:** `ATUALIZAR.bat` no servidor, fora do horário de uso.
6.  **Aviso:** a página **Novidades** e três linhas no relatório semanal.

Correção urgente (tela com erro, coleta parada) sai no mesmo dia como versão de correção.

### Lista inicial de melhorias

| Versão                   | Quando                 | Itens                                                                                                                                                                                                                                                                                                                                                                        |
|--------------------------|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **0.6.0 — Modo equipe**  | 1ª quinzena de outubro | Contas, perfis e troca de senha; bloqueio após tentativas erradas; acesso pela rede, com os botões Copiar funcionando sem HTTPS; nome, cargo e assinatura por usuário; trimestre e metas configuráveis; envio de arquivos pelo navegador; backup diário automático; `ATUALIZAR.bat` e **Novidades**; busca no manual; correção da lista quente com organização sem município |
| **0.6.x — Acabamento**   | 2ª quinzena de outubro | Trilha de auditoria de contatos, organizações e planos; registro de acessos; arquivar registros e exclusão a pedido do titular; botão **Sugerir melhoria**; filtros de frente e etapa no Funil; conferência de contato com nota e desfazer; relatório de qualquer mês por botão; nomes legíveis das fontes; textos antigos corrigidos; conector do app para o Claude Desktop |
| **0.7.0 — Servidor**     | Novembro               | Script de implantação no servidor pago, com HTTPS; sessão de 8 horas para acesso de fora; cópia externa automática do backup; painel do gestor para o Gilberto                                                                                                                                                                                                               |
| **0.8.0 — Inteligência** | Dezembro               | Ajudante IA embutido; participação especial; correção dos Diários (erro de SSL); nomes de operadores atualizados                                                                                                                                                                                                                                                             |

## Ajudante IA dentro do app

Sim, dá para ter um ajudante IA, e recomendo fazê-lo em duas etapas:
- **Outubro:** um conector do app no Claude Desktop do Uendry, sem custo extra, mais uma busca no manual dentro do app.
- **Dezembro, no servidor do escritório ou no pago:** um painel **Pergunte ao app** para toda a equipe. Ele usa a API da Claude, custa de R$ 50 a 150 por mês e tem teto de gasto.

Nas duas etapas, o ajudante lê e rascunha. Quem grava e envia é uma pessoa.

### O que o ajudante faria

| Tipo de ajuda       | Exemplo de pedido                                                                                            | O que ele entrega                                                                 |
|---------------------|--------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Tirar dúvida de uso | "Como importo a produção de setembro?"                                                                       | O passo a passo do manual e o link da tela                                        |
| Consultar dados     | "Quais municípios do 1º círculo ainda não foram abordados?" ou "Quanto Macau recebeu de excedentes em 2026?" | A resposta com números e a tela de origem                                         |
| Preparar abordagem  | "Rascunhe o follow-up D+4 para Areia Branca"                                                                 | Um rascunho com os dados do app, dentro das regras de ouro, para revisar e enviar |
| Preparar reunião    | "Resuma o histórico de Lucena para amanhã"                                                                   | Histórico, contatos, plano diretor e sinais numa página                           |
| Triar sinais        | "Este edital do PNCP serve para a CartoGeo?"                                                                 | Prós e contras do sinal. A decisão continua sendo sua                             |
| Prestar contas      | "Como foi a semana?" (Gilberto)                                                                              | Abordagens, reuniões, propostas e atrasos a partir dos registros                  |
| Conferir regras     | "Este texto fere alguma regra?"                                                                              | Checagem contra as seis regras de ouro: método, mapa, receita e PMRR              |

### As quatro formas possíveis

| Forma                                      | Como funciona                                                                                                                                                                                                       | Custo                                                                                                                                                                         | A favor                                                                                                                                                          | Contra                                                                                                                                  |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| **1. Painel embutido com a API da Claude** | Botão **Pergunte ao app** em todas as telas. O servidor do app envia a pergunta à API da Claude junto com funções só de leitura (oportunidades, royalties, metas, manual). A IA consulta, e o app mostra a resposta | Por uso, de R$ 50 a 150 por mês com teto (tabela abaixo)                                                                                                                     | Dentro do app, para toda a equipe; controle total do que sai                                                                                                     | Exige conta na API em nome da CartoGeo e cerca de uma semana de desenvolvimento                                                         |
| **2. Conector do app no Claude Desktop**   | Um pequeno programa deixa o Claude Desktop consultar o app pela rede, com login próprio e só para leitura, onde quer que o app esteja hospedado. O Claude Desktop no Windows aceita esse tipo de conector local     | Zero para o Uendry, que já usa o Claude. Para outras pessoas, um plano Claude para cada uma (o Team custa US$ 25 por usuário/mês, cerca de R$ 130, com mínimo de 2 pessoas) | Pronto em poucos dias; usa o modelo mais forte. Junta o app com Gmail, Agenda e pesquisa na web, por exemplo para criar rascunhos no Gmail dos follow-ups do dia | Fica fora do app; cada pessoa precisa do Claude instalado; os dados seguem as regras do plano Claude de quem usa, diferentes das da API |
| **3. Modelo local no próprio PC**          | Um modelo de IA gratuito roda no computador, sem internet                                                                                                                                                           | Zero por uso                                                                                                                                                                  | Nada sai do escritório                                                                                                                                           | Exige PC potente; responde pior em português e em raciocínio. Não recomendo agora                                                       |
| **4. Busca no manual, sem IA**             | Caixa de busca que acha a seção certa do manual                                                                                                                                                                     | Zero                                                                                                                                                                          | Instantânea e sem risco                                                                                                                                          | Não consulta dados nem escreve                                                                                                          |

### Quanto custa o painel embutido

Premissa de cálculo, sem desconto de cache: cada pergunta usa cerca de 16,4 mil tokens de entrada, somando as duas rodadas de consulta (regras, pergunta, trechos do manual e dados consultados) e 1,1 mil de saída. Valores sem IOF e impostos.

| Modelo            | Preço por milhão de tokens (entrada / saída) | Uso indicado        | Custo por pergunta | 440 perguntas/mês (2 pessoas, 10 por dia) | 1.000 perguntas/mês |
|-------------------|----------------------------------------------|---------------------|--------------------|-------------------------------------------|---------------------|
| Claude Haiku 4.5  | US$ 1 / US$ 5                              | Dúvidas e consultas | cerca de R$ 0,11  | cerca de R$ 50                           | cerca de R$ 114    |
| Claude Sonnet 5.5 | US$ 2 / US$ 10                             | Rascunhos e resumos | cerca de R$ 0,23  | cerca de R$ 101                          | cerca de R$ 229    |

Com 80% das perguntas no Haiku e 20% no Sonnet, o custo fica em cerca de R$ 60 por mês para 440 perguntas e R$ 137 para 1.000. O teto mensal no app impede surpresa.

### Riscos e regras do ajudante
1.  **Só leitura por padrão.** Registrar atividade ou criar oportunidade aparece como sugestão com botão **Aplicar**, clicado por uma pessoa.
2.  **Nunca envia** e-mail, mensagem ou arquivo.
3.  **Cita a origem de todo número** (tela ou registro). Sem o dado, diz que não tem; não estima.
4.  **Aplica as regras de ouro** em todo rascunho: sem método, sem mapa, sem promessa de receita, sem PMRR de Bayeux.
5.  **Dados pessoais mínimos:** telefone e e-mail só vão à API no rascunho para aquela pessoa. No conector do Claude Desktop, eles ficam de fora, e a conta deve estar com o uso das conversas para treinamento desligado nas configurações de privacidade. Pela política da Anthropic, dados da API comercial não treinam modelos, e o padrão é apagar as entradas e saídas em até 30 dias.
6.  **Teto de gasto** no app. Ao atingir o teto, o painel pausa até o mês seguinte.
7.  **Registro** de cada pergunta, resposta, usuário e custo, visível ao administrador.
8.  **A chave da API fica no servidor**, nunca no navegador. A conta é da CartoGeo, com créditos pré-pagos.

### Recomendação
1.  **Outubro:**
    - busca no manual dentro do app (versão 0.6.0);
    - conector no Claude Desktop do Uendry (0.6.x), lendo o app pela rede e sem telefone e e-mail de contatos. Ele dá ganho imediato na prospecção: rascunhos de follow-up no Gmail, resumo do dia, triagem de sinais.
2.  **Dezembro:** painel **Pergunte ao app** para a equipe, no servidor local ou no pago, com Haiku 4.5 nas consultas e Sonnet 5.5 nos rascunhos. Piloto de um mês com teto de R$ 100.
3.  **Depois do piloto:** manter, ajustar o teto ou desligar, conforme o uso real.

## Cronograma, custos e decisões para o Gilberto

Na proposta, o Gilberto acessa o app pela rede do escritório a partir de 13/10, sem custo. O servidor pago só entra em novembro, com aprovação. A decisão sobre ele fica para 30/10/2026, com o uso real de outubro na mão.

*[Diagrama: cronograma proposto · setembro a dezembro de 2026 — ver o documento online ou o PDF]*

As datas são proposta: dependem das decisões 1, 5 e 7 da tabela abaixo.

### Custos consolidados

| Item                         | Fase 1 (outubro)                                                                                                   | Fase 2 (novembro em diante)                                                              |
|------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Servidor                     | R$ 0 (PC do escritório)                                                                                           | R$ 30 a 63 por mês (Hostinger KVM 1 com contrato de 24 meses, ou Lightsail 2 GB mensal) |
| Acesso de fora do escritório | R$ 0 com Cloudflare (exige o DNS na Cloudflare ou domínio novo), ou cerca de R$ 42 por usuário/mês com Tailscale | Incluído: o servidor já tem HTTPS                                                        |
| Domínio                      | Só se o acesso de fora usar domínio novo: R$ 40 por ano                                                           | R$ 0 com subdomínio de cartogeo.org; R$ 40 por ano com .com.br novo                    |
| Ajudante IA                  | R$ 0 (conector no Claude Desktop do Uendry)                                                                       | R$ 50 a 150 por mês, com teto, a partir de dezembro                                     |
| Backup externo               | Drive da empresa                                                                                                   | Drive da empresa                                                                         |
| **Total por mês**            | **R$ 0 dentro do escritório**                                                                                     | **R$ 30 a 70 sem IA; R$ 80 a 220 com IA**                                              |

### Decisões

| Nº  | Decisão                                             | Opções                                                     | Recomendação                                                                                       | Decisão do Gilberto                                               |
|-----|-----------------------------------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| 1   | Onde o app mora na fase 1                           | PC do Gilberto; PC do Uendry; direto no servidor pago      | O computador que fica ligado no escritório o dia todo                                              | A decidir |
| 2   | Quem acessa e com qual perfil                       | Lista de pessoas e perfis                                  | Gilberto e Uendry administradores; demais em consulta                                              | A decidir |
| 3   | Cópia de consulta no PC do Gilberto já nesta semana | Sim; não                                                   | Sim: risco baixo (a cópia contém todos os contatos), e ele conhece o app antes da versão de equipe | A decidir |
| 4   | Acesso de fora do escritório na fase 1              | Nenhum; Cloudflare; Tailscale                              | Cloudflare, se o DNS de cartogeo.org estiver acessível; senão, esperar a fase 2                    | A decidir |
| 5   | Servidor pago                                       | Aprovar até R$ 70 por mês a partir de novembro; não agora | Decidir em 30/10, com o uso de outubro                                                             | A decidir |
| 6   | Endereço                                            | Subdomínio de cartogeo.org; .com.br novo                   | Subdomínio `app.cartogeo.org`. Falta saber quem administra o DNS                                   | A decidir |
| 7   | Ajudante IA                                         | Conta da API da Claude em nome da CartoGeo; teto mensal    | Aprovar o piloto de dezembro com teto de R$ 100                                                   | A decidir |
| 8   | Ritmo de atualizações                               | Quinzenal; mensal                                          | Versões quinzenais e priorização mensal de 15 minutos com o Gilberto                               | A decidir |

## Fontes

Preços e políticas consultados em 30/09/2026. Conversão a US$ 1 = R$ 5,22 ([valordolar.com.br](https://valordolar.com.br/cotacoes/dolar/)), sem IOF e impostos.
- Tailscale, planos e limites: [tailscale.com/pricing](https://tailscale.com/pricing)
- Cloudflare Access (gratuito até 50 usuários): [cloudflare.com/zero-trust/products/access](https://www.cloudflare.com/zero-trust/products/access/)
- Cloudflare Tunnel (exige domínio na Cloudflare): [developers.cloudflare.com/tunnel](https://developers.cloudflare.com/tunnel/)
- Hostinger VPS Brasil: [hostinger.com/br/servidor-vps](https://www.hostinger.com/br/servidor-vps)
- AWS Lightsail: [aws.amazon.com/lightsail/pricing](https://aws.amazon.com/lightsail/pricing/)
- Fly.io: [fly.io/docs/about/pricing](https://fly.io/docs/about/pricing/)
- Oracle Cloud Free Tier: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
- Magalu Cloud: [magalu.cloud/precos](https://magalu.cloud/precos/). Preço não verificado
- Render: [render.com/pricing](https://render.com/pricing)
- Railway: [railway.com/pricing](https://railway.com/pricing)
- PythonAnywhere: [pythonanywhere.com/pricing](https://www.pythonanywhere.com/pricing/)
- Regiões DigitalOcean: [docs.digitalocean.com](https://docs.digitalocean.com/platform/regional-availability/)
- Regiões Hetzner: [docs.hetzner.com](https://docs.hetzner.com/cloud/general/locations/)
- Domínio .com.br: [registro.br](https://registro.br/ajuda/pagamento/valores/)
- Preços da API da Claude: [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Uso de dados para treinamento: [privacy.claude.com](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)
- Retenção de dados da API: [privacy.claude.com](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)
- Plano Team: [claude.com/pricing](https://claude.com/pricing)
- Conectores locais no Claude Desktop: [support.claude.com](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
