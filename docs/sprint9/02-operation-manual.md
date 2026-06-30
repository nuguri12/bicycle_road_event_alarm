# Operation Manual

## 1. 운영 목표

운영자는 정기 실행이 성공했는지, 메시지가 발행되었는지, 실패 시 무엇을 확인해야 하는지 빠르게 알 수 있어야 합니다.

## 2. 정기 운영 절차

정기 실행 후 확인:

- GitHub Actions workflow 성공 여부
- run_logs 상태
- publish_attempts 성공 여부
- Telegram Channel 메시지 발행 여부
- 중복 발행 여부

## 3. 수동 실행 절차

수동 실행이 필요한 경우:

- 정기 실행 실패
- schedule 지연
- 운영자가 배포 전 테스트를 원함
- Telegram 발행만 재시도해야 함

수동 실행 전 확인:

- DRY_RUN 값
- ENABLE_TELEGRAM_PUBLISH 값
- 운영 Channel과 테스트 Channel 구분
- 동일 message_hash 성공 발행 여부

## 4. 운영자가 하지 말아야 할 일

- Bot Token을 문서나 이슈에 붙여 넣지 않습니다.
- 운영 Channel에서 live 테스트를 반복하지 않습니다.
- 실패 원인을 모른 채 schedule을 여러 번 수동 실행하지 않습니다.
- 데이터베이스에서 발행 이력을 임의 삭제하지 않습니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 정기 운영 확인 담당자
- `[사용자 입력 필요]` 수동 실행 승인 담당자
- `[사용자 입력 필요]` 운영 확인 주기
