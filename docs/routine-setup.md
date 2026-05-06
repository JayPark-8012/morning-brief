# Cloud Routine 자동 실행 가이드

매일 아침 7시에 자동으로 브리핑을 생성·발송하는 Routine 등록.

소요 시간: 약 10분

⚠️ **사전 조건**: 다음이 먼저 완료되어 있어야 함
- [ ] GitHub Pages 배포 작동 (briefing.hwion.app 접속됨)
- [ ] 텔레그램 봇 발송 테스트 성공
- [ ] 로컬에서 스킬 수동 실행 1회 이상 검증 완료

---

## STEP 1. Cloud Routine 페이지 접속

https://claude.ai/code/scheduled

처음 들어가면 빈 페이지. **+ New routine** 버튼 클릭.

---

## STEP 2. Routine 정보 입력

### 기본 정보

| 항목 | 값 |
|---|---|
| **Name** | `데일리 경제 브리핑` |
| **Description** | (선택) `매일 아침 7시 KST 자동 발송` |

### 트리거 (실행 시점)

- **Trigger type**: `Schedule`
- **Cron**: `0 22 * * *` (UTC 기준 — KST 07:00 = UTC 22:00)
  - 또는 Cron 입력기에서 "매일 오전 7시 KST" 선택

> ⚠️ **시간대 주의**: Cloud Routine은 UTC 기준으로 돌아갑니다.
> KST 07:00 = UTC 전날 22:00.
> Cron 표기: 분 시 일 월 요일 → `0 22 * * *`

### 모델

- **Model**: `claude-sonnet-4-6` 권장 (또는 `claude-opus-4-7`)

> 평일 정규 브리핑은 Sonnet으로 충분.
> 빅 이벤트 데이만 별도 Routine으로 Opus 사용 권장.

### 작업 폴더

- **Working folder**: 본인 PC의 morning-brief 폴더 경로
  - 예: `C:\Users\[사용자명]\Documents\morning-brief`

> 이 폴더가 있어야 Routine이 SKILL.md를 읽고 파일을 저장할 수 있음.

### 프롬프트 (가장 중요)

다음 내용을 **Prompt** 필드에 입력:

```
오늘 날짜의 데일리 경제 브리핑을 생성해줘.

작업 순서:
1. skills/economy-briefing/SKILL.md 스킬을 로드하고 따라서 실행
2. 어제 브리핑 (briefings/ 폴더의 최신 파일) 읽어서 변화 추적
3. 오늘 데이터로 브리핑 작성 (15개 셀프 체크 포함)
4. briefings/YYYY-MM-DD-morning.html 파일로 저장
5. index.json 갱신 (배열 맨 앞에 새 항목 추가)
6. index.html의 Featured Card 영역을 새 브리핑으로 교체, 어제 항목은 archive-list 맨 앞으로 이동
7. 어제 브리핑 HTML 파일의 next 네비게이션 갱신 (오늘 페이지로 연결, is-disabled 제거)
8. 새 브리핑 HTML의 prev 네비게이션을 어제 브리핑으로 연결
9. git add . && git commit + push (working folder에서)
10. subscribers.json의 active=true 사용자에게 텔레그램 메시지 발송
   - 메시지 형식: SKILL.md의 "9단계 텔레그램 발송" 템플릿 따름

성공 시: 발송 결과 요약 출력
실패 시: 단계별 에러 로그 + 어디서 멈췄는지 명시
```

### Permission Mode

- **Permission mode**: `Auto-accept` (자동 실행)
  - ⚠️ 주의: 이 모드는 Claude가 파일 쓰기/git push/메시지 발송을 모두 자동 수행
  - 안전: 결과물은 매번 검증 가능하고 git 히스토리에 남음

---

## STEP 3. 첫 실행 테스트 (수동)

Routine 등록 후 바로 다음 날 7시까지 기다리지 말고, **수동 실행으로 검증**:

1. 등록한 Routine의 **Run now** 버튼 클릭
2. 로그를 실시간으로 모니터링
3. 약 5-10분 후 완료
4. 다음 항목들을 차례로 확인:
   - https://briefing.hwion.app 에 새 브리핑 보이는지
   - 텔레그램 메시지 도착했는지
   - GitHub repo에 새 commit 추가됐는지
   - 어제 브리핑의 "다음" 네비가 활성화됐는지

문제 있으면 다음 섹션 참조.

---

## STEP 4. 자동 실행 모니터링

등록된 Routine이 매일 자동 실행되는지 확인하는 방법:

### 4-1. Routine 대시보드

https://claude.ai/code/scheduled 페이지에서:
- **Last run**: 마지막 실행 시각
- **Status**: Success / Failed
- **History**: 지난 실행 기록

### 4-2. 텔레그램 알림 (가장 직접적)

매일 아침 텔레그램에 메시지가 오면 = 정상 작동.
오지 않으면 즉시 점검 필요.

### 4-3. GitHub Commit History

repo의 commits 페이지에서 매일 새 commit이 추가되는지 확인.

---

## 🚨 트러블슈팅

### Routine은 실행되는데 git push 실패

원인: GitHub 인증 토큰 만료 또는 working folder의 git 설정 문제.

해결:
```powershell
cd C:\Users\[사용자명]\Documents\morning-brief
git pull
git push
# 인증 창 뜨면 GitHub Personal Access Token 입력
```

### 시간이 안 맞음 (오전 7시인데 발송 안 됨)

UTC ↔ KST 변환 확인:
- KST 07:00 = UTC **전날 22:00**
- Cron: `0 22 * * *`

또는 Cloud Routine 시간대 설정 확인.

### Pro 플랜 일일 한도(5회) 초과

해결책 3가지:
1. **Max 플랜으로 업그레이드** ($100/월, 일 15회)
2. **빅 이벤트 데이만 별도 Routine 분리** (정규 1회 + 이벤트 1회만)
3. **기본 모델을 Sonnet**으로 (Opus 대비 토큰 효율 우위)

### 브리핑 품질이 들쭉날쭉

원인: 프롬프트에 "셀프 체크 통과 후에만 발송" 지시가 약함.

해결: Routine Prompt에 다음 한 줄 추가:
```
⚠️ 절대 규칙: SKILL.md의 15개 셀프 체크를 모두 통과한 후에만 git push 및 텔레그램 발송 진행. 미달 항목 있으면 수정 후 재검증.
```

### 휴장일 처리

토요일/일요일 + 한국·미국 공휴일에는 시장 데이터 없음.

해결: SKILL.md의 "주말·공휴일 변형" 워크플로우가 자동 적용됨.
- 주말: 위클리 정리 형식
- 공휴일: 한쪽 시장 축약, 다른 쪽 중심

---

## 📅 운영 일정 권장

### 평일 (월-금) 07:00 KST
- **정규 데일리 브리핑** (모델: Sonnet)
- 정상 운영의 95%

### 평일 빅 이벤트 데이
- 정규 브리핑 + **이벤트 직후 추가 브리핑** (모델: Opus)
- 예: CPI 21:30 KST 발표 → 22:00 KST 추가 브리핑
- 별도 Routine 등록 또는 수동 실행

### 일요일 18:00 KST
- **위클리 정리** (선택, 모델: Opus)
- 한 주 시장 종합 + 다음 주 일정

### 한국 공휴일
- 미국 시장 마감 따라 정상 발송 (한국 섹션만 축약)

---

## 🔐 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 등록되어 있음
- [ ] GitHub Repo가 Public이지만 민감 정보 없음
- [ ] subscribers.json의 chat_id는 공개돼도 무방 (구독자 본인만 영향)
- [ ] 텔레그램 봇 토큰은 Routine 환경 변수로만 사용, 코드에 하드코딩 없음
- [ ] `/telegram:access policy allowlist` 설정으로 모르는 사람 차단됨

---

## 💰 비용 정리 (참고)

| 항목 | 비용 |
|---|---|
| Cloudflare 도메인 | 이미 보유 중 ($10/년 수준) |
| GitHub Pages | $0 |
| GitHub Actions | $0 (Public repo 무제한) |
| 텔레그램 봇 | $0 |
| Claude Pro | $20/월 (Routine 일 5회) |
| Cloudflare CDN/Proxy | $0 (Free 플랜) |
| **총 운영비** | **월 $20** |

---

## ✅ 운영 안정화 체크리스트

이 모든 항목이 1주일 이상 정상 작동하면 안정화 완료:

- [ ] 매일 정확한 시각에 브리핑 자동 생성
- [ ] HTML 파일 형식 일관성 유지 (15개 셀프 체크 통과)
- [ ] 텔레그램 메시지 발송 100% 성공
- [ ] briefing.hwion.app 페이지 정상 표시
- [ ] index.html의 archive 누적 표시
- [ ] 이전/다음 네비게이션 자동 갱신
- [ ] git history에 daily commit 일관성

축하합니다 🎉 데일리 브리핑 자동화 시스템 운영 시작!
