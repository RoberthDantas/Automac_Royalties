/* Local map using Leaflet 1.9.4; no external tiles or requests. */
window.drawWellMap=function(data,outlines,localLinks){
 const map=L.map('well-map',{preferCanvas:true}).setView([-7,-37],6);
 L.control.scale({imperial:false}).addTo(map);
 const names={'21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA'};
 const base=L.geoJSON(outlines,{style:{color:'#758992',weight:1,fillColor:'#f6f4ed',fillOpacity:1},onEachFeature:(f,l)=>{const name=names[f.properties.codarea];if(name)l.bindTooltip(name,{permanent:true,direction:'center',className:'state-label'})}}).addTo(map);
 map.createPane('wellPoints');map.getPane('wellPoints').style.zIndex=430;
 const renderer=L.canvas({padding:.4,pane:'wellPoints'});
 const wells=L.geoJSON(data,{pointToLayer:(f,ll)=>L.circleMarker(ll,{renderer:renderer,radius:3,weight:.5,color:f.properties.ambiente==='Mar'?'#126b9a':'#9a5418',fillOpacity:.85}),onEachFeature:(f,l)=>{
   l.bindPopup(()=>{const box=document.createElement('div');for(const [label,value] of [['Poço',f.properties.poco],['Cadastro ANP',f.properties.cadastro],['UF',f.properties.uf],['Ambiente',f.properties.ambiente],['Situação',f.properties.situacao],['Campo',f.properties.campo],['Operador',f.properties.operador]]){const p=document.createElement('p');p.style.margin='4px 0';p.textContent=label+': '+(value||'Não informado');box.appendChild(p)}if(localLinks){const a=document.createElement('a');a.href='/pocos/'+encodeURIComponent(f.id)+'/';a.textContent='Abrir ficha e produção';box.appendChild(a)}return box;});
 }}).addTo(map);
 if(wells.getBounds().isValid())map.fitBounds(wells.getBounds().pad(.12),{maxZoom:14});else if(base.getBounds().isValid())map.fitBounds(base.getBounds());
 const valid=data.features.filter(f=>f.geometry).length;
 document.getElementById('map-status').textContent=valid.toLocaleString('pt-BR')+' pontos no mapa · '+(data.features.length-valid)+' sem coordenadas';
 map.attributionControl.addAttribution('Poços: ANP · Limites simplificados: IBGE');
 return map;
};
