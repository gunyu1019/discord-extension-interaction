# 호환 범위 (0-e)

현재 `setup.py`의 설치 계약은 Python 3.10 이상과 `discord.py>=2.7.1,<3`이다.
`requirements.txt`도 같은 런타임 의존성 범위를 가진다. 이 작업에서는 이미 출시된
버전의 최소 Python 버전이나 `discord.py` 범위를 임의로 변경하지 않는다.
README에 남아 있던 Python 3.9 및 `discord.py` 2.3 표기는 1-f에서 메타데이터에 맞췄다.

## 유지할 기존 공개 사용법

- `from discord.ext import interaction` 및 `discord.ext.interaction`의 현재 공개 import.
- `Client`와 `AutoShardedClient`의 생성자, 특히 `global_sync_command` 인자.
- `@interaction.command`, `@interaction.user`, `@interaction.context`,
  `@interaction.detect_component`와 현재 선택·모달 구성 클래스.
- 기존 `add_interaction` 및 `delete_interaction`의 `sync_command` 인자.
- 기존 명령, 컴포넌트, 모달 context 이름과 응답 메서드.

현재 최상위 공개 이름은 유지한다. 이전 계층 경로의 별칭은 제거했으며,
기존 API 모듈은 패키지 루트에서, 추가 데이터 유형은 `models/`에서 가져온다.
새 `SyncCommand` 정책이 없는 범위에는 자동 동기화가 없다. 기존 `True` 설정은
사용자가 명시한 설정으로 보며, 새 정책과의 상세 우선순위는 3-g에서 실제 동작과
회귀 테스트를 확인한 후 정한다.

`py-cord` 등 다른 Discord 클라이언트 라이브러리는 현재 설치 계약에 포함되지 않는다.
실제 지원 여부를 확인하지 않은 Python 최신 버전이나 별도 클라이언트의 호환성을
문서에서 보장하지 않는다.
