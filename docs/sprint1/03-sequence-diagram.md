# Sequence Diagram

## 1. 정기 실행 시퀀스

```mermaid
sequenceDiagram
    participant GH as GitHub Actions
    participant Runner as Scheduler Runner
    participant Config as Config
    participant Crawler as Crawler
    participant Normalizer as Normalizer
    participant Classifier as Classifier
    participant DB as Database
    participant Generator as Message Generator
    participant OpenAI as OpenAI API
    participant Telegram as Telegram API

    GH->>Runner: start scheduled job
    Runner->>Config: load and validate settings
    Config-->>Runner: validated settings
    Runner->>Crawler: collect raw event candidates
    Crawler-->>Runner: raw event candidates
    Runner->>Normalizer: normalize candidates
    Normalizer-->>Runner: normalized events
    Runner->>Classifier: classify cyclist impact
    Classifier-->>Runner: publishable event candidates
    Runner->>DB: save events and check duplicates
    DB-->>Runner: new publishable events
    Runner->>Generator: generate weekend summary
    Generator->>OpenAI: request reasoning summary when needed
    OpenAI-->>Generator: generated summary
    Generator-->>Runner: Telegram message
    Runner->>Telegram: publish message
    Telegram-->>Runner: publish result
    Runner->>DB: record publish result
```

## 2. Fallback 시퀀스

AI 요약이 실패하면 Generator는 정규화된 이벤트 필드만 사용해 fallback 메시지를 생성합니다.

```mermaid
sequenceDiagram
    participant Runner as Scheduler Runner
    participant Generator as Message Generator
    participant OpenAI as OpenAI API
    participant Telegram as Telegram API

    Runner->>Generator: generate summary
    Generator->>OpenAI: request summary
    OpenAI--x Generator: timeout or API error
    Generator->>Generator: build deterministic fallback message
    Generator-->>Runner: fallback Telegram message
    Runner->>Telegram: publish fallback message
```

## 3. 중복 방지 시퀀스

```mermaid
sequenceDiagram
    participant Runner as Scheduler Runner
    participant DB as Database
    participant Generator as Message Generator

    Runner->>DB: find events by deterministic duplicate key
    DB-->>Runner: existing event matches
    Runner->>DB: exclude already published events
    DB-->>Runner: unpublished events
    Runner->>Generator: generate message for unpublished events only
```

## 4. 사용자 입력 필요 항목

- `[사용자 입력 필요]` AI 실패 시 fallback 메시지를 발행할지, 발행을 중단할지 여부
- `[사용자 입력 필요]` 중복으로 의심되지만 확실하지 않은 이벤트의 기본 처리 방식
