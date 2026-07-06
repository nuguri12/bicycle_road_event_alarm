# GitHub Actions Workflow

## 1. Workflow 목표

GitHub Actions workflow는 정해진 시간에 전체 배치 파이프라인을 실행합니다.

실행 단계:

1. 저장소 checkout
2. Python 설정
3. 의존성 설치
4. 환경 변수와 Secrets 주입
5. 테스트 또는 사전 검증
6. scheduler runner 실행
7. 실행 결과 로그 확인

## 2. 실행 트리거

MVP 트리거:

- `schedule`: 정기 실행
- `workflow_dispatch`: 운영자 수동 실행

권장:

- 주말 전 금요일 저녁 또는 토요일 이른 오전에 실행합니다.
- GitHub Actions cron은 UTC 기준이므로 한국 시간 변환을 명시합니다.

예:

```text
KST 토요일 06:00 = UTC 금요일 21:00
```

## 3. Workflow 이름

권장 이름:

- `weekend-cycling-alert`

이름 기준:

- 목적이 드러납니다.
- 운영자가 Actions 탭에서 찾기 쉽습니다.

## 4. 실행 제한

- 동시 실행은 1개로 제한합니다.
- 이전 실행이 진행 중이면 새 실행은 대기하거나 취소합니다.
- MVP에서는 matrix build를 사용하지 않습니다.

## 5. 사전 검증

실행 전 검증:

- 필수 Secrets 존재 여부
- Python 버전
- 설정값 파싱 가능 여부
- 메시지 발행 비활성화 dry-run 옵션 여부

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 기본 정기 실행 요일과 시간
- `[사용자 입력 필요]` 수동 실행 권한을 가진 GitHub 사용자
- `[사용자 입력 필요]` dry-run 실행 옵션을 workflow_dispatch에 둘지 여부
