# 아키텍처

## 패키지 구조

공개 API, 데이터 모델, 실행 코드는 원격 `main`과 같이
`discord.ext.interaction` 바로 아래에 둔다. 기능별 모듈만 유지한다.

| 경로 | 책임 |
| --- | --- |
| `commands.py`, `command_scope.py`, `command_permissions.py` | 명령과 범위·권한 데이터 |
| `components.py`, `component_models.py`, `component_codec.py` | 컴포넌트 API·데이터·payload 해석 |
| `client.py`, `sync.py`, `interaction.py`, `http.py` | 등록·동기화·이벤트·응답·REST 연결 |

데이터 모델은 실행 코드를 import하지 않는다. 별도 파일은 독립적으로 이해하거나
검증할 만한 동작이 있을 때만 유지한다. 예를 들어 명령 동기화의 계획 계산은
네트워크 호출 없이 실행되므로 `sync.py`에 남긴다.
Discord payload와 모델 사이의 변환은 해당 모델의 일부이거나 실제 송수신 과정의
일부로 배치한다. 이를 위한 별도의 `serialization` 계층은 두지 않는다.

## 공개 진입점

`from discord.ext import interaction`에서 제공하는 클래스와 함수 이름은 유지한다.
모듈은 `discord.ext.interaction`에서 직접 가져온다.
옛 `domain/`, `application/`, `serialization/`, `transport/`, `legacy_components/`
및 `implementation/`, `models/` 경로의 별칭은 제공하지 않는다.

## 주요 흐름

### 명령 동기화

1. `sync.CommandRegistry`가 범위와 유형별 선언을 저장한다.
2. `sync.plan_sync`가 로컬·원격 선언의 차이를 계산한다.
3. `sync.apply_sync_plan`이 `sync.SyncCommand` 정책에 따라 계획을 적용한다.
4. `http.CommandSyncAPI`가 Discord REST 요청을 수행한다.

### 인터랙션 처리

1. Gateway 또는 HTTP 수신 코드가 payload를 받는다.
2. `interaction_dispatcher`가 context를 만들고 이벤트를 전달한다.
3. 클라이언트가 등록된 콜백을 실행한다.
4. context의 응답 메서드가 상태를 확인하고 `http.InteractionHTTPClient`로 전송한다.

### 컴포넌트

`component_models`에 V2 유형별 객체와 필드 제약을 모은다. 기존 컴포넌트
API의 모델과 파서는 `components`에 둔다. `component_codec`은
V2 유형 번호로 객체를 복원하며 알 수 없는 유형의 원본 필드를 보존한다.

## 변경 기준

- 최상위 공개 이름과 동작을 유지한다.
- 새 유형은 모델, 필요한 송수신 동작, 왕복 검증을 함께 추가한다.
- 새로운 추상화는 실제 중복을 없애거나 별도 검증을 가능하게 할 때만 만든다.
