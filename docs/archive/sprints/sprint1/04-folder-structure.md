# Folder Structure

## 1. 목표 폴더 구조

Sprint 1은 구조만 정의합니다. 실제 파일 생성은 해당 Sprint 승인 후 구현 단계에서 진행합니다.

```text
bicycle_road_event_alarm/
  docs/
    sprint0/
    sprint1/
  src/
    bicycle_road_event_alarm/
      __init__.py
      scheduler/
        __init__.py
        runner.py
      config/
        __init__.py
        settings.py
      crawler/
        __init__.py
        base.py
        sources/
          __init__.py
      normalizer/
        __init__.py
        models.py
        service.py
      classifier/
        __init__.py
        service.py
      database/
        __init__.py
        models.py
        repository.py
        session.py
      generator/
        __init__.py
        prompt.py
        service.py
        fallback.py
      messenger/
        __init__.py
        telegram.py
      logging/
        __init__.py
        setup.py
  tests/
    fixtures/
    unit/
    integration/
  alembic/
  .github/
    workflows/
```

## 2. 구조 원칙

- `src/bicycle_road_event_alarm` 아래에 애플리케이션 코드를 둡니다.
- 각 모듈은 한 가지 책임을 갖습니다.
- 외부 API 직접 호출은 전용 모듈 안에 격리합니다.
- 테스트는 단위 테스트와 통합 테스트를 분리합니다.
- 마이그레이션은 Sprint 2 승인 후 `alembic`에 둡니다.

## 3. 보류 항목

- FastAPI 관련 `api/` 폴더는 MVP에서 만들지 않습니다.
- 웹 프론트엔드 폴더는 만들지 않습니다.
- 관리자 대시보드 폴더는 만들지 않습니다.

## 4. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 패키지 이름 `bicycle_road_event_alarm` 유지 여부
- `[사용자 입력 필요]` 테스트 디렉터리를 `tests/unit`, `tests/integration`으로 분리하는 방식 승인 여부
