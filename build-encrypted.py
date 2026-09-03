# -*- coding: utf-8 -*-
"""
swiftmr-log-jump 공개 배포본 빌더.

내부 사본(평문 HTML) 전체를 암호로 AES-256-GCM 암호화해서
비밀번호 입력 화면만 들어 있는 index.html 을 만든다.
공개 URL 의 소스를 받아도 암호 없이는 주소·클러스터명·datasource UID 가 읽히지 않는다.

  python build_encrypted.py <평문.html> <출력 index.html> <암호>

WebCrypto 와 파라미터를 맞춘다: PBKDF2-HMAC-SHA256 150,000회 / salt 16B / AES-256-GCM / IV 12B
"""
import base64
import hashlib
import io
import json
import os
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 150000

src_path, out_path = sys.argv[1], sys.argv[2]
if len(sys.argv) < 4:
    sys.exit("암호를 인자로 넘기세요. 이 파일에 암호를 적어 두지 마십시오.\n"
             "  python build_encrypted.py <평문.html> <출력.html> <암호>")
password = sys.argv[3]

plain = io.open(src_path, encoding="utf-8").read().encode("utf-8")

salt = os.urandom(16)
iv = os.urandom(12)
key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITER, dklen=32)
blob = AESGCM(key).encrypt(iv, plain, None)

payload = {
    "v": 1,
    "kdf": {"name": "PBKDF2", "hash": "SHA-256", "iter": ITER,
            "salt": base64.b64encode(salt).decode()},
    "iv": base64.b64encode(iv).decode(),
    "ct": base64.b64encode(blob).decode(),
}

loader = """<meta charset="utf-8">
<title>SwiftMR Log Jump</title>
<meta name="robots" content="noindex,nofollow,noarchive">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>
:root{
  --paper:#F2F6FC; --surface:#FFFFFF; --surface-2:#E9F0FA;
  --ink:#101B2D; --ink-2:#2C3E57; --muted:#5A6E8C; --faint:#8DA0BC;
  --edge:#D3E0F0; --edge-strong:#B4C8E4;
  --signal:#3D6FD1; --signal-ink:#25488F; --signal-wash:#E4EDFC;
  --danger:#B03038;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#0B121D; --surface:#131D2C; --surface-2:#1A2637;
  --ink:#E6EEFA; --ink-2:#C3D2E6; --muted:#93A6C2; --faint:#6D82A0;
  --edge:#243347; --edge-strong:#354963;
  --signal:#7FA8F5; --signal-ink:#B5CDFB; --signal-wash:#152540;
  --danger:#F08A90;
}}
:root[data-theme="dark"]{
  --paper:#0B121D; --surface:#131D2C; --surface-2:#1A2637;
  --ink:#E6EEFA; --ink-2:#C3D2E6; --muted:#93A6C2; --faint:#6D82A0;
  --edge:#243347; --edge-strong:#354963;
  --signal:#7FA8F5; --signal-ink:#B5CDFB; --signal-wash:#152540;
  --danger:#F08A90;
}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:var(--paper);color:var(--ink);
 font-family:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;
 display:flex;align-items:center;justify-content:center;padding:24px;
 background-image:linear-gradient(var(--edge) 1px,transparent 1px),
                  linear-gradient(90deg,var(--edge) 1px,transparent 1px);
 background-size:56px 56px,56px 56px;background-position:-1px -1px;word-break:keep-all;overflow-wrap:break-word}
.mono{font-family:'JetBrains Mono','SFMono-Regular',Consolas,monospace}
.box{width:100%;max-width:396px;background:var(--surface);
 border:1px solid var(--edge-strong);border-radius:10px;overflow:hidden;
 box-shadow:0 1px 2px rgba(16,27,45,.06),0 18px 44px -20px rgba(37,72,143,.38)}
.crown{display:flex;align-items:center;gap:8px;padding:10px 14px;
 background:var(--surface-2);border-bottom:1px solid var(--edge)}
.crown i{width:8px;height:8px;border-radius:2px;background:var(--signal);opacity:.6;flex:none}
.crown span{font-family:'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:.06em;
 color:var(--muted);text-transform:uppercase}
.body{padding:24px}
h1{margin:0 0 4px;font-size:21px;font-weight:700;letter-spacing:-.02em}
h1 em{font-style:normal;color:var(--signal)}
p{margin:0 0 18px;font-size:12.5px;color:var(--muted);line-height:1.6}
p .sent{display:block}
label{display:block;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.1em;
 text-transform:uppercase;color:var(--faint);margin:0 0 5px}
select,input{width:100%;padding:10px 11px;border:1px solid var(--edge-strong);border-radius:6px;
 background:var(--paper);color:var(--ink);font-family:inherit;font-size:14px}
input{font-family:'JetBrains Mono',monospace;letter-spacing:.14em}
select{font-size:13px;margin-bottom:14px}
input:focus,select:focus{outline:none;border-color:var(--signal);
 box-shadow:0 0 0 3px var(--signal-wash)}
button{width:100%;margin-top:14px;padding:11px;border:0;border-radius:6px;cursor:pointer;
 background:var(--signal);color:var(--paper);font-family:'JetBrains Mono',monospace;
 font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
button:hover{background:var(--signal-ink)}
button:disabled{opacity:.55;cursor:progress}
.err{margin-top:11px;font-size:12.5px;font-weight:600;color:var(--danger);display:none}
.foot{display:flex;justify-content:space-between;gap:10px;align-items:center;
 padding:10px 14px;border-top:1px solid var(--edge);background:var(--surface-2)}
.foot span{font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.06em;
 color:var(--faint);text-transform:uppercase}
:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
</style>
<div class="box">
  <div class="crown"><i></i><span>swiftmr-log-jump &#10095; auth</span></div>
  <div class="body">
    <h1>SwiftMR <em>Log Jump</em></h1>
    <p data-i="sub"></p>
    <label for="lang" data-i="langlab"></label>
    <select id="lang" aria-label="Language">
      <option value="ko">\ud55c\uad6d\uc5b4</option>
      <option value="en">English</option>
    </select>
    <label for="pw" data-i="pwlab"></label>
    <input type="password" id="pw" autocomplete="off">
    <button id="go" type="button"></button>
    <div class="err" id="err"></div>
  </div>
  <div class="foot">
    <span>AIRS Global Technical Support</span>
    <span>AES-256-GCM</span>
  </div>
</div>
<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
(function(){
  "use strict";
  var STR={
    ko:{sub:"<span class='sent'>사내 엔지니어용 도구입니다.</span><span class='sent'>공용 암호를 입력하세요.</span>",
        pw:"암호", go:"열기", going:"여는 중…",
        langlab:"언어", pwlab:"공용 암호",
        bad:"암호가 맞지 않습니다.",
        nocrypto:"이 브라우저/주소에서는 복호화를 할 수 없습니다. https 주소로 열어야 합니다(로컬 파일 불가)."},
    en:{sub:"<span class='sent'>Internal engineering tool.</span><span class='sent'>Enter the shared password.</span>",
        pw:"Password", go:"Open", going:"Opening…",
        langlab:"Language", pwlab:"Shared password",
        bad:"That password is not right.",
        nocrypto:"This browser or address cannot decrypt. Open it over https (local files will not work)."}
  };
  var P=JSON.parse(document.getElementById("payload").textContent);
  var pw=document.getElementById("pw"),go=document.getElementById("go"),
      err=document.getElementById("err"),lang=document.getElementById("lang");
  var LKEY="swiftmr-log-jump/lang", L="ko";
  try{ var v0=localStorage.getItem(LKEY); if(v0==="en"||v0==="ko")L=v0; }catch(e){}
  function paint(){
    var S=STR[L];
    document.querySelector('[data-i="sub"]').innerHTML=S.sub;
    document.querySelector('[data-i="langlab"]').textContent=S.langlab;
    document.querySelector('[data-i="pwlab"]').textContent=S.pwlab;
    pw.placeholder=S.pw; go.textContent=S.go; lang.value=L;
    document.documentElement.lang=L;
  }
  lang.onchange=function(){
    L=lang.value==="en"?"en":"ko";
    try{localStorage.setItem(LKEY,L);}catch(e){}
    paint();
  };
  function b(x){var r=atob(x),a=new Uint8Array(r.length);for(var i=0;i<r.length;i++)a[i]=r.charCodeAt(i);return a;}
  function fail(m){err.textContent=m;err.style.display="block";go.disabled=false;go.textContent=STR[L].go;}
  paint();
  if(!(window.crypto&&crypto.subtle)){
    fail(STR[L].nocrypto); pw.disabled=true; go.disabled=true; return;
  }
  function open_(){
    var v=pw.value||"";
    if(!v)return;
    err.style.display="none";go.disabled=true;go.textContent=STR[L].going;
    try{localStorage.setItem(LKEY,L);}catch(e){}
    crypto.subtle.importKey("raw",new TextEncoder().encode(v),{name:"PBKDF2"},false,["deriveKey"])
    .then(function(k){
      return crypto.subtle.deriveKey(
        {name:"PBKDF2",salt:b(P.kdf.salt),iterations:P.kdf.iter,hash:P.kdf.hash},
        k,{name:"AES-GCM",length:256},false,["decrypt"]);
    })
    .then(function(k){ return crypto.subtle.decrypt({name:"AES-GCM",iv:b(P.iv)},k,b(P.ct)); })
    .then(function(buf){
      var html=new TextDecoder("utf-8").decode(buf);
      document.open();document.write(html);document.close();
    })
    .catch(function(){ fail(STR[L].bad); pw.select(); });
  }
  go.onclick=open_;
  pw.onkeydown=function(e){if(e.key==="Enter")open_();};
  pw.focus();
})();
</script>
"""

loader = loader.replace("__PAYLOAD__", json.dumps(payload, separators=(",", ":")))
io.open(out_path, "w", encoding="utf-8").write(loader)

print("plain   : %8d bytes  %s" % (len(plain), src_path))
print("output  : %8d bytes  %s" % (len(loader.encode('utf-8')), out_path))
print("password: %s   (PBKDF2-SHA256 %d회 / AES-256-GCM)" % (password, ITER))
