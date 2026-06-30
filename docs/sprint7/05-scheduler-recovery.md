# Scheduler Recovery

## 1. 복구 목표

스케줄러 복구는 GitHub Actions 실행 실패, 지연, 중복 실행 상황에서도 메시지 중복 발행과 데이터 손상을 막는 것을 목표로 합니다.

## 2. 실패 유형

### 2.1 schedule 미실행 또는 지연

원인:

- GitHub Actions schedule 지연
- GitHub 서비스 장애
- 저장소 Actions 비활성화

처리:

- 운영자가 workflow_dispatch로 수동 실행합니다.
- 실행 로그에서 마지막 성공 run을 확인합니다.

### 2.2 실행 중 실패

원인:

- 크롤러 실패
- 데이터베이스 연결 실패
- OpenAI 실패
- Telegram 실패

처리:

- 실패 단계와 run_id를 로그에 남깁니다.
- 가능한 경우 partial_success로 종료합니다.
- 다음 실행에서 미발행 이벤트를 재처리합니다.

### 2.3 중복 실행

원인:

- schedule 실행 중 수동 실행
- 이전 실행이 오래 걸림

처리:

- GitHub Actions concurrency를 사용합니다.
- message_hash와 publish_attempts로 중복 발행을 방지합니다.

## 3. 수동 재실행 기준

수동 재실행이 필요한 경우:

- 정기 실행이 실패했습니다.
- Telegram 발행만 실패했습니다.
- 운영자가 테스트 Channel에서 검증하려고 합니다.

수동 재실행 전 확인:

- 동일 message_hash가 이미 success인지 확인합니다.
- 운영 Channel과 테스트 Channel 설정을 확인합니다.
- DRY_RUN 여부를 확인합니다.

## 4. 복구 우선순위

1. 중복 발행 방지
2. 비밀값 노출 방지
3. 실패 원인 로그 확보
4. 다음 실행에서 재처리 가능성 유지

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 수동 재실행 담당자
- `[사용자 입력 필요]` schedule 실패를 확인할 주기
- `[사용자 입력 필요]` partial_success 상태에서 Telegram 발행을 허용할지 여부
