#!/usr/bin/env python3
"""
Morning Brief — 텔레그램 발송 스크립트
subscribers.json의 active=true 구독자 전원에게 메시지를 보냅니다.

사용법:
  python send_telegram.py "메시지 내용"
  python send_telegram.py --date 2026-05-07  (해당 날짜 브리핑 자동 포맷)
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date

# Windows 콘솔 UTF-8 출력 강제
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    token = None
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                token = line.split("=", 1)[1].strip()
    if not token:
        raise ValueError(".env에서 TELEGRAM_BOT_TOKEN을 찾을 수 없습니다.")
    return token


def load_subscribers():
    path = os.path.join(BASE_DIR, "subscribers.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [s for s in data["subscribers"] if s.get("active", True)]


def load_index():
    path = os.path.join(BASE_DIR, "index.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_briefing_message(briefing):
    d = briefing["date"]
    wd = briefing.get("weekday", "")
    m, day = d.split("-")[1], d.split("-")[2]
    vol = briefing["vol"]
    theme = briefing["theme"]
    tagline = briefing.get("tagline", "")
    tldr_us = briefing.get("tldr_us", "")
    tldr_kr = briefing.get("tldr_kr", "")
    tldr_crypto = briefing.get("tldr_crypto", "")
    html_path = briefing.get("html_path", "")
    url = f"https://briefing.hwion.app/briefings/{html_path}" if html_path else ""

    msg = f"""📊 [{int(m)}/{int(day)}({wd})] 데일리 브리핑

「{theme}」

{tagline}

🇺🇸 {tldr_us}

🇰🇷 {tldr_kr}

₿ {tldr_crypto}

📄 전체 분석·시나리오·IT/게임 영향
👉 {url}

⚠️ 본 브리핑은 정보 제공 목적이며 투자 권유가 아닙니다."""
    return msg


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False), None
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return False, body
    except Exception as e:
        return False, str(e)


def main():
    token = load_env()
    subscribers = load_subscribers()

    if not subscribers:
        print("⚠️  활성 구독자가 없습니다. subscribers.json을 확인하세요.")
        sys.exit(0)

    # 메시지 결정
    if len(sys.argv) >= 3 and sys.argv[1] == "--date":
        target_date = sys.argv[2]
        idx = load_index()
        briefing = next((b for b in idx["briefings"] if b["date"] == target_date), None)
        if not briefing:
            print(f"❌  index.json에서 {target_date} 브리핑을 찾을 수 없습니다.")
            sys.exit(1)
        text = build_briefing_message(briefing)
    elif len(sys.argv) >= 2 and sys.argv[1] == "--latest":
        idx = load_index()
        briefing = idx["briefings"][0]
        text = build_briefing_message(briefing)
    elif len(sys.argv) >= 2:
        text = " ".join(sys.argv[1:])
    else:
        # 인자 없으면 최신 브리핑 발송
        idx = load_index()
        briefing = idx["briefings"][0]
        text = build_briefing_message(briefing)

    print(f"[SEND] {len(subscribers)}명에게 발송 시작...\n")
    print("-" * 50)
    print(text)
    print("-" * 50)

    ok_count = 0
    for sub in subscribers:
        chat_id = sub["chat_id"]
        name = sub.get("name", str(chat_id))
        success, err = send_message(token, chat_id, text)
        if success:
            print(f"  [OK]  {name} ({chat_id})")
            ok_count += 1
        else:
            print(f"  [FAIL] {name} ({chat_id}) - {err}")
            success2, err2 = send_message(token, chat_id, text)
            if success2:
                print(f"         retry OK")
                ok_count += 1
            else:
                print(f"         retry FAIL: {err2}")

    print(f"\n결과: {ok_count}/{len(subscribers)}명 발송 성공")


if __name__ == "__main__":
    main()
