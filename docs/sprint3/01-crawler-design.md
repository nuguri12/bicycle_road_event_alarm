# Crawler Design

## 1. 크롤러 목표

크롤러는 서울 및 경기도의 주말 자전거 통행에 영향을 줄 수 있는 공개 이벤트 후보를 수집합니다.

수집 대상 예시는 다음과 같습니다.

- 마라톤, 달리기 대회
- 걷기 행사
- 축제와 공공 행사
- 도로 통제
- 자전거 행사
- 한강 및 하천 공원 행사
- 지자체 공지사항

## 2. 크롤러 책임

크롤러가 하는 일:

- 승인된 출처의 목록 또는 상세 페이지를 요청합니다.
- 원문 제목, 본문 일부, 날짜 문자열, 장소 문자열, 원문 URL을 추출합니다.
- 수집 시각과 출처 이름을 함께 반환합니다.
- HTTP 상태, timeout, selector 실패를 기록 가능한 오류로 반환합니다.

크롤러가 하지 않는 일:

- 이벤트 영향도 최종 판단
- 지역명 표준화
- Telegram 메시지 생성
- 데이터베이스 직접 저장
- AI 호출

## 3. 크롤러 출력 모델

Sprint 2의 `raw_events` 저장 모델과 맞추기 위해 크롤러 출력은 다음 필드를 가져야 합니다.

| Field | Required | Description |
| --- | --- | --- |
| source_name | yes | 출처 이름 |
| source_url | yes | 상세 페이지 또는 원문 URL |
| fetched_at | yes | 수집 시각 |
| raw_title | no | 원문 제목 |
| raw_body | no | 원문 본문 또는 요약 |
| raw_date_text | no | 원문 날짜 표현 |
| raw_location_text | no | 원문 장소 표현 |
| content_hash_input | yes | 해시 생성에 사용할 원문 필드 묶음 |

## 4. 출처별 어댑터 구조

각 출처는 독립 어댑터로 설계합니다.

예상 구조:

```text
crawler/
  base.py
  sources/
    spatic.py
    seoul_notice.py
    hangang_notice.py
    gyeonggi_notice.py
```

설계 원칙:

- 출처별 HTML 구조 변경이 다른 출처에 영향을 주지 않게 합니다.
- 공통 HTTP 요청, timeout, user-agent 설정은 base 계층에 둡니다.
- selector는 출처별 모듈 안에만 둡니다.

## 5. Playwright 사용 기준

기본은 Requests와 BeautifulSoup입니다.

Playwright는 다음 조건 중 하나를 만족할 때만 사용합니다.

- 목록 또는 상세 내용이 JavaScript 실행 후에만 나타납니다.
- 서버가 정적 HTML에 의미 있는 데이터를 제공하지 않습니다.
- 공식 출처에 RSS, JSON, 정적 HTML 대안이 없습니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 첫 구현 출처를 서울경찰청 교통정보센터로 할지 여부
- `[사용자 입력 필요]` Playwright 사용을 허용할 출처 기준
- `[사용자 입력 필요]` 수집 대상 기간: 이번 주말만 볼지, 다음 14일까지 볼지 여부
