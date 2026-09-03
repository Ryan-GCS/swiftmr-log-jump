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
<style>
:root{--paper:#F7F9FA;--surface:#fff;--ink:#0E1418;--muted:#5D6B73;--edge:#DCE3E7;
 --edge-strong:#C2CED4;--signal:#0F6E7E;--danger:#A6231C}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --paper:#0E1418;--surface:#161E23;--ink:#E4EDF1;--muted:#93A3AB;--edge:#27343B;
 --edge-strong:#37474F;--signal:#35B6C7;--danger:#EE8078}}
:root[data-theme="dark"]{--paper:#0E1418;--surface:#161E23;--ink:#E4EDF1;--muted:#93A3AB;
 --edge:#27343B;--edge-strong:#37474F;--signal:#35B6C7;--danger:#EE8078}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:var(--paper);color:var(--ink);
 font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
 display:flex;align-items:center;justify-content:center;padding:24px}
.box{width:100%;max-width:380px;background:var(--surface);border:1px solid var(--edge);
 border-radius:8px;padding:26px;box-shadow:0 1px 2px rgba(0,0,0,.06),0 10px 28px -14px rgba(0,0,0,.28)}
h1{margin:0 0 5px;font-size:20px;font-weight:700;letter-spacing:-.02em}
p{margin:0 0 18px;font-size:12.5px;color:var(--muted);line-height:1.55}
select{width:100%;margin-bottom:10px;padding:9px;border:1px solid var(--edge-strong);border-radius:5px;
 background:var(--paper);color:var(--ink);font-family:inherit;font-size:13px}
input{width:100%;padding:10px;border:1px solid var(--edge-strong);border-radius:5px;
 background:var(--paper);color:var(--ink);font-family:inherit;font-size:14px}
button{width:100%;margin-top:12px;padding:11px;border:0;border-radius:5px;cursor:pointer;
 background:var(--signal);color:var(--paper);font-family:inherit;font-size:13.5px;font-weight:700}
button:disabled{opacity:.55;cursor:progress}
.err{margin-top:10px;font-size:12.5px;font-weight:600;color:var(--danger);display:none}
:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
</style>
<div class="box">
  <h1>SwiftMR Log Jump</h1>
  <p data-i="sub"></p>
  <select id="lang" aria-label="Language">
    <option value="ko">한국어</option>
    <option value="en">English</option>
  </select>
  <input type="password" id="pw" autocomplete="off">
  <button id="go" type="button"></button>
  <div class="err" id="err"></div>
</div>
<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
(function(){
  "use strict";
  var STR={
    ko:{sub:"사내 엔지니어용 도구입니다. 공용 암호를 입력하세요.",
        pw:"암호", go:"열기", going:"여는 중…",
        bad:"암호가 맞지 않습니다.",
        nocrypto:"이 브라우저/주소에서는 복호화를 할 수 없습니다. https 주소로 열어야 합니다(로컬 파일 불가)."},
    en:{sub:"Internal engineering tool. Enter the shared password.",
        pw:"Password", go:"Open", going:"Opening…",
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
    document.querySelector('[data-i="sub"]').textContent=S.sub;
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
