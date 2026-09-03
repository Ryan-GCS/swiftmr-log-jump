# swiftmr-log-jump

병원/사이트 프리셋을 고르면 클러스터·네임스페이스·datasource·시간창이 맞춰진
**Grafana Explore 딥링크**를 만들어 주는 사내 엔지니어용 정적 도구.

- 런처: `/` — `index.html`
- Loki 사용 매뉴얼(국·영문): `/manual` — `playbook.html`

배포: `swiftmr-log-jump.netlify.app` · `main` 에 푸시하면 자동 반영(빌드 단계 없음)

## ⚠️ 이 리포의 파일은 전부 암호화본입니다

`index.html` / `playbook.html` 은 **암호 입력 화면 + AES-256-GCM 암호문**입니다.
소스를 받아도 암호 없이는 내부 주소·클러스터명·datasource UID 가 읽히지 않습니다.
(PBKDF2-HMAC-SHA256 150,000회 / salt 16B / IV 12B)

**평문 원본은 이 리포에 없습니다.** 다음 위치에만 있습니다 —

```
G:\내 드라이브\12_업무자동화 feat. Claude\swiftmr-log-jump\
  swiftmr-log-jump-launcher-2026-09-03.html   ← 런처 평문(원본)
  swiftmr-loki-playbook-2026-09-03.html       ← 매뉴얼 평문(원본)
  swiftmr-log-jump-start-here.md              ← 먼저 읽는 문서
  swiftmr-loki-verify-evidence-2026-09-03.md  ← 검증 원문
```

## 고치는 절차

1. Drive 의 평문 파일을 고친다
2. 암호화본을 다시 만든다

```bash
python build-encrypted.py <평문.html> index.html    '<암호>'
python build-encrypted.py <매뉴얼.html> playbook.html '<암호>'
```

3. 커밋 · 푸시

`cryptography` 패키지가 필요합니다. **암호는 이 리포에 적지 마십시오** — 공용 암호는 슬랙/Drive 로만 전달합니다. **암호를 바꾸려면 반드시 다시 빌드해야 합니다** —
암호가 키 유도에 쓰이므로 로더만 고쳐서는 바뀌지 않습니다.

## 손볼 때 주의

- 프리셋 시드를 바꾸면 평문 안의 `KEY`(`swiftmr-log-jump/presets/vN`) 버전을 올려야
  기존 브라우저가 새 값을 받습니다. 헤더 버전 배지도 같이 올리세요.
- **URL 을 옮기면 모두의 저장된 프리셋이 사라집니다** — `localStorage` 가 origin 에 묶여 있습니다.
- 주소·클러스터 값의 출처는 DevOps 노션 서비스 매트릭스입니다.
  노션 CS 가이드 (0) 의 주소표는 6곳이 틀렸으니 근거로 쓰지 마세요.

## 확정값 (2026-09-03 실측)

| 항목 | 값 |
| --- | --- |
| OSS Grafana Loki datasource UID | `P8E80F9AEF21F6940` (legacy·euc1·use1 3곳 동일) |
| Grafana Cloud datasource UID | `grafanacloud-logs` |
| V4 | cloud-api 있음 → SwiftCloud Job ID(viewer F12) → Grafana Cloud |
| V3 | cloud-api 없음 → Job ID(admin) → 리전 / legacy Grafana |

DCS 로그(`job="dcs"`)는 Grafana Cloud 에 없습니다 — 리전 OSS 전용입니다.
`ACC-…` Accession 은 어느 로그에도 없고, 숫자 Accession 은 admin-connector 접근로그에만 남습니다.
