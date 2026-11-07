/* Internal territorial layers. Selectors focus the map; they never assign royalties or wells to municipalities. */
window.addTerritoryLayers=function(map,municipalities,lines,localLinks){
 const escText=(items)=>{const box=document.createElement('div');items.forEach(([k,v])=>{const p=document.createElement('p');p.style.margin='4px 0';p.textContent=k+': '+(v??'Não informado');box.appendChild(p)});return box;};
 map.createPane('municipal');map.getPane('municipal').style.zIndex=410;
 map.createPane('referenceLines');map.getPane('referenceLines').style.zIndex=420;
 const byMunicipality=new Map(),byLine=new Map();
 const municipal=L.geoJSON(municipalities,{pane:'municipal',style:{color:'#718b86',weight:1,fillOpacity:0.025},onEachFeature:(f,l)=>{
  byMunicipality.set(f.properties.codigo_ibge,l);
  l.bindTooltip(f.properties.nome+' / '+f.properties.uf);
  l.bindPopup(()=>{const box=escText([['Município',f.properties.nome],['UF',f.properties.uf],['IBGE',f.properties.codigo_ibge],['Base','IBGE simplificada; uso regional']]);if(localLinks){const a=document.createElement('a');a.textContent='Abrir ficha do município';a.href='/municipios/'+encodeURIComponent(f.properties.codigo_ibge)+'/';box.appendChild(a)}return box;});
 }}).addTo(map);
 const reference=L.geoJSON(lines,{pane:'referenceLines',style:{color:'#9642a0',weight:1.7,opacity:0.8},onEachFeature:(f,l)=>{
  byLine.set(String(f.id),l);l.bindTooltip(f.properties.NOME);
  l.bindPopup(()=>escText([['Linha',f.properties.NOME],['Ordem',f.properties.ORDEM],['Tipo',f.properties.TIPO],['Latitude de origem',f.properties.LAT_ORIG],['Longitude de origem',f.properties.LON_ORIG],['Azimute original',f.properties.AZ_ORIG],['Azimute mar',f.properties.AZ_MAR],['Validação','Camada fornecida pelo usuário; condição oficial não comprovada']]));
 }}).addTo(map);
 L.control.layers(null,{'Municípios IBGE (simplificados)':municipal,'Linhas LBR fornecidas (uso interno)':reference},{collapsed:false}).addTo(map);
 const uf=document.getElementById('map-uf'),mun=document.getElementById('map-municipality'),line=document.getElementById('map-line');
 const add=(s,value,label)=>{const o=document.createElement('option');o.value=value;o.textContent=label;s.appendChild(o)};
 const all=municipalities.features.slice().sort((a,b)=>a.properties.nome.localeCompare(b.properties.nome,'pt-BR'));
 const params=localLinks?new URLSearchParams(location.search):new URLSearchParams();
 const selected=params.get('municipio')||'';
 for(const state of ['PB','RN','CE','SE','AL'])add(uf,state,state);
 const first=all.find(f=>f.properties.codigo_ibge===selected);
 uf.value=first?first.properties.uf:(params.get('uf')||'');
 function filter(){mun.replaceChildren();add(mun,'','Escolher município (aproximar)');all.filter(f=>!uf.value||f.properties.uf===uf.value).forEach(f=>add(mun,f.properties.codigo_ibge,f.properties.nome+' / '+f.properties.uf));}
 function focusMunicipality(){municipal.resetStyle();const l=byMunicipality.get(mun.value);if(l){municipal.addTo(map);l.setStyle({color:'#126b69',weight:3,fillOpacity:.14});map.fitBounds(l.getBounds().pad(.15));l.openPopup()}}
 filter();if(selected){mun.value=selected;focusMunicipality()}
 uf.addEventListener('change',()=>{filter();municipal.resetStyle();const subset=all.filter(f=>!uf.value||f.properties.uf===uf.value);const b=L.geoJSON({type:'FeatureCollection',features:subset}).getBounds();if(b.isValid())map.fitBounds(b.pad(.06));});
 mun.addEventListener('change',focusMunicipality);
 lines.features.forEach(f=>add(line,String(f.id),f.properties.ORDEM+' · '+f.properties.NOME));
 line.addEventListener('change',()=>{reference.resetStyle();const l=byLine.get(line.value);if(l){reference.addTo(map);l.setStyle({weight:4,color:'#ad2c55'});map.fitBounds(l.getBounds().pad(.15));l.openPopup()}});
 map.attributionControl.addAttribution('Municípios: IBGE · Linhas: arquivo fornecido, validação pendente');
 document.getElementById('territory-status').textContent=municipalities.features.length+' municípios · '+lines.features.length+' linhas. Seletores aproximam o mapa; não filtram nem vinculam os poços.';
 return {municipal,reference};
};
