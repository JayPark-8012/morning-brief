#!/usr/bin/env python3
"""
Morning Brief — 텔레그램 채널 발송 스크립트

채널에 봇이 관리자로 추가되어 있어야 합니다.
.env 파일에 TELEGRAM_CHANNEL_ID 설정 필요.

사용법:
  python send_telegram.py                    # 최신 브리핑 발송
  python send_telegram.py --latest           # 최신 브리핑 발송 (동일)
  python send_telegram.py --date 2026-05-07  # 특정 날짜 브리핑 발송
  python send_telegram.py "직접 쓴 메시지"   # 공지 등 자유 문자 발송
"""

import json
import os
import sys
import urllib.request
import urllib.parse

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    config = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    token = config.get("TELEGRAM_BOT_TOKEN")
    channel_id = config.get("TELEGRAM_CHANNEL_ID")
    if not token:
        raise ValueError(".env에 TELEGRAM_BOT_TOKEN이 없습니다.")
    if not channel_id:
        raise ValueError(".env에 TELEGRAM_CHANNEL_ID가 없습니다. 채널 ID를 설정해주세요.")
    return token, channel_id


def load_index():
    path = os.path.join(BASE_DIR, "index.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_briefing_message(briefing):
    d = briefing["date"]
    wd = briefing.get("weekday", "")
    m, day = int(d.split("-")[1]), int(d.split("-")[2])
    theme = briefing["theme"]
    tagline = briefing.get("tagline", "")
    tldr_us = briefing.get("tldr_us", "")
    tldr_kr = briefing.get("tldr_kr", "")
    tldr_crypto = briefing.get("tldr_crypto", "")
    html_path = briefing.get("html_path", "")
    url = f"https://briefing.hwion.app/briefings/{html_path}" if html_path else ""

    return f"""📊 [{m}/{day}({wd})] 데일리 브리핑

「{theme}」

{tagline}

🇺🇸 {tldr_us}

🇰🇷 {tldr_kr}

₿ {tldr_crypto}

📄 전체 분석·시나리오·IT/게임 영향
👉 {url}

⚠️ 본 브리핑은 정보 제공 목적이며 투자 권유가 아닙니다."""


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False), None
    except urllib.error.HTTPError as e:
        return False, e.read().decode()
    except Exception as e:
        return False, str(e)


def main():
    token, channel_id = load_env()

    if len(sys.argv) >= 3 and sys.argv[1] == "--date":
        target_date = sys.argv[2]
        idx = load_index()
        briefing = next((b for b in idx["briefings"] if b["date"] == target_date), None)
        if not briefing:
            print(f"[ERROR] index.json에서 {target_date} 브리핑을 찾을 수 없습니다.")
            sys.exit(1)
        text = build_briefing_message(briefing)
    elif len(sys.argv) >= 2 and sys.argv[1] not in ("--latest",):
        text = " ".join(sys.argv[1:])
    else:
        idx = load_index()
        briefing = idx["briefings"][0]
        text = build_briefing_message(briefing)

    print(f"[SEND] 채널 {channel_id} 에 발송 중...\n")
    print("-" * 50)
    print(text)
    print("-" * 50)

    ok, err = send_message(token, channel_id, text)
    if ok:
        print("\n[OK] 발송 성공")
    else:
        print(f"\n[FAIL] 발송 실패: {err}")
        print("[RETRY] 재시도 중...")
        ok2, err2 = send_message(token, channel_id, text)
        if ok2:
            print("[OK] 재시도 성공")
        else:
            print(f"[FAIL] 재시도도 실패: {err2}")
            sys.exit(1)


if __name__ == "__main__":
    main()
