# swiftmr-log-jump

사내 엔지니어용 정적 도구. 사이트 프리셋을 고르면 클러스터·네임스페이스·datasource·시간창이
맞춰진 **Grafana Explore 딥링크**를 만들어 줍니다. 서버·백엔드 없음.

AIRS Global Technical Support · v1.0

- 런처: `/` — `public/index.html`
- Loki 사용 매뉴얼(국·영문): `/manual` — `public/playbook.html`

배포: Netlify 정적. `main` 에 푸시하면 자동 반영(빌드 단계 없음).

## ⚠️ 이 리포에는 평문이 없습니다

`public/` 의 두 HTML 은 **암호 입력 화면 + AES-256-GCM 암호문**입니다.
소스를 받아도 암호 없이는 내부 주소·클러스터명·datasource UID 가 읽히지 않습니다.
(PBKDF2-HMAC-SHA256 150,000회 / salt 16B / IV 12B)

**평문 원본과 모든 상수·검증 기록은 Google Drive 에만 있습니다** —
`12_업무자동화 feat. Claude\swiftmr-log-jump\` 의 `swiftmr-log-jump-start-here.md` 부터 읽으십시오.
호스트명·클러스터명·datasource UID 같은 값은 **이 리포에 적지 않습니다.**

## 고치는 절차

1. Drive 의 평문 HTML 을 고친다
2. 암호화본을 다시 만든다 — `cryptography` 패키지가 필요합니다

```bash
python build-encrypted.py <평문런처.html>   public/index.html    '<암호>'
python build-encrypted.py <평문매뉴얼.html> public/playbook.html '<암호>'
```

3. 커밋 · 푸시

**암호는 이 리포에 적지 마십시오** — 공용 암호는 슬랙/Drive 로만 전달합니다.
빌더는 암호를 인자로만 받고, 없으면 종료합니다.
**암호를 바꾸려면 반드시 다시 빌드**해야 합니다(키 유도에 쓰이므로 로더만 고쳐서는 안 바뀝니다).

## 배포 구조

`netlify.toml` 의 `publish = "public"` 입니다. 서빙되는 것은 `public/` 안의 파일뿐이고
`README.md` 와 `build-encrypted.py` 는 웹으로 노출되지 않습니다. **이 분리를 유지하십시오** —
`publish = "."` 로 되돌리면 이 문서까지 공개 URL 로 읽힙니다.

`noindex` 는 세 겹입니다: HTML 메타 · `public/robots.txt` · `netlify.toml` 의 `X-Robots-Tag`.

## 손볼 때 주의

- 프리셋 시드를 바꾸면 평문 안의 저장 키(`swiftmr-log-jump/presets/vN`) 버전을 올려야
  기존 브라우저가 새 값을 받습니다. 헤더 버전 배지도 같이 올리세요.
- **URL 을 옮기면 모두의 저장된 프리셋이 사라집니다** — `localStorage` 가 origin 에 묶여 있습니다.
- 프리셋은 처음 열면 **0개로 시작**합니다. 빈 상태 배너의 되돌리기로 기본값을 받습니다.
- 팀 공유는 프리셋 JSON 파일(«파일로 저장» → «파일에서»)로 합니다.
