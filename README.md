# Morning Brief — 데일리 경제 브리핑

매일 아침 7시 KST에 한국·미국 증시와 디지털 자산의 핵심을 자동으로 정리해 발송하는 시스템.

---

## 🚀 라이브 사이트

**https://briefing.hwion.app**

---

## 📐 시스템 구조

```
┌──────────────────────────────────────┐
│  Claude Cloud Routine (07:00 KST)    │
│  ↓ Skill: economy-briefing           │
└──────────────────────────────────────┘
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
  [HTML 파일 생성]      [텔레그램 발송]
   briefings/*.html      via 봇 API
        ↓
  [git push origin main]
        ↓
  [GitHub Pages 배포]
        ↓
  briefing.hwion.app
```

---

## 📁 폴더 구조

```
morning-brief/
├── CNAME                      # 커스텀 도메인 설정 (briefing.hwion.app)
├── README.md                  # 이 문서
├── index.html                 # 메인 페이지 (지난 브리핑 목록)
├── index.json                 # 브리핑 메타데이터 (Routine이 매일 갱신)
├── subscribers.json           # 텔레그램 발송 대상 리스트
├── 404.html                   # 잘못된 주소 페이지
├── briefings/                 # 일별 브리핑 HTML
│   ├── 2026-05-06-morning.html
│   ├── 2026-05-07-morning.html
│   └── ...
├── skills/
│   └── economy-briefing/
│       └── SKILL.md           # Claude 스킬 정의
└── .github/
    └── workflows/             # GitHub Actions (선택)
```

---

## 🛠️ 초기 셋업

### 1단계: 로컬 폴더 준비

이 폴더(`morning-brief/`)를 본인 PC의 적당한 위치에 둠. 예:
```
C:\Users\[사용자명]\Documents\morning-brief
```

### 2단계: GitHub Repo 생성

1. https://github.com/new 접속
2. **Repository name**: `morning-brief`
3. **Public** 선택 (Pages 무료 사용을 위해)
4. README, .gitignore 등 체크 해제 (이미 있음)
5. Create repository

### 3단계: 로컬 → GitHub 푸시

Windows PowerShell 또는 Git Bash에서:

```bash
cd C:\Users\[사용자명]\Documents\morning-brief
git init
git add .
git commit -m "Initial commit: Morning Brief setup"
git branch -M main
git remote add origin https://github.com/[GitHub_사용자명]/morning-brief.git
git push -u origin main
```

### 4단계: GitHub Pages 활성화

1. Repo 페이지 → **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main`, `/ (root)`
4. **Save**
5. 잠시 후 `Custom domain`에 `briefing.hwion.app` 입력 → Save
6. **Enforce HTTPS** 체크

### 5단계: Cloudflare DNS 설정

1. Cloudflare 대시보드 → `hwion.app` 선택 → **DNS** → **Records**
2. **Add record**:
   - Type: `CNAME`
   - Name: `briefing`
   - Target: `[GitHub_사용자명].github.io`
   - Proxy status: **DNS only** (회색 구름) ⚠️ 중요
3. **Save**

> Proxy를 켜면(주황 구름) GitHub Pages SSL이 충돌할 수 있어 처음엔 DNS only로.
> 나중에 안정화되면 Cloudflare Proxy로 전환 가능 (CDN/DDoS 방어 활용).

### 6단계: HTTPS 인증서 발급 대기

GitHub이 자동으로 Let's Encrypt 인증서를 발급해줍니다. 보통 5-30분 소요.
완료되면 https://briefing.hwion.app 접속 시 정상 표시.

### 7단계: Claude 스킬 설치

`skills/economy-briefing/SKILL.md`를 다음 경로에 복사:

**Windows**:
```
%APPDATA%\Claude\skills\economy-briefing\SKILL.md
```

또는 Claude 데스크탑 앱 → Settings → Skills 메뉴에서 Import.

### 8단계: 텔레그램 봇 셋업

자세한 가이드: `docs/telegram-setup.md` 참조

---

## 🔄 일일 자동 운영

### Cloud Routine 등록

1. https://claude.ai/code/scheduled 접속
2. **+ New routine** 클릭
3. 다음 정보 입력:
   - **Name**: 데일리 경제 브리핑
   - **Schedule**: `0 7 * * *` (매일 07:00 KST)
   - **Model**: claude-sonnet-4-6 (또는 4-7)
   - **Prompt**: `economy-briefing 스킬을 실행해서 오늘의 데일리 브리핑을 생성해줘`
   - **Working folder**: 로컬 morning-brief 폴더 경로
4. **Create**

### 매일 자동 흐름

```
07:00 → Routine 시작
07:01 → 어제 브리핑 + 인덱스 로드
07:02 → 웹 검색 (8-14회)
07:04 → 데이터 가공 + HTML 생성
07:06 → 셀프 체크 통과
07:07 → briefings/[오늘날짜]-morning.html 저장
07:07 → index.html, index.json 갱신
07:08 → git commit + push
07:09 → 텔레그램 봇으로 발송
07:10 → GitHub Pages 배포 완료
       → 구독자가 메시지 받음
```

---

## 🚨 트러블슈팅

### Pages가 404 표시됨
- Settings → Pages 다시 확인. Custom domain 등록되어 있는지.
- DNS 전파 시간 (10분-1시간) 기다리기.

### HTTPS 인증서 발급 안 됨
- Cloudflare Proxy를 **DNS only**로 설정했는지 확인.
- GitHub Settings → Pages → "Enforce HTTPS" 회색이면 인증서 미발급 상태. 1시간 후 재시도.

### Routine 실행되었는데 push 안 됨
- 로컬 working folder의 git 인증 확인.
- GitHub Personal Access Token 만료 여부 확인.

### 텔레그램 메시지 안 옴
- subscribers.json의 chat_id가 정확한지 확인.
- 봇과 1:1 대화방을 한 번이라도 시작했는지 확인 (그래야 봇이 메시지 보낼 수 있음).
- access.json의 allowlist에 본인 ID 있는지 확인.

---

## 📊 운영 가이드

### 매주 일요일 점검

- 지난 7일 브리핑 품질 리뷰 (15개 셀프 체크 통과율)
- 어제 시나리오 예측 적중률 추적
- subscribers.json 업데이트 (구독 추가/제거)

### 빅 이벤트 데이

CPI/FOMC/한은 금통위/빅테크 어닝 등은 정규 브리핑 외 추가 브리핑 권장.
SKILL.md의 "빅 이벤트 데이 워크플로우" 참조.

---

## 📝 라이선스 / 면책

본 시스템에서 생성하는 콘텐츠는 정보 제공 목적이며 투자 권유나 자문이 아닙니다.
