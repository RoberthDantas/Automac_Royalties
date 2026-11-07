"""Opcional, para auditoria técnica. Requer pyshp e pyproj; não usado na execução do aplicativo.
Recria apenas a conversão de formato/visualização, sem gerar novos traçados.
"""
from pathlib import Path
import json,hashlib,zipfile,tempfile
import shapefile
from pyproj import Transformer
root=Path(__file__).resolve().parents[1]
source=root/'referencias/planejamento_20260921/LBR_corrigida_Brasil.zip'
features=[];tr=Transformer.from_crs(4674,4326,always_xy=True)
with tempfile.TemporaryDirectory() as tmp:
    with zipfile.ZipFile(source) as z:
        for suffix in ['shp','shx','dbf','prj','cpg']:
            name='LBR_corrigida_Brasil.'+suffix
            (Path(tmp)/name).write_bytes(z.read(name))
    reader=shapefile.Reader(str(Path(tmp)/'LBR_corrigida_Brasil.shp'),encoding='utf-8')
    for sr in reader.iterShapeRecords():
        p=sr.record.as_dict()
        p.update(fonte='Arquivo LBR_corrigida_Brasil.zip fornecido pelo usuário',src_original='EPSG:4674 / SIRGAS 2000',src_visualizacao='EPSG:4326',validacao='Origem, autoria, data e condição oficial não comprovadas; uso interno',arquivo_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        features.append({'type':'Feature','id':str(p['ORDEM']),'properties':p,'geometry':{'type':'LineString','coordinates':[list(tr.transform(x,y)) for x,y in sr.shape.points]}})
(root/'staticfiles/linhas_lbr.geojson').write_text(json.dumps({'type':'FeatureCollection','name':'LBR fornecida — linhas de referência internas','features':features},ensure_ascii=False),encoding='utf-8')
print(len(features),'linhas convertidas. Nenhum traçado novo gerado.')
