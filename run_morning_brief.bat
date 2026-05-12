@echo off
chcp 65001 > nul
cd /d D:\Claude\morning-brief

echo. >> logs\automation.log
echo ============================================ >> logs\automation.log
echo [%date% %time%] Starting morning brief... >> logs\automation.log
echo ============================================ >> logs\automation.log

call claude -p "skills/economy-briefing/SKILL.md를 따라 오늘의 데일리 경제 브리핑을 만들어서 main에 push해줘. 텔레그램 발송은 GitHub Actions가 처리하니 하지 마." --dangerously-skip-permissions --allowedTools "Read,Write,Edit,Bash,WebSearch,WebFetch,Glob,Grep" >> logs\automation.log 2>&1

echo [%date% %time%] Done. Exit code: %errorlevel% >> logs\automation.log
echo. >> logs\automation.log