const API='';
let lastPhase='', feedItems=[], pollTimer, lastSources=[];

// === CAPABILITIES (Vorschlag 9): Endpunkt-Sichtbarkeit aus EINER Quelle ===
// Das UI fragt GET /api/capabilities einmal beim Boot. Endpunkte mit
// "live only" werden hier lokal abgeschirmt, statt Poll-404-Zyklen zu
// fahren. Fehlt das Manifest, bleibt das alte Verhalten (Degradierung).
let dashCaps=null;
(async()=>{try{const c=await fetch(API+'/api/capabilities');if(c.ok)dashCaps=await c.json();}catch(e){}})();
function liveOnly(path){
  return !!dashCaps && Array.isArray(dashCaps.live_only)
         && dashCaps.live_only.includes(path);
}

// === THEME (hell/dunkel): gespeicherte Wahl > Systemvorgabe > dunkel ===
(function(){
  const stored=localStorage.getItem('dash-theme');
  const prefersLight=window.matchMedia&&window.matchMedia('(prefers-color-scheme: light)').matches;
  const start=(stored==='light'||stored==='dark')?stored:(prefersLight?'light':'dark');
  document.documentElement.setAttribute('data-theme',start);
  const btn=document.getElementById('themeToggle');
  if(btn){
    btn.textContent=start==='light'?'☀':'☽';
    btn.addEventListener('click',()=>{
      const cur=document.documentElement.getAttribute('data-theme')==='light'?'light':'dark';
      const next=cur==='light'?'dark':'light';
      document.documentElement.setAttribute('data-theme',next);
      localStorage.setItem('dash-theme',next);
      btn.textContent=next==='light'?'☀':'☽';
    });
  }
})();

// === TABS ===
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('tp-'+t.dataset.tab).classList.add('active');
    // Draw the graph right away instead of waiting for the next poll tick
    if(t.dataset.tab==='graph'&&typeof pollGraph==='function')pollGraph(true);
    if(t.dataset.tab==='coverage'&&typeof pollCoverage==='function')pollCoverage();
    if(t.dataset.tab==='meta'&&typeof pollMeta==='function')pollMeta();
  });
});

// === CLOCK ===
setInterval(()=>{
  document.getElementById('clock').textContent=new Date().toLocaleTimeString();
},1000);

// === FEED ===
function addFeed(type, text){
  feedItems.unshift({type, text, time: new Date()});
  if(feedItems.length>50)feedItems.pop();
  renderFeed();
}
function renderFeed(){
  const el=document.getElementById('feed');
  if(!feedItems.length){el.innerHTML='<div class="empty">No activity yet</div>';return}
  el.innerHTML=feedItems.map(f=>`<div class="feed-item"><div class="feed-dot fd-${f.type}"></div><div><span style="color:var(--t3);font-size:10px;font-variant-numeric:tabular-nums">${f.time.toLocaleTimeString()}</span> ${esc(f.text)}</div></div>`).join('');
  document.getElementById('feedCnt').textContent=feedItems.length;
}

// === SOURCES FILTER ===
function renderSources(){
  const srcs=lastSources||[];
  const term=(document.getElementById('srcSearch')?.value||'').toLowerCase().trim();
  let filtered=srcs;
  if(term){
    filtered=srcs.filter(s=>{
      const hay=((s.title||'')+' '+(s.url||'')+' '+(s.source_type||'')+' '+(s.summary||'')).toLowerCase();
      return hay.includes(term);
    });
  }
  document.getElementById('srcCnt').textContent=srcs.length;
  const cntEl=document.getElementById('srcFilterCnt');
  if(term&&filtered.length<srcs.length){
    cntEl.textContent=filtered.length+' of '+srcs.length;
  }else{
    cntEl.textContent='';
  }
  document.getElementById('srcList').innerHTML=filtered.length?filtered.map(s=>`
    <div class="item">
      <div class="item-top">
        <span class="tag t-${s.source_type==='arxiv'?'plausible':s.source_type==='pubmed'?'supported':'proposed'}">${s.source_type}</span>
        <span style="font-size:11px;color:var(--t3)">Cred: ${(s.credibility||0).toFixed(1)}</span>
      </div>
      <div class="item-title" style="margin-top:4px"><a href="${esc(s.url)}" target="_blank">${esc(s.title||'Untitled')}</a></div>
      <div class="item-meta">${esc(truncate(s.summary,150))}</div>
    </div>
  `).join(''):'<div class="empty">'+(term?'No sources match "'+esc(term)+'"':'No sources yet')+'</div>';
}

document.getElementById('srcSearch').addEventListener('input',()=>renderSources());

// === HELPERS ===
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function confPct(c){return Math.round((c||0)*100)}
function confClass(c){return c>0.7?'cf-high':c>0.4?'cf-med':'cf-low'}
function statusClass(s){return s==='supported'?'t-supported':s==='contested'?'t-contested':s==='confirmed'?'t-confirmed':s==='rejected'?'t-rejected':s==='plausible'?'t-plausible':'t-proposed'}
function truncate(s,n){return (s||'').length>n?(s||'').substring(0,n)+'...':s||''}

// === CONTROLS ===
async function doStart(){
  const topic=document.getElementById('topicInput').value.trim();
  if(!topic){alert('Enter a topic first');return}
  try{await fetch(API+'/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic})});addFeed('cycle','Started research: '+topic)}catch(e){alert('Failed: '+e)}
}
async function doPause(){
  try{await fetch(API+'/api/pause',{method:'POST'});addFeed('info','Research paused')}catch(e){}
}
async function doResume(){
  try{await fetch(API+'/api/resume',{method:'POST'});addFeed('info','Research resumed')}catch(e){}
}
async function doStop(){
  try{await fetch(API+'/api/stop',{method:'POST'});addFeed('info','Research stopped')}catch(e){}
}
async function doExport(){
  addFeed('info','Exporting dataset...');
  try{const r=await fetch(API+'/api/dataset');const d=await r.json();addFeed('source','Dataset exported: '+Object.keys(d.files||{}).length+' files')}catch(e){addFeed('info','Export failed: '+e)}
}
async function doFinetune(){
  addFeed('info','Exporting fine-tuning dataset...');
  try{const r=await fetch(API+'/api/finetune');const d=await r.json();addFeed('source','Fine-tune dataset: '+d.file)}catch(e){addFeed('info','Export failed: '+e)}
}

// === RENDER STATUS ===
let prevPhase='';
function render(d){
  const phase=d.phase||'idle';
  const stats=d.stats||{};

  // Badge
  const b=document.getElementById('badge');
  b.textContent=phase.toUpperCase();
  b.className='badge b-'+phase;
  document.getElementById('spinner').style.display=(phase!=='idle'&&phase!=='stopped'&&phase!=='error')?'inline-block':'none';

  // Phase bar
  document.querySelectorAll('.phase').forEach(p=>{p.classList.remove('active');if(p.dataset.p===phase)p.classList.add('active')});

  // Stats
  document.getElementById('sCycles').textContent=stats.total_cycles||d.cycle_count||0;
  document.getElementById('sSources').textContent=stats.sources||0;
  document.getElementById('sFacts').textContent=stats.facts||0;
  const ft=stats.fulltext||{};
  document.getElementById('sFulltext').textContent=ft.sources_with_fulltext||0;
  document.getElementById('sQuotes').textContent=ft.facts_with_quote||0;
  document.getElementById('sHyps').textContent=stats.hypotheses||0;
  document.getElementById('sQuestions').textContent=stats.open_questions||0;
  document.getElementById('sContras').textContent=stats.contradictions||0;

  // Focus
  document.getElementById('fQuestion').textContent=d.current_question||'Waiting for research to start...';
  const fTaskElr=document.getElementById('fTask');
  const fFindElr=document.getElementById('fFinding');
  fTaskElr.textContent=d.current_task||'--';
  fFindElr.textContent=truncate(d.last_finding,200)||'--';
  const fcTask=fTaskElr.closest('.focus-card'), fcFind=fFindElr.closest('.focus-card');
  // Platzhalter ('', '--', '-', '-' auch vom Server) gilt als leer.
  const hasTask=!/^[\-\u2010-\u2014 ]{0,3}$/.test((d.current_task||'').trim());
  const hasFind=!/^[\-\u2010-\u2014 ]{0,3}$/.test((d.last_finding||'').trim());
  if(fcTask) fcTask.style.display=hasTask?'':'none';
  if(fcFind) fcFind.style.display=hasFind?'':'none';

  // Forschungsprogramm: welche Teilfrage gerade läuft, was abgeschlossen ist
  // und warum - die Agenda des Laufs.
  const prog=d.program||{};
  const pc=prog.counts||{};
  document.getElementById('progCnt').textContent=(pc.done||0)+'/'+(pc.total||0);
  const pa=prog.active;
  document.getElementById('progActive').innerHTML=pa
    ? `<b>Aktuell:</b> ${esc(pa.question)} <span style="color:var(--t3)">(${esc(pa.kind)}, Zyklus ${(pa.cycles_spent||0)+1}, Wert ${(pa.marginal_value||0).toFixed(3)})</span>`
    : (pc.total?`<span style="color:var(--t3)">Alle Teilfragen abgeschlossen (${pc.cycles_spent||0} Zyklen, +${pc.facts_gained||0} Fakten)</span>`:'');
  document.getElementById('progList').innerHTML=(prog.items||[]).length?prog.items.map(p=>{
    const cls=p.status==='done'?'t-supported':p.status==='active'?'t-plausible':'t-proposed';
    const verdict=p.verdict_text?`<div style="font-size:12px;color:var(--grn);margin-top:3px">Verdikt: ${esc(p.verdict_text)}</div>`:'';
    const reason=p.close_reason?`<div style="font-size:11px;color:var(--t3);margin-top:3px">${esc(p.close_reason)}</div>`:'';
    return `<div class="item">
      <div class="item-top">
        <span class="tag ${cls}">${esc(p.status)}</span>
        <span style="font-size:11px;color:var(--t3)">${esc(p.kind)} | Zyklen ${p.cycles_spent||0} | Quellen +${p.sources_gained||0} | Fakten +${p.facts_gained||0} | Wert ${(p.marginal_value||0).toFixed(3)}</span>
      </div>
      <div class="item-body">${esc(p.question)}</div>
      ${reason}${verdict}
    </div>`;
  }).join(''):'<div class="empty">Noch kein Programm</div>';

  // Feed on phase change
  if(phase!==prevPhase&&prevPhase&&phase!=='idle'){
    addFeed('cycle','Phase: '+phase);
  }
  prevPhase=phase;

  // Hypotheses
  const hyps=d.active_hypotheses||[];
  document.getElementById('hypCnt').textContent=hyps.length;
  document.getElementById('hypList').innerHTML=hyps.length?hyps.map(h=>{
    const c=confPct(h.confidence);
    // Status-Akzent: Konfidenz faerbt den linken Rand dezent (gruen = belastbar).
    const accent=c>=66?'var(--grn)':c>=33?'var(--ac)':'var(--bdr2)';
    return `<div class="item" style="cursor:pointer;border-left:3px solid ${accent}" onclick="openHypModal('${h.id}')">
      <div class="item-top">
        <span class="tag ${statusClass(h.status)}">${h.status}</span>
        <span style="font-size:12px;color:var(--t2);font-variant-numeric:tabular-nums">${c}%</span>
      </div>
      <div class="item-title" style="margin-top:6px">${esc(h.claim)}</div>
      <div class="conf-bar"><div class="conf-fill ${confClass(h.confidence)}" style="width:${c}%"></div></div>
    </div>`;
  }).join(''):'<div class="empty">No active hypotheses yet</div>';

  // Questions
  const qs=d.open_questions||[];
  document.getElementById('qCnt').textContent=qs.length;
  document.getElementById('qList').innerHTML=qs.length?qs.map(q=>`
    <div class="item">
      <div class="item-top">
        <span class="tag t-${q.priority_score>0.7?'high':q.priority_score>0.4?'medium':'low'}">P ${(q.priority_score||0).toFixed(2)}</span>
        <span style="font-size:11px;color:var(--t3)">Imp ${(q.importance||0).toFixed(1)} | Unc ${(q.uncertainty||0).toFixed(1)}</span>
      </div>
      <div class="item-title" style="margin-top:4px">${esc(q.question)}</div>
    </div>
  `).join(''):'<div class="empty">No open questions</div>';

  // Sources
  lastSources=d.recent_sources||[];
  renderSources();

  // Contradictions
  const contras=d.contradictions||[];
  document.getElementById('cCnt').textContent=contras.length;
  document.getElementById('cList').innerHTML=contras.length?contras.map(c=>`
    <div class="item" style="border-left:3px solid var(--red)">
      <div class="item-title" style="color:var(--red)">Conflict</div>
      <div class="item-meta"><strong>A:</strong> ${esc(c.claim_a)}</div>
      <div class="item-meta"><strong>B:</strong> ${esc(c.claim_b)}</div>
      ${c.resolution_note?`<div class="item-meta" style="margin-top:4px;font-style:italic">${esc(c.resolution_note)}</div>`:''}
    </div>
  `).join(''):'<div class="empty">No contradictions found</div>';

  // Topic
  if(d.topic)document.getElementById('topicInput').value=d.topic;
}

// === RENDER JOURNAL ===
function renderJournal(entries){
  document.getElementById('jCnt').textContent=entries.length;
  document.getElementById('jList').innerHTML=entries.length?entries.map(e=>{
    let findings=[],hyps=[];
    try{findings=JSON.parse(e.important_findings||'[]')}catch(x){}
    try{hyps=JSON.parse(e.new_hypotheses||'[]')}catch(x){}
    return `<div class="journal-entry">
      <div style="display:flex;justify-content:space-between">
        <div class="je-cycle">Cycle ${e.cycle_number}</div>
        <div class="je-time">${e.timestamp||''}</div>
      </div>
      <div class="je-q">${esc(e.research_question)}</div>
      ${findings.length?`<div class="je-label">Findings</div><div class="je-findings">${findings.map(f=>'<div>- '+esc(f)+'</div>').join('')}</div>`:''}
      ${hyps.length?`<div class="je-label">New Hypotheses</div><div class="je-findings">${hyps.map(h=>'<div>- '+esc(h)+'</div>').join('')}</div>`:''}
      ${e.confidence_change?`<div class="je-label">Confidence</div><div class="je-findings">${esc(e.confidence_change)}</div>`:''}
    </div>`;
  }).join(''):'<div class="empty">Journal empty</div>';
}

// === RENDER REJECTED ===
function renderRejected(hyps){
  document.getElementById('rejectedList').innerHTML=hyps.length?hyps.map(h=>`
    <div class="item" style="border-left:3px solid var(--t3)">
      <div class="item-top">
        <span class="tag t-rejected">Rejected</span>
        <span style="font-size:11px;color:var(--t3)">${h.confidence?confPct(h.confidence)+'%':''}</span>
      </div>
      <div class="item-title" style="margin-top:4px;opacity:.7">${esc(h.claim)}</div>
      ${h.rejection_reason?`<div class="item-meta" style="color:var(--red)">Reason: ${esc(h.rejection_reason)}</div>`:''}
    </div>
  `).join(''):'<div class="empty">None yet</div>';
}

// === D3.JS KNOWLEDGE GRAPH ===
let graphSim=null,graphSvg=null,graphG=null,graphZoom=null;
// Physics starts OFF: the layout is settled before drawing, so the graph appears
// immediately and pans/zooms without per-frame DOM churn. "Physics: ON" brings
// the live simulation back.
let graphNodes=[],graphEdges=[],graphShowLabels=true,graphPhysicsOn=false;
let graphHighlightType=null;
const COLORS={hypothesis:'#4da6ff',source:'#fb923c',fact:'#34d399',question:'#a78bfa',evidence:'#f87171',concept:'#8899b0',claim:'#fbbf24'};

function initGraph(){
  const container=document.getElementById('graphContainer');
  const w=container.clientWidth,h=container.clientHeight;
  
  // Create SVG
  graphSvg=d3.select('#graphContainer').append('svg').attr('width',w).attr('height',h);
  
  // Add zoom behavior
  graphZoom=d3.zoom().scaleExtent([0.1,5]).on('zoom',(e)=>{
    graphG.attr('transform',e.transform);
  });
  graphSvg.call(graphZoom);
  
  // Create main group
  graphG=graphSvg.append('g');
  
  // Create arrow markers
  graphSvg.append('defs').selectAll('marker')
    .data(['supports','contradicts','evidence','related'])
    .enter().append('marker')
      .attr('id',d=>'arrow-'+d)
      .attr('viewBox','0 -5 10 10')
      .attr('refX',20)
      .attr('refY',0)
      .attr('markerWidth',6)
      .attr('markerHeight',6)
      .attr('orient','auto')
    .append('path')
      .attr('d','M0,-5L10,0L0,5')
      .attr('fill',d=>d==='contradicts'?'#f87171':'#4da6ff');
  
  // Handle resize
  window.addEventListener('resize',()=>{
    const w2=container.clientWidth,h2=container.clientHeight;
    graphSvg.attr('width',w2).attr('height',h2);
  });
}

function drawGraph(data){
  if(!graphSvg)initGraph();
  
  const container=document.getElementById('graphContainer');
  const w=container.clientWidth,h=container.clientHeight;
  
  graphNodes=(data.nodes||[]).map(n=>({...n,r:n.type==='hypothesis'?12:n.type==='source'?8:6}));
  graphEdges=(data.edges||[]).map(e=>({...e}));
  
  // Update stats
  document.getElementById('graphStats').innerHTML=
    `${graphNodes.length} nodes | ${graphEdges.length} edges`;
  
  if(!graphNodes.length){
    graphG.selectAll('*').remove();
    graphG.append('text').attr('x',w/2).attr('y',h/2)
      .attr('text-anchor','middle').attr('fill','#5a6a80').attr('font-size','14px')
      .text('Knowledge graph will appear after a few research cycles');
    return;
  }
  
  // Clear and redraw
  graphG.selectAll('*').remove();
  
  // Filter nodes if needed
  let visNodes=graphNodes,visEdges=graphEdges;
  if(graphHighlightType){
    visNodes=graphNodes.filter(n=>n.type===graphHighlightType);
    const visIds=new Set(visNodes.map(n=>n.id));
    visEdges=graphEdges.filter(e=>visIds.has(e.source?.id||e.source)&&visIds.has(e.target?.id||e.target));
  }
  
  // Create simulation and settle it before anything is drawn. Hundreds of nodes
  // with ~1000 links cost more in per-tick DOM updates than in the simulation
  // itself (measured ~2 fps while ticking), so positions are computed up front
  // and written once; the tick handler only runs while the user drags or turns
  // physics on.
  if(graphSim)graphSim.stop();
  graphSim=d3.forceSimulation(visNodes)
    .force('link',d3.forceLink(visEdges).id(d=>d.id).distance(80))
    .force('charge',d3.forceManyBody().strength(-200))
    .force('center',d3.forceCenter(w/2,h/2))
    .force('collision',d3.forceCollide().radius(d=>d.r+4))
    .stop();
  const settleTicks=Math.min(300, 60+visNodes.length*2);
  for(let i=0;i<settleTicks;i++)graphSim.tick();
  
  // Draw edges
  const edge=graphG.append('g').selectAll('line')
    .data(visEdges).enter().append('line')
    .attr('stroke',d=>d.relation==='contradicts'?'#f87171':d.relation==='supports'?'#34d399':'rgba(77,166,255,0.3)')
    .attr('stroke-width',d=>Math.max(1,d.weight||1))
    .attr('stroke-dasharray',d=>d.relation==='contradicts'?'4,2':'none')
    .attr('marker-end',d=>'url(#arrow-'+(d.relation||'related')+')');
  
  // Draw nodes
  const node=graphG.append('g').selectAll('g')
    .data(visNodes).enter().append('g')
    .attr('cursor','pointer')
    .call(d3.drag()
      .on('start',(e,d)=>{if(!e.active)graphSim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y})
      .on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y})
      .on('end',(e,d)=>{if(!e.active)graphSim.alphaTarget(0);if(!graphPhysicsOn){d.fx=d.x;d.fy=d.y}})
    );
  
  // Node circles
  node.append('circle')
    .attr('r',d=>d.r)
    .attr('fill',d=>COLORS[d.type]||'#8899b0')
    .attr('stroke',d=>d.type==='hypothesis'?'rgba(77,166,255,0.5)':'rgba(255,255,255,0.15)')
    .attr('stroke-width',d=>d.type==='hypothesis'?2:1)
    .on('mouseover',(e,d)=>showTooltip(e,d))
    .on('mouseout',()=>hideTooltip())
    .on('click',(e,d)=>showNodeDetail(d));
  
  // Confidence ring for hypotheses
  node.filter(d=>d.type==='hypothesis'&&d.confidence)
    .append('circle')
    .attr('r',d=>d.r+3)
    .attr('fill','none')
    .attr('stroke',d=>d.confidence>0.6?'#34d399':d.confidence>0.4?'#fbbf24':'#f87171')
    .attr('stroke-width',2)
    .attr('stroke-dasharray',d=>{const c=d.confidence*2*Math.PI*(d.r+3);return c+' '+(2*Math.PI*(d.r+3)-c)})
    .attr('stroke-dashoffset',d=>2*Math.PI*(d.r+3)*0.25);
  
  // Labels
  if(graphShowLabels){
    node.append('text')
      .attr('dx',d=>d.r+4).attr('dy',3)
      .attr('font-size','10px').attr('fill','#8899b0')
      .text(d=>truncate(d.label,25));
  }
  
  // Tick handler (positions were settled above; this runs on drag or with physics on)
  const positionAll=()=>{
    edge.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
      .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    node.attr('transform',d=>`translate(${d.x},${d.y})`);
  };
  positionAll();
  graphSim.on('tick',positionAll);
  if(graphPhysicsOn)graphSim.alpha(0.3).restart();
}

function showTooltip(event,d){
  const tt=document.getElementById('graphTooltip');
  const conf=d.confidence?`Confidence: ${(d.confidence*100).toFixed(0)}%`:'';
  const status=d.status?`Status: ${d.status}`:'';
  tt.innerHTML=`<div class="tt-type" style="color:${COLORS[d.type]||'#8899b0'}">${d.type}</div>`+
    `<div class="tt-label">${truncate(d.label,60)}</div>`+
    (d.content?`<div class="tt-content">${truncate(d.content,120)}</div>`:'')+
    (conf||status?`<div class="tt-meta">${conf} ${status}</div>`:'');
  tt.style.display='block';
  tt.style.left=(event.offsetX+15)+'px';
  tt.style.top=(event.offsetY-10)+'px';
}

function hideTooltip(){
  document.getElementById('graphTooltip').style.display='none';
}

function showNodeDetail(d){
  const el=document.getElementById('nodeDetail');
  const conns=graphEdges.filter(e=>(e.source?.id||e.source)===d.id||(e.target?.id||e.target)===d.id);
  const supCount=conns.filter(e=>e.relation==='supports').length;
  const contraCount=conns.filter(e=>e.relation==='contradicts').length;
  el.innerHTML=`<div class="node-detail">
    <span class="nd-close" onclick="document.getElementById('nodeDetail').innerHTML=''">&times;</span>
    <div class="nd-type" style="color:${COLORS[d.type]||'#8899b0'}">${d.type}</div>
    <h4>${d.label}</h4>
    ${d.content?`<div class="nd-content">${d.content}</div>`:''}
    ${d.confidence?`<div class="nd-content" style="margin-top:4px">Confidence: <b>${(d.confidence*100).toFixed(0)}%</b> (${d.status||'proposed'})</div>`:''}
    <div class="nd-connections">${conns.length} connections (${supCount} supporting, ${contraCount} contradicting)</div>
  </div>`;
}

function graphFilterType(type){
  graphHighlightType=graphHighlightType===type?null:type;
  pollGraph();
}

function graphZoomIn(){graphSvg.transition().duration(300).call(graphZoom.scaleBy,1.5)}
function graphZoomOut(){graphSvg.transition().duration(300).call(graphZoom.scaleBy,0.67)}
function graphReset(){graphSvg.transition().duration(500).call(graphZoom.transform,d3.zoomIdentity)}
function graphToggleLabels(){graphShowLabels=!graphShowLabels;document.getElementById('btnLabels').classList.toggle('active');pollGraph(true)}
function graphTogglePhysics(){
  graphPhysicsOn=!graphPhysicsOn;
  document.getElementById('btnPhysics').textContent='Physics: '+(graphPhysicsOn?'ON':'OFF');
  document.getElementById('btnPhysics').classList.toggle('active');
  if(graphSim){graphPhysicsOn?graphSim.alpha(0.3).restart():graphSim.stop()}
}

// === HYPOTHESIS DETAIL MODAL ===
async function openHypModal(hypId) {
  const overlay = document.getElementById('hypModal');
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';

  // Show loading state
  document.getElementById('hmClaim').textContent = 'Loading...';
  document.getElementById('hmEvidence').innerHTML = '<div class="md-empty">Loading evidence...</div>';
  document.getElementById('hmPredictions').innerHTML = '';
  document.getElementById('hmAlternatives').innerHTML = '';
  document.getElementById('hmFalsification').innerHTML = '';
  document.getElementById('hmContradictions').innerHTML = '';
  document.getElementById('hmRelated').innerHTML = '';

  try {
    const r = await fetch(API + '/api/hypothesis/' + encodeURIComponent(hypId));
    const h = await r.json();
    if (h.error) {
      document.getElementById('hmClaim').textContent = 'Error: ' + h.error;
      return;
    }

    // Status badge
    document.getElementById('hmStatus').innerHTML = `<span class="tag ${statusClass(h.status)}" style="font-size:12px;padding:4px 12px">${h.status}</span>`;

    // Claim
    document.getElementById('hmClaim').textContent = h.claim || '';

    // Meta
    const conf = confPct(h.confidence);
    document.getElementById('hmConf').innerHTML = `Confidence: <b style="color:${h.confidence>0.6?'var(--grn)':h.confidence>0.4?'var(--yel)':'var(--red)'}">${conf}%</b>`;
    document.getElementById('hmDate').textContent = h.date_added ? 'Added: ' + h.date_added.split('T')[0] : '';
    document.getElementById('hmTopic').textContent = h.topic || '';

    // Evidence records from DB
    const evs = h.evidence_records || [];
    document.getElementById('hmEvCnt').textContent = evs.length;
    document.getElementById('hmEvidence').innerHTML = evs.length ? evs.map(ev => `
      <div class="md-evidence-card">
        <div class="ec-header">
          <span class="ec-type ${ev.evidence_type || 'evidence'}">${ev.evidence_type || 'evidence'}</span>
          <span class="ec-strength">Strength: ${ev.strength ? (ev.strength * 100).toFixed(0) + '%' : 'N/A'}</span>
        </div>
        <div class="ec-content">${esc(ev.content || '')}</div>
        <div class="ec-source">
          ${ev.source_url ? `<a href="${esc(ev.source_url)}" target="_blank" rel="noopener">${esc(ev.source_title || ev.source_url)}</a>` : (ev.source_title ? esc(ev.source_title) : '<span style="color:var(--t3)">No source linked</span>')}
          ${ev.credibility ? `<span class="ec-cred">Cred: ${ev.credibility.toFixed(1)}</span>` : ''}
          ${ev.source_type ? `<span class="tag t-${ev.source_type==='arxiv'?'plausible':ev.source_type==='pubmed'?'supported':'proposed'}" style="font-size:9px">${ev.source_type}</span>` : ''}
        </div>
      </div>
    `).join('') : '<div class="md-empty">No evidence records found for this hypothesis.</div>';

    // Also show inline evidence from JSON fields
    const supporting = h.supporting_evidence || [];
    const contradicting = h.contradicting_evidence || [];
    if (supporting.length || contradicting.length) {
      const extraHtml = [];
      if (supporting.length) {
        extraHtml.push('<div style="margin-top:8px"><div style="font-size:10px;color:var(--grn);font-weight:700;margin-bottom:6px">SUPPORTING EVIDENCE (' + supporting.length + ')</div>');
        supporting.forEach(s => {
          extraHtml.push(`<div class="md-evidence-card"><div class="ec-header"><span class="ec-type supports">supports</span></div><div class="ec-content">${esc(s)}</div></div>`);
        });
        extraHtml.push('</div>');
      }
      if (contradicting.length) {
        extraHtml.push('<div style="margin-top:8px"><div style="font-size:10px;color:var(--red);font-weight:700;margin-bottom:6px">CONTRADICTING EVIDENCE (' + contradicting.length + ')</div>');
        contradicting.forEach(s => {
          extraHtml.push(`<div class="md-evidence-card"><div class="ec-header"><span class="ec-type contradicts">contradicts</span></div><div class="ec-content">${esc(s)}</div></div>`);
        });
        extraHtml.push('</div>');
      }
      document.getElementById('hmEvidence').innerHTML += extraHtml.join('');
    }

    // Predictions
    const preds = h.predictions || [];
    document.getElementById('hmPredictionsSection').style.display = preds.length ? '' : 'none';
    document.getElementById('hmPredictions').innerHTML = preds.map(p => `<div class="md-prediction">${esc(p)}</div>`).join('');

    // Alternatives
    const alts = h.alternative_explanations || [];
    document.getElementById('hmAlternativesSection').style.display = alts.length ? '' : 'none';
    document.getElementById('hmAlternatives').innerHTML = alts.map(a => `<div class="md-alternative">${esc(a)}</div>`).join('');

    // Falsification
    const fals = h.falsification_conditions || [];
    document.getElementById('hmFalsificationSection').style.display = fals.length ? '' : 'none';
    document.getElementById('hmFalsification').innerHTML = fals.map(f => `<div class="md-falsification">${esc(f)}</div>`).join('');

    // Contradictions
    const contras = h.contradictions || [];
    document.getElementById('hmContraCnt').textContent = contras.length;
    document.getElementById('hmContradictionsSection').style.display = contras.length ? '' : 'none';
    document.getElementById('hmContradictions').innerHTML = contras.map(c => `
      <div class="md-contradiction">
        <div class="mc-label">Unresolved Contradiction</div>
        <div class="mc-claim"><strong>A:</strong> ${esc(c.claim_a || '')}</div>
        <div class="mc-claim"><strong>B:</strong> ${esc(c.claim_b || '')}</div>
        ${c.resolution_note ? `<div class="mc-claim" style="font-style:italic;margin-top:4px">${esc(c.resolution_note)}</div>` : ''}
      </div>
    `).join('');

    // Related hypotheses
    const rels = h.related_hypotheses || [];
    document.getElementById('hmRelCnt').textContent = rels.length;
    document.getElementById('hmRelatedSection').style.display = rels.length ? '' : 'none';
    document.getElementById('hmRelated').innerHTML = rels.map(r => `
      <div class="md-related-hyp" onclick="openHypModal('${r.id}')">
        <span class="rh-claim">${esc(r.claim || '')}</span>
        <span class="rh-conf">${r.confidence ? confPct(r.confidence) + '%' : ''} <span class="tag ${statusClass(r.status)}" style="font-size:9px">${r.status || ''}</span></span>
      </div>
    `).join('');

  } catch (e) {
    document.getElementById('hmClaim').textContent = 'Failed to load: ' + e.message;
  }
}

function closeHypModal() {
  document.getElementById('hypModal').classList.remove('open');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeHypModal();
});

// === POLL ===
let lastFetchCycle=0;
async function poll(){
  try{
    const r=await fetch(API+'/api/status');const d=await r.json();
    render(d);
    renderWorkQueue(d);
    renderExperiments(d);

    // Detect new cycle
    const curCycle=d.cycle_count||0;
    if(curCycle>lastFetchCycle){
      if(lastFetchCycle>0)addFeed('cycle','Cycle '+curCycle+' completed');
      lastFetchCycle=curCycle;
    }
  }catch(e){}

  try{
    const r=await fetch(API+'/api/journal');const d=await r.json();
    renderJournal(d);
  }catch(e){}

  try{
    const r=await fetch(API+'/api/rejected');const d=await r.json();
    renderRejected(d);
  }catch(e){}

  // Poll parallel stats
  await pollParallelStats();
}

function renderWorkQueue(d){
  const q=d.work_queue||{};
  const cw=d.cycle_work||{};
  const set=(id,v)=>{const el=document.getElementById(id); if(el) el.textContent=v;};
  set('wqTotal', q.total||0);
  set('wqOpen', q.open||0);
  set('wqDone', q.done||0);
  set('wqBlocked', q.blocked||0);
  set('wqCycle', (cw.done||0)+'/'+(cw.claimed||0));

  const kinds=document.getElementById('wqKinds');
  if(kinds){
    const by=q.open_by_kind||{};
    const keys=Object.keys(by);
    kinds.innerHTML=keys.length
      ? keys.map(k=>`<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2)">${k}: ${by[k]}</div>`).join('')
      : '<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">Queue empty</div>';
  }

  const brake=q.hypothesis_brake||{};
  const evidence=brake.evidence_open!==undefined?brake.evidence_open:(q.open_by_kind||{}).hypothesis_evidence||0;
  set('wqEvidence', evidence);
  const brakeEl=document.getElementById('wqBrake');
  if(brakeEl){
    const limit=brake.limit||0;
    const active=!!brake.active;
    const card=document.getElementById('wqEvidenceCard');
    if(card) card.style.borderLeft=active?'3px solid var(--yel)':'3px solid var(--grn)';
    brakeEl.innerHTML=limit
      ? `<span style="color:${active?'var(--yel)':'var(--grn)'};font-weight:700">Hypothesen-Bremse ${active?'greift':'offen'}</span>`+
        `<span style="color:var(--t2)"> &mdash; ${evidence} von ${limit} Hypothesen ohne Evidenz, `+
        `${active?'keine neuen Hypothesen bis der Rückstand fällt':'Erzeugung läuft'}</span>`
      : `<span style="color:var(--t3)">Hypothesen-Bremse aus (Limit 0)</span>`;
  }

  const next=document.getElementById('wqNext');
  if(next){
    const items=q.next||[];
    next.innerHTML=items.length
      ? items.map(i=>`<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2)">[${i.kind}]        ${esc((i.title||'').slice(0,110))}</div>`).join('')
      : '<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">Queue empty</div>';
  }
}

function renderExperiments(d){
  const exp=d.experiments||{};
  const set=(id,v)=>{const el=document.getElementById(id); if(el) el.textContent=v;};
  const by=exp.by_verdict||{};
  set('labTotal', exp.total||0);
  set('labSupports', by.supports||0);
  set('labContradicts', by.contradicts||0);
  set('labNeutral', by.neutral||0);
  const recent=exp.recent||[];
  set('labSplit', recent.reduce((a,e)=>a+(e.deviations||0),0));
  // Known-answer checks only exist for runs that reached the gate; show the
  // ratio over those rather than pretending untested runs passed.
  const tested=recent.filter(e=>(e.kat_total||0)>0);
  const katEl=document.getElementById('labKat');
  if(katEl){
    if(tested.length){
      const passed=tested.reduce((a,e)=>a+(e.kat_passed||0),0);
      const total=tested.reduce((a,e)=>a+(e.kat_total||0),0);
      katEl.textContent=passed+'/'+total;
      katEl.style.color=passed===total?'var(--grn)':'var(--yel)';
    }else{
      katEl.textContent='--';
      katEl.style.color='var(--t3)';
    }
  }
  const el=document.getElementById('labRecent');
  if(!el) return;
  el.innerHTML = recent.length
    ? recent.map(e=>{
        const rate=Math.round((e.replication_rate||0)*100);
        const color=e.verdict==='supports'?'var(--grn)':(e.verdict==='contradicts'?'var(--purp)':'var(--yel)');
        const reps=e.replications?`${rate}% von ${e.replications}`:(e.status||'');
        const kat=(e.kat_total||0)>0
          ? `<span style="color:${e.kat_passed===e.kat_total?'var(--grn)':'var(--yel)'}">KAT ${e.kat_passed}/${e.kat_total}</span> `
          : '';
        return `<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2)">`+
               `<span style="color:${color};font-weight:700">${e.verdict||'?'}</span> `+
               `<span style="color:var(--t3)">${reps}</span> ${kat}`+
               `${esc((e.claim||'').slice(0,90))}</div>`;
      }).join('')
    : '<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">Keine Simulationen</div>';
}

let parStatsUnavailable=false;
async function pollParallelStats(){
  if(parStatsUnavailable||liveOnly('/api/parallel-stats')) return;
  try{
    const r=await fetch(API+'/api/parallel-stats');
    if(r.status===404){
      // Standalone-Server kennt diesen Endpunkt nicht - einmal degradieren,
      // danach wird nicht weiter gepolt (keine permanenten 404-Fehler).
      parStatsUnavailable=true;
      const hint='<div style="padding:4px 10px;background:var(--bg);border-radius:6px;'
        +'font-size:11px;color:var(--t3)">Nur im Live-Betrieb verfuegbar '
        +'(interner Orchestrator-Endpunkt)</div>';
      const bt=document.getElementById('pPhaseTimings');if(bt)bt.innerHTML=hint;
      const at=document.getElementById('pActiveTasks');if(at)at.innerHTML=hint;
      return;
    }
    const d=await r.json();
    renderParallelStats(d);
  }catch(e){}
}

function renderParallelStats(d){
  // Active tasks
  document.getElementById('pActive').textContent=d.active_tasks||0;
  document.getElementById('pActive').style.color=(d.active_tasks||0)>0?'var(--ac)':'var(--t3)';
  
  // Total tasks run
  document.getElementById('pTotal').textContent=d.total_tasks_run||0;
  
  // Parallel time
  const parTime=d.total_parallel_time||0;
  document.getElementById('pParallelTime').textContent=parTime>60?Math.round(parTime/60)+'m':parTime.toFixed(1)+'s';
  
  // Phase timings
  const timings=d.phase_timings||{};
  const timingsEl=document.getElementById('pPhaseTimings');
  const timingKeys=Object.keys(timings);
  if(timingKeys.length){
    timingsEl.innerHTML=timingKeys.map(k=>{
      const v=timings[k];
      const pct=Math.min(100,Math.round((v/(parTime||1))*100));
      return `<div style="padding:6px 12px;background:var(--bg);border-radius:6px;font-size:11px;border-left:3px solid var(--ac);flex:1;min-width:100px">
        <div style="color:var(--t2);font-weight:600;text-transform:capitalize">${esc(k)}</div>
        <div style="color:var(--grn);font-size:14px;font-weight:800;margin-top:2px">${v.toFixed(1)}s</div>
        <div style="height:3px;background:var(--bg3);border-radius:2px;margin-top:4px"><div style="height:100%;background:var(--ac);border-radius:2px;width:${pct}%"></div></div>
      </div>`;
    }).join('');
  }else{
    timingsEl.innerHTML='<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">No timing data yet</div>';
  }
  
  // Active tasks list
  const tasks=d.current_phase_tasks||[];
  const tasksEl=document.getElementById('pActiveTasks');
  if(tasks.length){
    tasksEl.innerHTML=tasks.map(t=>{
      const isRunning=(d.active_tasks||0)>0;
      return `<div style="padding:4px 10px;background:${isRunning?'rgba(77,166,255,.15)':'var(--bg)'};border-radius:6px;font-size:11px;color:${isRunning?'var(--ac)':'var(--t3)'};display:flex;align-items:center;gap:4px">
        ${isRunning?'<span class="spin" style="width:10px;height:10px;border-width:1.5px"></span>':''}
        ${esc(t)}
      </div>`;
    }).join('');
  }else{
    tasksEl.innerHTML='<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">Idle</div>';
  }
}

let lastGraphSig='';
async function pollGraph(force){
  // Rebuilding a few hundred nodes is the expensive part: skip the poll while
  // the graph tab is hidden, and skip the redraw when nothing changed.
  const panel=document.getElementById('tp-graph');
  if(!force&&panel&&!panel.classList.contains('active'))return;
  try{
    const r=await fetch(API+'/api/graph');const d=await r.json();
    const sig=(d.nodes||[]).length+'/'+(d.edges||[]).length+'/'+(d.nodes||[]).map(n=>n.id).sort().join(',');
    if(!force&&sig===lastGraphSig)return;
    lastGraphSig=sig;
    drawGraph(d);
  }catch(e){}
}

// Start polling
poll();
pollTimer=setInterval(poll,2000);
setInterval(pollGraph,10000);

// Graph search and filter
let graphSearchTerm='';
document.getElementById('graphSearch').addEventListener('input',(e)=>{
  graphSearchTerm=e.target.value.toLowerCase();
  filterGraphNodes();
});
document.getElementById('graphFilter').addEventListener('change',(e)=>{
  graphHighlightType=e.target.value==='all'?null:e.target.value;
  pollGraph(true);
});

function filterGraphNodes(){
  if(!graphG)return;
  graphG.selectAll('g').each(function(d){
    if(!d||!d.label)return;
    const match=!graphSearchTerm||d.label.toLowerCase().includes(graphSearchTerm)||(d.content||'').toLowerCase().includes(graphSearchTerm);
    d3.select(this).style('opacity',match?1:0.15);
  });
}

// Resize graph on window resize
window.addEventListener('resize',()=>pollGraph(true));

// === MONITORING PANELS ===
let monPollTimer;

async function pollMonitoring(){
  // Only poll if the monitoring tab is active
  const monTab = document.querySelector('.tab[data-tab="monitoring"]');
  if(!monTab || !monTab.classList.contains('active')) return;

  await Promise.all([
    pollSystemHealth(),
    pollSourceAnalytics(),
    pollSessions(),
    pollErrors(),
    pollConfidenceHistory(),
    pollLLMStats(),
  ]);
}

async function pollSystemHealth(){
  try{
    const r=await fetch(API+'/api/system-health');const d=await r.json();
    renderSystemHealth(d);
  }catch(e){}
}

function renderSystemHealth(d){
  // DB Size
  const sz = d.db_size_mb || 0;
  document.getElementById('mhDbSize').textContent = sz >= 1 ? sz.toFixed(1)+' MB' : (d.db_size_bytes||0).toLocaleString()+' B';

  // Total rows
  const tc = d.table_counts || {};
  const totalRows = Object.values(tc).reduce((a,b)=>a+b, 0);
  document.getElementById('mhTables').textContent = totalRows.toLocaleString();

  // Uptime (from session start time)
  const statusData = lastStatusData || {};
  if(statusData.start_time){
    const start = new Date(statusData.start_time);
    const now = new Date();
    const diff = Math.floor((now - start) / 1000);
    if(diff > 3600) document.getElementById('mhUptime').textContent = Math.floor(diff/3600)+'h '+Math.floor((diff%3600)/60)+'m';
    else if(diff > 60) document.getElementById('mhUptime').textContent = Math.floor(diff/60)+'m '+Math.floor(diff%60)+'s';
    else document.getElementById('mhUptime').textContent = diff+'s';
  }else{
    document.getElementById('mhUptime').textContent = '--';
  }

  // Embeddings
  document.getElementById('mhEmbeddings').textContent = (tc.embeddings||0).toLocaleString();

  // Table counts
  const el = document.getElementById('mhTableCounts');
  const entries = Object.entries(tc).filter(([k,v])=>v>0).sort((a,b)=>b[1]-a[1]);
  el.innerHTML = entries.map(([k,v])=>{
    const name = k.replace(/_/g,' ');
    return `<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;border-left:2px solid var(--ac)"><span style="color:var(--t2)">${name}:</span> <span style="color:var(--grn);font-weight:700">${v}</span></div>`;
  }).join('') || '<div style="padding:4px 10px;font-size:11px;color:var(--t3)">No data</div>';
}

async function pollSourceAnalytics(){
  try{
    const r=await fetch(API+'/api/source-analytics');const d=await r.json();
    renderSourceAnalytics(d);
  }catch(e){}
}

function renderSourceAnalytics(d){
  // Source type distribution
  const typeEl = document.getElementById('saTypeBars');
  const types = d.type_counts || [];
  const maxCount = Math.max(...types.map(t=>t.count), 1);
  const typeColors = {'arxiv':'#a78bfa','pubmed':'#34d399','web':'#fb923c','duckduckgo':'#4da6ff'};
  typeEl.innerHTML = types.map(t=>{
    const pct = Math.round((t.count/maxCount)*100);
    const color = typeColors[t.source_type] || '#8899b0';
    return `<div class="analytics-bar">
      <div class="ab-label" style="color:${color}">${esc(t.source_type)}</div>
      <div class="ab-track"><div class="ab-fill" style="width:${pct}%;background:${color}">${pct}%</div></div>
      <div class="ab-count">${t.count}</div>
    </div>`;
  }).join('') || '<div style="padding:4px 10px;font-size:11px;color:var(--t3)">No source data</div>';

  // Credibility distribution
  const credEl = document.getElementById('saCredBars');
  const creds = d.credibility_distribution || [];
  const maxCred = Math.max(...creds.map(c=>c.count), 1);
  const credColors = {'High (0.8+)':'#34d399','Medium (0.6-0.8)':'#4da6ff','Low (0.4-0.6)':'#fbbf24','Very Low (<0.4)':'#f87171'};
  credEl.innerHTML = creds.map(c=>{
    const pct = Math.round((c.count/maxCred)*100);
    const color = credColors[c.bucket] || '#8899b0';
    return `<div class="analytics-bar">
      <div class="ab-label">${esc(c.bucket)}</div>
      <div class="ab-track"><div class="ab-fill" style="width:${pct}%;background:${color}">${pct}%</div></div>
      <div class="ab-count">${c.count}</div>
    </div>`;
  }).join('') || '<div style="padding:4px 10px;font-size:11px;color:var(--t3)">No credibility data</div>';

  // Avg credibility
  document.getElementById('saAvgCred').textContent = d.avg_credibility ? d.avg_credibility.toFixed(2) : '--';
}

async function pollSessions(){
  try{
    const r=await fetch(API+'/api/sessions');const d=await r.json();
    renderSessions(d);
  }catch(e){}
}

function renderSessions(sessions){
  document.getElementById('shCnt').textContent = sessions.length;
  const el = document.getElementById('shList');
  if(!sessions.length){el.innerHTML='<div class="empty">No sessions recorded</div>';return}
  el.innerHTML = sessions.map(s=>{
    const isActive = s.status === 'active';
    const startDate = s.start_time ? new Date(s.start_time).toLocaleDateString() : '--';
    const startTime = s.start_time ? new Date(s.start_time).toLocaleTimeString() : '';
    const endDate = s.end_time ? new Date(s.end_time).toLocaleDateString() : (isActive ? 'ongoing' : '--');
    return `<div class="item ${isActive ? 'active-row' : ''}" style="${isActive ? 'border-left:3px solid var(--grn)' : ''}">
      <div class="item-top">
        <div style="flex:1">
          <div class="item-title">${esc(s.topic || 'Unknown Topic')}</div>
          <div class="item-meta">
            <span class="tag ${isActive ? 't-supported' : 't-proposed'}">${esc(s.status)}</span>
            <span>${startDate} ${startTime}</span>
            <span>${s.cycle_count || 0} cycles</span>
            <span>${s.sources_found || 0} sources</span>
            <span>${s.hypotheses_generated || 0} hypotheses</span>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

async function pollErrors(){
  try{
    const r=await fetch(API+'/api/errors');const d=await r.json();
    renderErrors(d);
  }catch(e){}
}

function renderErrors(d){
  const errors = d.errors || [];
  document.getElementById('elCnt').textContent = errors.length;
  const el = document.getElementById('elList');
  if(!errors.length){el.innerHTML='<div class="empty">No errors logged - all clear!</div>';return}
  el.innerHTML = errors.slice().reverse().map(e=>{
    const time = e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : '';
    const cat = (e.category || 'info').toLowerCase();
    return `<div class="error-item">
      <span class="ei-time">${time}</span>
      <span class="ei-cat ${cat}">${esc(cat)}</span>
      <span class="ei-msg">${esc(e.message)}</span>
    </div>`;
  }).join('');
}

// Store status data for uptime calculation
let lastStatusData = null;
const origRender = render;
render = function(d){
  lastStatusData = d;
  origRender(d);
};

// === LLM STATS ===
async function pollLLMStats(){
  try{
    const r=await fetch(API+'/api/llm-stats');const d=await r.json();
    renderLLMStats(d);
  }catch(e){}
}

const PHASE_COLORS = {'planning':'#4da6ff','searching':'#a78bfa','extracting':'#fb923c','analyzing':'#e879f9','hypothesizing':'#34d399','critiquing':'#f87171','synthesizing':'#2d7fd3','evidence_eval':'#fbbf24','updating':'#818cf8','idle':'#5a6a80'};

function renderLLMStats(d){
  // Summary stats
  document.getElementById('llmCalls').textContent = (d.total_calls||0).toLocaleString();
  const totalTok = d.total_tokens||0;
  document.getElementById('llmTokens').textContent = totalTok >= 1000 ? (totalTok/1000).toFixed(1)+'k' : totalTok;
  document.getElementById('llmAvgTok').textContent = Math.round(d.avg_tokens_per_call||0);
  document.getElementById('llmAvgTime').textContent = Math.round(d.avg_time_ms||0)+'ms';
  document.getElementById('llmErrors').textContent = d.errors||0;

  // Stored usage (database): today's totals and the last days. These survive a
  // restart, so they are the number to quote for "what did today cost?".
  const persisted = d.persisted || null;
  const today = (persisted && persisted.today) || {};
  const fmt = v => v >= 1000000 ? (v/1000000).toFixed(2)+'M' : (v >= 1000 ? (v/1000).toFixed(1)+'k' : String(v||0));
  const setTx = (id, v) => { const el=document.getElementById(id); if(el) el.textContent = v; };
  setTx('llmTodayTok', fmt(today.total_tokens||0));
  setTx('llmTodayCalls', (today.calls||0).toLocaleString());
  setTx('llmTodayAvg', Math.round(today.tokens_per_call||0));
  setTx('llmTodayErr', today.errors||0);
  setTx('llmAllTok', fmt(((persisted&&persisted.all_time)||{}).total_tokens||0));
  const daysEl = document.getElementById('llmDays');
  if(daysEl){
    const days = (persisted && persisted.by_day) || [];
    daysEl.innerHTML = days.length
      ? days.map(row=>`<div style="display:flex;gap:8px;align-items:center;padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px">
           <span style="color:var(--t2);font-weight:600;width:90px">${esc(row.day)}</span>
           <span style="color:var(--grn);font-variant-numeric:tabular-nums;width:70px">${fmt(row.total_tokens||0)}</span>
           <span style="color:var(--t3)">${(row.calls||0).toLocaleString()} Aufrufe`+
           (row.errors ? ` &middot; <span style="color:var(--red)">${row.errors} Fehler</span>` : '') + `</span>
         </div>`).join('')
      : '<div style="padding:4px 10px;font-size:11px;color:var(--t3)">Noch keine gespeicherten Aufrufe</div>';
  }

  // Phase bars: the database rows cover the whole day, the in-memory counters
  // only cover this process, so prefer the stored breakdown when it exists.
  let phaseRows = [];
  if(persisted && (persisted.by_phase||[]).length){
    phaseRows = persisted.by_phase.map(r=>({
      phase: r.phase || 'idle', tokens: r.total_tokens||0,
      calls: r.calls||0, ms: r.time_ms||0,
    }));
  }else{
    const phaseTokens = d.phase_tokens || {};
    const phaseTime = d.phase_time_ms || {};
    const phaseCalls = d.phase_calls || {};
    phaseRows = Object.entries(phaseTokens)
      .map(([ph, tok])=>({phase: ph, tokens: tok, calls: phaseCalls[ph]||0, ms: phaseTime[ph]||0}))
      .sort((a,b)=>b.tokens-a.tokens);
  }
  const maxPTok = Math.max(...phaseRows.map(r=>r.tokens), 1);
  const barsEl = document.getElementById('llmPhaseBars');
  if(phaseRows.length){
    barsEl.innerHTML = phaseRows.map(r=>{
      const pct = Math.round((r.tokens/maxPTok)*100);
      const color = PHASE_COLORS[r.phase] || '#8899b0';
      const tokStr = fmt(r.tokens);
      return `<div class="llm-phase-row">
        <div class="lpr-name" style="color:${color}">${esc(r.phase)}</div>
        <div class="lpr-track"><div class="lpr-fill" style="width:${pct}%;background:${color}">${r.calls} calls</div></div>
        <div class="lpr-val">${tokStr} tok | ${Math.round(r.ms)}ms</div>
      </div>`;
    }).join('');
  }else{
    barsEl.innerHTML = '<div style="padding:4px 10px;font-size:11px;color:var(--t3)">No phase data yet</div>';
  }

  // Recent calls log
  const calls = (d.recent_calls || []).slice(-20).reverse();
  const logEl = document.getElementById('llmCallLog');
  if(calls.length){
    logEl.innerHTML = calls.map(c=>{
      const time = c.timestamp ? new Date(c.timestamp*1000).toLocaleTimeString() : '';
      const phase = c.phase || 'idle';
      const color = PHASE_COLORS[phase] || '#8899b0';
      const tok = c.total_tokens || 0;
      const ms = Math.round(c.time_ms || 0);
      const ok = c.success ? '&#10003;' : '&#10007;';
      const okColor = c.success ? 'var(--grn)' : 'var(--red)';
      return `<div class="llm-call-row">
        <span style="font-size:9px;color:var(--t3);width:55px;flex-shrink:0;font-variant-numeric:tabular-nums">${time}</span>
        <span class="lcr-phase" style="color:${color}">${esc(phase)}</span>
        <span class="lcr-tokens">${tok >= 1000 ? (tok/1000).toFixed(1)+'k' : tok} tok</span>
        <span class="lcr-time">${ms}ms</span>
        <span class="lcr-ok" style="color:${okColor}">${ok}</span>
      </div>`;
    }).join('');
  }else{
    logEl.innerHTML = '<div style="padding:4px 10px;font-size:11px;color:var(--t3)">No calls yet</div>';
  }
}

// === CONFIDENCE TREND CHART (D3.js) ===
const CONF_COLORS = ['#4da6ff','#34d399','#f87171','#fbbf24','#a78bfa','#fb923c','#f472b6','#818cf8','#22d3ee','#a3e635'];
let confChartRendered = false;

async function pollConfidenceHistory(){
  try{
    const r=await fetch(API+'/api/confidence-history');const d=await r.json();
    renderConfidenceChart(d);
  }catch(e){}
}

function renderConfidenceChart(data){
  const hypotheses = data.hypotheses || [];
  document.getElementById('ctCnt').textContent = hypotheses.length;

  const container = document.getElementById('confChartContainer');
  const tooltip = document.getElementById('confChartTooltip');
  const legend = document.getElementById('confChartLegend');

  // Remove old SVG if any
  d3.select('#confChartContainer svg').remove();

  if (!hypotheses.length) {
    legend.innerHTML = '';
    tooltip.style.display = 'none';
    container.insertAdjacentHTML('afterbegin', '<div class="conf-chart-empty">No confidence data yet. Charts appear after research cycles.</div>');
    return;
  }

  // Remove empty state text
  const emptyEl = container.querySelector('.conf-chart-empty');
  if (emptyEl) emptyEl.remove();

  const W = container.clientWidth;
  const H = container.clientHeight;
  const margin = {top: 20, right: 20, bottom: 40, left: 50};
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const svg = d3.select('#confChartContainer').append('svg')
    .attr('width', W).attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  // Flatten all data points and find max cycle
  let maxCycle = 0;
  const series = hypotheses.map((hyp, i) => {
    const pts = hyp.data.map(d => ({
      cycle: d.cycle || 0,
      confidence: d.confidence || 0,
      reason: d.reason || '',
      timestamp: d.timestamp || '',
      claim: hyp.claim || '',
    }));
    if (pts.length) maxCycle = Math.max(maxCycle, ...pts.map(p => p.cycle));
    return {id: hyp.id, claim: hyp.claim, points: pts, color: CONF_COLORS[i % CONF_COLORS.length]};
  });

  // If all cycles are 0, use index as x
  if (maxCycle === 0) {
    series.forEach(s => s.points.forEach((p, i) => p.cycle = i + 1));
    maxCycle = Math.max(...series.map(s => s.points.length), 1);
  }

  // Scales
  const x = d3.scaleLinear().domain([1, maxCycle]).range([0, w]);
  const y = d3.scaleLinear().domain([0, 1]).range([h, 0]);

  // Grid lines
  g.append('g').attr('class', 'grid')
    .selectAll('line')
    .data(y.ticks(5))
    .enter().append('line')
    .attr('x1', 0).attr('x2', w)
    .attr('y1', d => y(d)).attr('y2', d => y(d))
    .attr('stroke', '#1a2130').attr('stroke-width', 1);

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).ticks(Math.min(maxCycle, 20)).tickFormat(d => 'C' + d))
    .selectAll('text').attr('fill', '#5a6a80').attr('font-size', '10px');
  g.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => Math.round(d * 100) + '%'))
    .selectAll('text').attr('fill', '#5a6a80').attr('font-size', '10px');

  // Style axes
  g.selectAll('.domain').attr('stroke', '#2a3548');
  g.selectAll('.tick line').attr('stroke', '#2a3548');

  // Y-axis label
  g.append('text').attr('transform', 'rotate(-90)')
    .attr('y', -40).attr('x', -h / 2)
    .attr('text-anchor', 'middle').attr('fill', '#5a6a80').attr('font-size', '11px')
    .text('Confidence');

  // X-axis label
  g.append('text')
    .attr('x', w / 2).attr('y', h + 35)
    .attr('text-anchor', 'middle').attr('fill', '#5a6a80').attr('font-size', '11px')
    .text('Research Cycle');

  // Draw lines
  const line = d3.line()
    .x(d => x(d.cycle))
    .y(d => y(d.confidence))
    .curve(d3.curveMonotoneX);

  series.forEach(s => {
    if (s.points.length < 1) return;
    // Line
    g.append('path').datum(s.points)
      .attr('fill', 'none').attr('stroke', s.color)
      .attr('stroke-width', 2.5).attr('stroke-linecap', 'round')
      .attr('d', line);
    // Area fill
    const area = d3.area()
      .x(d => x(d.cycle)).y0(h).y1(d => y(d.confidence))
      .curve(d3.curveMonotoneX);
    g.append('path').datum(s.points)
      .attr('fill', s.color).attr('fill-opacity', 0.06)
      .attr('d', area);
    // Dots
    g.selectAll('.dot-' + s.id).data(s.points).enter()
      .append('circle')
      .attr('cx', d => x(d.cycle)).attr('cy', d => y(d.confidence))
      .attr('r', 3.5).attr('fill', s.color).attr('stroke', '#0a0e14').attr('stroke-width', 1.5)
      .attr('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 6);
        const conf = Math.round(d.confidence * 100);
        const shortClaim = d.claim.length > 80 ? d.claim.substring(0, 80) + '...' : d.claim;
        tooltip.innerHTML = `<div class="cct-conf" style="color:${s.color}">${conf}%</div>` +
          `<div class="cct-claim">${esc(shortClaim)}</div>` +
          (d.reason ? `<div class="cct-reason">${esc(d.reason)}</div>` : '');
        tooltip.style.display = 'block';
        tooltip.style.left = Math.min(event.offsetX + 15, W - 200) + 'px';
        tooltip.style.top = (event.offsetY - 10) + 'px';
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 3.5);
        tooltip.style.display = 'none';
      });
  });

  // Legend
  legend.innerHTML = series.map(s => {
    const shortClaim = s.claim.length > 30 ? s.claim.substring(0, 30) + '...' : s.claim;
    const lastConf = s.points.length ? Math.round(s.points[s.points.length - 1].confidence * 100) : 0;
    return `<div class="ccl-item"><div class="ccl-line" style="background:${s.color}"></div><span class="ccl-label" title="${esc(s.claim)}">${esc(shortClaim)} (${lastConf}%)</span></div>`;
  }).join('');
}

// Poll monitoring when tab is active
setInterval(pollMonitoring, 3000);

// Poll coverage when tab is active (reads /api/coverage, read-only)
async function pollCoverage(){
  const covTab=document.querySelector('.tab[data-tab="coverage"]');
  if(!covTab||!covTab.classList.contains('active'))return;
  if(liveOnly('/api/coverage'))return;
  try{
    const r=await fetch(API+'/api/coverage');const d=await r.json();
    const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
    set('covIdentified',d.identified??0);
    set('covPct',(d.fulltext_coverage_pct??0)+'%');
    set('covFulltext',d.fulltext_available??0);
    set('covExtracted',d.data_extracted??0);
    set('covPoolable',d.poolable_effects??0);
    set('covManual',d.manual_required??0);
    set('covUnclear',d.license_unclear??0);
    set('covFailed',d.failed??0);
    set('covAuthorReq',d.author_requests_awaiting_approval??0);
    set('covNoEndpoints',d.fulltext_without_endpoints??0);
    const sc=d.status_counts||{};
    const entries=Object.entries(sc);
    const box=document.getElementById('covStatus');
    if(box)box.innerHTML=entries.length
      ?entries.map(([k,v])=>`<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2)">${esc(k)}: <b style="color:var(--t1)">${v}</b></div>`).join('')
      :'<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">Kein Studium registriert</div>';
    const cnt=document.getElementById('covStatusCnt');
    if(cnt)cnt.textContent=entries.reduce((a,[,v])=>a+v,0);
  }catch(e){}
}
setInterval(pollCoverage,3000);
// Poll meta-analysis when tab is active (reads /api/metaanalysis, read-only)
async function pollMeta(){
  const tab=document.querySelector('.tab[data-tab="meta"]');
  if(!tab||!tab.classList.contains('active'))return;
  if(liveOnly('/api/metaanalysis'))return;
  try{
    const r=await fetch(API+'/api/metaanalysis');const d=await r.json();
    const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
    set('maUsable',d.usable??0);
    set('maEffectRows',d.effect_rows??0);
    const box=document.getElementById('maGroups');
    const groups=Object.entries(d.groups||{});
    const grades=d.grade||{};
    if(box)box.innerHTML=groups.length
      ?groups.map(([key,g])=>{
        const show=g.pooled!=null;
        const gr=grades[key];
        const gradeLine=gr
          ?'<br>GRADE (maschinell): <b style="color:var(--t1)">'+esc(gr.rating)+'</b>'
            +' <span style="color:var(--t3)">(Start '+esc(gr.start)+'; '
            +((gr.downgrades||[]).length?'Abwertungen: '+esc((gr.downgrades||[]).join(' | ')):'keine Abwertung')+')</span>'
          :'';
        return '<div style="padding:10px;background:var(--bg2);border:1px solid var(--bdr);border-radius:8px;margin-bottom:8px">'
          +'<div style="font-size:12px;color:var(--t1);font-weight:600;margin-bottom:4px">'+esc(g.outcome??key)+'</div>'
          +'<div style="font-size:11px;color:var(--t2)">k=<b>'+(g.k??0)+'</b> '
          +(show
            ?'· gepoolt <b>'+Number(g.pooled).toFixed(3)+'</b> ['+Number(g.ci_low).toFixed(3)+'; '+Number(g.ci_high).toFixed(3)+']'
              +(g.weight_type?' <span style="color:var(--t3)">('+esc(g.weight_type)+')</span>':'')
              +(g.i2!=null?' · I\u00B2='+Number(g.i2).toFixed(1)+'%':'')
              +(g.tau!=null?' · \u03C4='+Number(g.tau).toFixed(3):'')
            :'<span style="color:var(--t3)">kein Pooling ('+esc(g.note||'')+')</span>')
          +(show&&g.pi_low!=null
            ?'<br>Pr\u00E4diktionsintervall: '+Number(g.pi_low).toFixed(3)+' bis '+Number(g.pi_high).toFixed(3)
            :'')
          +gradeLine
          +'</div></div>';
      }).join('')
      :'<div class="empty">Noch keine poolbaren Effektzeilen</div>';
    const pr=d.prisma||{};
    const pbox=document.getElementById('maPrisma');
    const robCounts={low:0,some_concerns:0,high:0,strittig:0};
    (d.risk_of_bias||[]).forEach(r=>{
      if(!r||!r.overall)return;
      if(r.disputed){robCounts.strittig++;return;}
      const k=String(r.overall).toLowerCase();
      if(k in robCounts)robCounts[k]++;
    });
    const robLine='<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2)">Risk-of-Bias (maschinell): '
      +'<b style="color:var(--t1)">'+robCounts.low+'</b> low / '
      +'<b style="color:var(--t1)">'+robCounts.some_concerns+'</b> concerns / '
      +'<b style="color:var(--t1)">'+robCounts.high+'</b> high'
      +(robCounts.strittig?' / <b>'+robCounts.strittig+'</b> strittig':'')+'</div>';
    const pent=Object.entries(pr).concat([['__rob__',robLine]]);
    if(pbox)pbox.innerHTML=pent.length
      ?pent.map(([k,v])=>k==='__rob__'?v:'<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2)">'+esc(k)+': <b style="color:var(--t1)">'+v+'</b></div>').join('')
      :'<div style="padding:4px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t3)">Keine Screening-Daten</div>';
    const exl=(d.excluded||[]).concat(d.off_target||[]);
    const eCnt=document.getElementById('maExcludedCnt');
    if(eCnt)eCnt.textContent=exl.length;
    const ex=document.getElementById('maExcluded');
    if(ex)ex.innerHTML=exl.length
      ?exl.slice(0,20).map(e=>'<div style="padding:6px 10px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--t2);margin-bottom:4px">'+esc(e.label||e.outcome||'-')+' \u2014 <span style="color:var(--t3)">'+esc(e.reason||'')+'</span></div>').join('')
      :'<div class="empty">Keine Ausschl\u00FCsse</div>';
  }catch(e){}
}
setInterval(pollMeta,3000);
// Initial poll if monitoring tab is active
setTimeout(pollMonitoring, 500);
