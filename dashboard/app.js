/* Public poster aggregates and independently generated fictional labs. */
'use strict';
const $ = id => document.getElementById(id);
const SCENARIOS = ['RCP 2.6','RCP 4.5','RCP 8.5'];
const COLORS = ['#087e8b','#b26b00','#cb4260'];
const YEARS = Array.from({length:9},(_,i)=>2020+i*10);
const state = {scenario:'RCP 2.6',view:'map',dataset:'poster',timer:null};
let facilities=[], exposure=[], poster=[], land=[], lookup=new Map(), selected=[];
const sum = (rows,key) => rows.reduce((a,r)=>a+Number(r[key]),0);
const fmt = n => Number(n).toLocaleString('en-US');
const config = {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d']};
const base = {font:{family:'system-ui, sans-serif',color:'#123341'},paper_bgcolor:'#fff',plot_bgcolor:'#fff',margin:{l:55,r:24,t:44,b:48},legend:{orientation:'h',y:1.2},hovermode:'closest'};
function options(id,values,value='All') {
  const e=$(id); e.replaceChildren(...['All',...new Set(values)].map(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;return o;}));
  e.value=[...e.options].some(o=>o.value===value)?value:'All';
}
function current() {return {year:+$('year').value,threshold:+$('threshold').value/100,country:$('country').value,city:$('city').value,scope:$('scope').value};}
function syncFilters(reset=false) {
  const demo=state.dataset==='synthetic', c=current();
  const choices=demo?facilities:poster.filter(r=>r.scope==='city'&&r.year===2030&&r.scenario==='RCP 2.6');
  options('country',choices.map(r=>r.country).sort(),reset?'All':c.country);
  options('city',choices.filter(r=>$('country').value==='All'||r.country===$('country').value).map(r=>r.city).sort(),reset?'All':c.city);
  ['serviceLabel','supportLabel','thresholdLabel'].forEach(id=>$(id).hidden=!demo);
  $('scopeLabel').hidden=demo;
  $('country').disabled=$('city').disabled=!demo&&c.scope==='portfolio';
  if(!demo&&c.scope==='portfolio'){$('country').value='All';$('city').value='All';}
  $('year').min=demo?2020:2030;
  if(+$('year').value<+$('year').min)$('year').value=$('year').min;
  $('notice').className=demo?'notice demo':'notice';
  $('notice').textContent=demo?'FICTIONAL LAB · All facility locations, support flags, service loads and probabilities are invented for teaching. These are not real PEPFAR facilities or Climate Central projections.':'PUBLISHED EVIDENCE · Counts transcribed from Tables 1–3 of Tobias et al. (AIDS 2024). Map pins mark approximate city locations, never facilities. City, district and whole-portfolio rows are separate reporting units.';
  $('filterHint').textContent=demo?'Cards count each fictional facility once at the selected scenario and year. The threshold changes the exposure classification, not the denominator.':c.scope==='portfolio'?'Whole-portfolio totals include locations outside the five mapped cities. Choose Published cities or Published districts to activate geographic filters.':'These five published city groups are a subset of the portfolio. District boundaries are not supplied, and city/district overlap is unspecified; never sum both scopes.';
}
function cohort() {
  const c=current();
  return facilities.filter(f=>(c.country==='All'||f.country===c.country)&&(c.city==='All'||f.city===c.city)&&($('service').value==='All'||f.service_type===$('service').value)&&(!$('supported').checked||f.pepfar_demo===1));
}
function posterRows(s=state.scenario,y=current().year,scope=current().scope) {
  const c=current();
  return poster.filter(r=>r.scenario===s&&r.year===y&&r.scope===scope&&(scope==='portfolio'||((c.country==='All'||r.country===c.country)&&(c.city==='All'||r.city===c.city))));
}
function demoRows(s=state.scenario,y=current().year) {
  return cohort().map(f=>({...f,...lookup.get(`${f.facility_id}|${s}|${y}`)}));
}
function mappedRows(s=state.scenario,y=current().year) {
  return state.dataset==='synthetic'?demoRows(s,y):posterRows(s,y,current().scope==='portfolio'?'city':current().scope);
}
function landTrace() {
  let x=[],y=[];
  land.forEach(f=>{const polys=f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[f.geometry.coordinates];polys.forEach(p=>p.forEach(ring=>{ring.forEach(p=>{x.push(p[0]);y.push(p[1]);});x.push(null);y.push(null);}));});
  return {type:'scatter',x,y,mode:'lines',line:{color:'#9aafb4',width:.7},fill:'toself',fillcolor:'#ecf1ef',hoverinfo:'skip',showlegend:false};
}
function geographyLayout(rows) {
  let xs=rows.map(r=>r.longitude),ys=rows.map(r=>r.latitude),xr=[-20,120],yr=[-35,32];
  if(rows.length&&(state.dataset==='synthetic'||current().scope!=='portfolio')){
    const dx=Math.max(1,Math.max(...xs)-Math.min(...xs)),dy=Math.max(1,Math.max(...ys)-Math.min(...ys));
    xr=[Math.min(...xs)-dx*.12,Math.max(...xs)+dx*.12];yr=[Math.min(...ys)-dy*.15,Math.max(...ys)+dy*.15];
  }
  if(state.dataset==='synthetic'&&current().city!=='All'&&rows.length){xr=[Math.min(...xs)-.04,Math.max(...xs)+.04];yr=[Math.min(...ys)-.04,Math.max(...ys)+.04];}
  return {...base,xaxis:{title:{text:'Longitude (°E)'},range:xr,gridcolor:'#e6eff2',constrain:'domain'},yaxis:{title:{text:'Latitude (°N)'},range:yr,gridcolor:'#e6eff2',scaleanchor:'x',scaleratio:1,constrain:'domain'},plot_bgcolor:'#eaf4f8'};
}
function metrics() {
  const demo=state.dataset==='synthetic',c=current();selected=demo?demoRows():posterRows();
  const total=demo?selected.length:sum(selected,'facilities_2023');
  const atRisk=demo?selected.filter(r=>r.annual_probability>=c.threshold):selected;
  const exposed=demo?atRisk.length:sum(atRisk,'potentially_flooded');
  $('label1').textContent=demo?'Fictional facilities':c.scope==='portfolio'?'Facilities in portfolio (2023)':'Facilities in selected published rows';
  $('label2').textContent=demo?'At or above threshold':'Potentially flooded facilities';
  $('label3').textContent=total?'Share of denominator':'No matching rows';
  $('label4').textContent=demo?'Hypothetical annual service load at exposed sites':'Projection year';
  $('card1').textContent=fmt(total);$('card2').textContent=fmt(exposed);$('card3').textContent=total?(100*exposed/total).toFixed(2)+'%':'—';
  $('card4').textContent=demo?fmt(sum(atRisk,'service_load')):c.year;
  $('yearOut').textContent=c.year;$('thresholdOut').textContent=(c.threshold*100).toFixed(0)+'%';
  document.querySelectorAll('[data-scenario]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.scenario===state.scenario)));
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===state.view)));
}
function mapPlot() {
  const rows=mappedRows(), demo=state.dataset==='synthetic', c=current();
  const values=rows.map(r=>demo?r.annual_probability:r.percent/100);
  const text=rows.map(r=>demo?`${r.facility_id}<br>${r.city}<br>Invented annual probability: ${(100*r.annual_probability).toFixed(1)}%`:`${r.city} (${r.scope})<br>${r.potentially_flooded} / ${r.facilities_2023} potentially flooded`);
  let traces,layout={...base};
  if(state.view==='map') {
    traces=[landTrace(),{type:'scatter',mode:'markers',x:rows.map(r=>r.longitude),y:rows.map(r=>r.latitude),text,hovertemplate:'%{text}<extra></extra>',name:demo?'Fictional facilities':'Published city groups',showlegend:false,
      marker:{color:values,cmin:0,cmax:1,colorscale:[[0,'#4c8993'],[.1,'#edb54a'],[.5,'#e17544'],[1,'#b72951']],size:demo?9:rows.map(r=>12+Math.sqrt(r.potentially_flooded)*3),line:{color:'#fff',width:1},colorbar:{title:{text:demo?'Annual p':'Share'},tickformat:'.0%'}}}];
    layout={...geographyLayout(rows),title:{text:`${state.scenario} · ${c.year} · ${demo?'fictional sites':'public city summaries'}`,font:{size:16}}};
  } else if(state.view==='cube') {
    const years=demo?YEARS:YEARS.slice(1),points=years.flatMap(y=>mappedRows(state.scenario,y));
    traces=[{type:'scatter3d',mode:'markers',x:points.map(r=>r.longitude),y:points.map(r=>r.latitude),z:points.map(r=>r.year),
      text:points.map(r=>`${r.city} · ${r.year}<br>${demo?r.facility_id:'Published '+r.scope}`),hovertemplate:'%{text}<extra></extra>',
      marker:{size:demo?3:6,color:points.map(r=>demo?r.annual_probability:r.percent/100),cmin:0,cmax:1,colorscale:'YlOrRd',opacity:.75,colorbar:{title:{text:demo?'Annual p':'Share'},tickformat:'.0%'}}}];
    layout={...base,title:{text:'Space–time cube · height is year, not elevation',font:{size:16}},scene:{xaxis:{title:{text:'Longitude'}},yaxis:{title:{text:'Latitude'}},zaxis:{title:{text:'Year'},range:[2020,2100]},aspectmode:'cube'}};
  } else if(state.view==='bars') {
    traces=[];
    rows.forEach((r,i)=>traces.push({type:'scatter3d',mode:'lines+markers',x:[r.longitude,r.longitude],y:[r.latitude,r.latitude],z:[0,100*values[i]],line:{color:COLORS[SCENARIOS.indexOf(state.scenario)],width:7},marker:{size:3},text:[text[i],text[i]],hovertemplate:'%{text}<extra></extra>',showlegend:false}));
    layout={...base,title:{text:'3D geographic stems · height is a percentage',font:{size:16}},scene:{xaxis:{title:{text:'Longitude'}},yaxis:{title:{text:'Latitude'}},zaxis:{title:{text:demo?'Annual probability (%)':'Potentially flooded (%)'},range:[0,100]},aspectmode:'cube'}};
  } else {
    const a=Array.from({length:41},(_,i)=>i/10), z=a.map(y=>a.map(x=>.15+.48*x+.16*Math.sin(2*x+y)+.08*Math.cos(3*y))),t=(c.year-2020)/80;
    const end={'RCP 2.6':.45,'RCP 4.5':.65,'RCP 8.5':1}[state.scenario],water=.7+.2*t+(end-.2)*t*t;
    traces=[{type:'surface',x:a,y:a,z,colorscale:'Earth',showscale:false,name:'Fictional terrain',hovertemplate:'x %{x} km<br>y %{y} km<br>Height %{z:.2f} m<extra></extra>'},
      {type:'surface',x:a,y:a,z:a.map(()=>a.map(()=>water)),colorscale:[[0,'#209bd1'],[1,'#209bd1']],opacity:.6,showscale:false,name:'Water plane',hovertemplate:`Illustrative water level: ${water.toFixed(2)} m<extra></extra>`}];
    layout={...base,title:{text:'Fictional coast · water plane and terrain (not a flood model)',font:{size:15}},scene:{xaxis:{title:{text:'x (km)'}},yaxis:{title:{text:'y (km)'}},zaxis:{title:{text:'Toy elevation (m)'}},aspectratio:{x:1,y:1,z:.6}}};
  }
  if(!rows.length&&state.view!=='terrain')layout.annotations=[{text:'No matching rows. Reset a filter to continue.',showarrow:false,xref:'paper',yref:'paper',x:.5,y:.5}];
  Plotly.react('visual',traces,layout,config).catch(showError);
  $('mapCaption').textContent=state.view==='terrain'?'This independent, invented 4 × 4 km scene illustrates a water-level threshold. It does not use the selected facilities or represent their terrain. Connectivity, drainage, waves and defences are omitted. Axes have different units and vertical exaggeration.':state.view==='cube'?'Each horizontal time slice shows the same locations in one decade. The vertical axis is time; these points are not a topographic surface. Colours retain the same 0–100% scale.':demo?'Fictional coordinates around approximate city anchors. Small-scale Natural Earth land outlines are context only and may be too coarse at city zoom. Marker colour is annual probability, not observed flooding.':'Only the five city groups published in the poster are mapped. Symbol area is proportional to neither land area nor population. Coordinates are approximate city anchors, not facility locations or district centroids. The 1:110m land layer cannot resolve local flooding.';
}
function otherPlots() {
  const demo=state.dataset==='synthetic',c=current(),years=demo?YEARS:YEARS.slice(1);
  const traces=SCENARIOS.map((s,i)=>({type:'scatter',mode:'lines+markers',name:s,x:years,y:years.map(y=>demo?demoRows(s,y).filter(r=>r.annual_probability>=c.threshold).length:sum(posterRows(s,y),'potentially_flooded')),line:{color:COLORS[i],width:3}}));
  Plotly.react('series',traces,{...base,margin:{l:55,r:24,t:85,b:48},legend:{orientation:'h',y:1.18,x:0},title:{text:demo?'Fictional facilities above threshold':'Published potentially flooded facilities',font:{size:14}},xaxis:{title:{text:'Year'},dtick:20},yaxis:{title:{text:'Facilities'},rangemode:'tozero'},shapes:[{type:'line',x0:c.year,x1:c.year,y0:0,y1:1,yref:'paper',line:{dash:'dot',color:'#617981'}}]},config).catch(showError);
  const rows=mappedRows(),group=new Map();
  rows.forEach(r=>{const g=group.get(r.city)||{n:0,total:0};g.n+=demo?Number(r.annual_probability>=c.threshold):r.potentially_flooded;g.total+=demo?1:r.facilities_2023;group.set(r.city,g);});
  const entries=[...group.entries()].sort((a,b)=>b[1].n-a[1].n);
  Plotly.react('composition',[{type:'bar',x:entries.map(e=>e[0]),y:entries.map(e=>e[1].n),marker:{color:COLORS[SCENARIOS.indexOf(state.scenario)]},customdata:entries.map(e=>e[1].total),hovertemplate:'%{x}<br>%{y} / %{customdata} facilities<extra></extra>'}],{...base,title:{text:'By city · selected decade',font:{size:14}},xaxis:{automargin:true},yaxis:{title:{text:'Facilities'},rangemode:'tozero'}},config).catch(showError);
  $('barCaption').textContent=!demo&&c.scope==='portfolio'?'The five published city rows shown here do not sum to the whole portfolio.':'Counts are within the selected scope. A large count does not necessarily imply a large percentage.';
}
function listing() {
  const demo=state.dataset==='synthetic',q=$('search').value.toLowerCase();
  const rows=selected.filter(r=>Object.values(r).some(v=>String(v).toLowerCase().includes(q)));
  const cols=demo?[['facility_id','Fictional ID'],['country','Country'],['city','City'],['service_type','Service'],['annual_probability','Annual p (%)'],['elevation_m','Toy elevation (m)'],['service_load','Hypothetical annual visits']]:[['country','Country'],['city','Reporting group'],['scope','Scope'],['facilities_2023','2023 denominator'],['potentially_flooded','Potentially flooded'],['percent','Share (%)']];
  const head=document.createElement('tr');cols.forEach(([k,t])=>{const th=document.createElement('th');th.scope='col';th.textContent=t;head.append(th);});$('listing').tHead.replaceChildren(head);
  const body=rows.map(r=>{const tr=document.createElement('tr');cols.forEach(([k])=>{const td=document.createElement('td');td.textContent=k==='annual_probability'?(100*r[k]).toFixed(2):k==='percent'?Number(r[k]).toFixed(2):r[k];tr.append(td);});return tr;});$('listing').tBodies[0].replaceChildren(...body);
  $('tableTitle').textContent=demo?'Fictional facility line listing':'Published aggregate line listing';$('tableCount').textContent=`${rows.length} of ${selected.length} selected rows shown · ${state.scenario} · ${current().year}`;
}
function render() {metrics();mapPlot();otherPlots();listing();window.coastDashboard={state:{...state,timer:null},cards:{total:$('card1').textContent,exposed:$('card2').textContent},rowCount:selected.length};}
function stop() {if(state.timer)clearInterval(state.timer);state.timer=null;$('play').textContent='▶ Play decades';}
function showError(e) {stop();$('notice').textContent='Unable to load or draw the dashboard. Serve this site over HTTP, refresh, and check the network connection. '+e.message;$('notice').className='notice demo';console.error(e);}
async function init() {
  try {
    const urls=['../data/dashboard-data.json','../data/poster-aggregates.json','../data/natural-earth-land.geojson'];
    const [demo,pub,geo]=await Promise.all(urls.map(async u=>{const r=await fetch(u);if(!r.ok)throw new Error(`${u}: HTTP ${r.status}`);return r.json();}));
    facilities=demo.facilities;exposure=demo.exposure;poster=pub;land=geo.features;
    exposure.forEach(r=>lookup.set(`${r.facility_id}|${r.scenario}|${r.year}`,r));
    const params=new URLSearchParams(location.search);
    if(SCENARIOS.includes(params.get('scenario')))state.scenario=params.get('scenario');
    if(['map','bars','cube','terrain'].includes(params.get('view')))state.view=params.get('view');
    if(params.get('dataset')==='synthetic'||state.view==='terrain')state.dataset='synthetic';
    $('dataset').value=state.dataset;syncFilters(true);
    document.querySelectorAll('[data-scenario]').forEach(b=>b.addEventListener('click',()=>{state.scenario=b.dataset.scenario;render();}));
    document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{state.view=b.dataset.view;if(state.view==='terrain'){state.dataset='synthetic';$('dataset').value='synthetic';syncFilters(true);}render();}));
    $('dataset').addEventListener('change',()=>{stop();state.dataset=$('dataset').value;if(state.dataset==='poster'&&state.view==='terrain')state.view='map';syncFilters(true);render();});
    ['country','city','scope','service','supported'].forEach(id=>$(id).addEventListener('change',()=>{if(id==='country')$('city').value='All';syncFilters();render();}));
    ['year','threshold'].forEach(id=>$(id).addEventListener('input',render));$('search').addEventListener('input',listing);
    $('reset').addEventListener('click',()=>{stop();$('scope').value='portfolio';$('service').value='All';$('supported').checked=false;$('year').value=2030;$('threshold').value=10;$('search').value='';state.scenario='RCP 2.6';state.view='map';syncFilters(true);render();});
    $('play').addEventListener('click',()=>{if(state.timer){stop();return;}$('play').textContent='❚❚ Pause';state.timer=setInterval(()=>{const y=+$('year').value;$('year').value=y>=2100?$('year').min:y+10;render();},1400);});
    $('download').addEventListener('click',()=>{const rows=selected.map(r=>({...r,evidence_layer:state.dataset,scenario:state.scenario,year:current().year}));if(!rows.length)return;const keys=Object.keys(rows[0]),quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';const csv=[keys.map(quote).join(','),...rows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`coastal-${state.dataset}-${state.scenario.replace(' ','-')}-${current().year}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
    render();
    // Grid breakpoints settle after the window resize event; observe plot containers too.
    const resizeObserver=new ResizeObserver(()=>requestAnimationFrame(()=>{
      ['visual','series','composition'].forEach(id=>{if($(id).data)Plotly.Plots.resize($(id));});
    }));
    ['visual','series','composition'].forEach(id=>resizeObserver.observe($(id)));
  }catch(e){showError(e);}
}
init();
