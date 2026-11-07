# Fluxo de trabalho CartoGeo — menos repetição, mais execução

## Abrir uma sessão

Envie o objetivo da rodada e o resumo baixado em **Planejamento interno → Baixar resumo para continuar no chat**. Quando houver erro, acrescente o diagnóstico e o trecho completo do erro. Não reenvie o histórico inteiro ou bases já presentes no pacote.

Exemplo: “Continuar CartoGeo 0.2.0. Objetivo: validar a fonte técnica da LBR. Resumo anexo. Trabalhar internamente; registrar resultados e pendências.”

## Executar uma rodada

1. Ler `ESTADO_PROJETO.md` e o resumo atualizado; consultar outros arquivos somente quando necessários à tarefa.
2. Separar implementação técnica autorizada de decisão comercial ainda aberta. Executar a primeira; preparar evidências para a segunda.
3. Processar bases em código, com contagens, validações e hashes. Trazer ao chat resultados e exceções, sem despejar tabelas inteiras.
4. Fazer buscas com pergunta específica. Guardar fonte, data, recorte e resultado. Reconsultar informação quando precisar confirmar atualidade; não repetir consulta só para reconstituir contexto.
5. Testar o risco alterado: migração/preservação de dados, fluxo da função e regressão pertinente. Evitar verificações redundantes depois de resolver o risco.

## Encerrar uma rodada

Registrar no planejamento: resultado verificável, pendência, responsável e próxima ação. Atualizar o estado do projeto e entregar um pacote consolidado quando houver código novo. Responder com o que mudou, o que foi validado e o próximo passo local.

## Divisão de responsabilidades

- Aplicativo: guardar dados, anexos, fontes, tarefas e histórico; executar coletas existentes quando acionadas.
- Assistente: analisar exceções, pesquisar questões específicas, editar código e preparar decisões.
- Uendry: definir prioridade comercial, validar escopo, destinatários, preço, contato e envio.

## Regras de economia

- Manter uma versão identificada como base; acumular alterações sobre ela.
- Usar o código IBGE como chave municipal; não conciliar por nome sem conferência.
- Reusar arquivos validados e resumos curtos; abrir dados brutos apenas para resolver dúvida concreta.
- Preservar datas históricas e distinguir fonte atual de registro antigo.
- Manter respostas e atualizações curtas. Documentação detalhada fica nos arquivos.
- Esta rotina reduz repetição, mas não garante um percentual de economia nem fornece contador preciso dos tokens da conversa. Não existe monitoramento automático configurado por esta atualização.
