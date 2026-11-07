# CartoGeo 0.4.2 — ajustes de 29/09/2026

Atualização aplicada sobre a instalação 0.4.1, sem apagar dados. Backup prévio: `_backups/backup_antes_ajustes_20260929_1558.zip`.

## Novo
- **Lista quente — Frente 1**: os 20 municípios dos três círculos do Plano Comercial (RN, SE, CE/AL), carregados como oportunidades em "Identificada", com prefeitura, excedentes 2021–2025 e costa (valores do plano até a coleta ANP substituí-los), etapa, próxima ação e contatos. Inclui a produção marítima ativa por campo, a partir do cadastro ANP.
- **Metas e relatório**: indicadores da seção 9 do plano (contratos, propostas, contatos qualificados, reuniões, editais triados), abordagens da semana contra a meta de 10, ações atrasadas e dos próximos 7 dias, funil por frente. Relatório em Markdown da semana ou de qualquer período (`/metas/relatorio.md?de=AAAA-MM-DD&ate=AAAA-MM-DD`).
- **Cadência automática**: registrar "Contato realizado" leva a oportunidade a "Contato realizado" e agenda follow-up D+4; um segundo contato na mesma janela agenda D+10. "Proposta" leva a "Proposta enviada"; "Reunião" leva a "Diagnóstico". Toda mudança automática fica no histórico.
- **Planilha de poços** (Excel) do filtro atual, com resumo por UF e produção marítima ativa.

## Corrigido
- Radar do PNCP: filtro de exclusão para compra de bens e software (equipamentos, aparelhos, frota, licença de uso etc.). Os 4 editais da primeira coleta eram desse tipo e foram descartados com a justificativa registrada.
- Tela "Continuidade e evidências" dava erro 500 quando uma UF do PNCP falhava (defeito da 0.4.1).
- Coleta ANP de royalties aceita os pacotes anuais com várias planilhas (2022, 2024, 2025); usa só a planilha que passar na validação municipal.
- PNCP passa de 30 minutos para 12 horas (a fonte já respondia HTTP 429 por excesso de consultas); Diários, de 6 horas para 1 vez ao dia. Rotinas editadas por você não são alteradas.
- Respostas não compactadas são gravadas uma única vez (antes, em dobro).

## Validação
33 testes automatizados (28 anteriores + 5 novos), 72 telas conferidas numa cópia do banco real, instalação nova conferida em base vazia. Ambiente Linux/Python 3.13; a abertura no Windows precisa ser conferida no seu PC.

## Pendente
- Rodar em Fontes e coletas → "ANP — royalties anuais" os anos 2021 a 2026. O leiaute de anos antigos não pôde ser testado aqui (sem acesso à ANP neste ambiente); a validação recusa o arquivo em vez de gravar valores errados.
- Tirar a pasta do OneDrive (após a reunião de 30/09).
- Diários (Querido Diário) seguem falhando por erro de SSL no seu PC; causa não diagnosticada.
- O MANIFESTO.json da pasta raiz descreve o pacote 0.4.1 original.
