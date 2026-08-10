/* Smoke tests for index.html
   Run:  npm i jsdom  &&  node trading-glossary-v3.test.js
   Every assertion below protects something that is easy to break by accident. */
const {JSDOM}=require("jsdom");
const fs=require("fs"),path=require("path");
const FILE=path.join(__dirname,"index.html");
const EXPECT_TERMS=1006, EXPECT_CHARTS=73, EXPECT_SECTIONS=48;

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
eq(d.querySelectorAll('[role="tab"]').length,4,"four tabs with role=tab");
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

console.log("\n"+(fail?"FAILED":"PASSED")+" \u2014 "+pass+" assertions passed, "+fail+" failed\n");
process.exit(fail?1:0);
})();
