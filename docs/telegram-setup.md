# 텔레그램 봇 셋업 가이드

데일리 브리핑을 자동으로 발송할 텔레그램 봇 만들기.

소요 시간: 약 15분

---

## 🤖 텔레그램 봇이란?

텔레그램에서 만들어지는 자동화 계정. 토큰만 있으면 누구든 코드/Claude로 메시지 보낼 수 있어요.
구독자는 봇과 1:1 대화방을 한 번 시작해두면 그 대화방으로 매일 메시지가 옴.

---

## STEP 1. 봇 생성 (5분)

### 1-1. BotFather 찾기

텔레그램 앱 또는 웹(https://web.telegram.org)에서:
1. 검색창에 `@BotFather` 입력
2. 파란 체크 마크 있는 공식 계정 클릭
3. **Start** 또는 `/start` 입력

### 1-2. 새 봇 생성

BotFather에게 차례로 입력:

```
/newbot
```

**봇 이름 (Display name)** 입력 — 사람이 보는 이름. 예:
```
Morning Brief Bot
```

**봇 사용자명 (Username)** 입력 — 반드시 `bot`으로 끝나야 함. 예:
```
morning_brief_bot
```
(이미 사용 중인 이름이면 다른 거 시도. `hwion_brief_bot`, `mbrief_kr_bot` 등)

### 1-3. 토큰 복사 + 안전하게 보관

생성 성공하면 다음과 같은 메시지가 옴:

```
Done! Congratulations on your new bot. ...

Use this token to access the HTTP API:
123456789:AAHfiqksKZ8aBcDeFgHiJkLmNoPqRsTuVwX

Keep your token secure...
```

이 **토큰 전체** (`:` 포함)를 어딘가 안전한 곳에 복사. ⚠️ 절대 GitHub에 commit하지 말 것.

권장 저장 위치:
- 본인 PC의 `.env` 파일 (gitignore에 등록되어 있음)
- 1Password, Bitwarden 같은 비밀번호 관리자

### 1-4. 봇 프로필 설정 (선택)

BotFather에서 추가로:
```
/setdescription
```
"매일 아침 7시 KST에 한국·미국 증시와 코인 시장의 핵심을 정리해서 보내드립니다." 같은 설명.

```
/setuserpic
```
프로필 사진 설정 (브랜드 'M' 같은 이미지).

---

## STEP 2. 본인 chat_id 확보 (2분)

봇이 메시지를 보내려면 받는 사람의 **chat_id** 숫자를 알아야 함.

### 2-1. UserInfoBot 찾기

텔레그램 검색에서 `@userinfobot` 검색 → Start.

### 2-2. ID 받기

봇이 자동으로 본인 정보를 알려줌:

```
Id: 123456789
First: 제이
Username: @your_username
```

이 `Id` 숫자(123456789)가 본인 **chat_id**.

### 2-3. 봇과 1:1 대화 시작

방금 만든 본인 봇 (`@morning_brief_bot` 같은) 검색 → Start. 이걸 안 하면 봇이 메시지를 보낼 권한이 없음.

---

## STEP 3. subscribers.json 업데이트 (1분)

`morning-brief/subscribers.json` 파일 수정:

```json
{
  "subscribers": [
    {
      "chat_id": "123456789",
      "name": "제이",
      "active": true,
      "preferences": {
        "format": "full",
        "include_crypto": true,
        "morning_only": true
      },
      "added_at": "2026-05-06"
    }
  ]
}
```

`123456789` 자리에 본인 chat_id 입력.

---

## STEP 4. Claude Telegram Plugin 설치 (5분)

Claude가 텔레그램으로 메시지 보낼 수 있게 공식 플러그인 설치.

### 4-1. Bun 설치

플러그인이 Bun이라는 런타임 사용. PowerShell 관리자 권한으로:

```powershell
powershell -c "irm bun.sh/install.ps1 | iex"
```

설치 후 PowerShell 재시작.

### 4-2. Claude Code 데스크탑에서 플러그인 설치

Claude 데스크탑 앱 또는 터미널에서:

```bash
claude --channels plugin:telegram@claude-plugins-official
```

### 4-3. 봇 토큰 등록

플러그인 설정 파일 위치:
```
%USERPROFILE%\.claude\channels\telegram\.env
```

이 파일을 메모장으로 열고:
```
TELEGRAM_BOT_TOKEN=123456789:AAHfiqksKZ8aBcDeFgHiJkLmNoPqRsTuVwX
```

방금 BotFather에서 받은 토큰을 입력하고 저장.

### 4-4. Claude 재시작

Claude 데스크탑 종료 후 다시 시작.

---

## STEP 5. 페어링 (2분)

봇과 Claude를 연결하는 단계.

### 5-1. 봇과 페어링 시작

텔레그램에서 본인 봇 (`@morning_brief_bot`)에게 아무 메시지 입력:
```
hi
```

봇이 자동 응답으로 페어링 코드를 보냄:
```
Pairing code: ABC123
```

### 5-2. Claude에 페어링 코드 입력

Claude 데스크탑 앱 또는 CLI에서:
```
/telegram:pair ABC123
```

### 5-3. Allowlist 설정 (보안)

기본은 페어링한 사용자만 접근 가능. 다음 명령으로 본인 ID를 명시적으로 추가:
```
/telegram:access add 123456789
```

---

## STEP 6. 발송 테스트 (1분)

Claude에게:
```
텔레그램 봇으로 chat_id 123456789에게 "테스트 메시지: Morning Brief 셋업 완료" 라고 보내줘
```

본인 텔레그램에 메시지 도착하면 ✅ 셋업 완료.

---

## 🔧 구독자 추가 방법 (지인용)

지인 1명 추가하는 흐름:

### 지인이 할 일
1. 텔레그램에서 `@userinfobot` 시작 → ID 받기 (예: 987654321)
2. 본인 봇 (`@morning_brief_bot`) 검색 → Start

### 제이가 할 일
1. `subscribers.json`에 추가:
   ```json
   {
     "chat_id": "987654321",
     "name": "지인A",
     "active": true,
     "preferences": { "format": "full", ... }
   }
   ```
2. Claude에서 access 추가:
   ```
   /telegram:access add 987654321
   ```
3. git commit + push.

---

## 🚨 자주 겪는 문제

### "Bot was blocked by the user"
- 그 사람이 본인 봇을 차단했거나, 봇과 대화방을 한 번도 시작 안 함.
- 그 사람에게 봇 검색 → Start 한 번 누르라고 안내.

### Bun 설치 실패
- Windows Defender나 백신이 차단. 일시 비활성화 후 재시도.
- 또는 https://bun.sh 에서 수동 다운로드.

### 페어링 코드 안 옴
- Claude를 `--channels plugin:telegram` 옵션으로 켰는지 확인.
- BotFather에서 토큰 재발급 시도.

### 메시지 발송 시 "Forbidden: bot can't initiate conversation"
- chat_id가 잘못됐거나, 그 사람이 봇과 대화 시작 안 함.

---

## 보안 주의사항

⚠️ **봇 토큰을 절대 GitHub에 올리지 마세요.**

- `.env` 파일은 `.gitignore`에 이미 등록되어 있음
- 실수로 push했다면 즉시 BotFather에서 `/revoke` 후 재발급
- subscribers.json의 chat_id는 노출돼도 큰 문제 없음 (그 사람들에게만 영향)

---

## ✅ 셋업 완료 체크리스트

- [ ] BotFather로 봇 생성, 토큰 안전하게 저장
- [ ] 본인 chat_id 확보 (`@userinfobot`)
- [ ] subscribers.json에 본인 추가
- [ ] Claude Telegram Plugin 설치 완료
- [ ] `.env`에 토큰 등록
- [ ] 페어링 + Allowlist 설정
- [ ] 테스트 메시지 발송 성공

다음 단계: **Cloud Routine 등록** (`docs/routine-setup.md`)
