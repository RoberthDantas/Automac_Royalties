import json,gzip,urllib.request,hashlib,concurrent.futures,datetime
from shapely.geometry import shape, mapping
from shapely.validation import make_valid, explain_validity
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; raw=ROOT/'referencias/cartografia_20260921'; raw.mkdir(parents=True,exist_ok=True)
STATES={'PB':25,'RN':24,'CE':23,'SE':28,'AL':27}
def get(url,path):
 if path.exists():return json.loads(path.read_text())
 with urllib.request.urlopen(url,timeout=45) as r:data=r.read()
 if data.startswith(b'\x1f\x8b'):data=gzip.decompress(data)
 obj=json.loads(data);path.write_bytes(data);return obj
def fetch(item):
 uf,code=item
 catalog_url=f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{code}/municipios'
 geom_url=f'https://servicodados.ibge.gov.br/api/v3/malhas/estados/{code}?formato=application/vnd.geo+json&qualidade=intermediaria&intrarregiao=municipio'
 cat=get(catalog_url,raw/f'{uf}_cadastro.json');geo=get(geom_url,raw/f'{uf}_malha.geojson');lookup={str(x['id']):x['nome'] for x in cat}
 codes=[str(f['properties']['codarea']) for f in geo['features']]
 assert len(codes)==len(set(codes)) and set(codes)==set(lookup),(uf,len(codes),len(lookup))
 for f in geo['features']:
  c=str(f['properties']['codarea']);f['id']=c;f['properties'].update(codigo_ibge=c,nome=lookup[c],uf=uf,fonte=geom_url,consulta='2026-09-21',precisao='Malha simplificada para visualização; período não informado na resposta.')
 for f in geo['features']:
  g=shape(f['geometry'])
  if not g.is_valid:
   issue=explain_validity(g);fixed=make_valid(g)
   assert fixed.is_valid and fixed.geom_type in ('Polygon','MultiPolygon')
   f['geometry']=mapping(fixed)
   f['properties']['ajuste_topologico']='Cópia de visualização: shapely.make_valid; fonte original preservada. '+issue
 print(uf,len(codes),flush=True)
 return geo['features'],[{'code':c,'name':n,'uf':uf,'source_url':catalog_url} for c,n in lookup.items()],{'uf':uf,'municipios':len(cat),'catalogo':catalog_url,'malha':geom_url,'sha256_malha':hashlib.sha256((raw/f'{uf}_malha.geojson').read_bytes()).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:results=list(e.map(fetch,STATES.items()))
features=[];catalog=[];sources=[]
for f,c,s in results:features.extend(f);catalog.extend(c);sources.append(s)
(ROOT/'staticfiles/municipios_ibge.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False),encoding='utf-8')
(raw/'municipios.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf-8')
(raw/'fontes.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
