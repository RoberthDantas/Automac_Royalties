# CartoGeo — Poços e cartografia

Atualização preparada em 19/09/2026. Base geográfica consultada em 18/09/2026.

## Instalação no aplicativo existente

1. Aguarde terminar qualquer coleta e encerre o aplicativo com Ctrl+C na janela preta.
2. Extraia todo o ZIP desta atualização.
3. Copie as pastas **core**, **cartogeo**, **staticfiles**, **referencias** e o arquivo **launch.py** para a pasta do aplicativo que contém **INICIAR.bat** e **manage.py**.
4. Aceite mesclar pastas e substituir arquivos. Não apague as pastas existentes.
5. Abra **INICIAR.bat**. Antes de criar as novas tabelas, o programa faz um backup automático em **dados/backups**. Aguarde abrir o Chrome.
6. Entre em **Fontes e coletas** e selecione **ANP — poços: primeira carga, base verificada 18/09/2026**. Clique em **Buscar na fonte oficial**. Essa opção lê a cópia oficial incluída no pacote; funciona sem internet.
7. Abra **Poços e cartografia** no menu lateral.

As correções anteriores de ANP, timeout PNCP e backup Windows estão incluídas. O pacote não contém um banco para substituir o seu. Cartórios, contatos, royalties e anotações permanecem no banco existente. Não é necessário instalar bibliotecas novas.

## Resultado esperado da primeira carga

| UF | Registros de poços |
|---|---:|
| PB | 5 |
| RN | 8.586 |
| CE | 1.273 |
| SE | 4.923 |
| AL | 991 |
| **Total** | **15.778** |

São 14.569 registros em terra e 1.209 no mar, todos com coordenadas na cópia consultada. Inclui situações diversas: produzindo, fechado, abandonado etc. Não são 15.778 poços em produção.

**A execução pode aparecer como Parcial por uma inconsistência na própria fonte:** o cadastro 72100029800 aparece em sete poços com nomes distintos. Os sete foram preservados separadamente e a mensagem informa o motivo. Nessa cópia não faltam páginas: o total esperado é 15.778. Na ficha de cada um desses registros aparece a observação para conferência.

O escopo usa o atributo ESTADO informado pela ANP. Os cinco registros da PB são o resultado desse filtro nessa camada; não significam cinco produtores ativos nem cobertura de todo poço marinho que possa influenciar royalties paraibanos. Não foi atribuído município a nenhum poço por proximidade.

## Atualizar automaticamente na fonte

Depois da primeira carga, use **ANP — poços: atualização online** em Fontes e coletas. Essa opção consulta o serviço WFS oficial e pagina o conjunto. As novas tentativas de conexão e o andamento ficam visíveis.

O aplicativo valida todas as páginas antes de atualizar o cadastro. Se uma página falhar, os arquivos completos já recebidos ficam preservados e o cadastro anterior permanece. Uma cópia antiga não substitui automaticamente uma coleta mais nova; por isso a opção de primeira carga só funciona enquanto a tabela de poços estiver vazia.

Registros ausentes em uma atualização são mantidos com sua fonte anterior e a execução informa essa diferença. Sua ausência não é interpretada como encerramento do poço.

## Mapa e QGIS

Em **Poços e cartografia**, filtre UF, Terra/Mar, situação, nome, campo ou operador.

- **Abrir mapa:** desenha os registros filtrados e limites estaduais simplificados. Clique nos pontos para ver atributos e abrir a ficha.
- **Baixar mapa offline + dados QGIS:** gera um ZIP com mapa.html, GeoJSON dos poços, limites estaduais e os arquivos necessários ao mapa. Extraia todo o ZIP antes de abrir mapa.html.
- **GeoJSON:** baixa somente os pontos filtrados e os metadados de origem.

No QGIS, arraste **pocos_anp.geojson** e **limites_estaduais_ibge.geojson** para o projeto. As coordenadas dos poços foram solicitadas ao WFS em **EPSG:4326 / WGS84**, com ordem longitude, latitude. O campo de datum original da ANP é preservado separadamente. As malhas simplificadas do IBGE servem de contexto regional; não devem ser usadas como delimitação de precisão.

O mapa não consulta serviços externos de imagens de fundo, não precisa de chave de API e funciona sem internet após a carga. Não contém as linhas oficiais de confrontação marítima e não calcula municípios beneficiários ou valores de royalties.

## Produção mensal: onde baixar e onde colocar

1. No aplicativo, abra **Poços e cartografia → Importar produção mensal**.
2. Clique em **Consultar produção no CDP**.
3. No site oficial da ANP, selecione mês/ano e ambiente **Terra** ou **Mar**, preencha o CAPTCHA e clique em **Buscar**.
4. Clique em **Exportar p/ csv**; se houver menu Ações, escolha o download CSV.
5. Volte ao aplicativo, selecione esse arquivo e indique o mesmo ambiente consultado. Clique em **Importar e conferir CSV**.

**Não precisa depositar o CSV em uma pasta especial.** Pode ficar em Downloads. O aplicativo guarda a cópia original, a origem declarada e o SHA-256 automaticamente. Não abra e salve novamente no Excel antes de importar.

A ANP informa uma defasagem usual de dois meses para publicar produção. Escolha um mês efetivamente disponível. A interface atual exige CAPTCHA: essa etapa deve ser feita por você. Não foi implementado contorno dessa proteção.

O parser segue os metadados oficiais atualizados em 11/03/2026, com os cabeçalhos:

- Nome Poço ANP
- Estado
- Período
- Petróleo (bbl/dia)
- Gás Natural (Mm³/dia) Total

O CSV atual do seu CDP ainda precisa ser conferido em uso real. Os testes da importação usam exemplos com o leiaute documentado; não houve exportação por trás do CAPTCHA. Se o cabeçalho do arquivo recebido diferir, a importação interrompe, guarda o original e informa que o leiaute precisa de adaptação. Envie esse CSV para ajuste, sem transcrever números.

O programa aceita ponto ou vírgula decimal, guarda números com até oito casas decimais e não substitui campo vazio por zero. Preserva o rótulo de unidade do gás conforme a ANP, sem assumir conversão para metros cúbicos ou milhões de metros cúbicos. Os valores em bbl/dia são médias diárias referentes ao mês: não são volumes mensais e não devem ser somados como tal.

O vínculo usa nome ANP normalizado e UF, exigindo um único cadastro correspondente. Linhas sem correspondência única permanecem registradas na produção, com pendência de vínculo. A importação não muda a situação cadastral do poço.

**Pré-sal é subconjunto de Mar.** Não some essas duas exportações. A chave poço/UF/mês impede criar uma segunda produção para o mesmo período. Se uma importação de pré-sal divergir de valores já registrados, o lote é interrompido para revisão.

## O que ainda está pendente

- Validação do primeiro CSV de produção exportado por você no CDP atual.
- Camadas oficiais de linhas ortogonais/paralelas e confrontações marinhas, com metadados, edição, datum e critérios. **Não estão incluídas nesta entrega e não foram desenhadas por aproximação.**
- Participação especial.
- PNCP/CE: continua dependendo de resposta da API.

A camada do IBGE de municípios defrontantes com o mar foi localizada, mas ela não equivale às linhas de projeção marítima e não foi apresentada como substituta.

## Fontes e rastreabilidade

- GeoMapsANP: https://www.gov.br/anp/pt-br/assuntos/exploracao-e-producao-de-oleo-e-gas/dados-tecnicos/geomapsanp
- Serviço geográfico ANP: https://gishub.anp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetCapabilities
- Camada consultada: BD_ANP:POCOS_SIRGAS. Filtro ESTADO IN ('PB','RN','CE','SE','AL'). GeoJSON em EPSG:4326, ordenado por OGR_FID, páginas de 5.000.
- Produção: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/producao-de-petroleo-e-gas-natural-por-poco
- Metadados CSV: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-producao-de-petroleo-e-gas-natural-por-poco/metadados-dados-producao-poco.pdf
- CDP: https://cdp.anp.gov.br/ords/r/cdp_apex/consulta-dados-publicos-cdp/consulta-produ%C3%A7%C3%A3o-por-po%C3%A7o
- Malhas estaduais: API IBGE v3 /malhas/estados/{codigo}, formato GeoJSON, qualidade mínima, códigos 21 a 29 para contexto do Nordeste. URLs completas nos metadados de pocos_ufs.geojson.
- Municípios defrontantes: https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/municipios_defrontantes_com_o_mar/2024/

## Verificações realizadas

28 testes automatizados: autenticação, CSRF, importação, precisão decimal, unidades reconhecidas, coordenadas, paginação incompleta, cadastros repetidos, proteção da base mais recente, pré-sal e preservação dos fluxos existentes.

A base real com 15.778 registros foi importada e reimportada em banco separado, sem duplicatas. A migração preservou organização e contato pré-existentes de teste, e o backup anterior à migração foi criado. O Windows real do usuário ainda deve executar a atualização; o ambiente de desenvolvimento é Linux.

As telas foram conferidas no Chromium. O mapa do aplicativo e o mapa offline abriram os 15.778 pontos sem erros de JavaScript.
