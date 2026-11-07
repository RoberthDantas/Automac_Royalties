# CartoGeo protocolo de fontes e procedimentos
Versão 0.3.0. Preparado em 21/09/2026 para uso interno e revisão técnica e jurídica.

## Finalidade e alcance
Organizar evidências sobre origem dos dados, processamento, decisões e integridade dos arquivos. O conjunto é subsídio documental, não certificado de autenticidade, ata notarial ou garantia de aceitação judicial. A implantação no computador do usuário e os atos externos não foram executados pelo assistente.

## Identificação e responsabilidades
Projeto CartoGeo. Gestão informada: Uendry Maia. Elaboração assistida por IA, sujeita à revisão de responsável técnico e jurídico a designar. Não atribui assinatura, credenciamento, autoria de terceiros ou responsabilidade profissional sem validação. Registrar nome, função, data e objeto de cada aprovação na ficha do caso.

## Inventário de fontes
1. Municípios: API de Localidades e API de Malhas do IBGE. Cinco UFs, 751 códigos conciliados. Respostas originais preservadas em referencias/cartografia_20260921. Malhas simplificadas para contexto; ano territorial não explicitado na resposta utilizada. A data da consulta não é a competência da malha.
2. Linhas: LBR_corrigida_Brasil.zip fornecido pelo usuário, 279 feições, SIRGAS 2000 EPSG:4674. Origem técnica, autoria, data e condição oficial não comprovadas. Original preservado; não há códigos IBGE/UF. Não foi reconstruído o método proprietário nem produzida nova ortogonal.
3. Estatísticas: UFs_Municipios.zip, nove tabelas XLS e índice HTML do Censo 2010 sobre aglomerados subnormais. Referência histórica; não é malha nem diagnóstico atual de demanda.
4. Cabedelo: notícias municipais de 11/08/2022 e 21/03/2024 e duas fotos recebidas do folheto Casa Legal. Datas de notícia preservadas; data de publicação do folheto desconhecida. A menção à Portaria 009/2025 ainda exige cotejo com ato original. Atualização cadastral não foi tratada como titulação registral.
5. Poços: cópia ANP incluída no pacote anterior, identificada como consultada em 18/09/2026. Sua referência não equivale a produção atual; não há atribuição de direitos a royalties por proximidade ou sobreposição.
6. Editais: API pública de consulta PNCP, propostas abertas no horizonte de 30 dias. Respostas e parâmetros das coletas concluídas são preservados no computador que executa a busca. A tentativa desta rodada falhou por resolução de endereço em todas as cinco UFs; não houve leitura de publicações nem constatação de ausência de editais.

## Procedimentos efetivamente implementados
Coleta HTTP pública com limite de tamanho e duração; armazenamento do corpo recebido e, se gzip, da cópia descompactada; hash SHA-256 de cada representação. Novas capturas registram URL solicitada e final, status, cabeçalhos selecionados, horários locais em UTC e versão do coletor. O corpo armazenado não é uma captura da sessão TLS nem do tráfego completo.

Metadados antigos ausentes não são preenchidos retroativamente como se tivessem sido capturados. A data de inclusão no dossiê não substitui a data de origem. Fotografias e anexos fornecidos mantêm seus bytes; autoria e contexto dependem de confirmação externa.

Municípios são conciliados por código IBGE, sem associação automática por nome. A geometria de Barbalha apresentou autointerseção: make_valid foi aplicado somente ao derivado de visualização e registrado nos atributos; original mantido. A LBR foi convertida de formato para visualização em EPSG:4326, com longitude e latitude nessa ordem, preservando traçados e atributos. Não há certificação de precisão cadastral do derivado.

O PNCP é filtrado por termos do objeto em quatro grupos: regularização/cadastro, levantamentos, geoprocessamento/cartografia e planejamento territorial. Correspondência textual é um sinal a revisar. Não certifica habilitação, disponibilidade de equipamentos, atribuição profissional, preço ou viabilidade de contratação. Não lê automaticamente todos os anexos. A paginação é dinâmica; retomadas podem sofrer deslocamentos de registros, exigindo nova varredura completa periodicamente.

Tarefas e oportunidades conservam estágio, responsável, próxima ação, prazo e pendências. Alterações do planejamento têm histórico local. O banco é administrável localmente e o histórico não é inviolável. A exportação não envia nada ao ChatGPT; o usuário anexa o arquivo deliberadamente.

## Integridade e preservação
O dossiê contém manifesto com caminho, tamanho e SHA-256 de cada arquivo. O verificador identifica divergências em relação ao manifesto e arquivos extras ou ausentes. Fonte registrada cujo arquivo esteja ausente ou com hash diferente bloqueia a geração, para não ocultar lacunas. O hash do ZIP é salvo ao lado do pacote.

Hash comprova igualdade de bytes frente a uma referência, não veracidade, autoria ou existência em uma data anterior. Quem modificar todos os arquivos e o manifesto poderá criar outro pacote internamente coerente. Preservar o ZIP original, sua soma de verificação e uma cópia independente; evitar sobrescrever versões. Registrar transferências, destinatário, finalidade, data e protocolo em controle de custódia. Assinatura e ancoragem temporal externas permanecem pendentes.

## Enquadramento jurídico para revisão
O CPC, arts. 369 e 371, trata dos meios de prova e de sua apreciação. O art. 384 disciplina a ata notarial. O art. 439 trata do uso de documentos eletrônicos em processo convencional. A MP 2.200-2, art. 10, disciplina documentos eletrônicos e meios de comprovação de autoria e integridade, inclusive a certificação ICP-Brasil. O tratamento jurídico concreto depende do caso, da autenticidade demonstrada e da revisão profissional. Este pacote não executou assinatura digital, autenticação cartorial nem carimbo de tempo confiável.

## Lacunas para um caso concreto
Conferir ato vigente do Casa Legal; obter documentação técnica e autoridade da LBR; selecionar base cartográfica adequada à precisão requerida; obter edital, anexos e retificações em sua íntegra; confirmar habilitação e responsáveis; revisar cálculo ou conclusão antes de uso externo. Registrar limitações e confrontar dados com a documentação oficial pertinente ao caso.

## Referências consultadas
- CPC, Lei 13.105/2015, texto oficial: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm
- MP 2.200-2/2001, texto oficial: https://www.planalto.gov.br/ccivil_03/mpv/antigas_2001/2200-2.htm
- IBGE, documentação: https://servicodados.ibge.gov.br/api/docs/malhas?versao=3
- PNCP: https://pncp.gov.br/
- Endereços completos das notícias, consultas IBGE e arquivos: acoes.json e fontes.json nas referências do aplicativo.

Os textos legais foram consultados pela ferramenta de pesquisa na web. A tentativa de baixar os corpos HTTP pelo coletor local falhou; não há cópia HTTP original dessas páginas neste dossiê. O registro da falha foi preservado e não substituído por uma captura inventada.
