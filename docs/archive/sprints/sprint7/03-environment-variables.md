# Environment Variables

## 1. 환경 변수 목표

환경 변수는 실행마다 달라지는 설정을 코드와 분리하기 위한 것입니다.

## 2. 필수 환경 변수

| Name | Secret | Description |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | yes | Telegram Bot API token |
| `TELEGRAM_CHANNEL_ID` | yes | 발행 대상 Channel ID 또는 사용자명 |
| `OPENAI_API_KEY` | yes | OpenAI API key |
| `SUPABASE_DATABASE_URL` | yes | Supabase PostgreSQL 연결 문자열 |
| `APP_ENV` | no | `local`, `test`, `production` |
| `LOG_LEVEL` | no | 기본값 `INFO` |

## 3. 선택 환경 변수

| Name | Secret | Description |
| --- | --- | --- |
| `ALERT_LOOKAHEAD_DAYS` | no | 기본값 14 |
| `MAX_EVENTS_PER_MESSAGE` | no | 기본값 5 |
| `ENABLE_TELEGRAM_PUBLISH` | no | true일 때만 실제 발행 |
| `DRY_RUN` | no | true이면 외부 발행 없이 검증 |
| `REQUEST_TIMEOUT_SECONDS` | no | 기본값 10 |
| `CRAWLER_MAX_RETRIES` | no | 기본값 2 |

## 4. 환경 변수 검증 원칙

- 필수 Secret이 없으면 실행 초기에 실패합니다.
- Secret 값은 로그에 출력하지 않습니다.
- 숫자 설정은 범위를 검증합니다.
- boolean 설정은 명시적 문자열만 허용합니다.

## 5. 로컬 실행 정책

- 로컬에서는 `.env`를 사용할 수 있습니다.
- `.env`는 저장소에 커밋하지 않습니다.
- `.env.example`은 구현 단계에서 실제 값 없이 생성할 수 있습니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` `ENABLE_TELEGRAM_PUBLISH` 기본값을 false로 둘지 여부
- `[사용자 입력 필요]` `ALERT_LOOKAHEAD_DAYS` 기본값 14 승인 여부
- `[사용자 입력 필요]` `.env.example` 생성 여부
