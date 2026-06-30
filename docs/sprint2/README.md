# Sprint 2 Database Documents

## 목적

Sprint 2는 이벤트 수집, 정규화, 중복 방지, Telegram 발행 이력을 저장하기 위한 데이터베이스 설계를 확정하는 단계입니다.

## 산출물

1. [Database ERD](./01-database-erd.md)
2. [Entity Definitions](./02-entity-definitions.md)
3. [Relationships](./03-relationships.md)
4. [Indexes](./04-indexes.md)
5. [Migration Strategy](./05-migration-strategy.md)
6. [Backup Strategy](./06-backup-strategy.md)
7. [Data Retention Policy](./07-data-retention-policy.md)

## 승인 조건

Sprint 2 문서가 승인되기 전에는 Alembic 마이그레이션, SQLAlchemy 모델, 저장소 코드, Supabase 테이블 생성을 시작하지 않습니다.

## 설계 범위

- MVP 운영에 필요한 최소 테이블만 정의합니다.
- 개인 사용자, 인증, 결제, 분석 테이블은 만들지 않습니다.
- 원문 데이터와 정규화 데이터를 분리해 추적 가능성을 유지합니다.
- Telegram 발행 중복 방지를 위해 발행 이력을 별도로 저장합니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 Sprint 3 또는 구현 시작 전에 확정되어야 합니다.
