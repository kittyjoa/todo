# STRATEGY.md — 설계 원칙 및 하네스 방어

이 문서는 CLAUDE.md가 @docs/STRATEGY.md로 참조한다.

## 프로젝트 목적

"AI가 만든 것 같지 않은" UX. MUJI 스타일 — 꾸미지 않아서 아름다운 것.
Bootstrap을 쓰되 Bootstrap스럽지 않게. 색상 3개, 이모지 없음, 그라디언트 없음.

## 설계 원칙 4개

1. **단방향 의존성**: models → database → routers → main. 역방향 참조 금지.
2. **DB 단일 진입점**: aiosqlite는 database.py만 import. 나머지는 함수 호출만.
3. **Optimistic UI**: 서버 응답 전에 UI 먼저 반영. 실패 시 롤백.
4. **정책 우선**: 코드에서 "안전하다"고 판단해도 CLAUDE.md 정책을 따른다.

## 하네스 방어 8개

① **할루시네이션**: 함수 호출 전 시그니처를 읽는다. 가정 금지.
② **확증 편향**: 같은 접근 2번 실패 시 접근 자체를 바꾼다.
③ **유령 수정**: 수정 후 반드시 make test. "맞을 것"을 신뢰 금지.
④ **스코프 팽창**: 수락 조건만 구현. "이것도 같이"는 금지.
⑤ **숫자 전파**: 숫자 변경 시 grep으로 전수 검색.
⑥ **테스트 환각**: @pytest_asyncio.fixture 사용. 조건부 assertion 금지.
⑦ **보안 정책**: f-string SQL 금지 (화이트리스트라도). 정책 변경은 CLAUDE.md에서.
⑧ **접근성**: 터치 타겟 ≥ 44px. 시각적 크기가 작으면 ::after로 히트 영역 확장.

## 품질 기준 (Evaluation)

```bash
grep -c "gradient" app/static/css/style.css       # → 0
grep -c "location.reload" app/static/js/app.js    # → 0
grep -c 'f"' app/database.py                       # → 0
grep -c "::after" app/static/css/style.css         # ≥ 2
grep -c "field_validator" app/models.py            # ≥ 2
```
