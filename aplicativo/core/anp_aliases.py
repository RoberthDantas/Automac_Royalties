"""Correspondências explícitas ANP → cadastro municipal IBGE.

Nomes e códigos de destino conferidos nas APIs estaduais do IBGE em
18/09/2026. Cada alias só é aceito se UF, nome atual e código coincidirem
com o cadastro IBGE carregado. Não usa aproximação textual.
"""

# (UF, denominação normalizada ANP): (código IBGE, nome atual)
ANP_ALIASES = {
    ('CE', 'itapage'): ('2306306', 'Itapajé'),
    ('PB', 'campo de santana'): ('2516409', 'Tacima'),
    ('PB', 'iguaracy'): ('2502607', 'Igaracy'),
    ('PB', 'santarem'): ('2513653', 'Joca Claudino'),
    ('PB', 'sao domingos de pombal'): ('2513968', 'São Domingos'),
    ('PB', 'serido'): ('2515401', 'São Vicente do Seridó'),
    ('RN', 'acu'): ('2400208', 'Assú'),
    ('RN', 'ares'): ('2401206', 'Arez'),
    ('RN', 'augusto severo'): ('2401305', 'Campo Grande'),
    ('RN', 'presidente juscelino'): ('2410306', 'Serra Caiada'),
    ('RN', 'sao miguel de touros'): ('2412559', 'São Miguel do Gostoso'),
    ('SE', 'amparo de sao francisco'): ('2800100', 'Amparo do São Francisco'),
    ('SE', 'gracho cardoso'): ('2802601', 'Graccho Cardoso'),
}
