# Backup Procedure

## 1. 백업 목표

백업은 발행 이력과 이벤트 데이터를 복구 가능한 상태로 유지하기 위한 절차입니다.

## 2. 백업 대상

대상:

- run_logs
- raw_events
- normalized_events
- publish_attempts

제외:

- Telegram Bot Token
- OpenAI API Key
- Supabase 연결 문자열
- GitHub Secrets 값

## 3. 백업 절차

MVP 기본:

1. Supabase 기본 백업 제공 여부를 확인합니다.
2. 운영 전환 전 수동 export 또는 dump를 수행합니다.
3. 백업 파일을 저장소 밖 안전한 위치에 보관합니다.
4. 복구 테스트를 test database에서 수행합니다.

## 4. 복구 절차

1. schedule을 비활성화합니다.
2. 현재 DB 상태를 보존합니다.
3. 백업 파일을 test DB에 먼저 복구합니다.
4. 주요 조회를 확인합니다.
5. 운영 DB 복구를 승인받습니다.
6. 운영 DB에 복구합니다.
7. dry-run workflow를 실행합니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 백업 파일 보관 위치
- `[사용자 입력 필요]` 백업 수행 담당자
- `[사용자 입력 필요]` 복구 승인 담당자
- `[사용자 입력 필요]` 허용 가능한 데이터 손실 범위
