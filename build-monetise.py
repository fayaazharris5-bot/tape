import io, re

P = 'index.html'
s = io.open(P, encoding='utf-8').read()

MODULE = r'''
<script>
/* ====================================================================
   TAPE — CONFIG
   Every commercial surface is driven from here. An EMPTY string means
   the feature is completely hidden and the app behaves exactly as it
   did before this block existed. Nothing here phones home.
   ==================================================================== */
var TAPE = {
  name:      "Tape",
  wordmark:  "TAPE",
  url:       "",           /* e.g. "tape.example.com" — shown on exported images */
  accent:    "",           /* e.g. "#C0800C" — overrides --signal when set */
  supportUrl:"",           /* footer support link; hidden while empty */
  workbookUrl:"",          /* paid workbook link; hidden while empty */
  sections:  null,         /* null = all; or ["basics","risk"] to ship a subset */
  footer:    ""            /* extra footer line; hidden while empty */
};
if(TAPE.accent){
  try{ document.documentElement.style.setProperty("--signal", TAPE.accent); }catch(e){}
}
</script>

<script>
/* ====================================================================
   IMAGE EXPORT
   Serialises an existing SVG through XMLSerializer into a canvas and
   hands back a PNG blob. No library, no network.

   The one real trap: the charts are drawn with CSS custom properties
   (var(--up), var(--accent)...). Those do not resolve inside a
   standalone serialised SVG, so every var() is substituted with its
   computed value before rasterising, or the export comes out black.
   ==================================================================== */
var TAPE_PRESETS = {
  square:    {w:1080, h:1080, label:"Square 1080×1080"},
  portrait:  {w:1080, h:1920, label:"Portrait 1080×1920"},
  landscape: {w:1200, h:630,  label:"Landscape 1200×630"}
};

function tapeVars(){
  var cs = getComputedStyle(document.documentElement);
  var names = ["--paper","--card","--ink","--ink2","--ink3","--rule","--rule2",
               "--up","--down","--accent","--signal","--tint"];
  var out = {};
  names.forEach(function(n){ out[n] = (cs.getPropertyValue(n) || "").trim() || "#888"; });
  return out;
}

function tapeInlineVars(svgText, vars){
  return svgText.replace(/var\(\s*(--[a-z0-9-]+)\s*(?:,[^)]*)?\)/gi, function(m, name){
    return vars[name] || "#888";
  });
}

function tapeWrapText(ctx, text, maxW){
  var words = String(text).split(/\s+/), lines = [], line = "";
  for(var i=0;i<words.length;i++){
    var probe = line ? line+" "+words[i] : words[i];
    if(ctx.measureText(probe).width > maxW && line){ lines.push(line); line = words[i]; }
    else line = probe;
  }
  if(line) lines.push(line);
  return lines;
}

/* Returns a Promise for a PNG Blob. */
function tapeExportPng(svgEl, opts){
  opts = opts || {};
  var preset = TAPE_PRESETS[opts.preset] || TAPE_PRESETS.square;
  var vars = tapeVars();
  var W = preset.w, H = preset.h;

  var clone = svgEl.cloneNode(true);
  if(!clone.getAttribute("xmlns")) clone.setAttribute("xmlns","http://www.w3.org/2000/svg");
  var raw = new XMLSerializer().serializeToString(clone);
  raw = tapeInlineVars(raw, vars);
  /* the chart's text classes live in the page stylesheet, not the svg */
  raw = raw.replace(/<svg([^>]*)>/, '<svg$1><style>'+
    'text{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:9px;fill:'+vars["--ink3"]+'}'+
    '.lb{fill:'+vars["--ink3"]+'}.lbu{fill:'+vars["--up"]+'}.lbd{fill:'+vars["--down"]+'}'+
    '.lba{fill:'+vars["--accent"]+'}.lbs{fill:'+vars["--signal"]+'}.lbk{fill:'+vars["--ink"]+'}'+
    '</style>');

  var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(raw);

  return new Promise(function(resolve, reject){
    var img = new Image();
    img.onload = function(){
      try{
        var cv = document.createElement("canvas");
        cv.width = W; cv.height = H;
        var ctx = cv.getContext("2d");

        ctx.fillStyle = vars["--paper"]; ctx.fillRect(0,0,W,H);

        var pad = Math.round(W * 0.075);
        var innerW = W - pad*2;

        /* title */
        var titleSize = Math.round(W * 0.062);
        ctx.fillStyle = vars["--ink"];
        ctx.font = "700 "+titleSize+"px ui-sans-serif, system-ui, sans-serif";
        ctx.textBaseline = "top";
        var titleLines = tapeWrapText(ctx, opts.title || "", innerW).slice(0,2);
        var y = pad;
        titleLines.forEach(function(L){ ctx.fillText(L, pad, y); y += titleSize*1.12; });

        /* one line of definition */
        if(opts.subtitle){
          var subSize = Math.round(W * 0.028);
          ctx.fillStyle = vars["--ink2"];
          ctx.font = "400 "+subSize+"px ui-sans-serif, system-ui, sans-serif";
          y += Math.round(W*0.014);
          tapeWrapText(ctx, opts.subtitle, innerW).slice(0,3).forEach(function(L){
            ctx.fillText(L, pad, y); y += subSize*1.42;
          });
        }

        /* chart, scaled to fit what's left above the footer */
        var footerH = Math.round(W * 0.085);
        var availTop = y + Math.round(W*0.035);
        var availH = H - availTop - footerH - pad*0.5;
        var ar = (img.width && img.height) ? img.width/img.height : 320/150;
        var dw = innerW, dh = dw/ar;
        if(dh > availH){ dh = availH; dw = dh*ar; }
        var dx = pad + (innerW - dw)/2;
        var dy = availTop + Math.max(0,(availH - dh)/2);

        ctx.fillStyle = vars["--tint"];
        ctx.fillRect(pad, dy - Math.round(W*0.02), innerW, dh + Math.round(W*0.04));
        ctx.drawImage(img, dx, dy, dw, dh);

        /* caption */
        if(opts.caption){
          var capSize = Math.round(W*0.022);
          ctx.fillStyle = vars["--ink3"];
          ctx.font = "400 "+capSize+"px ui-sans-serif, system-ui, sans-serif";
          var capY = dy + dh + Math.round(W*0.032);
          tapeWrapText(ctx, opts.caption, innerW).slice(0,2).forEach(function(L){
            ctx.fillText(L, pad, capY); capY += capSize*1.4;
          });
        }

        /* attribution — the only thing that survives the file being copied */
        var markSize = Math.round(W*0.026);
        ctx.font = "700 "+markSize+"px ui-monospace, Menlo, Consolas, monospace";
        ctx.fillStyle = vars["--signal"];
        ctx.textBaseline = "alphabetic";
        ctx.fillText(TAPE.wordmark || "TAPE", pad, H - pad*0.75);
        if(TAPE.url){
          ctx.font = "400 "+markSize+"px ui-monospace, Menlo, Consolas, monospace";
          ctx.fillStyle = vars["--ink3"];
          ctx.textAlign = "right";
          ctx.fillText(TAPE.url, W - pad, H - pad*0.75);
          ctx.textAlign = "left";
        }

        if(cv.toBlob) cv.toBlob(function(b){ b ? resolve(b) : reject(new Error("toBlob returned null")); }, "image/png");
        else reject(new Error("canvas.toBlob unavailable"));
      }catch(err){ reject(err); }
    };
    img.onerror = function(){ reject(new Error("svg failed to rasterise")); };
    img.src = url;
  });
}

function tapeDownload(blob, filename){
  try{
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a); a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    return true;
  }catch(e){ return false; }
}

/* expose for tests and for the post builder */
window.tapeExportPng = tapeExportPng;
window.tapeDownload = tapeDownload;
window.TAPE_PRESETS = TAPE_PRESETS;
window.tapeInlineVars = tapeInlineVars;
</script>

<script>
/* ====================================================================
   EXPORT BUTTONS on every chart, plus the config-driven footer line.
   ==================================================================== */
(function(){
"use strict";
if(typeof document==="undefined") return;

function slugOf(el){
  var e = el.closest ? el.closest(".entry") : null;
  return e ? (e.dataset.slug||"chart") : "chart";
}
function titleOf(el){
  var e = el.closest ? el.closest(".entry") : null;
  if(!e) return TAPE.name;
  var h = e.querySelector(".term");
  if(!h) return TAPE.name;
  var c = h.cloneNode(true);
  Array.prototype.forEach.call(c.querySelectorAll("button"), function(b){ b.remove(); });
  return c.textContent.trim();
}
function defOf(el){
  var e = el.closest ? el.closest(".entry") : null;
  var p = e ? e.querySelector(".def") : null;
  return p ? p.textContent.trim() : "";
}
function capOf(fig){
  var c = fig.querySelector("figcaption");
  return c ? c.textContent.trim() : "";
}

function mountExport(fig){
  if(fig.querySelector(".expbar")) return;
  var svg = fig.querySelector("svg");
  if(!svg) return;
  var bar = document.createElement("div");
  bar.className = "expbar";
  bar.innerHTML = '<span class="explab">Export</span>';
  Object.keys(TAPE_PRESETS).forEach(function(k){
    var b = document.createElement("button");
    b.type = "button"; b.className = "expbtn"; b.dataset.preset = k;
    b.textContent = TAPE_PRESETS[k].label.split(" ")[0];
    b.setAttribute("aria-label","Export chart as "+TAPE_PRESETS[k].label+" PNG");
    b.onclick = function(ev){
      ev.stopPropagation();
      b.disabled = true;
      tapeExportPng(svg, {
        preset:k, title:titleOf(fig), subtitle:defOf(fig), caption:capOf(fig)
      }).then(function(blob){
        tapeDownload(blob, (TAPE.wordmark||"tape").toLowerCase()+"-"+slugOf(fig)+"-"+k+".png");
        if(window.__toast) window.__toast("Exported "+TAPE_PRESETS[k].label);
      }).catch(function(err){
        if(window.__toast) window.__toast("Export failed: "+err.message);
      }).then(function(){ b.disabled = false; });
    };
    bar.appendChild(b);
  });
  fig.appendChild(bar);
}

function mountAll(){
  document.querySelectorAll("#grid figure").forEach(mountExport);
}
mountAll();

/* config-driven footer additions; invisible while the constants are empty */
(function(){
  var f = document.getElementById("foot");
  if(!f) return;
  var bits = [];
  if(TAPE.footer) bits.push(TAPE.footer);
  if(TAPE.supportUrl) bits.push('<a href="'+TAPE.supportUrl+'" rel="noopener noreferrer">Support this project</a>');
  if(TAPE.workbookUrl) bits.push('<a href="'+TAPE.workbookUrl+'" rel="noopener noreferrer">Printable workbook</a>');
  if(!bits.length) return;
  var p = document.createElement("p");
  p.className = "tapefoot";
  p.innerHTML = bits.join(" &middot; ");
  f.appendChild(p);
})();
})();
</script>

<style>
.expbar{display:flex;gap:6px;align-items:center;margin-top:8px;flex-wrap:wrap}
.explab{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3)}
.expbtn{font-family:var(--mono);font-size:10.5px;padding:5px 9px;min-height:32px;
  background:none;border:1px solid var(--rule2);border-radius:3px;color:var(--ink3);cursor:pointer}
.expbtn:hover:not(:disabled){border-color:var(--accent);color:var(--accent)}
.expbtn:disabled{opacity:.5;cursor:wait}
.tapefoot{margin-top:10px}
@media (max-width:900px), (pointer: coarse){ .expbtn{min-height:44px} }
@media print{.expbar{display:none!important}}
</style>
'''

s = s.rstrip() + '\n' + MODULE
io.open(P, 'w', encoding='utf-8').write(s)

o = len(re.findall(r'<script(?:\s[^>]*)?>', s)); c = s.count('</script>')
print('script tags:', o, '/', c, 'OK' if o == c else 'IMBALANCED')
print('size KB:', round(len(s.encode('utf-8'))/1024))
