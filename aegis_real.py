"""AEGIS Field Intelligence - single-file edition (visuals + app).

Run:      streamlit run aegis_single.py
Install:  pip install streamlit folium streamlit-folium plotly pandas requests openpyxl reportlab arabic-reshaper python-bidi
"""
from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd
import plotly.graph_objects as go

SG_DEPTHS = [("0-5cm", 5), ("5-15cm", 10), ("15-30cm", 15), ("30-60cm", 30), ("60-100cm", 40)]


def safe_float(v: Any) -> float | None:
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


APP_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=Manrope:wght@400;600;700;800&display=swap');
:root {--bg:#06110c;--panel:rgba(12,30,20,.82);--line:rgba(120,210,157,.16);--mint:#8bf0b2;--muted:#91a99a;}
html, body, [class*="css"] {font-family:'Cairo',sans-serif;}
.stApp {background:radial-gradient(ellipse at 77% 3%,rgba(31,112,66,.24),transparent 34%),radial-gradient(ellipse at 4% 65%,rgba(15,83,52,.16),transparent 35%),linear-gradient(145deg,#050d09,#0a1910 52%,#07110b);color:#effcf4}
[data-testid="stHeader"] {background:transparent}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0b1b12,#07120c);border-left:1px solid var(--line)}
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:var(--mint);font-weight:800}
[data-testid="stMetric"] {background:linear-gradient(145deg,rgba(18,47,31,.94),rgba(10,27,18,.88));border:1px solid var(--line);padding:16px 18px;border-radius:18px;box-shadow:inset 0 1px rgba(255,255,255,.035),0 14px 35px rgba(0,0,0,.16)}
[data-testid="stMetricLabel"] {color:#a9c1b0;font-size:.84rem}
[data-testid="stMetricValue"] {color:#8bf0b2;font-family:'Manrope','Cairo',sans-serif;font-weight:800}
section.main > div {padding:1.2rem 2.2rem 3rem;max-width:1600px}
h1,h2,h3,h4 {letter-spacing:-.025em}
h2 {color:#e7f7ec;font-weight:800}
[data-testid="stDataFrame"] {border:1px solid var(--line);border-radius:14px;overflow:hidden}
[data-testid="stAlert"] {border-radius:14px;border:1px solid rgba(139,240,178,.15)}
.stButton > button,.stDownloadButton > button {border:1px solid rgba(139,240,178,.24);border-radius:12px;background:linear-gradient(135deg,#9bf3bb,#54d88c);color:#082313;font-family:'Cairo',sans-serif;font-weight:800}
[data-testid=stButton] > button{min-height:48px;transition:transform .2s ease,box-shadow .2s ease,filter .2s ease}
[data-testid=stButton] > button:hover{transform:translateY(-2px);filter:brightness(1.06);box-shadow:0 12px 28px rgba(84,216,140,.22)}

[data-baseweb="input"] > div,[data-baseweb="select"] > div {background:#0a1b11;border-color:rgba(139,240,178,.18);border-radius:11px;color:#effcf4}
.agiz-hero {position:relative;overflow:hidden;display:flex;justify-content:space-between;align-items:center;gap:24px;margin:0 0 25px;padding:27px 32px;border:1px solid rgba(139,240,178,.2);border-radius:24px;background:radial-gradient(ellipse at 15% 50%,rgba(74,207,122,.2),transparent 38%),linear-gradient(110deg,rgba(17,52,32,.9),rgba(7,22,14,.95));box-shadow:0 24px 70px rgba(0,0,0,.3)}
.hero-kicker {display:flex;align-items:center;gap:9px;color:#8bf0b2;font-size:11px;letter-spacing:.16em;font-family:'Manrope','Cairo',sans-serif;font-weight:800}.hero-kicker i {display:inline-block;width:7px;height:7px;background:#70efa3;border-radius:50%;box-shadow:0 0 14px #70efa3}
.hero-title {margin:8px 0 2px;color:#f3fff6;font-size:clamp(27px,3vw,40px);font-weight:900;line-height:1.25;letter-spacing:.04em}.hero-title span {color:#8bf0b2}
.hero-desc {color:#a5bdad;font-size:13px;margin-top:6px}
.hero-orb {width:74px;height:74px;flex:none;border-radius:24px;display:grid;place-items:center;font-size:32px;background:linear-gradient(145deg,rgba(115,244,165,.19),rgba(33,125,73,.08));border:1px solid rgba(139,240,178,.25)}
@media(max-width:700px){section.main > div{padding:1rem .8rem 2rem}.agiz-hero{padding:21px 19px}.hero-orb{width:56px;height:56px;font-size:25px}}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes heroShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes pulseDot{0%,100%{opacity:1}50%{opacity:.25}}
[data-testid="stMetric"]{animation:fadeUp .7s cubic-bezier(.16,1,.3,1) backwards;transition:transform .25s,border-color .25s}
[data-testid="stMetric"]:hover{transform:translateY(-3px);border-color:rgba(139,240,178,.45)}
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"]{animation-delay:.08s}
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"]{animation-delay:.16s}
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetric"]{animation-delay:.24s}
div[data-baseweb="tab-panel"]{animation:fadeUp .55s cubic-bezier(.16,1,.3,1) backwards}
.agiz-hero{background-size:220% 220%;animation:heroShift 14s ease infinite}
.hero-orb{animation:floatY 4.5s ease-in-out infinite}
.hero-kicker i{animation:pulseDot 1.6s ease-in-out infinite}
.aegis-brand{display:flex;align-items:center;justify-content:center;gap:12px;direction:ltr;margin:0 0 16px;padding:4px 0 16px;border-bottom:1px solid var(--line)}
.aegis-brand .aegis-logo{filter:drop-shadow(0 0 14px rgba(110,240,160,.35))}
.aegis-brand b{display:block;font-family:'Manrope',sans-serif;font-weight:800;font-size:23px;letter-spacing:.16em;color:#eafff1;line-height:1.1}
.aegis-brand span{display:block;font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:.18em;color:#8bf0b2;margin-top:3px}
.hero-orb .aegis-logo{filter:drop-shadow(0 0 12px rgba(110,240,160,.4))}
@media(prefers-reduced-motion:reduce){*{animation:none !important}}
</style>
"""


def aegis_logo(size: int = 52, uid: str = "a") -> str:
    """AEGIS mark: the letter A inside a leaf."""
    return (f'<svg class="aegis-logo" viewBox="0 0 64 64" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="agl{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c4ffd9"/><stop offset="1" stop-color="#3fcf7c"/></linearGradient></defs>'
            '<path d="M32 56V62" stroke="#3fcf7c" stroke-width="3" stroke-linecap="round" fill="none"/>'
            f'<path d="M32 2C50 11 57 30 47 46 41 54 35 56 32 56 29 56 23 54 17 46 7 30 14 11 32 2Z" fill="url(#agl{uid})" stroke="#e2ffec" stroke-opacity=".7" stroke-width="1.2"/>'
            '<path d="M22 45L32 16 42 45M26.5 35.5H37.5" stroke="#07210f" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
            '</svg>')


# =========================================================
# 3D INTRO (outside the dashboard): rotating Earth + glass enter button
# =========================================================
INTRO_HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&family=Manrope:wght@700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/globe.gl@2.45.1"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:transparent;overflow:hidden;font-family:'Cairo',sans-serif;color:#effcf4}
.wrap{position:relative;height:100%;border-radius:24px;overflow:hidden;border:1px solid rgba(139,240,178,.2);
 background:radial-gradient(ellipse at 28% 55%,rgba(31,112,66,.5),transparent 55%),linear-gradient(145deg,#030a06,#08170e 55%,#050e08)}
.stars,.stars:after{position:absolute;inset:0;content:"";opacity:.75;animation:drift 160s linear infinite;
 background-size:300px 300px;background-image:radial-gradient(1.2px 1.2px at 30px 40px,#fff,transparent),radial-gradient(1px 1px at 140px 210px,#cfe9ff,transparent),radial-gradient(1.6px 1.6px at 230px 90px,#fff,transparent),radial-gradient(1px 1px at 80px 160px,#fff,transparent)}
.stars:after{background-size:470px 470px;opacity:.5;animation-direction:reverse;animation-duration:260s}
@keyframes drift{to{background-position:-600px 300px}}
#globe{position:absolute;left:0;top:0;width:62%;height:100%}
.text{position:absolute;right:4%;top:50%;transform:translateY(-50%);width:34%;z-index:2}
.kicker{display:flex;align-items:center;gap:9px;color:#8bf0b2;font:800 11px 'Manrope',sans-serif;letter-spacing:.16em;direction:ltr;justify-content:flex-end}
.kicker i{width:7px;height:7px;background:#70efa3;border-radius:50%;box-shadow:0 0 14px #70efa3}
h1{margin:12px 0 10px;font-family:'Manrope','Cairo',sans-serif;font-size:clamp(28px,4.2vw,56px);font-weight:800;line-height:1.2;color:#f3fff6;letter-spacing:.06em;direction:ltr;text-align:right}
h1 span{color:#8bf0b2}
p{color:#a9c1b0;font-size:clamp(13px,1.35vw,17px);line-height:1.9}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;pointer-events:none}
.chips b{font-weight:600;font-size:12px;padding:6px 12px;border-radius:99px;border:1px solid rgba(139,240,178,.25);background:rgba(18,47,31,.7);color:#cdeed8}
.enter{margin-top:22px;display:flex}
.glass-btn{pointer-events:auto;cursor:pointer;font-family:'Cairo',sans-serif;font-weight:800;font-size:clamp(13px,1.2vw,15px);color:#effcf4;
 padding:11px 26px;border-radius:99px;border:1px solid rgba(139,240,178,.38);
 background:linear-gradient(145deg,rgba(139,240,178,.2),rgba(18,47,31,.55));
 -webkit-backdrop-filter:blur(14px) saturate(140%);backdrop-filter:blur(14px) saturate(140%);
 box-shadow:inset 0 1px rgba(255,255,255,.18),0 10px 30px rgba(0,0,0,.28),0 0 0 rgba(139,240,178,0);
 display:inline-flex;align-items:center;gap:10px;transition:transform .25s,box-shadow .25s,border-color .25s,background .25s}
.glass-btn:hover{transform:translateY(-2px);border-color:rgba(139,240,178,.7);
 background:linear-gradient(145deg,rgba(139,240,178,.32),rgba(18,47,31,.6));
 box-shadow:inset 0 1px rgba(255,255,255,.25),0 14px 34px rgba(0,0,0,.32),0 0 26px rgba(139,240,178,.28)}
.glass-btn:active{transform:translateY(0)}
.glass-btn i{font-style:normal;transition:transform .25s}
.glass-btn:hover i{transform:translateX(-4px)}
.err{display:none;margin-top:10px;font-size:12px;color:#f5c97a}
.hint{position:absolute;left:0;width:62%;bottom:14px;text-align:center;font-size:12px;color:#7f9a89;z-index:2;pointer-events:none}
#fallback{display:none;position:absolute;left:0;top:45%;width:62%;text-align:center;color:#a9c1b0}
.rise{opacity:0;transform:translateY(14px);animation:rise .9s cubic-bezier(.16,1,.3,1) forwards}
@keyframes rise{to{opacity:1;transform:none}}
@media(max-width:800px){
 #globe{width:100%;height:50%}.hint,#fallback{width:100%}.hint{bottom:auto;top:calc(50% - 22px)}
 .text{right:6%;left:6%;width:auto;top:auto;bottom:3%;transform:none;text-align:center}
 h1{text-align:center;font-size:30px;margin:6px 0}p{font-size:12px;line-height:1.6}
 .kicker{justify-content:center}.chips{justify-content:center;margin-top:10px}.chips b{font-size:11px;padding:4px 9px}
 .enter{justify-content:center;margin-top:12px}.glass-btn{padding:9px 22px}}
@media(prefers-reduced-motion:reduce){.stars,.stars:after{animation:none}.rise{animation:none;opacity:1;transform:none}}
</style></head>
<body><div class="wrap"><div class="stars"></div>
<div id="globe"></div><div id="fallback">تعذر تشغيل الكرة ثلاثية الأبعاد على هذا المتصفح. اضغط «ادخل المنصة» للمتابعة.</div>
<div class="hint">اسحب الكرة لتدويرها</div>
<div class="text">
 <div class="kicker rise" style="animation-delay:.2s">AEGIS <i></i></div>
 <h1 class="rise" style="animation-delay:.4s">AEGIS</h1>
 <p class="rise" style="animation-delay:.65s">من الفضاء إلى حقلك: بيانات NASA وMODIS وOpen-Meteo وSoilGrids تتحوّل إلى قرار ري واضح.</p>
 <div class="chips rise" style="animation-delay:.9s"><b>🛰️ NASA POWER</b><b>🌿 MODIS NDVI</b><b>🌦️ Open-Meteo</b><b>🧪 SoilGrids</b></div>
 <div class="enter rise" style="animation-delay:1.15s"><button class="glass-btn" id="enterBtn" type="button">ادخل إلى المنصة <i>←</i></button></div>
 <div class="err" id="enterErr">تعذر الدخول تلقائيًا، حدّث الصفحة وحاول مرة أخرى.</div>
</div></div>
<script>
(function(){
  document.getElementById('enterBtn').addEventListener('click',function(){
    try{
      var d=window.parent.document,b=d.querySelector('.st-key-aegis_enter button');
      if(!b){var all=d.querySelectorAll('button');for(var i=0;i<all.length;i++){if((all[i].textContent||'').indexOf('AEGIS_ENTER')>-1){b=all[i];break;}}}
      if(!b)throw new Error('no button');
      b.click();
    }catch(e){document.getElementById('enterErr').style.display='block';}
  });
  var el=document.getElementById('globe');
  if(typeof Globe==='undefined'){document.getElementById('fallback').style.display='block';return;}
  var F={lat:30.4167,lng:31.5667,text:'AEGIS'};
  var world=new Globe(el,{waitForGlobeReady:false,animateIn:true})
    .backgroundColor('rgba(0,0,0,0)')
    .globeImageUrl('https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-blue-marble.jpg')
    .bumpImageUrl('https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png')
    .showAtmosphere(true).atmosphereColor('#8bf0b2').atmosphereAltitude(0.22)
    .ringsData([F]).ringColor(function(){return function(t){return 'rgba(139,240,178,'+(1-t)+')';};})
    .ringMaxRadius(5).ringPropagationSpeed(2).ringRepeatPeriod(1400)
    .pointsData([F]).pointColor(function(){return '#8bf0b2';}).pointAltitude(0.06).pointRadius(0.45)
    .labelsData([F]).labelSize(1.3).labelDotRadius(0.5).labelColor(function(){return '#effcf4';}).labelAltitude(0.07);
  function size(){world.width(el.clientWidth).height(el.clientHeight);}
  addEventListener('resize',size);size();
  var c=world.controls();c.enableZoom=false;
  world.pointOfView({lat:20,lng:-20,altitude:4.2},0);
  setTimeout(function(){world.pointOfView({lat:27,lng:31,altitude:2.1},3200);},300);
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
    setTimeout(function(){c.autoRotate=true;c.autoRotateSpeed=0.45;},4200);
  }
})();
</script></body></html>"""


# =========================================================
# LIVE SCENE + 3D FIGURES (all driven by the real data above)
# =========================================================
SCENE_HTML = r"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Manrope:wght@800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%;background:transparent;overflow:hidden;font-family:'Cairo',sans-serif;color:#fff}
.box{position:relative;height:100%;border-radius:22px;overflow:hidden;border:1px solid rgba(139,240,178,.25)}
canvas{position:absolute;inset:0;width:100%;height:100%}
.hud{position:absolute;inset:0;padding:14px 18px;display:flex;flex-direction:column;justify-content:space-between;pointer-events:none}
.top{display:flex;justify-content:space-between;align-items:center}
.live{font:800 11px 'Manrope',sans-serif;letter-spacing:.14em;color:#8bf0b2;display:flex;gap:8px;align-items:center;direction:ltr;text-shadow:0 1px 8px rgba(0,0,0,.6)}
.live i{width:8px;height:8px;border-radius:50%;background:#70efa3;box-shadow:0 0 12px #70efa3;animation:p 1.4s infinite}@keyframes p{50%{opacity:.25}}
.clk{font:800 12px 'Manrope','Cairo',sans-serif;letter-spacing:.06em;direction:ltr;padding:3px 10px;border-radius:99px;background:rgba(6,20,12,.5);border:1px solid rgba(139,240,178,.25);backdrop-filter:blur(4px)}
.row{display:flex;align-items:flex-end;justify-content:space-between;gap:12px}
.temp{font:800 54px 'Manrope',sans-serif;line-height:1;text-shadow:0 4px 22px rgba(0,0,0,.5)}
.temp small{font-size:22px;opacity:.85}
.cond{text-align:left;text-shadow:0 2px 12px rgba(0,0,0,.6)}
.cond b{display:block;font-size:17px;font-weight:900}
.cond span{font-size:12px;opacity:.9}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
.chips span{background:rgba(6,20,12,.62);border:1px solid rgba(139,240,178,.28);border-radius:99px;padding:3px 10px;font-size:11.5px;font-weight:700;backdrop-filter:blur(4px)}
.chips b{font-family:'Manrope',sans-serif;color:#8bf0b2}
</style></head><body><div class="box"><canvas id="c"></canvas>
<div class="hud"><div class="top"><div class="live"><i></i>LIVE · OPEN-METEO / MODIS</div><div class="clk" id="clk">--:--</div></div>
<div><div class="row"><div class="temp"><span id="t">0</span><small> °م</small></div><div class="cond"><b id="cd">–</b><span id="fl"></span></div></div>
<div class="chips"><span>💧 رطوبة <b id="h">0</b>%</span><span>🌬️ رياح <b id="w">0</b> م/ث <em id="wd" style="font-style:normal"></em></span><span>☁️ سحب <b id="cl">0</b>%</span><span>🔥 ET₀ <b id="e">0</b> مم</span><span>🌿 NDVI <b id="n">–</b></span><span id="sun">🌅 –</span><span id="moon">🌙 –</span><span id="pr"></span></div></div></div></div>
<script>
(function(){
var D=__DATA__;
var cv=document.getElementById('c'),x=cv.getContext('2d'),W=0,H=0,dpr=Math.min(window.devicePixelRatio||1,2);
var cl=document.createElement('canvas'),cx2=cl.getContext('2d');
function fit(){W=cv.clientWidth;H=cv.clientHeight;cv.width=W*dpr;cv.height=H*dpr;x.setTransform(dpr,0,0,dpr,0,0);cl.width=W*dpr;cl.height=H*dpr;cx2.setTransform(dpr,0,0,dpr,0,0);}
addEventListener('resize',fit);fit();

function c01(v){return v<0?0:v>1?1:v;}
function mixc(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t];}
function css(c,a){return 'rgba('+Math.round(c[0])+','+Math.round(c[1])+','+Math.round(c[2])+','+(a===undefined?1:a)+')';}
function pad(n){return (n<10?'0':'')+n;}
function rnd(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

/* ---------- real time + astronomy (sun and moon position from lat/lon/time) ---------- */
var T0=performance.now();
var base=D.time?Date.parse(D.time+':00Z')-(D.utc||0)*1000:Date.now();
if(isNaN(base))base=Date.now();
function nowMs(){return base+(performance.now()-T0);}
function astro(ms){
 var rad=Math.PI/180,jd=ms/86400000+2440587.5,n=jd-2451545.0;
 var L=((280.460+0.9856474*n)%360+360)%360,g=((357.528+0.9856003*n)%360)*rad;
 var lam=L+1.915*Math.sin(g)+0.020*Math.sin(2*g);
 var gm=(((18.697374558+24.06570982441908*n)%24)+24)%24;
 return {lam:lam,eps:(23.439-0.0000004*n)*rad,gmst:gm*15,jd:jd};
}
function horiz(lamDeg,A){
 var rad=Math.PI/180,lam=lamDeg*rad,eps=A.eps,phi=D.lat*rad;
 var ra=Math.atan2(Math.cos(eps)*Math.sin(lam),Math.cos(lam)),dec=Math.asin(Math.sin(eps)*Math.sin(lam));
 var Hh=(A.gmst+D.lon)*rad-ra;
 var alt=Math.asin(Math.sin(phi)*Math.sin(dec)+Math.cos(phi)*Math.cos(dec)*Math.cos(Hh));
 var az=Math.atan2(Math.sin(Hh),Math.cos(Hh)*Math.sin(phi)-Math.tan(dec)*Math.cos(phi))+Math.PI;
 return {alt:alt/rad,az:(((az/rad)%360)+360)%360};
}

/* ---------- real weather ---------- */
var cloud=c01((D.cloud||0)/100),hum=c01((D.hum==null?50:D.hum)/100);
var wsp=D.wind||0,windN=c01(wsp/12),gustN=c01(((D.gust==null?wsp:D.gust)-wsp)/10);
var code=D.code==null?-1:D.code;
var rainy=(code>=51&&code<=67)||(code>=80&&code<=82)||(code>=95&&code<=99)||(D.rain||0)>0;
var snowy=(code>=71&&code<=77)||code===85||code===86,fog=(code===45||code===48),storm=code>=95;
var rainMM=(D.rain||0)>0?D.rain:(rainy?((code===65||code===82)?4:(code===63||code===81)?1.5:.4):0);
var fromR=(D.wdir==null?270:D.wdir)*Math.PI/180;
var vdir=Math.sin(fromR);if(Math.abs(vdir)<.15)vdir=vdir<0?-.15:.15;
var CODES={0:'صحو',1:'صحو غالبًا',2:'غائم جزئيًا',3:'غائم كليًا',45:'ضباب',48:'ضباب صقيعي',51:'رذاذ خفيف',53:'رذاذ',55:'رذاذ كثيف',56:'رذاذ متجمد',57:'رذاذ متجمد',61:'مطر خفيف',63:'مطر متوسط',65:'مطر غزير',66:'مطر متجمد',67:'مطر متجمد',71:'ثلج خفيف',73:'ثلج',75:'ثلج كثيف',77:'حبيبات ثلج',80:'زخات مطر خفيفة',81:'زخات مطر',82:'زخات مطر عنيفة',85:'زخات ثلج',86:'زخات ثلج كثيفة',95:'عاصفة رعدية',96:'عاصفة رعدية مع برد',99:'عاصفة رعدية مع برد'};
var DIRS=['شمالية','شمالية شرقية','شرقية','جنوبية شرقية','جنوبية','جنوبية غربية','غربية','شمالية غربية'];

function count(id,v,dec){var el=document.getElementById(id);if(v===null||v===undefined){el.textContent='–';return;}
 var t0=performance.now();(function s(t){var k=Math.min(1,(t-t0)/1400),e=1-Math.pow(1-k,3);el.textContent=(v*e).toFixed(dec);if(k<1)requestAnimationFrame(s);})(t0);}
count('t',D.temp,1);count('h',D.hum,0);count('w',D.wind,1);count('cl',D.cloud,0);count('e',D.et0,1);count('n',D.ndvi,2);
document.getElementById('cd').textContent=CODES[code]||(cloud>.85?'غائم كليًا':cloud>.45?'غائم جزئيًا':'صحو');
if(D.feels!=null)document.getElementById('fl').textContent='المحسوسة '+D.feels.toFixed(1)+' °م';
if(D.wdir!=null)document.getElementById('wd').textContent='· '+DIRS[Math.round(D.wdir/45)%8];
if(D.sunrise&&D.sunset)document.getElementById('sun').textContent='🌅 '+D.sunrise.slice(11,16)+' · 🌇 '+D.sunset.slice(11,16);
if(D.press!=null)document.getElementById('pr').textContent='🧭 '+Math.round(D.press)+' هـ.ب';else document.getElementById('pr').style.display='none';

/* ---------- scene objects ---------- */
function sprite(w,h,seed){var c=document.createElement('canvas');c.width=w;c.height=h;var g=c.getContext('2d'),r=rnd(seed),n=10+Math.floor(r()*6);
 for(var i=0;i<n;i++){var u=i/(n-1),px=w*(.14+.72*u+(r()-.5)*.08),rad=h*(.2+.2*r())*(1-Math.abs(u-.5)*.85),py=h*.62-Math.sin(u*Math.PI)*h*.2*(.4+r())-rad*.15;
  var gr=g.createRadialGradient(px,py-rad*.25,rad*.08,px,py,rad);gr.addColorStop(0,'rgba(255,255,255,.95)');gr.addColorStop(.55,'rgba(255,255,255,.55)');gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;g.beginPath();g.arc(px,py,rad,0,6.2832);g.fill();}
 g.globalCompositeOperation='source-atop';var sh=g.createLinearGradient(0,h*.3,0,h*.85);sh.addColorStop(0,'rgba(255,255,255,0)');sh.addColorStop(1,'rgba(88,102,128,.6)');g.fillStyle=sh;g.fillRect(0,0,w,h);return c;}
var sprites=[];for(var si=0;si<6;si++)sprites.push(sprite(340,150,1000+si*77));
var clouds=[],nCl=cloud<.04?0:Math.max(1,Math.round(cloud*(cloud>.8?14:9))),rr=rnd(42);
for(var ci=0;ci<nCl;ci++){var yf=.04+rr()*.5;clouds.push({x:(rr()*1.6-.3)*600,yf:yf,s:1.35-yf*1.6,sp:sprites[ci%sprites.length],o:.55+.45*cloud});}
var stars=[];for(var k=0;k<130;k++)stars.push({x:rr(),y:rr()*.7,r:rr()*1.3+.3,p:rr()*6.28});
var rows=[{n:90,y:.07,h:.05,w:1,d:.45},{n:60,y:.4,h:.09,w:1.4,d:.75},{n:38,y:.8,h:.17,w:2.1,d:1}];
rows.forEach(function(row,ri){var r=rnd(300+ri);row.st=[];for(var i=0;i<row.n;i++)row.st.push({x:(i+r()*.9)/row.n,p:r()*6.28,hv:.75+r()*.5});});
var nDrops=rainy?Math.min(260,Math.round(70+rainMM*55)):(snowy?140:0),drops=[];
for(var di=0;di<nDrops;di++)drops.push({x:Math.random(),y:Math.random(),v:.55+Math.random()*.6,l:8+Math.random()*10,ly:.74+Math.random()*.26});
var flash=0,nextFlash=performance.now()+3000+Math.random()*5000;
var greenN=D.ndvi==null?.6:D.ndvi,green=c01(greenN/.7),soilMix=D.ndvi==null?0:c01((.28-greenN)/.2);
var SK=[[-18,[2,4,12],[6,13,31]],[-12,[5,10,28],[20,33,63]],[-6,[12,26,58],[58,63,107]],[-1,[27,47,99],[224,135,90]],[3,[58,111,181],[244,178,106]],[10,[63,134,214],[191,224,247]],[30,[47,120,209],[169,214,245]]];
function skyStops(e){if(e<=SK[0][0])return [SK[0][1],SK[0][2]];for(var i=1;i<SK.length;i++){if(e<=SK[i][0]){var a=SK[i-1],b=SK[i],t=(e-a[0])/(b[0]-a[0]);return [mixc(a[1],b[1],t),mixc(a[2],b[2],t)];}}var l=SK[SK.length-1];return [l[1],l[2]];}
function drawMoon(cx,cy,r,ph,alpha){
 x.save();x.globalAlpha=alpha;
 var gl=x.createRadialGradient(cx,cy,r*.6,cx,cy,r*4);gl.addColorStop(0,'rgba(220,230,255,.35)');gl.addColorStop(1,'rgba(220,230,255,0)');x.fillStyle=gl;x.fillRect(cx-r*4,cy-r*4,r*8,r*8);
 x.fillStyle='rgba(46,58,82,.7)';x.beginPath();x.arc(cx,cy,r,0,6.2832);x.fill();
 var waxing=ph<.5,c=Math.cos(ph*2*Math.PI),rx=Math.abs(c)*r,bulgeRight=waxing?c>0:c<0;
 x.fillStyle='#f4f2e3';x.beginPath();x.arc(cx,cy,r,-Math.PI/2,Math.PI/2,!waxing);x.ellipse(cx,cy,Math.max(rx,.01),r,0,Math.PI/2,-Math.PI/2,bulgeRight);x.fill();
 x.fillStyle='rgba(120,120,110,.18)';x.beginPath();x.arc(cx-r*.25,cy-r*.2,r*.18,0,6.2832);x.arc(cx+r*.3,cy+r*.25,r*.12,0,6.2832);x.fill();
 x.restore();}
function proj(az,alt,gy){return {x:W*(.5+((az-180)/130)*.46),y:gy-(alt/70)*(gy-H*.1)};}

var lastT=performance.now(),lastClk=0;
function frame(tm){
 var dt=Math.min(.05,(tm-lastT)/1000);lastT=tm;
 var ms=nowMs(),A=astro(ms),sp=horiz(A.lam,A),e=sp.alt;
 var mph=((A.jd-2451550.1)/29.530588853)%1;if(mph<0)mph+=1;
 var mo=horiz(A.lam+mph*360,A),illum=(1-Math.cos(mph*2*Math.PI))/2;
 var dayL=c01((e+6)/16),warm=c01(1-Math.abs(e-3)/10)*(1-cloud*.5),gy=H*.72;
 function shade(c){var f=.14+.86*dayL,r=c[0]*f*(1+.25*warm),g=c[1]*f*(1+.05*warm),b=c[2]*f*(1-.25*warm);return [Math.min(255,r),Math.min(255,g),Math.min(255,b)];}
 if(tm-lastClk>900){lastClk=tm;var lt=new Date(ms+(D.utc||0)*1000);document.getElementById('clk').textContent=pad(lt.getUTCHours())+':'+pad(lt.getUTCMinutes())+(e>0?'  ☀️':'  🌙');
  var mn=mph<.03||mph>.97?'محاق':mph<.22?'هلال متزايد':mph<.28?'تربيع أول':mph<.47?'أحدب متزايد':mph<.53?'بدر':mph<.72?'أحدب متناقص':mph<.78?'تربيع أخير':'هلال متناقص';
  document.getElementById('moon').textContent='🌙 '+mn+' '+Math.round(illum*100)+'%';}
 /* sky */
 var st=skyStops(e),oc=cloud*(rainy?.75:.55),g1=60+110*dayL;
 var top=mixc(st[0],[g1*.8,g1*.85,g1*.95],oc),bot=mixc(st[1],[g1*.95,g1,g1*1.05],oc);
 var haze=c01((hum-.55)/.45)*.35+(fog?.5:0);bot=mixc(bot,[205*(.25+.75*dayL),214*(.25+.75*dayL),216*(.25+.75*dayL)],c01(haze));
 var sg=x.createLinearGradient(0,0,0,gy);sg.addColorStop(0,css(top));sg.addColorStop(1,css(bot));x.fillStyle=sg;x.fillRect(0,0,W,H);
 var gk=c01(1-Math.abs(e-1)/8)*.55*(1-cloud*.5);
 if(gk>.02){var s0=proj(sp.az,0,gy),hg=x.createRadialGradient(s0.x,gy,2,s0.x,gy,W*.55);hg.addColorStop(0,'rgba(255,150,70,'+gk+')');hg.addColorStop(1,'rgba(255,150,70,0)');x.fillStyle=hg;x.fillRect(0,0,W,gy);}
 /* stars */
 var sa=c01((-e-3)/9)*(1-cloud*.92)*(1-illum*Math.max(0,mo.alt>0?.45:0));
 if(sa>.02){x.fillStyle='#fff';stars.forEach(function(s){x.globalAlpha=sa*(.45+.55*Math.abs(Math.sin(tm*.0012+s.p)));x.beginPath();x.arc(s.x*W,s.y*gy,s.r,0,6.2832);x.fill();});x.globalAlpha=1;}
 /* sun */
 if(e>-4){var sp2=proj(sp.az,e+.5,gy),wm=c01(1-(e+4)/24),col=mixc([255,250,235],[255,138,58],Math.pow(wm,1.5)),vis=(1-cloud*.78)*c01((e+4)/4),sc=(W/560+.55),rad=(15+9*wm)*sc;
  var gl=x.createRadialGradient(sp2.x,sp2.y,rad*.4,sp2.x,sp2.y,rad*7);gl.addColorStop(0,css(col,.75*vis));gl.addColorStop(1,css(col,0));x.fillStyle=gl;x.fillRect(sp2.x-rad*7,sp2.y-rad*7,rad*14,rad*14);
  x.fillStyle=css(col,Math.min(1,vis+.1));x.beginPath();x.arc(sp2.x,sp2.y,rad,0,6.2832);x.fill();}
 /* moon */
 if(mo.alt>-2){var mp=proj(mo.az,mo.alt,gy),ma=(.25+.75*c01(-e/6))*(1-cloud*.85);if(ma>.03)drawMoon(mp.x,mp.y,12*(W/560+.55),mph,ma);}
 /* clouds (drawn on their own layer, then tinted by the real light) */
 cx2.setTransform(dpr,0,0,dpr,0,0);cx2.globalCompositeOperation='source-over';cx2.clearRect(0,0,W,H);
 clouds.forEach(function(c){var cw=340*c.s*(W/560+.4),ch=150*c.s*(W/560+.4);c.x+=vdir*(4+wsp*3.2)*c.s*dt;
  if(c.x>W+cw)c.x=-cw*1.2;if(c.x<-cw*1.3)c.x=W+cw*.2;cx2.globalAlpha=c.o;cx2.drawImage(c.sp,c.x,c.yf*gy-ch*.4,cw,ch);});
 var oc2=cloud*(rainy?.9:.5),cb=mixc([255,255,255],[148,156,168],oc2);cb=mixc(cb,[255,150,95],warm*.85);cb=mixc(cb,[34,46,78],c01(1-dayL)*.9);
 cx2.globalAlpha=1;cx2.globalCompositeOperation='source-atop';cx2.fillStyle=css(cb,.5+(1-dayL)*.35+oc2*.2);cx2.fillRect(0,0,W,H);
 x.globalAlpha=1;x.drawImage(cl,0,0,W,H);
 if(cloud>.6){var og=x.createLinearGradient(0,0,0,gy);var gc=mixc([120,128,140],[20,26,40],1-dayL);og.addColorStop(0,css(gc,(cloud-.6)/.4*.5));og.addColorStop(1,css(gc,0));x.fillStyle=og;x.fillRect(0,0,W,gy);}
 /* distant tree line */
 x.fillStyle=css(mixc(shade([40,72,46]),bot,.5));x.beginPath();x.moveTo(0,gy+2);
 for(var i=0;i<=W;i+=6)x.lineTo(i,gy-3-Math.abs(Math.sin(i*.037)*4+Math.sin(i*.091)*3+Math.sin(i*.013)*5));
 x.lineTo(W,gy+2);x.closePath();x.fill();
 /* field */
 var farC=mixc(mixc([92,134,70],[200,172,122],soilMix),bot,.3),nearC=mixc([40,96,46],[150,120,82],soilMix);
 var fg=x.createLinearGradient(0,gy,0,H);fg.addColorStop(0,css(shade(farC)));fg.addColorStop(1,css(shade(nearC)));x.fillStyle=fg;x.fillRect(0,gy,W,H-gy);
 x.strokeStyle='rgba(0,0,0,.08)';x.lineWidth=1;for(var f=1;f<8;f++){var fy=gy+(H-gy)*Math.pow(f/8,1.6);x.beginPath();x.moveTo(0,fy);x.lineTo(W,fy);x.stroke();}
 var vis2=1-soilMix*.92,yel=c01((1-green)*.9);
 rows.forEach(function(row){var by=gy+(H-gy)*row.y,cnt=Math.floor(row.n*vis2);
  x.lineWidth=row.w;x.strokeStyle=css(shade(mixc(mixc([78,138,56],[198,172,80],yel),[30,70,34],1-row.d)),.95);
  for(var i=0;i<cnt;i++){var s=row.st[i],bx=s.x*W,hh=row.h*H*(.6+green*.8)*s.hv,
   sw=Math.sin(tm*.0021*(.7+windN*2)+s.p+bx*.01)*(1.5+windN*14)*row.d+Math.sin(tm*.0007+s.x*6)*gustN*10*row.d+vdir*windN*8*row.d;
   x.beginPath();x.moveTo(bx,by);x.quadraticCurveTo(bx+sw*.2,by-hh*.6,bx+sw,by-hh);x.stroke();
   if(row.d>.7){x.fillStyle=css(shade(mixc([196,170,70],[90,150,60],green)),.95);x.beginPath();x.ellipse(bx+sw,by-hh-3,2,5,sw*.025,0,6.2832);x.fill();}}});
 /* fog / low haze */
 if(fog||haze>.1){var fa=(fog?.55:haze*.9),fgr=x.createLinearGradient(0,gy-H*.25,0,H);var fc=[210*(.3+.7*dayL),216*(.3+.7*dayL),218*(.3+.7*dayL)];fgr.addColorStop(0,css(fc,0));fgr.addColorStop(.45,css(fc,fa*.8));fgr.addColorStop(1,css(fc,fa*.2));x.fillStyle=fgr;x.fillRect(0,gy-H*.25,W,H);}
 /* rain / snow */
 if(drops.length){
  if(snowy){x.fillStyle='rgba(255,255,255,.85)';drops.forEach(function(p){p.y+=p.v*dt*.18;p.x+=vdir*windN*dt*.05+Math.sin(tm*.001+p.l)*.0005;if(p.y>1){p.y=0;p.x=Math.random();}x.beginPath();x.arc(p.x*W,p.y*H,1.4+p.l*.05,0,6.2832);x.fill();});}
  else{x.strokeStyle='rgba(195,225,255,.65)';x.lineWidth=1.1;var slant=vdir*(2+windN*10);
   drops.forEach(function(p){p.y+=p.v*dt*1.5;if(p.y>=p.ly){var sx=p.x*W,sy=p.ly*H;x.fillStyle='rgba(200,225,255,.5)';x.beginPath();x.ellipse(sx,sy,3,1,0,0,6.2832);x.fill();p.y=-.05;p.x=Math.random();p.ly=.74+Math.random()*.26;}
    x.beginPath();x.moveTo(p.x*W,p.y*H);x.lineTo(p.x*W-slant,p.y*H+p.l);x.stroke();});}}
 /* lightning */
 if(storm){if(tm>nextFlash){flash=1;nextFlash=tm+4000+Math.random()*9000;}if(flash>0){x.fillStyle='rgba(235,240,255,'+(flash*.35)+')';x.fillRect(0,0,W,H);flash=Math.max(0,flash-dt*3.2);}}
 requestAnimationFrame(frame);}
requestAnimationFrame(frame);
})();
</script></body></html>"""


def scene_html(weather: dict, cur: dict, et0_3, ndvi, today, lat: float, lon: float) -> str:
    """Live scene driven by real data: Open-Meteo current conditions + sunrise/sunset,
    MODIS NDVI, and the sun/moon position computed astronomically for this place and time."""
    d = weather.get("daily", {}) or {}
    ts = d.get("time", []) or []
    sunrise = sunset = None
    if str(today) in ts:
        i = ts.index(str(today))
        sunrise = (d.get("sunrise") or [None] * len(ts))[i]
        sunset = (d.get("sunset") or [None] * len(ts))[i]
    data = {"temp": safe_float(cur.get("temperature_2m")), "feels": safe_float(cur.get("apparent_temperature")),
            "hum": safe_float(cur.get("relative_humidity_2m")), "wind": safe_float(cur.get("wind_speed_10m")),
            "gust": safe_float(cur.get("wind_gusts_10m")), "wdir": safe_float(cur.get("wind_direction_10m")),
            "cloud": safe_float(cur.get("cloud_cover")), "rain": safe_float(cur.get("precipitation")) or 0,
            "code": cur.get("weather_code"), "press": safe_float(cur.get("surface_pressure")),
            "time": cur.get("time"), "utc": weather.get("utc_offset_seconds", 0),
            "sunrise": sunrise, "sunset": sunset, "lat": lat, "lon": lon,
            "et0": et0_3, "ndvi": ndvi}
    return SCENE_HTML.replace("__DATA__", json.dumps(data))


def plotly_html(fig, rotate: bool = True) -> str:
    """Plotly figure as embeddable HTML; the camera orbits slowly until the user touches it."""
    js = ""
    if rotate:
        js = ("var gd=document.getElementById('{plot_id}');var a=0.8;var t=setInterval(function(){a+=0.012;"
              "Plotly.relayout(gd,{'scene.camera.eye':{x:1.9*Math.cos(a),y:1.9*Math.sin(a),z:0.9}});},60);"
              "['mousedown','touchstart','wheel'].forEach(function(e){gd.addEventListener(e,function(){clearInterval(t);});});")
    return fig.to_html(include_plotlyjs="cdn", full_html=False, post_script=js, config={"displayModeBar": False})


def _clay_color(clay: float) -> str:
    f = min(max((clay - 5) / 50, 0), 1)
    a, b = (222, 186, 112), (88, 60, 38)
    return "rgb(%d,%d,%d)" % tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def _cylinder(z_top, z_bot, r, color, opacity=1.0, hover=None, n=44):
    th = [2 * math.pi * i / n for i in range(n)]
    xs = [r * math.cos(t) for t in th] * 2 + [0]
    ys = [r * math.sin(t) for t in th] * 2 + [0]
    zs = [z_top] * n + [z_bot] * n + [z_top]
    i, j, k = [], [], []
    for a in range(n):
        b = (a + 1) % n
        i += [a, b, 2 * n]
        j += [b, b + n, a]
        k += [a + n, a + n, b]
    return go.Mesh3d(x=xs, y=ys, z=zs, i=i, j=j, k=k, color=color, opacity=opacity, flatshading=True,
                     hovertext=hover, hoverinfo="text" if hover else "skip",
                     lighting=dict(ambient=.65, diffuse=.85, specular=.15))


def soil_profile_fig(sg: dict, root_m: float, avail_frac: float | None) -> go.Figure:
    """3D soil core from SoilGrids layers (colour = clay content); blue sleeve = water still available in the root zone."""
    fig, top = go.Figure(), 0
    for label, thick in SG_DEPTHS:
        l = sg.get(label, {})
        clay, sand = safe_float(l.get("clay")) or 25, safe_float(l.get("sand")) or 40
        ph = safe_float(l.get("phh2o"))
        hover = f"{label}<br>طين {clay:.0f}% · رمل {sand:.0f}%" + (f"<br>pH {ph:.1f}" if ph else "")
        fig.add_trace(_cylinder(-top, -(top + thick), 1.0, _clay_color(clay), hover=hover))
        top += thick
    root_cm = min(root_m * 100, 100)
    fig.add_trace(_cylinder(0, -root_cm, 1.14, "#8bf0b2", opacity=.14))
    if avail_frac is not None:
        fig.add_trace(_cylinder(-root_cm + root_cm * avail_frac, -root_cm, 1.07, "#38bdf8", opacity=.5,
                                hover=f"ماء متاح في منطقة الجذور: {avail_frac * 100:.0f}%"))
    ax = dict(visible=False)
    fig.update_layout(height=470, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                      scene=dict(xaxis=ax, yaxis=ax, bgcolor="rgba(0,0,0,0)", aspectmode="manual", aspectratio=dict(x=1, y=1, z=1.5),
                                 zaxis=dict(title="العمق (سم)", range=[-105, 5], color="#a9c1b0", gridcolor="rgba(139,240,178,.15)"),
                                 camera=dict(eye=dict(x=1.9, y=0.8, z=0.9))))
    return fig


def climate_cube_fig(hist: pd.DataFrame) -> go.Figure:
    cols = ["متوسط الحرارة °م", "المطر مم/يوم", "الإشعاع الشمسي MJ/m²/يوم"]
    h = hist[cols].dropna()
    fig = go.Figure(go.Scatter3d(x=h[cols[0]], y=h[cols[1]], z=h[cols[2]], mode="lines+markers",
                                 line=dict(color="#8bf0b2", width=4),
                                 marker=dict(size=5, color=list(range(len(h))), colorscale="Viridis"),
                                 text=[d.strftime("%Y-%m-%d") for d in h.index], hoverinfo="text+x+y+z"))
    ax = lambda t: dict(title=t, color="#a9c1b0", gridcolor="rgba(139,240,178,.15)", backgroundcolor="rgba(0,0,0,0)")
    fig.update_layout(height=470, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      scene=dict(xaxis=ax("حرارة °م"), yaxis=ax("مطر مم"), zaxis=ax("إشعاع MJ/m²"), bgcolor="rgba(0,0,0,0)",
                                 camera=dict(eye=dict(x=1.9, y=0.8, z=0.9))))
    return fig


import io
import os
import re
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import folium
import requests
import streamlit as st
import streamlit.components.v1 as components
from folium.plugins import Draw, Fullscreen, MeasureControl
from streamlit_folium import st_folium


# AEGIS Field Intelligence - real-data edition.
# Every number on screen comes from a live public source or from a transparent formula
# applied to those sources. If a source fails, the app says so; it never fills in fake values.
#   Open-Meteo : forecast (daily + hourly) + past daily ET0/rain, modeled soil moisture
#   NASA POWER : 30-day climate history
#   MODIS NDVI : is there green vegetation here? (NASA ORNL DAAC)
#   SoilGrids  : soil texture, pH, organic carbon, water-holding capacity (ISRIC)
#   Water balance: FAO-56 method (ETc = ET0 x Kc, root-zone bucket)
#   Alerts / GDD / spray windows: transparent rules applied to the forecast

st.set_page_config(page_title="AEGIS | Field Intelligence", page_icon="🛡️", layout="wide")

st.markdown(APP_CSS, unsafe_allow_html=True)

API_TIMEOUT = 25
HEADERS = {"User-Agent": "AEGIS-AgriDashboard/3.0 (Streamlit)"}

# Approximate FAO-56 reference values (Kc ini/mid/end, root depth m, allowed depletion p).
# Planning values only: calibrate locally when you can.
CROPS = {
    "طماطم":  {"kc": (0.60, 1.15, 0.80), "root": 1.0, "p": 0.40},
    "قمح":    {"kc": (0.30, 1.15, 0.25), "root": 1.0, "p": 0.55},
    "ذرة":    {"kc": (0.30, 1.20, 0.60), "root": 1.0, "p": 0.55},
    "باذنجان": {"kc": (0.60, 1.05, 0.90), "root": 0.8, "p": 0.45},
    "بطاطس":  {"kc": (0.50, 1.15, 0.75), "root": 0.6, "p": 0.35},
    "قطن":    {"kc": (0.35, 1.15, 0.70), "root": 1.0, "p": 0.65},
    "أرز":    {"kc": (1.05, 1.20, 0.90), "root": 0.5, "p": 0.20},
    "محصول آخر": {"kc": (0.50, 1.00, 0.70), "root": 0.6, "p": 0.45},
}
STAGES = ["تأسيس/إنبات", "نمو خضري", "إزهار/إثمار", "نضج"]

# Approximate base temperatures (°C) for growing degree days. Planning values only.
GDD_BASE = {"طماطم": 10.0, "قمح": 0.0, "ذرة": 10.0, "باذنجان": 12.0, "بطاطس": 7.0,
            "قطن": 15.5, "أرز": 10.0, "محصول آخر": 10.0}
GDD_UPPER = 30.0

def kc_for(crop: str, stage: str) -> float:
    ini, mid, end = CROPS[crop]["kc"]
    return {"تأسيس/إنبات": ini, "نمو خضري": (ini + mid) / 2, "إزهار/إثمار": mid, "نضج": end}[stage]


# =========================================================
# DATA SOURCES (each one fails on its own, never fakes data)
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def get_weather(lat: float, lon: float) -> dict[str, Any]:
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,surface_pressure,is_day",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration,precipitation_probability_max,wind_speed_10m_max,sunrise,sunset",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "forecast_days": 7, "past_days": 30, "timezone": "auto", "wind_speed_unit": "ms",
    }
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=API_TIMEOUT, headers=HEADERS)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=1800, show_spinner=False)
def get_soil_moisture(lat: float, lon: float) -> pd.DataFrame:
    """Modeled soil moisture (m3/m3) from Open-Meteo - a model estimate, not a probe reading."""
    cols = ["soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm"]
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon, "hourly": ",".join(cols),
        "past_days": 7, "forecast_days": 1, "timezone": "auto"}, timeout=API_TIMEOUT, headers=HEADERS)
    r.raise_for_status()
    h = r.json()["hourly"]
    df = pd.DataFrame({c: h[c] for c in cols}, index=pd.to_datetime(h["time"]))
    return df.dropna(how="all")


@st.cache_data(ttl=86400, show_spinner=False)
def get_nasa_power(lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
    params = {"parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN", "community": "AG",
              "longitude": lon, "latitude": lat, "start": start, "end": end, "format": "JSON", "time-standard": "UTC"}
    r = requests.get("https://power.larc.nasa.gov/api/temporal/daily/point", params=params, timeout=API_TIMEOUT, headers=HEADERS)
    r.raise_for_status()
    payload = r.json()
    if "properties" not in payload or "parameter" not in payload["properties"]:
        raise ValueError("استجابة NASA POWER لا تحتوي على بيانات متوقعة")
    return payload


@st.cache_data(ttl=86400, show_spinner=False)
def geocode(place: str) -> list[dict[str, Any]]:
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name": place, "count": 6, "language": "ar", "format": "json"}, timeout=API_TIMEOUT, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("results", [])


SG_PROPS = ["clay", "sand", "silt", "phh2o", "soc", "nitrogen", "wv0033", "wv1500"]
SG_FACTOR = {"clay": 10, "sand": 10, "silt": 10, "phh2o": 10, "soc": 10, "nitrogen": 100, "wv0033": 10, "wv1500": 10}


@st.cache_data(ttl=7 * 86400, show_spinner=False)
def get_soilgrids(lat: float, lon: float) -> dict[str, dict[str, float | None]]:
    """SoilGrids 2.0 (ISRIC, 250 m, machine-learning map). Returns {depth_label: {property: value}}."""
    params = [("lat", lat), ("lon", lon), ("value", "mean")]
    params += [("property", p) for p in SG_PROPS] + [("depth", d) for d, _ in SG_DEPTHS]
    r = requests.get("https://rest.isric.org/soilgrids/v2.0/properties/query", params=params, timeout=45, headers=HEADERS)
    r.raise_for_status()
    out: dict[str, dict[str, float | None]] = {}
    for layer in r.json()["properties"]["layers"]:
        name = layer["name"]
        factor = (layer.get("unit_measure") or {}).get("d_factor") or SG_FACTOR.get(name, 10)
        for dep in layer["depths"]:
            v = dep["values"].get("mean")
            out.setdefault(dep["label"], {})[name] = None if v is None else v / factor
    if not out:
        raise ValueError("SoilGrids لم يرجع طبقات لهذه النقطة (ربما مياه أو منطقة بلا بيانات).")
    return out


def root_zone_awc(sg: dict, root_m: float) -> float | None:
    """Available water (mm per metre of soil) from SoilGrids field capacity minus wilting point,
    weighted over the crop's root depth. None if data is missing or implausible."""
    root_cm, top, total_mm, used_cm = min(root_m * 100, 100), 0, 0.0, 0.0
    for label, thick in SG_DEPTHS:
        if top >= root_cm:
            break
        layer = sg.get(label, {})
        fc, wp = safe_float(layer.get("wv0033")), safe_float(layer.get("wv1500"))
        if fc is None or wp is None:
            return None
        t = min(thick, root_cm - top)
        total_mm += max(fc - wp, 0) / 100 * t * 10
        used_cm += t
        top += thick
    if used_cm <= 0:
        return None
    awc = total_mm / (used_cm / 100)
    return awc if 30 <= awc <= 250 else None  # outside this range = suspicious units, don't trust


def usda_texture(clay: float | None, sand: float | None, silt: float | None) -> str:
    """USDA soil texture class from clay/sand/silt percentages (standard triangle rules)."""
    if clay is None or sand is None or silt is None:
        return "—"
    if silt + 1.5 * clay < 15:
        return "رملية"
    if silt + 1.5 * clay >= 15 and silt + 2 * clay < 30:
        return "رملية طميية"
    if (7 <= clay < 20 and sand > 52 and silt + 2 * clay >= 30) or (clay < 7 and silt < 50 and silt + 2 * clay >= 30):
        return "طميية رملية"
    if 7 <= clay < 27 and 28 <= silt < 50 and sand <= 52:
        return "طميية"
    if (silt >= 50 and 12 <= clay < 27) or (50 <= silt < 80 and clay < 12):
        return "طميية سلتية"
    if silt >= 80 and clay < 12:
        return "سلتية"
    if 20 <= clay < 35 and silt < 28 and sand > 45:
        return "طينية رملية طميية"
    if 27 <= clay < 40 and 20 < sand <= 45:
        return "طينية طميية"
    if 27 <= clay < 40 and sand <= 20:
        return "طينية سلتية طميية"
    if clay >= 35 and sand > 45:
        return "طينية رملية"
    if clay >= 40 and silt >= 40:
        return "طينية سلتية"
    if clay >= 40:
        return "طينية"
    return "طميية"


MODIS = "https://modis.ornl.gov/rst/api/v1"


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def get_ndvi(lat: float, lon: float) -> dict[str, Any]:
    """Median MODIS NDVI (250 m, 16-day composites) around the point. NDVI = how green, not which crop."""
    err = "لا توجد بيانات."
    for product in ("MOD13Q1", "MYD13Q1"):
        try:
            r = requests.get(f"{MODIS}/{product}/dates", params={"latitude": lat, "longitude": lon},
                             headers={"Accept": "application/json"}, timeout=(5, 30))
            r.raise_for_status()
            payload = r.json()
            items = payload.get("dates", []) if isinstance(payload, dict) else payload
            dates = sorted(d["modis_date"] if isinstance(d, dict) else d for d in items)[-10:]
            if not dates:
                err = f"{product}: لا توجد فترات لهذه النقطة"
                continue
            r = requests.get(f"{MODIS}/{product}/subset", params={
                "latitude": lat, "longitude": lon, "startDate": dates[0], "endDate": dates[-1],
                "kmAboveBelow": 1, "kmLeftRight": 1}, headers={"Accept": "application/json"}, timeout=(5, 60))
            r.raise_for_status()
            subset = r.json()["subset"]
            nd = {s["modis_date"]: s["data"] for s in subset if s["band"].endswith("_NDVI")}
            ql = {s["modis_date"]: s["data"] for s in subset if s["band"].endswith("pixel_reliability")}
            pts = {}
            for code, vals in nd.items():
                flags = ql.get(code) or [0] * len(vals)
                good = [v * 0.0001 for v, q in zip(vals, flags) if v > -2000 and q in (0, 1)]
                if good:
                    pts[datetime.strptime(code[1:], "%Y%j")] = statistics.median(good)
            if not pts:
                err = f"{product}: كل البكسلات سحاب/غير صالحة"
                continue
            series = pd.Series(pts).sort_index()
            latest = float(series.iloc[-1])
            level = "barren" if latest < 0.12 else "sparse" if latest < 0.20 else "moderate" if latest < 0.40 else "dense"
            return {"ok": True, "series": series, "latest": latest, "date": series.index[-1].strftime("%Y-%m-%d"), "level": level}
        except (requests.RequestException, KeyError, ValueError, TypeError) as exc:
            err = f"{product}: {exc.__class__.__name__}"
    return {"ok": False, "message": err}


def nasa_frame(payload: dict[str, Any]) -> pd.DataFrame:
    frames = []
    for key, vals in payload["properties"]["parameter"].items():
        s = pd.Series(vals, name=key)
        s.index = pd.to_datetime(s.index, format="%Y%m%d", errors="coerce")
        frames.append(s)
    return pd.concat(frames, axis=1).sort_index().replace(-999, float("nan"))


def polygon_stats(feature: dict) -> tuple[float, float, float]:
    ring = feature["geometry"]["coordinates"][0]
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    clng, clat = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    ml, mn = 111320.0, 111320.0 * math.cos(math.radians(clat))
    xy = [((p[0] - clng) * mn, (p[1] - clat) * ml) for p in pts]
    area = abs(sum(xy[i][0] * xy[(i + 1) % len(xy)][1] - xy[(i + 1) % len(xy)][0] * xy[i][1] for i in range(len(xy)))) / 2
    return clat, clng, area


def water_balance(daily: pd.DataFrame, kc: float, taw: float, p: float, eff: float, start: date, today: date) -> pd.DataFrame:
    """FAO-56 root-zone bucket. Starts at field capacity on `start` (the farmer's last irrigation),
    then adds ETc and subtracts effective rain. Irrigation is only scheduled from today onward."""
    raw, dr, rows = p * taw, 0.0, []
    for d, row in daily[daily.index >= start].iterrows():
        et0, rain = safe_float(row["et0"]) or 0.0, safe_float(row["rain"]) or 0.0
        etc = et0 * kc
        eff_rain = 0.8 * rain if rain >= 2 else 0.0
        dr = min(max(dr + etc - eff_rain, 0.0), taw)
        irrigate, gross = False, 0.0
        if d >= today and dr >= raw:
            irrigate, gross, dr = True, dr / eff, 0.0
        rows.append({"date": d, "ET0": et0, "ETc": etc, "rain": rain, "eff_rain": eff_rain,
                     "depletion": dr, "irrigate": irrigate, "gross_mm": gross})
    return pd.DataFrame(rows)


# =========================================================
# FORECAST-DRIVEN TOOLS (transparent rules on real forecast data)
# =========================================================
def forecast_alerts(daily: pd.DataFrame, today: date) -> list[tuple[str, str, str]]:
    """Returns [(level, date, message)] from simple, stated thresholds on the 7-day forecast."""
    out: list[tuple[str, str, str]] = []
    for d, r in daily[daily.index >= today].iterrows():
        tmax, tmin = safe_float(r.get("tmax")), safe_float(r.get("tmin"))
        rain, wmax = safe_float(r.get("rain")), safe_float(r.get("wmax"))
        ds = d.strftime("%Y-%m-%d")
        if tmax is not None and tmax >= 38:
            out.append(("error", ds, f"🔥 حرارة شديدة: العظمى {tmax:.0f} °م — إجهاد حراري محتمل وزيادة في استهلاك الماء."))
        if tmin is not None and tmin <= 2:
            out.append(("error", ds, f"❄️ خطر صقيع: الصغرى {tmin:.0f} °م — احمِ الشتلات الحساسة."))
        if rain is not None and rain >= 10:
            out.append(("warning", ds, f"🌧️ مطر غزير متوقع: {rain:.0f} مم — أجّل الري والرش والتسميد."))
        if wmax is not None and wmax >= 10:
            out.append(("warning", ds, f"💨 رياح قوية: حتى {wmax:.0f} م/ث (≈ {wmax * 3.6:.0f} كم/س) — لا ترشّ في هذا اليوم."))
    return out


def spray_windows(weather: dict, today: date) -> pd.DataFrame | None:
    """Hours per day (06:00-18:00 local) with calm-enough conditions for spraying:
    wind 1-4 m/s, temperature <= 30 °C, humidity >= 40%, no rain. Rule of thumb, not a label instruction."""
    h = weather.get("hourly") or {}
    try:
        df = pd.DataFrame({"t": h["temperature_2m"], "rh": h["relative_humidity_2m"],
                           "w": h["wind_speed_10m"], "p": h["precipitation"]}, index=pd.to_datetime(h["time"]))
    except KeyError:
        return None
    df = df[(df.index >= pd.Timestamp(today)) & (df.index.hour >= 6) & (df.index.hour <= 18)].dropna()
    if df.empty:
        return None
    ok = df["w"].between(1, 4) & (df["t"] <= 30) & (df["rh"] >= 40) & (df["p"] <= 0)
    first = ok.groupby(df.index.normalize()).apply(lambda s: ", ".join(f"{i.hour:02d}:00" for i in s.index[s]) or "—")
    cnt = ok.groupby(df.index.normalize()).sum()
    return pd.DataFrame({"التاريخ": cnt.index.strftime("%Y-%m-%d"), "ساعات مناسبة": cnt.values.astype(int),
                         "الساعات": first.values})


def gdd_frame(daily: pd.DataFrame, base: float, upper: float = GDD_UPPER) -> pd.DataFrame:
    """Growing degree days, modified method: Tmax capped at `upper`, Tmin floored at `base`."""
    d = daily[["tmax", "tmin"]].dropna().copy()
    tmax, tmin = d["tmax"].clip(upper=upper), d["tmin"].clip(lower=base)
    d["gdd"] = (((tmax + tmin) / 2) - base).clip(lower=0)
    d["cum"] = d["gdd"].cumsum()
    return d


# =========================================================
# EXPORT (Excel + PDF) and the small live 3D chart
# =========================================================
# EXPORT START
_EMOJI = re.compile("[\U00010000-\U0010ffff\u2600-\u27bf\u2b00-\u2bff\ufe0f\u200d]")
try:
    import arabic_reshaper
    try:
        from bidi import get_display
    except ImportError:
        from bidi.algorithm import get_display
    _AR_OK = True
except Exception:
    _AR_OK = False


def _ar(s: str) -> str:
    return get_display(arabic_reshaper.reshape(s)) if _AR_OK else s


def _fmt(v: Any) -> str:
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return "—"
    if isinstance(v, bool):
        return "نعم" if v else "لا"
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return str(v)


def _tidy(df: pd.DataFrame) -> pd.DataFrame:
    """Plain, export-friendly copy: dates as text, bools as نعم/لا, numbers rounded."""
    d = df.copy()
    if isinstance(d.index, pd.DatetimeIndex) or d.index.name == "date":
        d = d.reset_index()
        d = d.rename(columns={d.columns[0]: "التاريخ"})
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            d[c] = d[c].dt.strftime("%Y-%m-%d")
        elif d[c].dtype == bool:
            d[c] = d[c].map({True: "نعم", False: "لا"})
        elif pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].round(2)
        elif d[c].dtype == object:
            d[c] = d[c].map(lambda v: v.strftime("%Y-%m-%d") if hasattr(v, "strftime") else v)
    return d


def make_xlsx(summary: pd.DataFrame, sections: list[tuple[str, pd.DataFrame]]) -> bytes:
    import importlib.util
    engine = next((e for e in ("openpyxl", "xlsxwriter") if importlib.util.find_spec(e)), None)
    if engine is None:
        raise RuntimeError("ثبّت المكتبة: pip install openpyxl")
    bio, used = io.BytesIO(), set()
    with pd.ExcelWriter(bio, engine=engine) as xw:
        for title, df in [("ملخص", summary)] + sections:
            name = re.sub(r"[\[\]:*?/\\]", " ", title)[:31]
            while name in used:
                name = name[:29] + "_2"
            used.add(name)
            d = _tidy(df)
            d.to_excel(xw, sheet_name=name, index=False)
            ws = xw.sheets[name]
            widths = [min(max([len(str(c))] + [len(_fmt(v)) for v in d[c]]) + 3, 48) for c in d.columns]
            if engine == "openpyxl":
                from openpyxl.styles import Alignment, Font, PatternFill
                from openpyxl.utils import get_column_letter
                ws.sheet_view.rightToLeft = True
                ws.freeze_panes = "A2"
                for i, w in enumerate(widths, 1):
                    ws.column_dimensions[get_column_letter(i)].width = w
                for cell in ws[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="1F6B45")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                ws.right_to_left()
                for i, w in enumerate(widths):
                    ws.set_column(i, i, w)
    return bio.getvalue()


def _find_font() -> str | None:
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    local = [os.path.join(here, f) for f in ("Cairo-Regular.ttf", "Amiri-Regular.ttf", "NotoNaskhArabic-Regular.ttf")]
    system = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf",
              "C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/arial.ttf",
              "/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]
    return next((p for p in local + system if os.path.exists(p)), None)


def make_pdf(summary: pd.DataFrame, sections: list[tuple[str, pd.DataFrame]], title: str, subtitle: str) -> bytes:
    if not _AR_OK:
        raise RuntimeError("ثبّت المكتبتين: pip install arabic-reshaper python-bidi")
    fp = _find_font()
    if not fp:
        raise RuntimeError("لم أجد خطًا عربيًا. ضع ملف Cairo-Regular.ttf بجوار هذا الملف.")
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    font = "AegisAR"
    if font not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font, fp))
    green, size = colors.HexColor("#1f6b45"), 8
    s_cell = ParagraphStyle("c", fontName=font, fontSize=size, leading=size + 3, alignment=TA_CENTER)
    s_head = ParagraphStyle("h", parent=s_cell, textColor=colors.white)
    s_h1 = ParagraphStyle("h1", fontName=font, fontSize=19, leading=26, alignment=TA_RIGHT, textColor=green)
    s_h2 = ParagraphStyle("h2", fontName=font, fontSize=12, leading=18, alignment=TA_RIGHT, textColor=green, spaceBefore=10, spaceAfter=4)
    s_note = ParagraphStyle("n", fontName=font, fontSize=8, leading=12, alignment=TA_RIGHT, textColor=colors.HexColor("#555555"))
    page_w, margin = A4[0], 1.2 * cm
    avail = page_w - 2 * margin

    def wrap(text: str, width: float) -> list[str]:
        lines, cur = [], ""
        for w in text.split():
            t = f"{cur} {w}".strip()
            if cur and pdfmetrics.stringWidth(t, font, size) > width:
                lines.append(cur)
                cur = w
            else:
                cur = t
        return lines + [cur]

    def para(txt: Any, width: float, style) -> Paragraph:
        text = _EMOJI.sub("", _fmt(txt)).strip() or "—"
        return Paragraph("<br/>".join(escape(_ar(l)) for l in wrap(text, width - 8)), style)

    def line(txt: str, style) -> Paragraph:
        return Paragraph("<br/>".join(escape(_ar(l)) for l in wrap(_EMOJI.sub("", txt).strip(), avail - 4) ), style)

    def table(df: pd.DataFrame) -> Table:
        d = _tidy(df)
        cols = list(d.columns)[::-1]                       # RTL: first column on the right
        wts = [min(max(max([len(str(c))] + [len(_fmt(v)) for v in d[c]]), 6), 60) for c in cols]
        widths = [avail * w / sum(wts) for w in wts]
        rows = [[para(c, w, s_head) for c, w in zip(cols, widths)]]
        rows += [[para(r[c], w, s_cell) for c, w in zip(cols, widths)] for _, r in d.iterrows()]
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), green),
                               ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b9cfc0")),
                               ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f8f3")]),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
        return t

    story = [line(title, s_h1), line(subtitle, s_note), Spacer(1, 8), table(summary)]
    for name, df in sections:
        story += [line(name, s_h2), table(df)]
    story += [Spacer(1, 12), line("للتخطيط الزراعي فقط؛ لا تعتمد عليه وحده في قرارات المبيدات أو التسميد. "
                                  "المصادر: Open-Meteo، NASA POWER، MODIS NDVI، ISRIC SoilGrids.", s_note)]

    def footer(canvas, doc):
        canvas.setFont(font, 8)
        canvas.drawCentredString(page_w / 2, 0.7 * cm, f"AEGIS · {doc.page}")

    bio = io.BytesIO()
    SimpleDocTemplate(bio, pagesize=A4, leftMargin=margin, rightMargin=margin, topMargin=1.3 * cm, bottomMargin=1.4 * cm,
                      title="AEGIS Report").build(story, onFirstPage=footer, onLaterPages=footer)
    return bio.getvalue()


LIVE3D_HTML = r"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<style>
html,body{margin:0;height:100%;background:transparent;font-family:Cairo,'Segoe UI',Tahoma,sans-serif;color:#d7efe0;overflow:hidden}
.box{position:relative;height:100%;box-sizing:border-box;border:1px solid rgba(139,240,178,.2);border-radius:18px;overflow:hidden;
background:radial-gradient(ellipse at 50% 0%,rgba(46,140,86,.24),transparent 62%),linear-gradient(160deg,rgba(14,38,25,.94),rgba(7,20,13,.96))}
canvas{width:100%;height:100%;display:block;touch-action:pan-y}
.lg{position:absolute;top:9px;right:14px;left:14px;display:flex;gap:14px;flex-wrap:wrap;font-size:11px;color:#a9c1b0;pointer-events:none}
.lg b{display:inline-block;width:9px;height:9px;border-radius:3px;margin-left:5px;vertical-align:middle}
.ttl{position:absolute;bottom:6px;right:14px;font-size:10px;color:#7f9a8a;pointer-events:none}
#tip{position:absolute;pointer-events:none;display:none;white-space:nowrap;background:rgba(6,17,12,.94);
border:1px solid rgba(139,240,178,.4);border-radius:9px;padding:4px 9px;font-size:11.5px}
</style></head><body><div class="box"><canvas id="c"></canvas><div class="lg" id="lg"></div>
<div class="ttl">توقعات 7 أيام · الارتفاع نسبي لأعلى قيمة في كل لون · مرّر للتفاصيل</div><div id="tip"></div></div>
<script>
const D=__DATA__;
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),tip=document.getElementById('tip');
document.getElementById('lg').innerHTML=D.series.map(s=>'<span><b style="background:'+s.color+'"></b>'+s.name+'</span>').join('');
let W=0,H=0;
function fit(){const d=window.devicePixelRatio||1;W=cv.clientWidth;H=cv.clientHeight;cv.width=W*d;cv.height=H*d;ctx.setTransform(d,0,0,d,0,0);}
fit();addEventListener('resize',fit);
const nd=D.days.length,ns=D.series.length;
const rgb=h=>[1,3,5].map(i=>parseInt(h.substr(i,2),16));
const shade=(h,f)=>'rgb('+rgb(h).map(v=>Math.max(0,Math.min(255,Math.round(v*f)))).join(',')+')';
let mx=-1,my=-1,t0=performance.now();
function pt(e){const r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top;}
cv.addEventListener('pointermove',pt);cv.addEventListener('pointerdown',pt);
cv.addEventListener('pointerleave',()=>{mx=my=-1;});
const FACES=[[1,0,0.8],[-1,0,0.58],[0,1,0.92],[0,-1,0.68]];
function frame(now){
  const t=(now-t0)/1000;
  ctx.clearRect(0,0,W,H);
  const rise=Math.min(1,t/1.6),ease=1-Math.pow(1-rise,3);
  const ang=0.62+0.4*Math.sin(t*0.33),ca=Math.cos(ang),sa=Math.sin(ang);
  const S=Math.min(W/(nd+2.6),H/6.4),cx=W/2,cy=H*0.74,MH=2.5;
  const P=(x,y,z)=>[cx+(x*ca-z*sa)*S,cy+(x*sa+z*ca)*S*0.42-y*S];
  const ex=nd/2+0.3,ez=ns*0.75+0.1;
  // floor
  ctx.beginPath();[[-ex,-ez],[ex,-ez],[ex,ez],[-ex,ez]].forEach((p,i)=>{const q=P(p[0],0,p[1]);i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]);});
  ctx.closePath();ctx.fillStyle='rgba(139,240,178,.06)';ctx.fill();ctx.strokeStyle='rgba(139,240,178,.22)';ctx.lineWidth=1;ctx.stroke();
  ctx.strokeStyle='rgba(139,240,178,.09)';
  for(let i=0;i<nd;i++){const x=i-(nd-1)/2,a=P(x,0,-ez),b=P(x,0,ez);ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}
  // day labels on the near edge
  ctx.fillStyle='#86a393';ctx.font='9px sans-serif';ctx.textAlign='center';
  for(let i=0;i<nd;i++){const q=P(i-(nd-1)/2,0,ez+0.35);ctx.fillText(D.days[i],q[0],q[1]+3);}
  // bars, far to near
  const bars=[];
  for(let j=0;j<ns;j++)for(let i=0;i<nd;i++){
    const x=i-(nd-1)/2,z=(j-(ns-1)/2)*1.5,s=D.series[j];
    const h=(0.06+0.94*s.n[i])*MH*ease*(1+0.09*Math.sin(t*1.7+i*0.8+j*1.9));
    bars.push({i,j,x,z,h,d:x*sa+z*ca,s});
  }
  bars.sort((a,b)=>a.d-b.d);
  let best=null,bd=18;
  for(const b of bars){const q=P(b.x,b.h,b.z),dd=Math.hypot(q[0]-mx,q[1]-my);if(dd<bd){bd=dd;best=b;}}
  for(const b of bars){
    const hv=b===best,hh=b.h*(hv?1.05:1),x0=b.x-0.36,x1=b.x+0.36,z0=b.z-0.45,z1=b.z+0.45,k=hv?1.18:1;
    for(const f of FACES){
      if(f[0]*sa+f[1]*ca<=0)continue;
      const c=f[0]?[[f[0]>0?x1:x0,z0],[f[0]>0?x1:x0,z1]]:[[x0,f[1]>0?z1:z0],[x1,f[1]>0?z1:z0]];
      const p=[P(c[0][0],0,c[0][1]),P(c[1][0],0,c[1][1]),P(c[1][0],hh,c[1][1]),P(c[0][0],hh,c[0][1])];
      ctx.beginPath();p.forEach((q,n)=>n?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();
      ctx.fillStyle=shade(b.s.color,f[2]*k);ctx.fill();
    }
    const tp=[P(x0,hh,z0),P(x1,hh,z0),P(x1,hh,z1),P(x0,hh,z1)];
    ctx.beginPath();tp.forEach((q,n)=>n?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();
    ctx.fillStyle=shade(b.s.color,1.12*k);ctx.fill();
    const c=P(b.x,hh,b.z);
    ctx.beginPath();ctx.arc(c[0],c[1],2.2+1.4*Math.sin(t*3+b.i+b.j),0,6.283);
    ctx.fillStyle='rgba(255,255,255,'+(0.35+0.25*Math.sin(t*3+b.i+b.j))+')';ctx.fill();
  }
  if(best){
    tip.style.display='block';tip.textContent=D.days[best.i]+' · '+best.s.name+': '+best.s.v[best.i];
    tip.style.left=Math.min(W-170,Math.max(4,mx+10))+'px';tip.style.top=Math.max(26,my-30)+'px';
  }else tip.style.display='none';
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
</script></body></html>"""


def live3d_html(daily: pd.DataFrame, today: date) -> str:
    """Small animated 3D bar chart of the next 7 forecast days (real Open-Meteo values)."""
    f = daily[daily.index >= today].head(7)
    if f.empty:
        return "<div></div>"
    defs = [("tmax", "أقصى حرارة °م", "#ffb35c"), ("rain", "المطر مم", "#62c7ff"), ("et0", "ET₀ مم/يوم", "#8bf0b2")]
    series = []
    for col, name, color in defs:
        vals = [safe_float(v) or 0.0 for v in f[col]]
        m = max(vals)
        series.append({"name": name, "color": color, "v": [round(v, 1) for v in vals], "n": [v / m if m > 0 else 0 for v in vals]})
    days = [pd.Timestamp(d).strftime("%m-%d") for d in f.index]
    return LIVE3D_HTML.replace("__DATA__", json.dumps({"days": days, "series": series}))


def collect_sections(rep: dict, status: dict) -> list[tuple[str, pd.DataFrame]]:
    order = [("fc", "توقعات 7 أيام"), ("irr", "جدول الري"), ("soil", "خصائص التربة"), ("alerts", "التنبيهات"),
             ("spray", "نوافذ الرش"), ("gdd", "الحرارة التراكمية GDD"), ("bal", "ميزان المطر والتبخر"), ("hist", "سجل NASA POWER")]
    out = [(title, rep[k]) for k, title in order if rep.get(k) is not None and len(rep[k])]
    out.append(("مصادر البيانات", pd.DataFrame([{"المصدر": k, "الحالة": "متاح" if ok else "فشل", "التفاصيل": note}
                                                for k, (ok, note) in status.items()])))
    return out
# EXPORT END


# =========================================================
# UI
# =========================================================
if "entered" not in st.session_state:
    st.session_state.entered = False
if not st.session_state.entered:
    # Sidebar hidden on the intro. The real Streamlit button is kept off-screen; the glass
    # button inside the globe iframe clicks it, so the entrance lives inside the Earth scene.
    st.markdown("""<style>
[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl'],[data-testid='collapsedControl']{display:none}
.st-key-aegis_enter{position:fixed;left:-10000px;top:0;width:1px;height:1px;overflow:hidden;opacity:0}
</style>""", unsafe_allow_html=True)
    components.html(INTRO_HTML, height=600, scrolling=False)
    if st.button("AEGIS_ENTER", key="aegis_enter"):
        st.session_state.entered = True
        st.rerun()
    st.stop()

st.markdown("""
<div class="agiz-hero">
  <div class="hero-copy">
    <div class="hero-kicker"><i></i> AEGIS</div>
    <div class="hero-title">AEGIS</div>
    <div class="hero-desc">AEGIS · بيانات حقيقية من Open-Meteo وNASA POWER وMODIS NDVI وSoilGrids — مع حساب ري بمعادلات FAO-56</div>
  </div>
  <div class="hero-orb">__LOGO__</div>
</div>
""".replace("__LOGO__", aegis_logo(46, "hero")), unsafe_allow_html=True)

for k, v in {"lat": 30.4167, "lon": 31.5667, "field_poly": None, "poly_sig": None, "last_click": None, "area_m2": None}.items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    st.markdown(f'<div class="aegis-brand">{aegis_logo(54, "sb")}<div><b>AEGIS</b><span>FIELD INTELLIGENCE</span></div></div>', unsafe_allow_html=True)
    st.header("إعدادات الحقل")
    if st.button("🌍 العودة للمقدمة"):
        st.session_state.entered = False
        st.rerun()
    place_text = st.text_input("ابحث عن مدينة أو قرية", value="بلبيس، مصر")
    if st.button("🔎 البحث عن الموقع"):
        try:
            res = geocode(place_text.strip()) if place_text.strip() else []
            st.session_state.location_choices = res
            if not res:
                st.warning("لم يتم العثور على الموقع؛ أدخل الإحداثيات يدويًا.")
        except requests.RequestException as e:
            st.error(f"تعذر الاتصال بخدمة تحديد المواقع: {e}")
    choices = st.session_state.get("location_choices", [])
    if choices:
        sel = st.selectbox("اختر نتيجة البحث", choices, format_func=lambda x: f"{x['name']} — {x.get('admin1', '')} {x.get('country', '')}")
        if st.button("اعتماد الموقع"):
            st.session_state.lat, st.session_state.lon = float(sel["latitude"]), float(sel["longitude"])
            st.rerun()
    lat = st.number_input("خط العرض", -90.0, 90.0, float(st.session_state.lat), format="%.5f")
    lon = st.number_input("خط الطول", -180.0, 180.0, float(st.session_state.lon), format="%.5f")
    st.session_state.lat, st.session_state.lon = lat, lon

    crop = st.selectbox("المحصول", list(CROPS.keys()))
    stage = st.selectbox("مرحلة النمو", STAGES, index=2)
    efficiency = st.slider("كفاءة نظام الري (%)", 40, 100, 85) / 100
    manual_area = st.number_input("مساحة الحقل (هكتار) — تُستبدل بمساحة المضلع لو رسمته", 0.01, 100000.0, 2.205, step=0.1)
    know_irrigation = st.checkbox("أعرف تاريخ آخر ري (أو آخر مرة التربة كانت مشبعة)")
    last_irrigation = None
    if know_irrigation:
        last_irrigation = st.date_input("تاريخ آخر ري", value=date.today() - timedelta(days=3),
                                        min_value=date.today() - timedelta(days=29), max_value=date.today())
    use_manual_awc = st.checkbox("إدخال السعة المائية للتربة يدويًا")
    manual_awc = st.number_input("السعة المائية المتاحة (مم/متر)", 30, 250, 140) if use_manual_awc else None
    sowing_date = st.date_input("تاريخ الزراعة (اختياري — لحساب الحرارة التراكمية GDD)", value=None,
                                min_value=date.today() - timedelta(days=29), max_value=date.today())
    if st.button("🔄 تحديث البيانات"):
        st.cache_data.clear()
        st.rerun()

today = date.today()
status: dict[str, tuple[bool, str]] = {}


rlat, rlon = round(lat, 5), round(lon, 5)
NDVI_NAME = "MODIS NDVI (الغطاء النباتي)"
JOBS = {
    "Open-Meteo (الطقس والتوقعات)": (get_weather, (rlat, rlon)),
    "Open-Meteo (رطوبة التربة المُنمذجة)": (get_soil_moisture, (rlat, rlon)),
    "NASA POWER (سجل المناخ)": (get_nasa_power, (rlat, rlon, (today - timedelta(days=31)).strftime("%Y%m%d"),
                                                (today - timedelta(days=2)).strftime("%Y%m%d"))),
    NDVI_NAME: (get_ndvi, (rlat, rlon)),
    "SoilGrids (خصائص التربة)": (get_soilgrids, (rlat, rlon)),
}


def _run(fn, args):
    try:
        return True, fn(*args)
    except Exception as exc:  # network/parsing/service errors are reported, never replaced by fake values
        return False, f"{exc.__class__.__name__}: {str(exc)[:110]}"


try:  # lets the worker threads use Streamlit's cache without warnings
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
    _ctx = get_script_run_ctx()
    _init = lambda: add_script_run_ctx(threading.current_thread(), _ctx)
except Exception:
    _init = None

# All five sources are requested at the same time, so the wait is the slowest one, not the sum.
with st.spinner("جارٍ جلب البيانات الحقيقية من المصادر..."):
    with ThreadPoolExecutor(max_workers=len(JOBS), initializer=_init) as pool:
        futures = {name: pool.submit(_run, fn, args) for name, (fn, args) in JOBS.items()}
        results = {name: f.result() for name, f in futures.items()}

for name, (ok, val) in results.items():
    status[name] = (ok, "تم جلب البيانات" if ok else val)


def _val(name):
    ok, val = results[name]
    return val if ok else None


weather = _val("Open-Meteo (الطقس والتوقعات)")
moisture = _val("Open-Meteo (رطوبة التربة المُنمذجة)")
nasa = _val("NASA POWER (سجل المناخ)")
soilgrids = _val("SoilGrids (خصائص التربة)")
_ok, _v = results[NDVI_NAME]
ndvi_res = _v if _ok else {"ok": False, "message": _v}
status[NDVI_NAME] = (ndvi_res["ok"], "تم جلب البيانات" if ndvi_res["ok"] else ndvi_res["message"])

area_ha = (st.session_state.area_m2 / 10000) if st.session_state.area_m2 else manual_area

# ---------- daily frame (past 30 days + 7 forecast) ----------
daily_df = None
if weather:
    d = weather["daily"]
    n_days = len(d["time"])
    daily_df = pd.DataFrame({"tmax": d["temperature_2m_max"], "tmin": d["temperature_2m_min"], "rain": d["precipitation_sum"],
                             "et0": d["et0_fao_evapotranspiration"],
                             "pop": d.get("precipitation_probability_max", [None] * n_days),
                             "wmax": d.get("wind_speed_10m_max", [None] * n_days)},
                            index=pd.to_datetime(d["time"]).date)
    daily_df.index = pd.Index([x for x in daily_df.index], name="date")

# ---------- root-zone water capacity ----------
awc, awc_source = None, ""
if use_manual_awc:
    awc, awc_source = float(manual_awc), "قيمة أدخلتها يدويًا"
elif soilgrids:
    awc = root_zone_awc(soilgrids, CROPS[crop]["root"])
    awc_source = "محسوبة من SoilGrids (سعة الحقل − نقطة الذبول، موزونة على عمق الجذور)"
no_veg = ndvi_res["ok"] and ndvi_res["level"] == "barren"

dep_now, taw_val = None, None
REP: dict[str, Any] = {}   # tables collected from every tab, used by the export tab
tab_over, tab_irr, tab_soil, tab_alert, tab_hist, tab_src, tab_exp = st.tabs(
    ["🌤️ الملخص والخريطة", "💧 الري", "🌱 التربة والغطاء النباتي", "⚠️ تنبيهات ونمو المحصول", "🛰️ سجل المناخ", "🔎 مصادر البيانات", "📄 تصدير التقارير"])

# ---------- TAB 1: overview + map ----------
with tab_over:
    left, right = st.columns([1.25, 1.3], gap="large")
    with left:
        st.subheader("📍 موقع الحقل")
        poly_json = st.session_state.field_poly
        m = folium.Map(location=[lat, lon], zoom_start=17, max_zoom=21, control_scale=True, tiles=None)
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                         attr="Tiles © Esri", name="قمر صناعي", max_zoom=21, max_native_zoom=19).add_to(m)
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
                         attr="Labels © Esri", name="أسماء الأماكن", overlay=True, show=False, max_zoom=21, max_native_zoom=19).add_to(m)
        folium.TileLayer("OpenStreetMap", name="خريطة", show=False, max_zoom=21, max_native_zoom=19).add_to(m)
        if poly_json:
            folium.GeoJson(poly_json, style_function=lambda _: {"color": "#8bf0b2", "weight": 3, "fillOpacity": .15}).add_to(m)
            _pts = poly_json["geometry"]["coordinates"][0]
            m.fit_bounds([[min(p[1] for p in _pts), min(p[0] for p in _pts)], [max(p[1] for p in _pts), max(p[0] for p in _pts)]],
                         padding=(30, 30), max_zoom=19)
        folium.Marker([lat, lon], tooltip="مركز الحقل", icon=folium.Icon(color="green", icon="leaf")).add_to(m)
        Draw(export=False, draw_options={"polyline": False, "rectangle": True, "polygon": True, "circle": False,
                                         "marker": False, "circlemarker": False}).add_to(m)
        Fullscreen(position="topright", title="ملء الشاشة", title_cancel="خروج").add_to(m)
        MeasureControl(position="bottomright", primary_length_unit="meters", primary_area_unit="hectares").add_to(m)
        folium.LayerControl(collapsed=True).add_to(m)
        mr = st_folium(m, height=560, use_container_width=True, returned_objects=["last_clicked", "all_drawings"], key="agiz_real_map")
        if mr:
            clicked = mr.get("last_clicked")
            csig = (round(clicked["lat"], 6), round(clicked["lng"], 6)) if clicked else None
            poly = next((f for f in reversed(mr.get("all_drawings") or []) if f.get("geometry", {}).get("type") == "Polygon"), None)
            if poly and json.dumps(poly["geometry"]["coordinates"]) != st.session_state.poly_sig:
                clat, clng, a = polygon_stats(poly)
                st.session_state.update(poly_sig=json.dumps(poly["geometry"]["coordinates"]), field_poly=poly, area_m2=a,
                                        last_click=csig, lat=round(clat, 5), lon=round(clng, 5))
                st.rerun()
            if csig and csig != st.session_state.last_click:
                st.session_state.last_click = csig
                st.session_state.lat, st.session_state.lon = csig
                st.rerun()
        st.caption(f"مساحة الحقل المستخدمة: **{area_ha:.2f} هكتار** ({area_ha * 2.381:.2f} فدان) — "
                   + ("من المضلع المرسوم على الخريطة." if st.session_state.area_m2 else "من الرقم المُدخل. ارسم حدود الحقل للحصول على مساحة فعلية."))
        if daily_df is not None:
            components.html(live3d_html(daily_df, today), height=290, scrolling=False)
    with right:
        if weather:
            cur = weather.get("current", {})
            _next3 = daily_df[daily_df.index >= today].head(3)["et0"].mean()
            components.html(scene_html(weather, cur, safe_float(_next3), ndvi_res["latest"] if ndvi_res["ok"] else None, today, rlat, rlon), height=340, scrolling=False)
            st.subheader("🌤️ الظروف الحالية — Open-Meteo")
            a, b, c, dd = st.columns(4)
            t_now = safe_float(cur.get("temperature_2m"))
            a.metric("الحرارة", f"{t_now:.1f} °م" if t_now is not None else "—")
            b.metric("الرطوبة", f"{cur.get('relative_humidity_2m')}%" if cur.get("relative_humidity_2m") is not None else "—")
            c.metric("المطر الحالي", f"{cur.get('precipitation', '—')} مم")
            dd.metric("الرياح", f"{cur.get('wind_speed_10m', '—')} م/ث")
            _alerts = forecast_alerts(daily_df, today)
            if _alerts:
                st.warning(f"⚠️ يوجد {len(_alerts)} تنبيه في توقعات الأيام السبعة القادمة — التفاصيل في تبويب «تنبيهات ونمو المحصول».")
            st.subheader("📆 توقعات الأيام السبعة القادمة")
            fc = daily_df[daily_df.index >= today].rename(columns={"tmax": "العظمى °م", "tmin": "الصغرى °م", "rain": "المطر مم",
                                                                   "et0": "ET₀ مم/يوم", "pop": "احتمال المطر %", "wmax": "أقصى رياح م/ث"})
            fc.index = pd.to_datetime(fc.index)
            REP["fc"] = fc
            st.dataframe(fc)
            st.line_chart(fc[["العظمى °م", "الصغرى °م"]])
        else:
            st.error("تعذر جلب الطقس. لن تُعرض أرقام بديلة. اضغط «تحديث البيانات» أو راجع تبويب مصادر البيانات.")

# ---------- TAB 2: irrigation ----------
with tab_irr:
    st.subheader("💧 جدولة الري — طريقة FAO-56")
    if no_veg:
        st.error(f"🏜️ لا يوجد غطاء نباتي أخضر عند هذه النقطة (NDVI = {ndvi_res['latest']:.2f}، {ndvi_res['date']}). "
                 "تم إيقاف توصية الري. اختر موقعًا مزروعًا أو تحقق من الإحداثيات.")
    elif daily_df is None:
        st.warning("لا توجد بيانات طقس حالية، فلا يمكن حساب الري.")
    else:
        kc = kc_for(crop, stage)
        REP["kc"] = kc
        etc_next = daily_df[daily_df.index >= today].head(3)
        et0_3 = safe_float(etc_next["et0"].mean()) or 0.0
        rain_3 = safe_float(etc_next["rain"].mean()) or 0.0
        etc = et0_3 * kc
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ET₀ — الأيام الـ3 القادمة", f"{et0_3:.1f} مم/يوم")
        c2.metric(f"ETc (Kc = {kc:.2f})", f"{etc:.1f} مم/يوم")
        c3.metric("مطر متوقع", f"{rain_3:.1f} مم/يوم")
        c4.metric("استهلاك الحقل", f"{etc * 10 * area_ha:.0f} م³/يوم", help="ETc × المساحة، قبل خسائر نظام الري")
        if awc is None:
            st.warning("السعة المائية للتربة غير متاحة (فشل SoilGrids أو قيمها غير منطقية). أدخلها يدويًا من الشريط الجانبي لتفعيل الجدولة الكاملة.")
        else:
            taw = awc * CROPS[crop]["root"]
            raw = CROPS[crop]["p"] * taw
            REP["taw"], REP["raw"] = taw, raw
            st.caption(f"السعة المائية: **{awc:.0f} مم/متر** ({awc_source}). المياه المتاحة في منطقة الجذور TAW = {taw:.0f} مم، والعتبة المسموح استنزافها RAW = {raw:.0f} مم.")
            if last_irrigation is None:
                st.info("للحصول على جدول ري فعلي: فعّل «أعرف تاريخ آخر ري» من الشريط الجانبي. بدون هذا التاريخ لا يمكن معرفة رطوبة الحقل الحالية، ولن أخمّنها.")
            else:
                wb = water_balance(daily_df, kc, taw, CROPS[crop]["p"], efficiency, last_irrigation, today)
                now_row = wb[wb["date"] == today]
                dep_now = float(now_row["depletion"].iloc[0]) if not now_row.empty else float(wb["depletion"].iloc[-1])
                taw_val = taw
                nxt = wb[wb["irrigate"]]
                d1, d2, d3 = st.columns(3)
                d1.metric("استنزاف الماء اليوم", f"{dep_now:.0f} مم", f"{dep_now / taw * 100:.0f}% من TAW", delta_color="off")
                if dep_now >= raw and not nxt.empty and nxt.iloc[0]["date"] == today:
                    d2.metric("التوصية", "اروِ اليوم")
                elif not nxt.empty:
                    d2.metric("الري القادم", pd.Timestamp(nxt.iloc[0]["date"]).strftime("%Y-%m-%d"))
                else:
                    d2.metric("الري القادم", "لا حاجة خلال 7 أيام")
                if not nxt.empty:
                    g = float(nxt.iloc[0]["gross_mm"])
                    d3.metric("كمية الري الإجمالية", f"{g:.0f} مم", f"≈ {g * 10 * area_ha:.0f} م³ للحقل", delta_color="off")
                # total irrigation water scheduled over the forecast window
                _tot = float(wb["gross_mm"].sum())
                if _tot > 0:
                    st.caption(f"إجمالي ماء الري المجدول خلال الأيام القادمة: **{_tot:.0f} مم** ≈ **{_tot * 10 * area_ha:,.0f} م³** للحقل كله (بعد حساب كفاءة الري).")
                show = wb.assign(date=pd.to_datetime(wb["date"]).dt.strftime("%Y-%m-%d")).rename(columns={
                    "date": "التاريخ", "ETc": "ETc مم", "rain": "مطر مم", "depletion": "استنزاف مم", "gross_mm": "ري إجمالي مم", "irrigate": "ري؟"})
                REP["irr"] = show[["التاريخ", "ETc مم", "مطر مم", "استنزاف مم", "ري؟", "ري إجمالي مم"]].round(1)
                st.dataframe(REP["irr"])
                st.line_chart(wb.assign(date=pd.to_datetime(wb["date"])).set_index("date")[["depletion"]].rename(columns={"depletion": "استنزاف الماء (مم)"}))
                st.download_button("تنزيل جدول الري CSV", show.to_csv(index=False).encode("utf-8-sig"), "aegis_irrigation_schedule.csv", "text/csv")
        st.info("الحساب: ETc = ET₀ × Kc، ثم خزان مائي لمنطقة الجذور مع مطر فعّال (80% من الأمطار ≥ 2 مم). معاملات Kc وعمق الجذور مرجعية تقريبية من FAO-56. تحقق دائمًا من رطوبة منطقة الجذور فعليًا قبل الري.")

    if moisture is not None and not moisture.empty:
        st.subheader("رطوبة التربة المُنمذجة — Open-Meteo (آخر 7 أيام)")
        mm = (moisture.resample("D").mean() * 100).round(1)
        mm.columns = ["3–9 سم", "9–27 سم", "27–81 سم"]
        st.line_chart(mm)
        st.caption("نتائج نموذج (حجم مائي %)، وليست قراءة مجس داخل حقلك.")

# ---------- TAB 3: soil + vegetation ----------
with tab_soil:
    st.subheader("🌿 الغطاء النباتي — MODIS NDVI")
    if ndvi_res["ok"]:
        lvl = ndvi_res["level"]
        msg = {"barren": "🏜️ لا يوجد غطاء أخضر (أرض جرداء/صحراء أو لا محصول حاليًا)", "sparse": "🟡 غطاء ضعيف جدًا (محصول صغير أو بور)",
               "moderate": "🟢 غطاء نباتي متوسط", "dense": "🟢 غطاء نباتي كثيف"}[lvl]
        {"barren": st.error, "sparse": st.warning}.get(lvl, st.success)(f"{msg} — NDVI = {ndvi_res['latest']:.2f} ({ndvi_res['date']})")
        _ser = ndvi_res["series"]
        if len(_ser) >= 2:
            _chg = float(_ser.iloc[-1] - _ser.iloc[-2])
            _trend = "في ارتفاع 📈" if _chg > 0.02 else "في انخفاض 📉" if _chg < -0.02 else "مستقر ➖"
            st.metric("تغيّر NDVI عن الفترة السابقة (16 يومًا)", f"{_chg:+.2f}", _trend, delta_color="off")
        st.line_chart(_ser.rename("NDVI"))
        st.caption("NDVI يقول إن الأرض خضراء، لا يحدد نوع المحصول. الدقة 250 م وتجميع كل 16 يومًا؛ السحب أو الأرض البور قد تعطي قيمة منخفضة.")
    else:
        st.info(f"تعذر فحص الغطاء النباتي ({ndvi_res['message']}).")

    st.subheader("🧪 خصائص التربة — SoilGrids (ISRIC)")
    if soilgrids:
        rows = []
        for label, _ in SG_DEPTHS:
            l = soilgrids.get(label, {})
            rows.append({"العمق": label, "القوام (USDA)": usda_texture(safe_float(l.get("clay")), safe_float(l.get("sand")), safe_float(l.get("silt"))),
                         "طين %": l.get("clay"), "رمل %": l.get("sand"), "سلت %": l.get("silt"), "pH": l.get("phh2o"),
                         "كربون عضوي g/kg": l.get("soc"), "نيتروجين g/kg": l.get("nitrogen")})
        REP["soil"] = pd.DataFrame(rows).round(1)
        st.dataframe(REP["soil"])
        _ph = safe_float(soilgrids.get("0-5cm", {}).get("phh2o"))
        if _ph is not None and _ph >= 8.0:
            st.info(f"التربة السطحية قلوية (pH ≈ {_ph:.1f}): قد تقل إتاحة الحديد والزنك والفوسفور لبعض المحاصيل. أكّد بتحليل تربة قبل أي قرار تسميد.")
        if awc:
            st.metric("السعة المائية المتاحة لمنطقة الجذور", f"{awc:.0f} مم/متر")
        avail = None if (dep_now is None or not taw_val) else max(0.0, min(1.0, 1 - dep_now / taw_val))
        st.markdown("##### 🧊 قطاع التربة ثلاثي الأبعاد")
        components.html(plotly_html(soil_profile_fig(soilgrids, CROPS[crop]["root"], avail)), height=490, scrolling=False)
        st.caption("لون كل طبقة = نسبة الطين من SoilGrids (الأغمق أكثر طينًا). الغلاف الأخضر = منطقة الجذور. "
                   + ("الغلاف الأزرق = الماء المتاح المتبقي حسب جدولة الري." if avail is not None else "فعّل «أعرف تاريخ آخر ري» ليظهر مستوى الماء المتاح."))
        st.caption("SoilGrids خريطة تربة عالمية بدقة 250 م مبنية على نماذج تعلّم آلة، وليست تحليل مختبر لحقلك. استخدمها كتقدير أولي وتحقق بتحليل تربة.")
    else:
        st.info("تعذر جلب بيانات SoilGrids حاليًا (الخدمة قد تحدّ الطلبات). جرّب بعد دقيقة.")

# ---------- TAB 4: alerts, spray windows, GDD ----------
with tab_alert:
    if daily_df is None:
        st.warning("لا توجد بيانات طقس حالية، فلا يمكن حساب التنبيهات.")
    else:
        st.subheader("⚠️ تنبيهات الأيام السبعة القادمة")
        alerts = forecast_alerts(daily_df, today)
        REP["alerts"] = pd.DataFrame([{"المستوى": "خطر" if lv == "error" else "تحذير", "التاريخ": ds, "التنبيه": tx} for lv, ds, tx in alerts]
                                     or [{"المستوى": "—", "التاريخ": "—", "التنبيه": "لا توجد تنبيهات في توقعات الأيام السبعة"}])
        if alerts:
            for level, ds, text in alerts:
                (st.error if level == "error" else st.warning)(f"**{ds}** — {text}")
        else:
            st.success("لا توجد تنبيهات: لا حرارة شديدة ولا صقيع ولا مطر غزير ولا رياح قوية في التوقعات.")
        st.caption("العتبات المستخدمة: حرارة عظمى ≥ 38 °م، صغرى ≤ 2 °م، مطر ≥ 10 مم/يوم، رياح ≥ 10 م/ث. قواعد عامة وليست حدودًا خاصة بمحصول بعينه.")

        st.subheader("🧴 نوافذ الرش المناسبة (من التوقعات الساعية)")
        sw = spray_windows(weather, today)
        if sw is not None:
            REP["spray"] = sw
            st.dataframe(sw)
            st.caption("ساعة مناسبة = بين 6 ص و6 م مع رياح 1–4 م/ث، حرارة ≤ 30 °م، رطوبة ≥ 40%، وبدون مطر. قاعدة إرشادية عامة؛ التزم دائمًا بملصق المبيد وتعليمات الجهة المختصة.")
        else:
            st.info("التوقعات الساعية غير متاحة حاليًا.")

        st.subheader("🌡️ الحرارة التراكمية GDD")
        base = GDD_BASE[crop]
        g = gdd_frame(daily_df, base)
        g.index = pd.to_datetime(g.index)
        if sowing_date is not None:
            g = g[g.index >= pd.Timestamp(sowing_date)]
            g["cum"] = g["gdd"].cumsum()
            st.caption(f"محسوبة من تاريخ الزراعة {sowing_date} حتى نهاية التوقعات.")
        else:
            st.caption("محسوبة لآخر 30 يومًا + التوقعات. أدخل تاريخ الزراعة في الشريط الجانبي لحسابها من بدء الموسم.")
        if not g.empty:
            REP["gdd"] = g.rename(columns={"tmax": "العظمى °م", "tmin": "الصغرى °م", "gdd": "GDD اليومية", "cum": "GDD التراكمية"})
            past = g[g.index <= pd.Timestamp(today)]
            k1, k2, k3 = st.columns(3)
            k1.metric(f"GDD حتى اليوم (أساس {base:g} °م)", f"{past['gdd'].sum():.0f}" if not past.empty else "—")
            k2.metric("GDD متوقعة خلال 7 أيام", f"{g[g.index > pd.Timestamp(today)]['gdd'].sum():.0f}")
            k3.metric("متوسط GDD اليومي (آخر 7 أيام)", f"{past['gdd'].tail(7).mean():.1f}" if not past.empty else "—")
            st.line_chart(g[["cum"]].rename(columns={"cum": "GDD التراكمية"}))
            st.caption(f"طريقة الحساب: متوسط (أعلى حرارة مقيّدة بـ {GDD_UPPER:g} °م وأدنى حرارة لا تقل عن الأساس) − حرارة الأساس. قيمة الأساس تقريبية للمحصول؛ قارنها بمراحل النمو المعتمدة لصنفك.")

        st.subheader("💦 ميزان المطر والتبخر — آخر 30 يومًا")
        pastd = daily_df[daily_df.index < today].tail(30)
        r30, e30 = float(pastd["rain"].fillna(0).sum()), float(pastd["et0"].fillna(0).sum())
        w1, w2, w3 = st.columns(3)
        w1.metric("مطر آخر 30 يومًا", f"{r30:.0f} مم")
        w2.metric("ET₀ آخر 30 يومًا", f"{e30:.0f} مم")
        w3.metric("العجز المائي المناخي", f"{max(e30 - r30, 0):.0f} مم", help="ET₀ − المطر. قيمة موجبة كبيرة = الحقل اعتمد على الري.")
        _bal = pastd[["rain", "et0"]].fillna(0).rename(columns={"rain": "المطر مم", "et0": "ET₀ مم"})
        _bal.index = pd.to_datetime(_bal.index)
        REP["bal"] = _bal
        st.bar_chart(_bal)

# ---------- TAB 5: NASA history ----------
with tab_hist:
    st.subheader("🛰️ سجل NASA POWER — آخر 30 يومًا")
    if nasa:
        hist = nasa_frame(nasa).rename(columns={"T2M": "متوسط الحرارة °م", "T2M_MAX": "العظمى °م", "T2M_MIN": "الصغرى °م",
                                                "PRECTOTCORR": "المطر مم/يوم", "RH2M": "الرطوبة %",
                                                "ALLSKY_SFC_SW_DWN": "الإشعاع الشمسي MJ/m²/يوم"})
        st.caption("بيانات شبكة مناخية يومية (ليست محطة داخل الحقل) وقد تتأخر آخر يومين.")
        REP["hist"] = hist
        st.line_chart(hist[["متوسط الحرارة °م"]])
        st.bar_chart(hist[["المطر مم/يوم"]])
        st.markdown("##### 🧊 مسار المناخ ثلاثي الأبعاد (حرارة × مطر × إشعاع)")
        components.html(plotly_html(climate_cube_fig(hist)), height=490, scrolling=False)
        st.caption("كل نقطة يوم من آخر 30 يومًا (اللون يتدرج من الأقدم للأحدث). اسحب لتدوير المحاور.")
        st.dataframe(hist.tail(10).round(2))
        st.download_button("تنزيل سجل NASA POWER CSV", hist.to_csv(index_label="date").encode("utf-8-sig"), "aegis_nasa_power_daily.csv", "text/csv")
    else:
        st.info("تعذر جلب بيانات NASA POWER حاليًا.")

# ---------- TAB 6: data transparency ----------
with tab_src:
    st.subheader("🔎 حالة كل مصدر بيانات")
    st.dataframe(pd.DataFrame([{"المصدر": k, "الحالة": "✅" if ok else "⚠️", "التفاصيل": note} for k, (ok, note) in status.items()]))
    st.markdown("""
**حقيقي (بيانات فعلية):** طقس وتوقعات Open-Meteo (يومية وساعية)، سجل NASA POWER، خضرة MODIS NDVI، خصائص تربة SoilGrids.
**حسابات شفافة فوق بيانات حقيقية:** ET₀ (من Open-Meteo)، ETc = ET₀ × Kc، الخزان المائي FAO-56، قوام التربة USDA، الحرارة التراكمية GDD، تنبيهات الطقس ونوافذ الرش.
**تقديرات يجب تحقق ميداني منها:** رطوبة التربة المُنمذجة، قيم SoilGrids، معاملات Kc، حرارة الأساس لـ GDD، وتاريخ الري والزراعة (من إدخالك).
لا يوجد في التطبيق أي رقم ثابت يُعرض كأنه قياس. إن فشل مصدر تظهر رسالة بدل قيمة مختلقة.
""")
    st.caption(
        "المصادر: Open-Meteo، NASA POWER، NASA ORNL DAAC (MODIS)، "
        "ISRIC SoilGrids، Esri، OpenStreetMap. "
        "للتخطيط الزراعي فقط؛ لا تعتمد عليه وحده في قرارات المبيدات أو التسميد."
    )


# ---------- TAB 7: export everything to Excel / PDF ----------
with tab_exp:
    st.subheader("📄 تصدير كل التقارير")
    st.caption("ملف واحد فيه: الملخص، التوقعات، الري، التربة، التنبيهات، نوافذ الرش، GDD، ميزان المطر، سجل NASA، ومصادر البيانات.")
    _rows = [("تاريخ التقرير", str(today)), ("الموقع (خط العرض، خط الطول)", f"{lat:.5f}, {lon:.5f}"), ("المحصول", crop),
             ("مرحلة النمو", stage), ("مساحة الحقل", f"{area_ha:.2f} هكتار ({area_ha * 2.381:.2f} فدان)"),
             ("كفاءة الري", f"{efficiency * 100:.0f}%")]
    if weather:
        _c = weather.get("current", {})
        _rows += [("الحرارة الحالية °م", _c.get("temperature_2m")), ("الرطوبة %", _c.get("relative_humidity_2m")),
                  ("الرياح م/ث", _c.get("wind_speed_10m"))]
    if ndvi_res["ok"]:
        _rows.append(("NDVI (الغطاء النباتي)", f"{ndvi_res['latest']:.2f} ({ndvi_res['date']})"))
    if awc:
        _rows.append(("السعة المائية مم/متر", f"{awc:.0f}"))
    if REP.get("kc") is not None:
        _rows.append(("معامل المحصول Kc", f"{REP['kc']:.2f}"))
    if "taw" in REP:
        _rows += [("TAW مم", f"{REP['taw']:.0f}"), ("RAW مم", f"{REP['raw']:.0f}")]
    if dep_now is not None:
        _rows.append(("استنزاف الماء اليوم مم", f"{dep_now:.0f}"))
    _summary = pd.DataFrame(_rows, columns=["البند", "القيمة"])
    _sections = collect_sections(REP, status)
    st.write("الأقسام المتاحة الآن: " + "، ".join(t for t, _ in _sections))
    _sig = (rlat, rlon, crop, stage, str(today))
    if st.button("📦 تجهيز التقارير", key="build_reports"):
        out: dict[str, Any] = {"sig": _sig, "xlsx": None, "pdf": None, "errs": []}
        with st.spinner("جارٍ تجهيز ملفات Excel وPDF..."):
            try:
                out["xlsx"] = make_xlsx(_summary, _sections)
            except Exception as exc:
                out["errs"].append(f"Excel: {exc}")
            try:
                out["pdf"] = make_pdf(_summary, _sections, "تقرير AEGIS للحقل", f"{today} · {crop} · {lat:.4f}, {lon:.4f}")
            except Exception as exc:
                out["errs"].append(f"PDF: {exc}")
        st.session_state["reports"] = out
    _rp = st.session_state.get("reports")
    if _rp:
        if _rp["sig"] != _sig:
            st.warning("هذا التقرير لموقع أو محصول مختلف عن الحالي. اضغط «تجهيز التقارير» لتحديثه.")
        _c1, _c2 = st.columns(2)
        if _rp["xlsx"]:
            _c1.download_button("⬇️ تنزيل Excel", _rp["xlsx"], f"aegis_report_{today}.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx")
        if _rp["pdf"]:
            _c2.download_button("⬇️ تنزيل PDF", _rp["pdf"], f"aegis_report_{today}.pdf", "application/pdf", key="dl_pdf")
        for _e in _rp["errs"]:
            st.error(_e)
