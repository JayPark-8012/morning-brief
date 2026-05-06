# 텔레그램 봇 셋업 가이드

데일리 브리핑을 자동으로 발송할 텔레그램 봇 설정.

소요 시간: 약 10분

---

## ✅ 셋업 완료 체크리스트

- [x] BotFather로 봇 생성, 토큰 안전하게 저장
- [x] 본인 chat_id 확보
- [x] subscribers.json에 본인 추가
- [x] `.env`에 토큰 등록
- [x] 테스트 메시지 발송 성공

---

## 봇 정보

- 봇 이름: Morning Brief Bot
- 봇 유저명: @hwion_brief_bot
- 봇 ID: 8251801766

---

## 발송 방법

별도 플러그인 없이 Telegram Bot HTTP API를 직접 호출한다.

### curl로 메시지 발송

```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=CHAT_ID" \
  --data-urlencode "text=메시지 내용" \
  --data-urlencode "parse_mode=HTML"
```

### Python으로 메시지 발송

```python
import os, requests

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "1612013580"
text = "📊 오늘의 브리핑 내용"

resp = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
)
print(resp.json())
```

### Claude가 직접 발송할 때

Claude에게 다음과 같이 요청:

```
D:\Claude\morning-brief\.env 파일에서 TELEGRAM_BOT_TOKEN을 읽어서,
subscribers.json의 모든 active 구독자에게 텔레그램 메시지를 보내줘.
```

---

## 환경 변수

`.env` 파일 위치: `D:\Claude\morning-brief\.env`

```
TELEGRAM_BOT_TOKEN=<봇 토큰>
```

이 파일은 `.gitignore`에 등록되어 있어 GitHub에 올라가지 않는다.

---

## subscribers.json 관리

`subscribers.json`에서 구독자를 관리한다.

```json
{
  "subscribers": [
    {
      "chat_id": "1612013580",
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

### chat_id 확인 방법

텔레그램에서 `@userinfobot` 검색 → Start → 본인 ID 확인.

### 구독자 추가 흐름

1. 지인이 `@userinfobot`으로 chat_id 확인
2. 지인이 `@hwion_brief_bot`에게 /start
3. `subscribers.json`에 추가 후 git commit + push

---

## 봇 API 주요 엔드포인트

| 용도 | URL |
|---|---|
| 봇 정보 확인 | `GET /getMe` |
| 메시지 발송 | `POST /sendMessage` |
| 메시지 발송 (HTML) | `parse_mode=HTML` 파라미터 추가 |
| 메시지 발송 (Markdown) | `parse_mode=MarkdownV2` |

베이스 URL: `https://api.telegram.org/bot{TOKEN}/`

---

## 자주 겪는 문제

### "Bad Request: text must be encoded in UTF-8"

- `curl`에서 한글 포함 시 `-d` 대신 `--data-urlencode` 사용

### "Forbidden: bot can't initiate conversation"

- chat_id가 잘못됐거나, 그 사람이 봇과 대화를 시작하지 않음
- 그 사람에게 `@hwion_brief_bot` 검색 → Start 누르도록 안내

### "Bad Request: chat not found"

- chat_id 형식 확인 (문자열 또는 숫자 둘 다 가능)
- 봇과 대화방이 없는 경우 → 상대방이 먼저 /start 필요

---

## 보안 주의사항

⚠️ **봇 토큰을 절대 GitHub에 올리지 마세요.**

- `.env` 파일은 `.gitignore`에 이미 등록됨
- 실수로 push했다면 즉시 BotFather에서 `/revoke` 후 재발급
- `subscribers.json`의 chat_id는 노출돼도 큰 문제 없음

---

다음 단계: **Cloud Routine 등록** (`docs/routine-setup.md`)
