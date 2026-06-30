# Release Checklist

## 1. 릴리즈 목표

릴리즈 체크리스트는 구현 후 운영 배포 전에 누락된 설정, 테스트, Secret, 문서가 없는지 확인하기 위한 최종 점검표입니다.

## 2. 문서 승인

- [ ] Sprint 0 승인 완료
- [ ] Sprint 1 승인 완료
- [ ] Sprint 2 승인 완료
- [ ] Sprint 3 승인 완료
- [ ] Sprint 4 승인 완료
- [ ] Sprint 5 승인 완료
- [ ] Sprint 6 승인 완료
- [ ] Sprint 7 승인 완료
- [ ] Sprint 8 승인 완료
- [ ] Sprint 9 승인 완료
- [ ] 구현 전 통합 체크리스트 완료

## 3. 설정 확인

- [ ] GitHub Actions Secrets 설정 완료
- [ ] Supabase 연결 확인
- [ ] Telegram Bot 권한 확인
- [ ] 테스트 Channel 확인
- [ ] 운영 Channel 확인
- [ ] OpenAI API Key 확인
- [ ] dry-run 옵션 확인

## 4. 테스트 확인

- [ ] Pytest 통과
- [ ] Ruff 통과
- [ ] Black check 통과
- [ ] Mypy 통과
- [ ] Crawler fixture 테스트 통과
- [ ] AI mock 테스트 통과
- [ ] Telegram mock 테스트 통과
- [ ] 중복 발행 방지 테스트 통과

## 5. 운영 확인

- [ ] 테스트 Channel 수동 실행 성공
- [ ] publish_attempts 기록 확인
- [ ] run_logs 기록 확인
- [ ] 운영 Channel 전환 승인
- [ ] schedule 활성화 승인

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 릴리즈 승인 담당자
- `[사용자 입력 필요]` 운영 Channel 전환 시점
- `[사용자 입력 필요]` 첫 정기 실행 후 확인 담당자
