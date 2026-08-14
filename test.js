/* Smoke tests for index.html
   Run:  npm i jsdom  &&  node trading-glossary-v3.test.js
   Every assertion below protects something that is easy to break by accident. */
const {JSDOM}=require("jsdom");
const fs=require("fs"),path=require("path");
const FILE=path.join(__dirname,"index.html");
/* 1006 -> 1001 on 2026-08-13: five duplicate entries deleted (Killzone,
   Power of three, OTE, Order book / depth, and the ICT copy of Liquidity)
   — an intended content change, not a rendering regression. */
/* 1001 -> 995: six more merge-era duplicates deleted (Support, Resistance,
   Trendline / channel, Swing high / low, In-sample / out-of-sample,
   Multiple comparisons) — all had zero inbound references; names remain
   searchable via alt text on their keepers. Intended content change. */
/* CHARTS 73 -> 72: Support and Resistance each carried a chart; merged
   into Support / resistance, one chart renders in the grid and the other
   in the detail panel via viz2 — so the grid shows one fewer. */
/* CHARTS 72 -> 78 on 2026-08-14: six of the most-referenced structural
   terms shipped with no chart at all — Break of structure, Change of
   character, False breakout, Stop hunt, Retest and Trendline. Each gained
   a primary chart (which lands in the grid, hence this count) plus a
   counter-case second chart (which renders in the detail panel only and
   does not). Intended content change, added by add_charts.py — not a
   rendering regression. */
/* TERMS 995 -> 1002 and SECTIONS 48 -> 49 on 2026-08-14: a "Named systems
   & frameworks" section, added by add_systems.py, covering seven systems
   that come with a name attached — Orochi, the Turtle system, Connors
   RSI-2, Darvas box, dual momentum, pairs trading and statistical
   arbitrage. They are glossary ENTRIES describing frameworks, never rule
   sets, and none of them went anywhere near the strategy library, which
   test group 18 still requires to ship empty. No charts, so EXPECT_CHARTS
   is unchanged. Intended content change.
   1002 -> 1010: a second batch into the same section (add_systems2.py) —
   60/40, permanent portfolio, All Weather, value averaging, Dogs of the
   Dow, London breakout, Wolfe wave and the three-drive pattern. */
const EXPECT_TERMS=1010, EXPECT_CHARTS=78, EXPECT_SECTIONS=49;

let pass=0,fail=0;
const ok=(c,m)=>{if(c){pass++;}else{fail++;console.log("  FAIL  "+m);}};
const eq=(a,b,m)=>ok(a===b,m+"  (got "+JSON.stringify(a)+", want "+JSON.stringify(b)+")");
const near=(a,b,t,m)=>ok(Math.abs(a-b)<=t,m+"  (got "+a+", want ~"+b+")");

function boot(url,opts){
  opts=opts||{};
  const errs=[];
  const dom=new JSDOM(fs.readFileSync(FILE,"utf8"),{runScripts:"dangerously",url:url||"https://example.com/a.html",
    beforeParse(w){
      w.onerror=e=>errs.push(String(e));
      w.HTMLElement.prototype.scrollIntoView=function(){};
      Object.defineProperty(w,"isSecureContext",{value:true});
      /* jsdom <30 doesn't expose these to the window; the share path needs them.
         Node has them globally, so hand them over rather than pinning a version. */
      if(typeof w.TextEncoder==="undefined") w.TextEncoder=TextEncoder;
      if(typeof w.TextDecoder==="undefined") w.TextDecoder=TextDecoder;
      if(typeof w.CompressionStream==="undefined"&&typeof CompressionStream!=="undefined") w.CompressionStream=CompressionStream;
      /* jsdom implements no object URLs, so the CSV export's anchor path
         cannot run without this. Same reason as the polyfills above:
         supply what the environment lacks rather than pinning a version. */
      if(w.URL&&typeof w.URL.createObjectURL!=="function"){
        w.URL.createObjectURL=function(){return "blob:test";};
        w.URL.revokeObjectURL=function(){};
      }
      if(typeof w.DecompressionStream==="undefined"&&typeof DecompressionStream!=="undefined") w.DecompressionStream=DecompressionStream;
      Object.defineProperty(w.navigator,"clipboard",{value:{writeText:t=>{dom.__copied=t;return Promise.resolve();}},configurable:true});
      if(opts.offline){
        Object.defineProperty(w.navigator,"onLine",{value:false,configurable:true});
      }
      if(opts.noStorage){
        /* a browser with storage disabled throws on every access */
        Object.defineProperty(w,"localStorage",{configurable:true,get(){throw new Error("storage disabled");}});
      }
    }});
  dom.__errs=errs;
  return dom;
}
const wait=ms=>new Promise(r=>setTimeout(r,ms));

(async()=>{
console.log("\n1. Boot and content");
const dom=boot(); await wait(700);
const w=dom.window,d=w.document;
eq(dom.__errs.length,0,"no console errors on load");
eq(d.querySelectorAll("#grid .entry").length,EXPECT_TERMS,"term count");
eq(d.querySelectorAll("#grid figure svg").length,EXPECT_CHARTS,"chart count");
eq(d.querySelectorAll("#grid section").length,EXPECT_SECTIONS,"section count");
/* The corpus now legitimately contains the word "NaN" (the Data quality entry
   talks about NaNs in a feed), so scope the NaN check to chart output — which
   is what this assertion was actually protecting — and keep "undefined"
   checked across the whole grid. */
ok(![...d.querySelectorAll("#grid figure svg")].some(s=>/NaN/.test(s.outerHTML)),
   "no NaN coordinates in any rendered chart");
ok(!/undefined/.test(d.getElementById("grid").innerHTML),"no undefined leaked into the grid");
eq(d.querySelectorAll(".lnk").length,EXPECT_TERMS,"every term has a copy-link button");

console.log("2. Chart data integrity");
const blocks=[...fs.readFileSync(FILE,"utf8").matchAll(/<script>([\s\S]*?)<\/script>/g)]
  .map(m=>m[1]).filter(s=>!/document\.getElementById/.test(s));
const D=new Function(blocks.join("\n")+"; return D;")();
let badCandle=0;
D.forEach(x=>{ if(!x.v||x.v.k!=="c")return;
  x.v.d.forEach(c=>{ const[o,hi,lo,cl]=c;
    if(hi<Math.max(o,cl)-1e-9||lo>Math.min(o,cl)+1e-9||hi<lo) badCandle++; }); });
eq(badCandle,0,"every OHLC candle is internally valid");
const get=n=>D.find(x=>x.t===n);
const fvg=get("Fair value gap").v; ok(fvg.d[0][1]<fvg.d[2][2],"FVG: candle 1 high is below candle 3 low");
const en=get("Engulfing").v, p=en.d[1], c2=en.d[2];
ok(Math.min(c2[0],c2[3])<=Math.min(p[0],p[3])&&Math.max(c2[0],c2[3])>=Math.max(p[0],p[3]),"Engulfing: body covers prior body");
const hm=get("Hammer").v.d[1]; ok((Math.min(hm[0],hm[3])-hm[2])>2*Math.abs(hm[0]-hm[3]),"Hammer: lower wick > 2x body");
const sw=get("Liquidity sweep").v; ok(sw.d[3][1]>sw.hl[0].p&&sw.d[3][3]<sw.hl[0].p,"Sweep: wicks above then closes back inside");
const sp=get("Spring").v; ok(sp.d[3][2]<sp.hl[0].p&&sp.d[3][3]>sp.hl[0].p,"Spring: dips below range low and reclaims");

console.log("3. Search");
const q=d.getElementById("q");
const shown=()=>[...d.querySelectorAll("#grid .entry")].filter(e=>e.style.display!=="none");
q.value="stop hunt"; q.dispatchEvent(new w.Event("input"));
ok(shown().some(e=>/Liquidity sweep/.test(e.textContent)),"synonym: 'stop hunt' finds Liquidity sweep");
q.value="rr"; q.dispatchEvent(new w.Event("input"));
ok(shown().length<8&&shown().some(e=>/Risk:reward/.test(e.textContent)),"synonym: 'rr' finds Risk:reward without flooding");
q.value="liquidity"; q.dispatchEvent(new w.Event("input"));
ok(d.querySelectorAll("#grid mark").length>0,"matches get highlighted");
q.value=""; q.dispatchEvent(new w.Event("input"));
eq(d.querySelectorAll("#grid mark").length,0,"highlights cleared on empty search");
eq(shown().length,EXPECT_TERMS,"all terms restored");

console.log("4. Strategies: validation and evidence model");
d.getElementById("tab-strats").dispatchEvent(new w.Event("click"));
d.getElementById("b-add").dispatchEvent(new w.Event("click"));
d.getElementById("f-save").dispatchEvent(new w.Event("click"));
ok(/name/i.test(d.getElementById("f-err").textContent),"rejects a strategy with no name");
d.getElementById("f-name").value="Test play";
d.getElementById("f-save").dispatchEvent(new w.Event("click"));
ok(/entry|invalidation/i.test(d.getElementById("f-err").textContent),"rejects a strategy with no rules");
d.getElementById("f-entry").value="Sweep of the session high, 5m close back below.";
d.getElementById("f-evidence").value="backtested";
d.getElementById("f-sampleSize").value="0";
d.getElementById("f-save").dispatchEvent(new w.Event("click"));
ok(/sample size/i.test(d.getElementById("f-err").textContent),"rejects 'backtested' with sample size 0");
d.getElementById("f-sampleSize").value="120";
d.getElementById("f-save").dispatchEvent(new w.Event("click"));
ok(d.querySelectorAll(".scard").length>=2,"strategy added");

console.log("5. Trade log maths");
[...d.querySelectorAll("[data-t]")][0].dispatchEvent(new w.Event("click"));
const k=d.querySelector("[data-addtrade]").dataset.addtrade;
const log=r=>{d.getElementById("t-r-"+k).value=String(r);
  d.querySelector("[data-addtrade]").dispatchEvent(new w.Event("click"));};
[3,-1,-1,-1,3,-1,-1,3,-1,-1].forEach(log);   /* 3 wins @3R, 7 losses @1R */
const out=d.querySelector(".out").textContent.replace(/\s+/g," ");
ok(/n=10/.test(out),"sample size comes from the log");
ok(/30%/.test(out),"win rate computed (3 of 10)");
near(parseFloat(out.match(/expectancy \+?(-?\d+\.\d+)R/)[1]),0.20,0.01,"expectancy = (3*3 - 7*1)/10 = +0.20R");
ok(/max drawdown 3\.0R/.test(out),"max drawdown computed");
ok(/95% CI/.test(out),"confidence interval shown");
ok(/n=10/.test(d.querySelector(".badge").textContent),"badge uses the log length, not the typed number");
ok(d.querySelectorAll(".scard figure svg").length>0,"equity curve rendered");

console.log("6. Sharing round-trip");
d.getElementById("b-share").dispatchEvent(new w.Event("click"));
await wait(300);
ok(dom.__copied&&dom.__copied.indexOf("#lib=")>0,"share link built");
const dom2=boot(dom.__copied); await wait(800);
const d2=dom2.window.document;
eq(dom2.__errs.length,0,"recipient page loads without errors");
ok(!d2.getElementById("panel-strats").hidden,"recipient lands on the Strategies tab");
ok(!!d2.querySelector(".banner"),"recipient sees the Keep/Discard banner");
ok(d2.querySelectorAll(".scard").length>=2,"shared strategies visible before deciding");
eq(d2.defaultView.location.hash,"#strategies","giant payload cleaned out of the URL");
d2.getElementById("m-merge").dispatchEvent(new dom2.window.Event("click"));
ok(/Merged/.test(d2.querySelector(".note").textContent),"merge completes");

console.log("7. XSS from an untrusted share link");
const dom3=boot(); await wait(700);
const d3=dom3.window.document;
d3.getElementById("tab-strats").dispatchEvent(new dom3.window.Event("click"));
d3.getElementById("b-add").dispatchEvent(new dom3.window.Event("click"));
d3.getElementById("f-name").value='<img src=x onerror="window.__pwned=1">';
d3.getElementById("f-entry").value='<script>window.__pwned=1<\/script>';
d3.getElementById("f-save").dispatchEvent(new dom3.window.Event("click"));
await wait(150);
eq(d3.querySelectorAll("#slist img").length,0,"no img element created from a hostile name");
eq(d3.querySelectorAll("#slist script").length,0,"no script element created from hostile rule text");
ok(!dom3.window.__pwned,"payload did not execute");

console.log("8. Quiz");
d3.getElementById("tab-quiz").dispatchEvent(new dom3.window.Event("click"));
eq(d3.querySelectorAll(".qopt").length,4,"four options offered");
const secs=[...d3.querySelectorAll(".qopt .qsec")].map(x=>x.textContent);
eq(new Set(secs).size,1,"distractors come from the same section");
d3.querySelector(".qopt").dispatchEvent(new dom3.window.Event("click"));
ok(!!d3.querySelector(".qres"),"answer is graded");
ok(!!d3.querySelector(".qexp"),"explanation shown after answering");
d3.getElementById("q-next").dispatchEvent(new dom3.window.Event("click"));
eq(d3.querySelectorAll(".qopt").length,4,"next question loads");
d3.getElementById("q-mode").value="chart";
d3.getElementById("q-mode").dispatchEvent(new dom3.window.Event("change"));
ok(!!d3.querySelector("#qbody .qfig"),"chart mode shows a chart");
d3.getElementById("q-cat").value="ict";
d3.getElementById("q-cat").dispatchEvent(new dom3.window.Event("change"));
ok([...d3.querySelectorAll(".qopt .qsec")].every(x=>/ICT/.test(x.textContent)),"section filter applies");

console.log("9. Accessibility basics");
eq(d.getElementById("count").getAttribute("aria-live"),"polite","term count is announced");
eq(d.getElementById("sstats").getAttribute("aria-live"),"polite","strategy stats announced");
/* 4 -> 5 on 2026-08-13: the Paper tab (local simulator, Task 9) was added
   deliberately. */
eq(d.querySelectorAll('[role="tab"]').length,5,"five tabs with role=tab");
ok([...d.querySelectorAll('[role="tab"]')].every(t=>t.getAttribute("aria-controls")),"tabs point at their panels");
ok([...d.querySelectorAll(".lnk")].every(b=>b.getAttribute("aria-label")),"copy-link buttons are labelled");


console.log("10. Live chart tab");
const dom4=boot(); await wait(700);
const w4=dom4.window,d4=dom4.window.document;
d4.getElementById("tab-live").dispatchEvent(new w4.Event("click"));
ok(!d4.getElementById("panel-live").hidden,"live panel opens");
const frame=()=>d4.querySelector("#lframe iframe");
ok(!!frame(),"an iframe is built");
ok(/tradingview\.com/.test(frame().getAttribute("src")),"embed points at TradingView");
ok(/NAS100/.test(decodeURIComponent(frame().getAttribute("src"))),"default symbol is a verified-working Nasdaq feed");
ok(!/CME_MINI/.test(d4.getElementById("ltools").innerHTML),"no CME futures symbols offered — the free embed cannot render them");
ok(/proxy/i.test(d4.getElementById("lnote").textContent),"index proxies are labelled as proxies, not as the futures contract");
/* allow-same-origin is required for the widget to render at all, and is safe
   here because the frame is cross-origin — it grants TradingView its own origin,
   not ours. What actually matters is that the frame cannot navigate us away or
   pop modals, so assert on those. */
ok(/allow-same-origin/.test(frame().getAttribute("sandbox")||""),
   "frame keeps allow-same-origin (widget renders blank without it)");
ok(!/allow-top-navigation/.test(frame().getAttribute("sandbox")||""),
   "frame cannot navigate the top-level page");
ok(!/allow-modals|allow-downloads/.test(frame().getAttribute("sandbox")||""),
   "frame cannot open modals or trigger downloads");
ok(!!frame().getAttribute("title"),"iframe is labelled for screen readers");
const src0=frame().getAttribute("src");
const sym=d4.getElementById("l-sym"); sym.value="BINANCE:BTCUSDT";
sym.dispatchEvent(new w4.Event("change"));
ok(frame().getAttribute("src")!==src0,"changing symbol rebuilds the embed");
ok(/BTCUSDT/.test(decodeURIComponent(frame().getAttribute("src"))),"new symbol is in the embed url");
const src1=frame().getAttribute("src");
const tf=d4.getElementById("l-tf"); tf.value="D";
tf.dispatchEvent(new w4.Event("change"));
ok(frame().getAttribute("src")!==src1,"changing timeframe rebuilds the embed");
ok(/interval=D/.test(frame().getAttribute("src")),"new timeframe is in the embed url");
ok(!!d4.getElementById("lnote").textContent.trim(),"a note explains the tab needs a connection");
ok(!!d4.querySelector("#lhint .spotcard svg"),"spot-the-pattern card reuses the chart engine");
d4.getElementById("l-another").dispatchEvent(new w4.Event("click"));
ok(!!d4.querySelector("#lhint .spotcard svg"),"'Another' redraws the spot card");
eq(dom4.__errs.length,0,"no console errors on the live tab");

console.log("11. Offline degradation");
/* The static note always mentions needing a connection, so asserting on that
   word proves nothing. Require a distinct offline state that is absent when
   online, and require we don't build a frame we know cannot load. */
/* the load-failure fallback shares the .offline class but ships hidden, so
   assert on what the user can actually see */
ok(!d4.querySelector("#panel-live .offline:not([hidden])"),"no offline notice visible while online");
ok(!!d4.querySelector("#panel-live .framefail[hidden]"),"a load-failure fallback exists but starts hidden");
const dom5=boot(null,{offline:true}); await wait(700);
const d5=dom5.window.document;
d5.getElementById("tab-live").dispatchEvent(new dom5.window.Event("click"));
const off=d5.querySelector("#panel-live .offline");
ok(!!off,"offline shows a distinct notice rather than a blank box");
ok(/offline|no connection|reconnect/i.test(off?off.textContent:""),"the notice explains the state in plain words");
eq(d5.querySelectorAll("#lframe iframe").length,0,"no iframe is built when we already know we're offline");
ok(!!d5.querySelector("#lhint .spotcard svg"),"the offline-safe spot-the-pattern card still renders");
eq(dom5.__errs.length,0,"no console errors while offline");

console.log("12. Saved terms filter");
const star=d.querySelector("#grid .star");
ok(!!star,"every term has a save control");
eq(d.querySelectorAll("#grid .star").length,EXPECT_TERMS,"save control on all terms");
star.dispatchEvent(new w.Event("click"));
ok(star.classList.contains("on"),"clicking marks the term saved");
const savedChip=[...d.querySelectorAll(".chip")].find(c=>/Saved/.test(c.textContent));
ok(!!savedChip,"a Saved filter chip exists");
savedChip.dispatchEvent(new w.Event("click"));
eq(shown().length,1,"Saved filter shows only saved terms");
star.dispatchEvent(new w.Event("click"));
ok(!star.classList.contains("on"),"clicking again unsaves");
[...d.querySelectorAll(".chip")].find(c=>c.textContent.trim()==="All").dispatchEvent(new w.Event("click"));
eq(shown().length,EXPECT_TERMS,"clearing the filter restores every term");

console.log("13. Storage resilience");
const dom6=boot(null,{noStorage:true}); await wait(700);
eq(dom6.__errs.length,0,"boots with localStorage throwing");
eq(dom6.window.document.querySelectorAll("#grid .entry").length,EXPECT_TERMS,"terms still render without storage");

console.log("14. Deep links, detail modes and templates");
/* The copy-link button emits #term-<data-slug>. The element id must match it or
   every shared link lands nowhere — this was broken and is now fixed. */
var badIds=0, sampleIds=[];
d.querySelectorAll("#grid .entry").forEach(function(e){
  if(e.id!=="term-"+e.dataset.slug){badIds++; if(sampleIds.length<3)sampleIds.push(e.id+" vs "+e.dataset.slug);}
});
eq(badIds,0,"every entry id matches the slug its copy-link uses"+(sampleIds.length?" ["+sampleIds.join(", ")+"]":""));
ok([...d.querySelectorAll(".lnk")].every(function(b){return !!d.getElementById("term-"+b.dataset.slug);}),
   "every copy-link target resolves to a real element");

ok(!!d.getElementById("d-simple")&&!!d.getElementById("d-full"),"detail toggle exists");
d.getElementById("d-simple").dispatchEvent(new w.Event("click"));
ok(d.body.classList.contains("simple"),"simple mode engages");
ok(d.querySelectorAll('#grid .entry[data-lvl="3"]').length>0,"advanced terms are marked so simple mode can hide them");
ok(d.querySelectorAll(".plaindef").length>20,"plain-language rewrites are present");
d.getElementById("d-full").dispatchEvent(new w.Event("click"));
ok(!d.body.classList.contains("simple"),"detailed mode returns");

ok(d.querySelectorAll(".condbox").length>10,"'what has to be true' blocks are attached");
var sweepEl=d.getElementById("term-liquidity-sweep");
ok(sweepEl&&/close|reclaim/i.test(sweepEl.querySelector(".condbox").textContent),"sweep conditions mention the reclaim, not just the poke");

var icEl=d.getElementById("term-iron-condor");
ok(icEl&&!!icEl.querySelector("figure svg"),"iron condor has a payoff diagram");
ok(icEl&&/path/.test(icEl.querySelector("figure svg").innerHTML),"payoff is drawn as a real path, not a placeholder");

d.getElementById("tab-strats").dispatchEvent(new w.Event("click"));
var qaRow=d.getElementById("qadd");
ok(!!qaRow,"quick-add row is present");
var ictBtn=qaRow?[...qaRow.querySelectorAll(".qbtn")].find(function(b){return /ICT/.test(b.textContent);}):null;
ok(!!ictBtn,"an ICT template exists");
if(ictBtn){
  ictBtn.dispatchEvent(new w.Event("click"));
  await wait(80);
  eq((d.getElementById("f-entry")||{}).value,"","ICT template leaves the entry rule blank rather than inventing one");
  eq((d.getElementById("f-invalidation")||{}).value,"","ICT template leaves invalidation blank");
  ok(/ict/i.test((d.getElementById("f-tags")||{}).value||""),"ICT template still pre-fills the tags");
}

console.log("15. Tape: config, exports, metadata");

/* --- config: empty constants must leave the app untouched --- */
ok(typeof w.TAPE==="object","TAPE config object exists");
eq(w.TAPE.url,"","url ships empty");
eq(w.TAPE.supportUrl,"","support link ships empty");
eq(w.TAPE.workbookUrl,"","workbook link ships empty");
eq(w.TAPE.accent,"","accent ships empty");
eq(d.querySelectorAll(".tapefoot").length,0,"no commercial footer rendered while constants are empty");
ok(!/Support this project/.test(d.getElementById("foot").textContent),"no support copy visible while unset");

/* --- export plumbing --- */
ok(typeof w.tapeExportPng==="function","export function is exposed");
ok(!!w.TAPE_PRESETS.square&&!!w.TAPE_PRESETS.portrait&&!!w.TAPE_PRESETS.landscape,"three presets defined");
eq(w.TAPE_PRESETS.square.w,1080,"square is 1080 wide");
eq(w.TAPE_PRESETS.portrait.h,1920,"portrait is 1920 tall");
eq(w.TAPE_PRESETS.landscape.w,1200,"landscape is 1200 wide");
ok(d.querySelectorAll("#grid figure .expbar").length>50,"export controls mounted on the charts");
eq(d.querySelectorAll("#grid figure .expbar").length,d.querySelectorAll("#grid figure svg").length,
   "every chart has export controls");
ok([...d.querySelectorAll(".expbtn")].every(function(b){return !!b.getAttribute("aria-label");}),
   "export buttons are labelled for screen readers");

/* the css-variable substitution is what stops exports rendering black */
var inlined=w.tapeInlineVars('<rect fill="var(--up)" stroke="var(--rule2)"/>',{"--up":"#0f0","--rule2":"#333"});
ok(!/var\(/.test(inlined),"css custom properties are substituted before rasterising");
ok(/#0f0/.test(inlined)&&/#333/.test(inlined),"substituted values are the computed ones");
eq(w.tapeInlineVars('<rect fill="var(--nope)"/>',{}),'<rect fill="#888"/>',"unknown variables fall back rather than breaking the svg");

/* --- carousel + post builder --- */
ok(typeof w.tapeCarousel==="function","carousel export is available");
ok(typeof w.tapeCaptionFor==="function","caption builder is available");
var capT=D.find(function(x){return x.t==="Liquidity sweep";});
var cap=w.tapeCaptionFor(capT);
ok(/LIQUIDITY SWEEP/.test(cap),"caption leads with the term");
ok(cap.indexOf(capT.d)>-1,"caption carries the definition");
ok(!/undefined|NaN/.test(cap),"caption has no undefined or NaN");
ok(!!d.getElementById("postbuilder"),"post builder is mounted");
ok(!!d.getElementById("pb-surprise")&&!!d.getElementById("pb-run"),"surprise and carousel controls exist");
ok(d.querySelectorAll("#pb-sec option").length>5,"carousel offers sections that actually have charts");

/* --- metadata --- */
ok(!!d.querySelector('meta[property="og:title"]'),"open graph title present");
ok(!!d.querySelector('meta[property="og:image"]'),"open graph image present");
ok(!!d.querySelector('meta[name="twitter:card"]'),"twitter card present");
ok(!!d.querySelector('link[rel="manifest"]'),"web app manifest linked");
ok(!!d.querySelector('link[rel="apple-touch-icon"]'),"apple touch icon present");
eq(d.querySelectorAll('meta[name="theme-color"]').length,2,"theme-color set for both colour schemes");
var man=d.querySelector('link[rel="manifest"]').getAttribute("href");
var manJson=JSON.parse(decodeURIComponent(man.replace(/^data:application\/manifest\+json,/,"")));
eq(manJson.short_name,"Tape","manifest names the app Tape");
eq(manJson.display,"standalone","manifest requests standalone display");

var ld=d.querySelector('script[type="application/ld+json"]');
ok(!!ld,"json-ld block injected");
var parsed=JSON.parse(ld.textContent);
eq(parsed["@type"],"DefinedTermSet","json-ld is a DefinedTermSet");
ok(parsed.hasDefinedTerm.length>100,"json-ld carries the glossary entries");
ok(parsed.hasDefinedTerm.every(function(t){return t.name&&t.description&&t.termCode;}),
   "every json-ld term has a name, description and code");

/* --- offline / no network --- */
var html=fs.readFileSync(FILE,"utf8");
var ext=(html.match(/(?:href|src)="https?:\/\/[^"]+"/g)||[])
  .filter(function(u){return !/s\.tradingview\.com/.test(u);});
eq(ext.length,0,"no external resource requests outside the live chart embed"+(ext.length?" ["+ext.slice(0,2).join(", ")+"]":""));
ok(!/fonts\.googleapis|fonts\.gstatic/.test(html),"no external webfonts — the file works offline");

/* --- workbook --- */
ok(!!d.getElementById("wbprint"),"print/PDF control present");

console.log("16. Term detail panel");

/* the panel exists and cards are reachable */
ok(!!d.getElementById("tpanel"),"detail panel is in the DOM");
ok(d.getElementById("tpanel").hidden,"panel starts closed");
ok([...d.querySelectorAll("#grid .entry")].every(function(e){return e.getAttribute("role")==="button";}),
   "every card is exposed as a button");
ok([...d.querySelectorAll("#grid .entry")].every(function(e){return e.getAttribute("tabindex")==="0";}),
   "every card is keyboard reachable");

/* clicking a card opens it with the right content */
var lsCard=d.getElementById("term-liquidity-sweep");
ok(!!lsCard,"a known term card exists");
lsCard.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
ok(!d.getElementById("tpanel").hidden,"card click opens the panel");
eq(d.getElementById("tp-title").textContent,"Liquidity sweep","panel shows the clicked term");
ok(d.querySelectorAll("#tpanel .tplong p").length>=3,"expanded write-up renders as paragraphs");
ok(!!d.querySelector("#tpanel .tpfig svg"),"the term's chart is carried into the panel");
ok(/typically used/i.test(d.getElementById("tpanel").textContent),"usage section present");
ok(/Used in these strategies/i.test(d.getElementById("tpanel").textContent),"strategy section present");
ok(d.querySelectorAll("#tpanel [data-goterm]").length>2,"related terms render as chips");
ok(!/undefined|NaN/.test(d.getElementById("tpanel").textContent),"panel leaks no undefined or NaN");

/* every term with a long body renders cleanly */
var longTerms=(w.D||[]).filter(function(x){return x.long;});
ok(longTerms.length>=20,"at least 20 terms carry an expanded body");
ok(longTerms.every(function(x){return !/undefined|NaN/.test(x.long+(x.usage||""));}),
   "no long body or usage string contains undefined or NaN");
ok(longTerms.every(function(x){return x.long.split(/\s+/).length>80;}),
   "every long body is substantially longer than the one-line definition");
/* The rule is "never claim a PATTERN has an edge or a success rate". A worked
   arithmetic illustration ("a system winning 40% of the time with 3:1 wins...")
   is teaching the formula, not asserting a statistic, so target attribution
   rather than any appearance of a percentage. */
ok(longTerms.every(function(x){
  return !/(this|the)\s+(pattern|setup|signal)[^.]{0,40}\d{1,3}\s?%/i.test(x.long)
      && !/success rate/i.test(x.long)
      && !/win rate of\s+\d/i.test(x.long)
      && !/\d{1,3}\s?% (?:accurate|reliable|of trades win)/i.test(x.long);
}),"no long body attributes a win rate or success percentage to a pattern");

/* related links all resolve to real terms */
var names={}; (w.D||[]).forEach(function(x){names[x.t]=1;});
var badSee=[];
(w.D||[]).filter(function(x){return x.see;}).forEach(function(x){
  x.see.forEach(function(n){ if(!names[n]) badSee.push(x.t+" -> "+n); });
});
eq(badSee.length,0,"every manual see-link resolves"+(badSee.length?" ["+badSee.slice(0,2).join(", ")+"]":""));

/* navigation without closing */
var relBtn=d.querySelector('#tpanel [data-goterm="spring"]');
if(relBtn){
  relBtn.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
  eq(d.getElementById("tp-title").textContent,"Spring","related chip swaps the panel content");
  ok(!d.getElementById("tpanel").hidden,"panel stays open while navigating");
}
ok(!!d.getElementById("tp-next")&&!!d.getElementById("tp-prev"),"previous and next controls exist");

/* escape closes */
d.dispatchEvent(new w.KeyboardEvent("keydown",{key:"Escape",bubbles:true}));
ok(d.getElementById("tpanel").hidden,"Escape closes the panel");

/* close button closes */
d.getElementById("term-drawdown").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
ok(!d.getElementById("tpanel").hidden,"panel reopens on another card");
d.getElementById("tp-close").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
ok(d.getElementById("tpanel").hidden,"close button dismisses the panel");

/* a term with no long body degrades rather than showing a hole */
/* Fixture chosen dynamically: any hard-coded term eventually gets written,
   which broke this test once (Pip).
   2026-08-14: the corpus reached 100% written, so no real term lacks a body
   any more and the old "find one" fixture had nothing to find. The path
   still has to work — every term added from here starts without a body —
   so synthesise the empty case by removing a body in memory and restoring
   it afterwards. Intended content change; the behaviour assertions below
   are unchanged. */
var stubTerm=(w.D||[]).find(function(x){return !x.long;}), savedLong;
if(!stubTerm){
  stubTerm=(w.D||[])[0];
  savedLong=stubTerm.long;
  delete stubTerm.long;
}
ok(!!stubTerm,"a term with no expanded body is available to test the placeholder path");
d.getElementById("term-"+stubTerm.t.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""))
 .dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
ok(!!d.querySelector("#tpanel .tpstub"),"terms without an expanded body show an honest placeholder");
ok(!/undefined/.test(d.getElementById("tpanel").textContent),"placeholder path leaks no undefined");
d.getElementById("tp-close").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
if(savedLong!==undefined)stubTerm.long=savedLong;   /* leave D as we found it */

/* deep link opens the panel directly */
var domDeep=boot("https://example.com/a.html#t=order-block"); await wait(900);
var dd=domDeep.window.document;
ok(!dd.getElementById("tpanel").hidden,"#t=slug deep link opens the panel on load");
eq(dd.getElementById("tp-title").textContent,"Order block","deep link opens the right term");
eq(domDeep.__errs.length,0,"deep-link boot produces no console errors");

/* clicking the star or copy button must not also open the panel */
var starBtn=d.querySelector("#grid .star");
var before=d.getElementById("tpanel").hidden;
starBtn.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
eq(d.getElementById("tpanel").hidden,before,"clicking the save star does not open the panel");
starBtn.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));

console.log("17. Chart walkthroughs");

ok(w.__walkable>40,"a large share of charted terms can be walked bar by bar");
ok(w.__walkCaptioned>=8,"the priority structural terms carry written step captions");

/* opening a charted term mounts a walkthrough */
d.getElementById("term-liquidity-sweep").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
await wait(120);
ok(!!d.querySelector(".wkbox"),"walkthrough mounts inside the panel");
ok(!!d.querySelector(".wkstage svg"),"walkthrough renders through the existing chart engine");
var cnt=d.querySelector(".wkcount").textContent;
ok(/^\d+ \/ \d+$/.test(cnt),"step counter shows position and total");

/* restart draws a single bar, stepping forward adds bars */
d.querySelector('[data-w="restart"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
eq(d.querySelector(".wkcount").textContent.split(" / ")[0],"1","restart returns to the first bar");
var capOne=d.querySelector(".wkcap").textContent;
ok(capOne.length>20,"the first step has a written caption");
d.querySelector('[data-w="next"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
eq(d.querySelector(".wkcount").textContent.split(" / ")[0],"2","next advances one bar");
ok(d.querySelector(".wkcap").textContent!==capOne,"the caption changes with the step");
d.querySelector('[data-w="prev"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
eq(d.querySelector(".wkcount").textContent.split(" / ")[0],"1","previous steps back");
ok(d.querySelector('[data-w="prev"]').disabled,"previous is disabled at the first bar");

/* walkthrough controls must not close or navigate the panel */
var titleBefore=d.getElementById("tp-title").textContent;
d.querySelector('[data-w="next"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
eq(d.getElementById("tp-title").textContent,titleBefore,"stepping does not change the term");
ok(!d.getElementById("tpanel").hidden,"stepping does not close the panel");

/* equity-curve charts walk as well as candle charts */
d.getElementById("tp-close").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
d.getElementById("term-drawdown").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
await wait(120);
ok(!!d.querySelector(".wkbox"),"equity-curve terms get a walkthrough too");
ok(/\/ \d\d/.test(d.querySelector(".wkcount").textContent),"drawdown walkthrough has its full step count");
d.getElementById("tp-close").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));

/* captions must not smuggle in claims the rest of the app refuses to make */
var capText=Object.keys(w.__walkCaptionSample||{}).length?"":"";
ok(!/\bbuy here\b|\bsell here\b|\bwill\s+(?:go|reverse|continue)\b/i.test(d.body.textContent),
   "no walkthrough caption tells the reader to buy, sell, or predicts what price will do");

/* offline guarantee still holds after adding walkthroughs */
var htmlNow=fs.readFileSync(FILE,"utf8");
var extNow=(htmlNow.match(/(?:href|src)="https?:\/\/[^"]+"/g)||[])
  .filter(function(u){return !/s\.tradingview\.com/.test(u);});
eq(extNow.length,0,"walkthroughs added no external requests — no video embeds, still offline");
ok(!/youtube|youtu\.be|vimeo|iframe src="https/i.test(htmlNow.replace(/s\.tradingview\.com[^"]*/g,"")),
   "no third-party video embeds were introduced");

console.log("18. Strategy provenance guard");
/* Eleven strategies were removed from this library because their rules were
   written from recall and then given citations. These assertions exist so that
   cannot happen again without a test going red. */
var SEED=w.TAPE_SEED||[];
eq(SEED.length,0,"the library ships with no strategies — rules must come from the user or a named file");

/* if anything is ever seeded, it must carry provenance and must not be
   attributed to someone whose rules were not supplied */
var named=/TJR|ICT|Connors|Raschke|Donchian|Dennis|Eckhardt|LeBeau|Larry Williams|Jegadeesh|Titman|Wyckoff/i;
ok(!SEED.some(function(s){return named.test(s.source||"")||named.test(s.name||"");}),
   "no seeded strategy is attributed to a named author");
ok(SEED.every(function(s){return s.provenance==="dictated"||s.provenance==="file";}),
   "any seeded strategy declares where its rules came from");
ok(SEED.every(function(s){return s.evidence==="untested"&&s.sampleSize===0;}),
   "any seeded strategy still ships untested at sample size 0");

/* the loader must not resurrect anything */
ok(typeof w.__loadSeed==="function","seed loader still exists");
eq(w.__loadSeed(),0,"loading the empty library adds nothing");

console.log("19. Statement import");

ok(typeof w.__parseStatement==="function","statement parser is available");

/* Dialect A: a prop-firm style export with a P&L column and accounting negatives.
   Hand-computed: +150, -75, +300, -75, +200  ->  net 500 over 5 trades.
   3 wins / 2 losses = 60% win rate. Gross win 650, gross loss 150 -> PF 4.333.
   Expectancy 500/5 = 100. Equity 150,75,375,300,500 -> peak 375 then 300, so
   max drawdown 75. */
var propCsv=
 "Symbol,Side,Qty,Entry Price,Exit Price,Realized P/L\n"+
 "MNQ,Buy,2,17500,17575,150\n"+
 "MNQ,Sell,2,17600,17637.5,(75)\n"+
 "MNQ,Buy,4,17400,17475,300\n"+
 "MNQ,Buy,2,17500,17462.5,(75)\n"+
 "MNQ,Sell,2,17700,17600,200\n";
var A=w.__parseStatement(propCsv,"prop.csv");
ok(!!A.stats,"prop-style CSV parses");
eq(A.stats.n,5,"all five trades read");
near(A.stats.net,500,0.01,"net P&L matches the hand-computed figure");
near(A.stats.expectancy,100,0.01,"expectancy is net divided by trade count");
near(A.stats.winRate,60,0.01,"win rate computed from the log");
near(A.stats.profitFactor,650/150,0.01,"profit factor is gross win over gross loss");
near(A.stats.maxDrawdown,75,0.01,"max drawdown measured peak to trough");
ok(A.stats.ciLow<A.stats.winRate&&A.stats.ciHigh>A.stats.winRate,"a Wilson interval brackets the win rate");
ok(A.stats.ciHigh-A.stats.ciLow>30,"five trades produce a very wide interval, as they should");

/* accounting negatives in brackets must read as losses, not gains */
ok(A.stats.losses===2,"bracketed figures are read as losses");

/* Dialect B: no P&L column — derive it from entry, exit, quantity and side.
   Long 1 from 100 to 110 = +10. Short 2 from 50 to 45 = +10. Long 1 from 20
   to 15 = -5. Net +15 over 3. */
var derivedCsv=
 "Instrument,Direction,Quantity,Open Price,Close Price\n"+
 "AAA,Long,1,100,110\n"+
 "BBB,Short,2,50,45\n"+
 "CCC,Long,1,20,15\n";
var B=w.__parseStatement(derivedCsv,"derived.csv");
eq(B.stats.n,3,"rows without a P&L column still parse");
near(B.stats.net,15,0.01,"P&L derived correctly, including the short");
ok(B.stats.wins===2&&B.stats.losses===1,"direction is respected when deriving P&L");

/* Dialect C: commissions must be subtracted, not ignored */
var feeCsv=
 "Symbol,Side,Qty,Entry,Exit,PnL,Commission\n"+
 "MNQ,Buy,1,100,110,10,2\n"+
 "MNQ,Buy,1,100,110,10,2\n";
var C=w.__parseStatement(feeCsv,"fees.csv");
near(C.stats.net,16,0.01,"commissions are deducted from gross P&L");
ok(C.map.fees!==undefined,"a commission column is detected when present");

/* quoted fields containing commas must not split the row */
var quotedCsv='Symbol,Note,PnL\n"MNQ","bought, then sold",50\n';
var Q=w.__parseStatement(quotedCsv,"quoted.csv");
eq(Q.stats.n,1,"quoted commas do not break the row");
near(Q.stats.net,50,0.01,"value after a quoted comma is read correctly");

/* junk input must fail honestly rather than inventing numbers */
var junk=w.__parseStatement("hello there\nno columns here\n","junk.csv");
ok(!junk.stats||junk.stats.n===0,"a file with no usable columns yields no stats rather than guesses");
var empty=w.__parseStatement("","empty.csv");
ok(!empty.stats,"an empty file yields no stats");

/* the UI must never claim an edge from a small sample */
d.getElementById("tab-strats").dispatchEvent(new w.Event("click"));
await wait(60);
ok(!!d.getElementById("impbox"),"import panel is mounted on the strategies tab");
ok(!!d.getElementById("impdrop"),"a drop target exists");
ok(d.getElementById("impdrop").getAttribute("tabindex")==="0","the drop target is keyboard reachable");
ok(/not uploaded|stays on your machine/i.test(d.getElementById("impbox").textContent),
   "the panel states plainly that nothing is uploaded");

/* no credential capture anywhere in the file — non-negotiable 8 */
var htmlNow=fs.readFileSync(FILE,"utf8");
ok(!/type="password"/i.test(htmlNow),"no password field exists anywhere");
ok(!/\b(api[_-]?key|apikey|secret|accessToken|access_token|bearer)\b\s*[:=]\s*["'][^"']+["']/i.test(htmlNow),
   "no credential is stored or hard-coded");
ok(!/id="[^"]*(apikey|api-key|token|secret|password)[^"]*"/i.test(htmlNow),
   "no input is named to collect a key, token, secret or password");

console.log("\n20. Paper \u2192 strategy link");
/* Regression: on a fresh profile the library lives ONLY under tg.strats.v1
   (boot marks tape.migrated before the Strategies tab first saves), so the
   Paper tab must read and write that key \u2014 found broken in a real browser
   on 2026-08-13 when the dropdown stayed empty. */
{
const domP=boot(); await wait(700);
const wp=domP.window,dp=wp.document;
ok(wp.localStorage.getItem("tg.strats.v1")!==null,"fresh profile: library seeded under the tg key");
ok(wp.localStorage.getItem("tape.strats.v1")===null,"fresh profile: no tape.strats.v1 copy exists");
dp.getElementById("tab-paper").click();
const sel=dp.getElementById("pp-strat");
ok([...sel.options].some(o=>o.value==="Example \u2014 delete me"),
   "strategy dropdown lists the library despite the key split");
dp.getElementById("pp-entry").value="23450";
dp.getElementById("pp-stop").value="23440";
dp.getElementById("pp-risk").value="1";
sel.value="Example \u2014 delete me";
dp.getElementById("pp-open-btn").click();
const SP=JSON.parse(wp.localStorage.getItem("tape.paper.v1"));
eq(SP.positions.length,1,"position opened");
eq(SP.positions[0].qty,2,"size derived from risk and stop distance ($50 \u00f7 $20/contract \u2192 2)");
dp.getElementById("pp-exit-"+SP.positions[0].id).value="23460";
dp.querySelector('#pp-open button[data-act="close"]').click();
const lib=JSON.parse(wp.localStorage.getItem("tg.strats.v1"));
const ex=lib.find(s=>s.name==="Example \u2014 delete me");
eq(ex.trades.length,1,"closing writes the R entry to the tg key the Strategies tab reads");
const tr=ex.trades[0];
ok(tr.n==="paper"&&tr.dir==="long"&&typeof tr.r==="number"&&/^\d{4}-\d{2}-\d{2}$/.test(tr.d),
   "log entry is {d,dir,r,n:'paper'}");
near(tr.r,0.89,0.01,"R is net of spread and commission on both fills");
eq(ex.sampleSize,1,"sampleSize tracks the trade log like the Strategies tab does");
ok(wp.localStorage.getItem("tape.strats.v1")===null,"the write went to the live key, not a dead copy");
/* the Strategies tab must show the new n without a page reload */
dp.getElementById("tab-strats").click(); await wait(60);
ok(/n=1/.test(dp.getElementById("panel-strats").textContent),
   "Strategies tab re-renders on tape:strats-changed \u2014 n=1 without reload");
}

console.log("\n21. SM-2 quiz scheduling");
{
ok(typeof w.__qgrade==="function","SM-2 grader is exposed for testing");
const today=new Date().toISOString().slice(0,10);
let s={n:1,w:0};
w.__qgrade(s,true);
ok(s.reps===1&&s.iv===1,"first correct answer: interval 1 day");
near(s.ef,2.5,0.001,"quality 4 leaves the easiness factor unchanged");
ok(/^\d{4}-\d{2}-\d{2}$/.test(s.due)&&s.due>today,"a due date lands in the future");
w.__qgrade(s,true);
ok(s.reps===2&&s.iv===6,"second correct answer: interval 6 days");
w.__qgrade(s,true);
ok(s.reps===3&&s.iv===15,"third correct answer: interval grows by the easiness factor (6 \u00d7 2.5)");
w.__qgrade(s,false);
ok(s.reps===0&&s.iv===1,"a wrong answer resets the repetition count and brings the term back tomorrow");
near(s.ef,1.96,0.001,"a wrong answer lowers the easiness factor");
for(let i=0;i<9;i++)w.__qgrade(s,false);
near(s.ef,1.3,0.001,"the easiness factor never falls below the SM-2 floor of 1.3");
/* the quiz flow reports the schedule after an answer */
d.getElementById("tab-quiz").dispatchEvent(new w.Event("click"));
await wait(60);
const opt=d.querySelector("#qbody .qopt");
ok(!!opt,"a question renders on the main dom");
opt.click(); await wait(30);
ok(/Next review/.test(d.getElementById("qbody").textContent),
   "answering shows when the term comes back");
ok(/due for review/.test(d.getElementById("qscore").textContent),
   "the score line reports how many seen terms are due");
}

console.log("\n22. Strategy detail view");
/* Own dom, like group 20. The shared `d` has been through twenty groups by
   now: the term panel can be left open with a pushed history entry, jsdom
   fires popstate from earlier history.back() calls on later ticks, and the
   body scroll-lock class survives. All of that moves focus for reasons that
   have nothing to do with this feature, so measure it on a clean boot. */
{
const domD=boot(); await wait(700);
const wd=domD.window, dd2=domD.window.document;
const d=dd2, w=wd;   /* keep the assertions below reading naturally */
d.getElementById("tab-strats").dispatchEvent(new w.Event("click"));
await wait(60);
const db=d.querySelector("[data-det]");
ok(!!db,"every card offers a Detail button");
/* scroll lock uses the body class the term panel also uses, so compare
   against the state on entry rather than assuming it starts clear */
const lockedBefore=d.body.classList.contains("tpopen");
/* a real click focuses the button; jsdom's .click() does not, and the
   overlay restores focus to whatever was active when it opened */
db.focus();
db.click(); await wait(30);
const ov=d.getElementById("sdetwrap");
ok(!!ov,"the detail overlay opens");
ok(/computed from the log/i.test(ov.textContent)||/Nothing logged yet/.test(ov.textContent),
   "results are computed from the log or honestly absent");
ok(/only reads/.test(ov.textContent),"the view states that logging stays on the card");
/* modal semantics must match the term panel — without the trap, Tab walks
   out of the overlay and into the 995-card grid behind it */
const dp=ov.querySelector(".sdet");
eq(dp.getAttribute("role"),"dialog","detail overlay is a dialog");
eq(dp.getAttribute("aria-modal"),"true","detail overlay is modal");
ok(!!d.getElementById(dp.getAttribute("aria-labelledby")),
   "aria-labelledby points at a heading that exists");
ok(d.body.classList.contains("tpopen"),"background scroll is locked while open");
ok(dp.getAttribute("tabindex")==="-1","the panel itself is programmatically focusable");
ok(dp.contains(d.activeElement),"focus moves into the overlay on open");
/* A re-render replaces the overlay's DOM. It must not yank focus when
   focus is genuinely elsewhere — use a real focusable element, since
   body.focus() is a no-op and would leave focus inside the overlay. */
const outside=d.getElementById("sq");
outside.focus();
d.dispatchEvent(new w.CustomEvent("tape:strats-changed"));
await wait(30);
ok(!!d.getElementById("sdetwrap"),"the overlay survives a re-render");
ok(d.activeElement===outside,"a re-render does not steal focus when focus is elsewhere");
/* Untrusted text reaches this view: a shared library link carries another
   person's JSON straight into these fields. Nothing may render as markup. */
{
const lib=JSON.parse(w.localStorage.getItem("tg.strats.v1")||"[]");
if(lib[0]){
  const payload='<img src=x onerror="window.__pwnedDetail=true">';
  lib[0].notes=payload; lib[0].entry=payload; lib[0].tags=[payload];
  lib[0].trades=[{d:"2026-08-14",dir:"long",r:1.5,n:payload}];
  lib[0].sampleSize=1;
  w.localStorage.setItem("tg.strats.v1",JSON.stringify(lib));
  d.dispatchEvent(new w.CustomEvent("tape:strats-changed"));
  await wait(40);
  const live=d.querySelector(".sdet");
  ok(!w.__pwnedDetail,"an injected payload does not execute in the detail view");
  eq(live?live.querySelectorAll("img").length:0,0,"no element is created from injected markup");
  ok(live&&/<img/.test(live.textContent),"the payload is shown as literal text instead");
}
}
/* the overlay's nodes were just replaced, so re-query before using them */
const dp2=d.querySelector(".sdet");
const foc=dp2.querySelectorAll('button:not([disabled]),[href],input,select,textarea,[tabindex]:not([tabindex="-1"])');
foc[foc.length-1].focus();
d.dispatchEvent(new w.KeyboardEvent("keydown",{key:"Tab",bubbles:true}));
ok(d.activeElement===foc[0],"Tab wraps to the first control instead of escaping the overlay");
d.dispatchEvent(new w.KeyboardEvent("keydown",{key:"Escape",bubbles:true}));
/* Read focus synchronously: closeDet restores it inline, and jsdom fires
   popstate from earlier groups' history.back() on a later tick, which can
   move focus for reasons unrelated to this feature. */
const focusAfterClose=d.activeElement;
const closedNow=!d.getElementById("sdetwrap");
const lockAfter=d.body.classList.contains("tpopen");
await wait(30);
ok(closedNow,"Escape closes the detail view");
eq(lockAfter,lockedBefore,"background scroll lock returns to its prior state on close");
/* the re-render above detached the original button, so focus must land on
   its replacement rather than being silently lost to the body */
ok(focusAfterClose&&focusAfterClose.getAttribute&&
   focusAfterClose.getAttribute("data-det")===db.getAttribute("data-det"),
   "focus returns to the Detail button even after the card list was rebuilt");
ok(focusAfterClose!==d.body,"focus is never left on the body when the overlay closes");
}

console.log("\n23. Fill-log pairing (bot and exchange exports)");
{
/* ccxt and most exchange/bot exports log FILLS \u2014 one row per leg, no P&L
   and no exit column \u2014 so the row-per-trade reading yields nothing. These
   get paired FIFO into round trips. */
const ccxt=
 "timestamp,symbol,side,amount,price,cost,fee\n"+
 "2026-08-01T10:00:00Z,BTC/USDT,buy,0.5,60000,30000,15\n"+
 "2026-08-01T14:00:00Z,BTC/USDT,sell,0.5,61000,30500,15\n";
const F=w.__parseStatement(ccxt,"bot.csv");
eq(F.stats.n,1,"two opposing fills pair into one round trip");
ok(F.paired===true,"the result is flagged as having been paired from fills");
near(F.stats.net,470,0.01,"P&L is gross less both legs' fees (500 - 30)");
eq(F.trades[0].dir,"long","the opening leg sets the direction");

/* a partial close leaves the rest open \u2014 an open position is not a trade */
const partial=
 "timestamp,symbol,side,amount,price\n"+
 "2026-08-01T10:00:00Z,ETH/USDT,buy,2,3000\n"+
 "2026-08-01T11:00:00Z,ETH/USDT,sell,1,3100\n";
const P2=w.__parseStatement(partial,"partial.csv");
eq(P2.stats.n,1,"a partial close produces one trade");
near(P2.stats.net,100,0.01,"only the closed quantity is counted");
eq(P2.skipped,1,"the still-open lot is reported, not closed at an invented price");

/* shorts: the opening leg is a sell, so profit is entry minus exit */
const shorts=
 "timestamp,symbol,side,amount,price\n"+
 "2026-08-01T10:00:00Z,NQ,sell,1,20000\n"+
 "2026-08-01T11:00:00Z,NQ,buy,1,19900\n";
const S2=w.__parseStatement(shorts,"short.csv");
eq(S2.trades[0].dir,"short","a sell-first sequence is read as a short");
near(S2.stats.net,100,0.01,"a short that falls 100 points makes 100");

/* closing more than is open flips the position rather than inventing a trade */
const flip=
 "timestamp,symbol,side,amount,price\n"+
 "2026-08-01T10:00:00Z,NQ,buy,1,20000\n"+
 "2026-08-01T11:00:00Z,NQ,sell,2,20100\n";
const FL=w.__parseStatement(flip,"flip.csv");
eq(FL.stats.n,1,"only the matched quantity becomes a trade");
near(FL.stats.net,100,0.01,"the matched leg is priced, the remainder is not");
eq(FL.skipped,1,"the reversed remainder is left open, not counted as profit");

/* FIFO, not average cost: the oldest lot closes first */
const fifo=
 "timestamp,symbol,side,amount,price\n"+
 "2026-08-01T10:00:00Z,NQ,buy,1,20000\n"+
 "2026-08-01T10:30:00Z,NQ,buy,1,20200\n"+
 "2026-08-01T11:00:00Z,NQ,sell,1,20100\n";
const FI=w.__parseStatement(fifo,"fifo.csv");
near(FI.trades[0].entry,20000,0.01,"the oldest lot is the one closed");
near(FI.stats.net,100,0.01,"FIFO gives +100 here; average cost would give 0");

/* a row with no side cannot be paired — guessing would mis-pair everything
   after it, so it is skipped rather than assumed to be a buy */
const blankSide=
 "timestamp,symbol,side,amount,price\n"+
 "2026-08-01T10:00:00Z,NQ,buy,1,20000\n"+
 "2026-08-01T10:30:00Z,NQ,,1,20050\n"+
 "2026-08-01T11:00:00Z,NQ,sell,1,20100\n";
const BS=w.__parseStatement(blankSide,"blank.csv");
eq(BS.stats.n,1,"a row with a blank side does not create or corrupt a pairing");
near(BS.stats.net,100,0.01,"the blank row is ignored, not treated as a fill");
ok(BS.skipped>=1,"the unusable row is reported as skipped");

/* a row-per-trade file must not be re-read as fills */
const rowPerTrade=
 "Symbol,Side,Qty,Entry,Exit,PnL\n"+
 "MNQ,Buy,1,100,110,10\n";
const RT=w.__parseStatement(rowPerTrade,"rows.csv");
ok(!RT.paired,"a file with a P&L column is never treated as a fill log");
}

console.log("\n21b. Paper CSV export round-trips through the importer");
{
const domX=boot(); await wait(700);
const wx=domX.window, dx=domX.window.document;
ok(typeof wx.__paperCsv==="function","the paper CSV builder is exposed for testing");
/* open and close two trades so there is something to export */
dx.getElementById("tab-paper").dispatchEvent(new wx.Event("click"));
await wait(40);
const put=function(id,v){const e=dx.getElementById(id);e.value=v;
  e.dispatchEvent(new wx.Event("input",{bubbles:true}));
  e.dispatchEvent(new wx.Event("change",{bubbles:true}));};
const doTrade=function(dir,entry,stop,exit){
  put("pp-entry",entry);put("pp-stop",stop);put("pp-risk","1");
  const d=dx.getElementById("pp-dir");d.value=dir;
  d.dispatchEvent(new wx.Event("change",{bubbles:true}));
  dx.getElementById("pp-open-btn").click();
  const st=JSON.parse(wx.localStorage.getItem("tape.paper.v1"));
  put("pp-exit-"+st.positions[0].id,exit);
  dx.querySelector('#pp-open button[data-act="close"]').click();
};
doTrade("long","23450","23440","23470");
doTrade("short","23500","23510","23480");
const csv=wx.__paperCsv();
const head=csv.split("\n")[0];
eq(csv.split("\n").length-1,2,"every closed trade becomes a row");
ok(/PnL_Gross/.test(head),"P&L is exported gross and labelled as such");
ok(/Commission/.test(head),"commission is exported alongside it");
ok(!!dx.getElementById("pp-export"),"the export button is offered once trades exist");
/* the point of the format: it must read back through the app's own
   importer without a converter, and without double-counting costs —
   the importer treats a P&L column as gross and deducts commission */
const back=wx.__parseStatement(csv,"roundtrip.csv");
const paperNet=JSON.parse(wx.localStorage.getItem("tape.paper.v1"))
  .closed.reduce(function(a,t){return a+t.pnl;},0);
eq(back.stats.n,2,"the importer reads both rows back");
near(back.stats.net,paperNet,0.01,
  "net survives the round trip exactly — costs are not deducted twice");
ok(!back.paired,"a row-per-trade export is not mistaken for a fill log");

/* Two environments. Opened normally an anchor download works; inside the
   published artifact viewer the sandbox blocks page-initiated saves, so
   the viewer mediates them through the downloads capability. Exactly one
   mechanism must fire — firing both would attempt a blocked download
   alongside the real save. */
{
let anchors=0;
const realClick=wx.HTMLAnchorElement.prototype.click;
wx.HTMLAnchorElement.prototype.click=function(){anchors++;};
const saves=[];
wx.claude={use:function(n){return Promise.resolve(n==="downloads"?{
  save:function(r){saves.push(r.filename);return Promise.resolve({status:"saved"});}}:null);}};
dx.getElementById("pp-export").click();
await wait(120);
eq(saves.length,1,"the capability save is used when the viewer provides one");
eq(anchors,0,"the anchor download does NOT also fire alongside it");
ok(/exported/.test(dx.getElementById("pp-msg").textContent),
   "the export reports success — a missing msg helper used to throw here");

/* csv is in the viewer's extended type set and can be refused; the same
   text as .txt still opens in a spreadsheet */
saves.length=0;
let first=true;
wx.claude={use:function(n){return Promise.resolve(n==="downloads"?{
  save:function(r){saves.push(r.filename);
    if(first){first=false;return Promise.reject({code:"extension_not_enabled",message:"no csv"});}
    return Promise.resolve({status:"saved"});}}:null);}};
dx.getElementById("pp-export").click();
await wait(150);
eq(saves.length,2,"a refused extension is retried once");
ok(/\.txt$/.test(saves[1]),"the retry uses a base-set extension");

/* declined is the viewer saying no — never silently treated as success */
saves.length=0;
wx.claude={use:function(n){return Promise.resolve(n==="downloads"?{
  save:function(r){saves.push(r.filename);
    return Promise.reject({code:"declined",message:"no"});}}:null);}};
dx.getElementById("pp-export").click();
await wait(150);
ok(/cancelled/i.test(dx.getElementById("pp-msg").textContent),
   "a declined save says so instead of claiming the file was exported");

/* no capability at all: the anchor is the mechanism */
delete wx.claude;
anchors=0;
dx.getElementById("pp-export").click();
await wait(60);
eq(anchors,1,"without a capability the anchor download is used");
wx.HTMLAnchorElement.prototype.click=realClick;
}

/* CSV formula injection: instrument and strategy names are free text, and
   a strategy name can arrive from someone else's shared library link. A
   cell starting with = + - @ runs as a formula when the file is opened in
   Excel or Sheets. */
put("pp-inst","=cmd|' /C calc'!A0");
doTrade("long","100","99","101");
const evilCsv=wx.__paperCsv();
const evilRow=evilCsv.split("\n").filter(function(r){return /cmd/.test(r);})[0];
ok(!!evilRow,"the formula-shaped instrument reached the export");
ok(/'=cmd/.test(evilRow),"a formula-shaped cell is prefixed so it cannot execute on open");
ok(!/(^|,)=cmd/.test(evilRow),"no cell begins with a bare = after neutralising");
/* numbers must survive untouched, or negative P&L would export as text */
const evilBack=wx.__parseStatement(evilCsv,"evil.csv");
eq(evilBack.stats.n,3,"the neutralised row still imports as a trade");
ok(/,-?\d/.test(evilRow),"numeric cells are left as numbers, not quoted into text");
}

console.log("\n22b. Strategy templates and the testability hint");
{
const domT=boot(); await wait(700);
const wt=domT.window, dt=domT.window.document;
dt.getElementById("tab-strats").dispatchEvent(new wt.Event("click"));
await wait(60);
const qrow=dt.getElementById("qadd");
ok(!!qrow,"the quick-add row is mounted");
const btns=[...qrow.querySelectorAll(".qbtn")];
ok(btns.length>=10,"there are at least ten templates  (got "+btns.length+")");
/* the whole point: templates carry structure, never rules */
btns.find(function(b){return b.textContent==="Breakout";}).click();
await wait(60);
const g=function(id){return dt.getElementById(id);};
ok(["f-bias","f-entry","f-invalidation","f-target"].every(function(id){return g(id)&&g(id).value==="";}),
   "a template leaves every rule field empty — nothing is invented for you");
ok(g("f-timeframe").value!=="","structure like timeframe IS prefilled");
ok(g("f-entry").placeholder.length>20,"rule fields carry a prompt asking what a testable rule needs");
/* placeholders must never become saved content */
ok(!/placeholder/i.test(g("f-entry").value),"the prompt is not the value");

/* the hint judges wording, not the idea */
const fe=g("f-entry");
const typed=function(v){fe.value=v;fe.dispatchEvent(new wt.Event("input",{bubbles:true}));
  return dt.getElementById("f-entry-tst");};
let h=typed("Enter when price breaks out with strong confirmation");
ok(h&&/Hard to test/.test(h.textContent),"vague wording is flagged");
ok(/strong/.test(h.textContent),"the flag names the word it objected to");
h=typed("Enter on the retest of the zone");
ok(h&&/nothing to test against/.test(h.textContent),"a rule with no number or bar event is flagged");
h=typed("Enter on the 15m close above the prior day high");
ok(h&&/checkable/.test(h.textContent),"a specific rule is recognised as checkable");
fe.value="";fe.dispatchEvent(new wt.Event("input",{bubbles:true}));
ok(!dt.getElementById("f-entry-tst"),"the hint disappears when the field is emptied");
/* advisory only — it must never block saving */
ok(!g("f-entry").hasAttribute("aria-invalid"),"the hint does not mark the field invalid");
}

console.log("\n23b. SM-2 when everything is already scheduled ahead");
{
/* After a heavy study session every term can be scheduled into the future.
   The quiz must still produce a question — reviewing early, soonest-due
   first — rather than claiming there is nothing to ask. Records are
   written before the quiz tab is ever opened so the module loads them
   fresh rather than from its cache. */
const domQ=boot(); await wait(700);
const wq=domQ.window, dq=wq.document;
const far=new Date(Date.now()+90*864e5).toISOString().slice(0,10);
const recs={};
(wq.D||[]).forEach(function(x){
  const k=x.t.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
  recs[k]={n:3,w:0,ef:2.5,reps:3,iv:90,due:far};
});
wq.localStorage.setItem("tg.quiz.v1",JSON.stringify(recs));
dq.getElementById("tab-quiz").dispatchEvent(new wq.Event("click"));
await wait(80);
ok(!!dq.querySelector("#qbody .qopt"),
   "a question still renders when every term is scheduled ahead");
ok(!/Not enough terms/.test(dq.getElementById("qbody").textContent),
   "the quiz does not claim it has nothing to ask");
ok(/0 due for review/.test(dq.getElementById("qscore").textContent),
   "the score line reports honestly that nothing is actually due");
eq(dq.querySelectorAll("#qbody .qopt").length,4,"four options are still offered");
}

console.log("\n24. Second charts (viz2) on the structural terms");
{
/* viz2 draws the counter-case \u2014 the chart that looks identical until it
   resolves the other way. It renders in the detail panel only, so the grid
   chart count must NOT move. */
const withViz2=(w.D||[]).filter(function(x){return x.viz2&&x.viz2.length;});
ok(withViz2.length>=9,"the structural terms carry a second chart  (got "+withViz2.length+")");
eq(d.querySelectorAll("#grid figure svg").length,EXPECT_CHARTS,
   "viz2 does not add charts to the grid");
ok(withViz2.every(function(x){return x.viz2.every(function(v){return v.cap&&v.cap.length>20;});}),
   "every second chart carries a caption explaining what it shows");
/* every spec must actually render, and render clean */
let rendered=0, corrupt=0;
withViz2.forEach(function(x){
  x.viz2.forEach(function(v){
    const svg=w.svgFor(v.v||v);
    if(svg&&/<svg/.test(svg)) rendered++;
    if(/NaN|undefined/.test(svg||"")) corrupt++;
  });
});
eq(corrupt,0,"no second chart renders NaN or undefined");
ok(rendered>=withViz2.length,"every second chart produces an svg");
/* and it reaches the panel */
const lsTerm=(w.D||[]).find(function(x){return x.t==="Liquidity sweep";});
d.getElementById("term-"+lsTerm.slug).dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
await wait(40);
ok(d.querySelectorAll("#tpanel .tpfig").length>=2,"the detail panel shows both charts");
d.getElementById("tp-close").dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
}

console.log("\n"+(fail?"FAILED":"PASSED")+" \u2014 "+pass+" assertions passed, "+fail+" failed\n");
process.exit(fail?1:0);
})();
