# Java to Python migration

현재 `main`의 Spring Boot 서버는 비교 기준으로 유지하고, `python-backend/`에서 FastAPI 서버를 병행 개발합니다.

## Why both implementations exist temporarily

Git 기록만으로도 Java 코드를 복구할 수 있지만, 전환 중에는 두 서버에 같은 요청을 보내 응답과 DB 결과를 비교해야 합니다. 그래서 Python 구현의 API 동등성이 확인될 때까지만 Java를 유지합니다. 두 구현을 장기간 운영하지는 않습니다.

## Cutover checklist

- [ ] 커밋된 기존 DB 자격 증명을 교체하고 배포 secret으로 이전
- [ ] 운영 DB 백업
- [ ] 복합 유니크 제약을 위반하는 기존 중복 데이터 검사 및 정리
- [ ] Java와 Python API 계약 테스트 결과 비교
- [ ] 스테이징 MySQL에서 Alembic 기준점 기록
- [ ] 동시 답안 제출 테스트
- [ ] Python 서버로 트래픽 전환
- [ ] 관찰 기간 후 Java 소스 제거

Java 서버를 로컬에서 비교 실행하려면 `DB_URL`, `DB_USERNAME`, `DB_PASSWORD` 환경변수를 설정해야 합니다. Python 서버 실행 방법은 `python-backend/README.md`를 참고합니다.

