# Unit Tests

## 1. 단위 테스트 목표

단위 테스트는 네트워크와 데이터베이스 없이 각 모듈의 결정적 로직을 검증합니다.

## 2. 대상 모듈

- config
- normalizer
- classifier
- generator fallback
- duplicate key builder
- message hash builder
- retry decision helper
- settings validation

## 3. 주요 테스트 케이스

config:

- 필수 Secret 누락 시 실패합니다.
- boolean 환경 변수를 명시적으로 파싱합니다.
- 숫자 환경 변수 범위를 검증합니다.

normalizer:

- 제목 공백을 정리합니다.
- 날짜를 한국 시간 기준으로 해석합니다.
- 장소가 없으면 `needs_review` 또는 `invalid`가 됩니다.

classifier:

- 도로 통제 표현은 high로 분류합니다.
- 축제 표현은 medium 후보로 분류합니다.
- 영향 표현이 없으면 unknown입니다.

generator fallback:

- high, medium, low 순으로 정렬합니다.
- 최대 이벤트 수를 넘기지 않습니다.
- 원문 URL을 유지합니다.

## 4. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 단위 테스트 우선순위 모듈
- `[사용자 입력 필요]` 날짜 파싱 라이브러리 선택 후 테스트 기준
