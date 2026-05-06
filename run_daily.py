#!/usr/bin/env python3
"""
Morning Brief — 데일리 자동화 오케스트레이터

역할:
  1. 오늘이 공휴일/주말인지 자동 판단 → 모드 결정
  2. 적절한 모드를 Claude에게 전달 (브리핑 생성은 Claude가 수행)
  3. 브리핑 파일 생성 확인
  4. git fetch/pull --rebase/push (충돌 시 abort + 알림)
  5. send_telegram.py --latest 실행
  6. 실패 시 텔레그램 채널에 자동 실패 알림
  7. 모든 결과를 logs/YYYY-MM-DD.log에 기록

사용법:
  python run_daily.py            # 오늘 날짜 기준 자동 실행
  python run_daily.py --dry-run  # 실제 발송 없이 모드 판단만
  python run_daily.py --mode normal|weekend|us-holiday|kr-holiday|both-holiday
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.parse
from datetime import date, datetime, timedelta, timezone

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KST = timezone(timedelta(hours=9))


# ──────────────────────────────────────────────
# 로거
# ──────────────────────────────────────────────

class Logger:
    def __init__(self, log_date: str):
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        self.path = os.path.join(log_dir, f"{log_date}.log")
        self.lines = []

    def log(self, msg: str):
        ts = datetime.now(KST).strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.lines.append(line)
        print(line)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + "\n")


# ──────────────────────────────────────────────
# 환경 변수
# ──────────────────────────────────────────────

def load_env():
    config = {}
    env_path = os.path.join(BASE_DIR, ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()
    return config


# ──────────────────────────────────────────────
# 공휴일 판단
# ──────────────────────────────────────────────

def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """해당 월의 n번째 weekday (0=월요일)"""
    first = date(year, month, 1)
    delta = (weekday - first.weekday()) % 7
    return first + timedelta(days=delta + (n - 1) * 7)

def last_weekday(year: int, month: int, weekday: int) -> date:
    """해당 월의 마지막 weekday"""
    next_month = date(year, month % 12 + 1, 1) if month < 12 else date(year + 1, 1, 1)
    last_day = next_month - timedelta(days=1)
    delta = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=delta)

def good_friday(year: int) -> date:
    """Good Friday (부활절 전 2일)"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    easter = date(year, month, day)
    return easter - timedelta(days=2)

def us_holidays(year: int) -> set:
    holidays = {
        date(year, 1, 1),                              # New Year's Day
        nth_weekday(year, 1, 0, 3),                    # MLK Day
        nth_weekday(year, 2, 0, 3),                    # Presidents Day
        good_friday(year),                              # Good Friday
        last_weekday(year, 5, 0),                      # Memorial Day
        date(year, 6, 19),                             # Juneteenth
        date(year, 7, 4),                              # Independence Day
        nth_weekday(year, 9, 0, 1),                    # Labor Day
        nth_weekday(year, 11, 3, 4),                   # Thanksgiving
        date(year, 12, 25),                            # Christmas
    }
    # 주말에 겹치면 관측일(observed) 적용
    observed = set()
    for h in holidays:
        if h.weekday() == 5:   # 토요일 → 금요일
            observed.add(h - timedelta(days=1))
        elif h.weekday() == 6: # 일요일 → 월요일
            observed.add(h + timedelta(days=1))
        else:
            observed.add(h)
    return observed

def kr_holidays_fixed(year: int) -> set:
    """음력 연휴(설날·추석)는 제외한 고정 공휴일만"""
    return {
        date(year, 1, 1),   # 신정
        date(year, 3, 1),   # 삼일절
        date(year, 5, 5),   # 어린이날
        date(year, 6, 6),   # 현충일
        date(year, 8, 15),  # 광복절
        date(year, 10, 3),  # 개천절
        date(year, 10, 9),  # 한글날
        date(year, 12, 25), # 성탄절
    }

def determine_mode(today: date) -> str:
    """오늘 날짜 기준 발행 모드 결정"""
    year = today.year
    weekday = today.weekday()  # 0=월, 5=토, 6=일

    if weekday == 6:  # 일요일 — 건너뜀
        return "skip"
    if weekday == 5:  # 토요일 — 위클리
        return "weekend"

    us_off = today in us_holidays(year)
    kr_off = today in kr_holidays_fixed(year)

    if us_off and kr_off:
        return "both-holiday"
    if us_off:
        return "us-holiday"
    if kr_off:
        return "kr-holiday"
    return "normal"


# ──────────────────────────────────────────────
# 브리핑 파일 존재 확인
# ──────────────────────────────────────────────

def check_briefing_exists(today: date) -> bool:
    filename = f"{today.isoformat()}-morning.html"
    path = os.path.join(BASE_DIR, "briefings", filename)
    return os.path.isfile(path)


# ──────────────────────────────────────────────
# git 조작
# ──────────────────────────────────────────────

def git_push(log: Logger) -> bool:
    def run(cmd):
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

    log.log("git: fetch origin main ...")
    ok, out, err = run(["git", "fetch", "origin", "main"])
    if not ok:
        log.log(f"[WARN] git fetch 실패: {err}")

    log.log("git: pull --rebase origin main ...")
    ok, out, err = run(["git", "pull", "--rebase", "origin", "main"])
    if not ok:
        log.log(f"[ERROR] git rebase 충돌: {err}")
        run(["git", "rebase", "--abort"])
        log.log("git rebase --abort 실행됨")
        return False

    log.log("git: push origin main ...")
    ok, out, err = run(["git", "push", "origin", "main"])
    if not ok:
        log.log(f"[ERROR] git push 실패: {err}")
        return False

    log.log("git push 완료")
    return True


# ──────────────────────────────────────────────
# 텔레그램 알림
# ──────────────────────────────────────────────

def send_alert(token: str, channel_id: str, text: str, log: Logger):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": channel_id, "text": text}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                log.log("알림 발송 완료")
            else:
                log.log(f"[WARN] 알림 발송 실패: {result}")
    except Exception as e:
        log.log(f"[WARN] 알림 발송 예외: {e}")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────

def main():
    today = datetime.now(KST).date()
    log = Logger(today.isoformat())

    # 인자 파싱
    dry_run = "--dry-run" in sys.argv
    forced_mode = None
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            forced_mode = sys.argv[idx + 1]

    # 환경 변수 로드
    try:
        env = load_env()
        token = env.get("TELEGRAM_BOT_TOKEN", "")
        channel_id = env.get("TELEGRAM_CHANNEL_ID", "")
        if not token or not channel_id:
            raise ValueError("TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHANNEL_ID 미설정")
    except Exception as e:
        print(f"[ERROR] .env 로드 실패: {e}")
        sys.exit(1)

    # 모드 결정
    mode = forced_mode if forced_mode else determine_mode(today)
    log.log(f"=== Morning Brief 자동화 시작 ({today}) ===")
    log.log(f"모드: {mode}")

    MODE_DESC = {
        "normal":       "정규 브리핑 (양국 개장)",
        "us-holiday":   "미국 휴장 — 한국·코인 중심",
        "kr-holiday":   "한국 휴장 — 미국·코인 중심",
        "both-holiday": "양국 휴장 — 위클리 정리 형식",
        "weekend":      "주말 — 위클리 정리 형식 (토요일만 발행)",
        "skip":         "일요일 — 발행 건너뜀",
    }
    log.log(f"설명: {MODE_DESC.get(mode, mode)}")

    if mode == "skip":
        log.log("일요일 — 자동으로 건너뜀. 정상 종료.")
        log.save()
        sys.exit(0)

    if dry_run:
        log.log("[DRY-RUN] 실제 발송 없이 종료.")
        log.log(f"[DRY-RUN] 오늘 브리핑 파일 존재: {check_briefing_exists(today)}")
        log.log(f"[DRY-RUN] Claude에게 전달할 모드: {mode}")
        log.save()
        print(f"\n모드: {mode} / {MODE_DESC.get(mode, mode)}")
        sys.exit(0)

    # ── 브리핑 파일 존재 확인 ──────────────────
    # (이 시점에서 Claude가 이미 브리핑을 생성했어야 함)
    if not check_briefing_exists(today):
        msg = (
            f"⚠️ [{today}] 브리핑 생성 실패\n"
            f"briefings/{today}-morning.html 파일이 없습니다.\n"
            f"모드: {mode} / 수동 확인 필요"
        )
        log.log("[ERROR] 오늘 브리핑 HTML 파일 없음 — 셀프 체크 미통과 또는 생성 실패")
        send_alert(token, channel_id, msg, log)
        log.save()
        sys.exit(1)

    log.log(f"브리핑 파일 확인: briefings/{today}-morning.html 존재")

    # ── git push ───────────────────────────────
    git_ok = git_push(log)
    if not git_ok:
        msg = (
            f"⚠️ [{today}] git push 실패\n"
            f"충돌 또는 네트워크 오류. 수동 해결 필요.\n"
            f"`git status` 로 확인 후 재시도."
        )
        send_alert(token, channel_id, msg, log)
        log.save()
        sys.exit(1)

    # ── 텔레그램 발송 ──────────────────────────
    log.log("send_telegram.py --latest 실행 중...")
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "send_telegram.py"), "--latest"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    log.log(result.stdout.strip())
    if result.returncode != 0:
        log.log(f"[ERROR] 텔레그램 발송 실패: {result.stderr.strip()}")
        send_alert(token, channel_id, f"⚠️ [{today}] 텔레그램 발송 실패\n{result.stderr[:200]}", log)
        log.save()
        sys.exit(1)

    log.log(f"=== 완료: {today} 브리핑 발행 성공 ({mode} 모드) ===")
    log.save()
    sys.exit(0)


if __name__ == "__main__":
    main()
