# GitHub Pages + Cloudflare 셋업 가이드

`briefing.hwion.app`을 GitHub Pages에 연결하는 단계별 가이드.

소요 시간: 약 30분 (DNS 전파 대기 시간 포함)

---

## 사전 준비물 체크

- [ ] GitHub 계정
- [ ] Cloudflare에서 hwion.app 도메인 등록되어 있음
- [ ] Windows에 Git 설치됨 (없으면 https://git-scm.com/download/win)

Git 설치 확인:
```powershell
git --version
# git version 2.xx.x 같은 출력이 나오면 OK
```

---

## STEP 1. GitHub Repo 생성 (5분)

### 1-1. 새 Repo 만들기

1. https://github.com/new 접속
2. 다음 입력:
   - **Repository name**: `morning-brief`
   - **Description**: `데일리 경제 브리핑` (선택)
   - **Public** 선택 ⚠️ (GitHub Pages 무료 사용 조건)
   - **Add a README**, **Add .gitignore**, **license** 모두 **체크 해제**
3. **Create repository** 클릭

### 1-2. Repo 주소 확인

생성 후 페이지에서 다음을 확인하고 어딘가에 복사해두기:
```
https://github.com/[GitHub사용자명]/morning-brief.git
```

---

## STEP 2. 로컬에서 Git 푸시 (5분)

### 2-1. PowerShell 또는 Git Bash 열기

Windows 키 누르고 "PowerShell" 검색해서 열기.

### 2-2. 작업 폴더로 이동

`morning-brief` 폴더를 둔 곳으로 이동:
```powershell
cd C:\Users\[사용자명]\Documents\morning-brief
```

### 2-3. Git 초기 설정 (처음 한 번만)

```powershell
git config --global user.name "본인이름"
git config --global user.email "본인@email.com"
```

### 2-4. Git 초기화 + 푸시

```powershell
git init
git add .
git commit -m "Initial setup: Morning Brief launch"
git branch -M main
git remote add origin https://github.com/[GitHub사용자명]/morning-brief.git
git push -u origin main
```

마지막 명령 시 GitHub 로그인 창이 뜨면 로그인.

> **인증 오류 발생 시**: GitHub은 비밀번호 대신 **Personal Access Token** 사용.
> 1. https://github.com/settings/tokens 접속
> 2. **Generate new token (classic)** 클릭
> 3. Scope에서 `repo` 체크
> 4. 생성된 토큰을 비밀번호 자리에 입력

### 2-5. 푸시 확인

브라우저에서 본인 repo 페이지 새로고침. 파일들이 보이면 성공.

---

## STEP 3. GitHub Pages 활성화 (3분)

### 3-1. Pages 설정 진입

1. Repo 페이지 우측 상단 **Settings** 클릭
2. 좌측 메뉴에서 **Pages** 클릭

### 3-2. Source 설정

- **Source**: `Deploy from a branch` 선택
- **Branch**: `main` 선택, `/ (root)` 선택
- **Save** 클릭

### 3-3. 첫 배포 확인

위쪽에 다음 메시지가 떠야 함:
```
Your site is live at https://[GitHub사용자명].github.io/morning-brief/
```

이 주소로 한 번 들어가서 페이지가 뜨는지 확인. (약간의 대기 시간 필요)

### 3-4. 커스텀 도메인 입력

같은 Pages 설정 화면에서:
- **Custom domain**: `briefing.hwion.app` 입력
- **Save** 클릭
- ⚠️ "Domain's DNS record could not be retrieved" 경고가 나와도 무시 (다음 단계 후 사라짐)

---

## STEP 4. Cloudflare DNS 설정 (5분)

### 4-1. Cloudflare 대시보드 접속

1. https://dash.cloudflare.com 로그인
2. 도메인 목록에서 **hwion.app** 클릭

### 4-2. DNS 레코드 추가

좌측 메뉴 **DNS** → **Records** 클릭.

**Add record** 버튼을 누르고:

| 필드 | 값 |
|---|---|
| Type | `CNAME` |
| Name | `briefing` |
| Target | `[GitHub사용자명].github.io` (`.` 빼지 말고 그대로) |
| Proxy status | **DNS only** (회색 구름 ⚠️ 중요) |
| TTL | `Auto` |

**Save** 클릭.

> **왜 DNS only?** GitHub Pages의 SSL 인증서 발급이 Cloudflare Proxy(주황 구름)와 충돌합니다.
> 첫 셋업은 DNS only로 하고, 인증서 발급 완료 후 원하면 Proxy로 전환 가능.

### 4-3. DNS 전파 확인

PowerShell에서:
```powershell
nslookup briefing.hwion.app
```

`[GitHub사용자명].github.io`로 답변이 나오면 DNS 설정 OK.
보통 1-5분 내 전파되지만 최대 30분까지 걸릴 수 있음.

---

## STEP 5. HTTPS 인증서 대기 (10-30분)

GitHub이 자동으로 Let's Encrypt 인증서를 발급함. 대기만 하면 됨.

### 진행 상황 확인

GitHub Repo → Settings → Pages 페이지에서:

- 처음: "DNS check in progress" 표시
- 5-10분 후: "DNS check successful" 메시지로 변경
- 그 후: "Your site is live at https://briefing.hwion.app" 표시

마지막 단계에서 **Enforce HTTPS** 체크박스가 활성화됨 → 체크.

---

## STEP 6. 작동 확인

브라우저에서 다음 URL들이 모두 접속되는지 확인:

- ✅ https://briefing.hwion.app
- ✅ https://briefing.hwion.app/briefings/2026-05-06-morning.html
- ✅ https://briefing.hwion.app/존재하지않는페이지 → 404 페이지 표시

---

## 🚨 자주 겪는 문제

### "DNS_PROBE_FINISHED_NXDOMAIN" 에러
- DNS 전파 대기 중. 30분 후 재시도.

### Pages는 되는데 커스텀 도메인 404
- CNAME 파일이 repo에 있는지 확인 (`/CNAME`)
- 내용이 정확히 `briefing.hwion.app` 한 줄인지 확인

### "Your site is having problems building"
- 보통 HTML 문법 오류. Repo의 Actions 탭에서 빌드 로그 확인.

### 인증서 발급 1시간 넘게 안 됨
1. Cloudflare에서 Proxy를 **DNS only**로 확실히 했는지 재확인
2. GitHub Settings → Pages → Custom domain 한 번 지웠다 다시 입력
3. 그래도 안 되면 30분 후 재시도

---

## ✅ 셋업 완료 후

이제 매일 새 브리핑 HTML 파일을 push하면 자동으로 배포됩니다:

```powershell
cd C:\Users\[사용자명]\Documents\morning-brief
git add .
git commit -m "Daily briefing 2026-05-07"
git push
```

배포는 평균 30초-2분 내 완료. https://briefing.hwion.app 에서 즉시 확인 가능.

다음 단계: **텔레그램 봇 셋업** (`docs/telegram-setup.md`)
