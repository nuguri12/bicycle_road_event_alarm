# Secret Management

## 1. Secret 관리 목표

Bot Token, API Key, 데이터베이스 연결 문자열이 저장소나 로그에 노출되지 않도록 관리합니다.

## 2. GitHub Actions Secrets

필수 Secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`
- `OPENAI_API_KEY`
- `SUPABASE_DATABASE_URL`

선택 Secrets:

- `SUPABASE_SERVICE_ROLE_KEY`
- `TEST_TELEGRAM_CHANNEL_ID`

주의:

- `SUPABASE_SERVICE_ROLE_KEY`는 반드시 필요한 경우에만 사용합니다.
- 읽기/쓰기 범위가 제한된 DB 사용자 사용을 우선 검토합니다.

## 3. Secret 접근 정책

- workflow에서 필요한 job에만 Secret을 주입합니다.
- 로그에는 Secret 값을 출력하지 않습니다.
- 실패 메시지에는 Secret 이름만 기록하고 값은 기록하지 않습니다.
- pull request from fork에서는 운영 Secret 접근을 허용하지 않습니다.

## 4. Secret 회전 정책

회전이 필요한 경우:

- 토큰 노출 의심
- 운영 담당자 변경
- Channel 권한 변경
- 정기 보안 점검

회전 절차:

1. 새 Secret 발급
2. GitHub Actions Secrets 업데이트
3. 테스트 workflow 실행
4. 기존 Secret 폐기

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 운영 Secret 설정 담당자
- `[사용자 입력 필요]` Supabase 연결에 service role key를 사용할지 여부
- `[사용자 입력 필요]` Secret 정기 회전 주기
