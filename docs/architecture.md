# 설계 경계와 단계적 이전 (0-d)

## 목표

공개 API는 Discord API의 Application Command, Interaction, Component, Modal,
Interaction Response 용어를 사용한다. `discord.py`는 Gateway와 REST 통신을 위한
기반 라이브러리이며 새 공개 모델의 명명 기준이 아니다. 기존 공개 이름과 import 경로는
유지하면서 구현을 기능별 책임으로 분할한다.

## 현재 결합 지점

- `client.py`에는 명령 저장·동기화, 확장 모듈 로드, Gateway 이벤트 가로채기,
  명령·컴포넌트 실행 및 대기자가 함께 있다.
- `interaction.py`에는 수신 데이터 변환, Discord 객체 조회, 응답 상태, HTTP 호출,
  모달·자동완성·컴포넌트 응답이 함께 있다.
- `components.py`에는 컴포넌트 데이터 모델, JSON 변환, 이벤트 데코레이터가 함께 있다.
- `commands.py`에는 명령 데이터 모델, 옵션 변환, payload 비교와 데코레이터가 함께 있다.
- `parser.py`는 discord.py의 메시지 직렬화 함수와 라이브러리 자체 컴포넌트 변환을 연결한다.

## 대상 의존 방향

```text
공개 facade ───────────────┐
                          v
                    application
                    /         \
                   v           v
                domain       ports
                               ^
                               |
                     infrastructure adapters

serialization → domain
Gateway / HTTP / discord.py adapters → application ports
```

`domain`은 `discord.py`의 내부 객체·HTTPClient·ConnectionState를 import하지 않는다.
`application`은 Discord 호출의 의도와 상태를 결정하지만 `Route`나 Gateway parser를
직접 호출하지 않는다. 어댑터는 포트를 구현해 실제 Discord 입출력을 맡는다.

## 예정 모듈과 책임

다음 경로는 역할을 설명하는 설계안이며, 한 번에 파일을 옮기지 않는다.

| 경로 | 한 가지 주 책임 |
| --- | --- |
| `domain/command.py` | 명령, 옵션, 범위 및 비교 가능한 선언 데이터 |
| `domain/component.py` | 컴포넌트 공통 계약, 유형 번호, 공통 id |
| `domain/interaction.py` | 원본 payload와 공통 수신 메타데이터 |
| `domain/sync.py` | SyncCommand 정책, SyncPlan 작업과 결과 |
| `application/command_registry.py` | 범위와 유형별 로컬 명령 저장 |
| `application/sync_planner.py` | 로컬·원격 목록의 차이 계산; 네트워크 요청 없음 |
| `application/sync_executor.py` | 정책에 허용된 계획의 실행과 결과 수집 |
| `application/dispatcher.py` | 수신 유형에 따른 명령·컴포넌트·모달 콜백 호출 |
| `application/response.py` | 초기·지연·후속 응답 상태 전이 |
| `serialization/commands.py` | 명령 선언 ↔ Discord payload |
| `serialization/components.py` | 컴포넌트 트리 ↔ Discord payload, 유형 등록 |
| `serialization/resolved.py` | 선택·명령·모달의 resolved 데이터 해석 |
| `transport/command_api.py` | 전역·서버별 명령 REST 호출 |
| `transport/interaction_api.py` | callback과 followup webhook REST 호출 |
| `transport/gateway.py` | Gateway payload를 공통 dispatcher에 전달 |
| `transport/webhook.py` | HTTP 서명 검증, PING 및 공통 dispatcher 전달 |
| `client.py`, `commands.py`, `components.py`, `interaction.py` | 기존 공개 경로와 얇은 조합·호환 계층 |

한 모듈에 새 유형 전체를 모으지 않는다. Components V2의 레이아웃·미디어·인터랙티브
유형과 모달 입력은 각각의 세부 모듈로 나누고 공통 codec에 등록한다.

## 중요한 흐름

### 명령 동기화

1. Registry가 범위별 로컬 명령 선언을 제공한다.
2. CommandApi가 같은 범위의 원격 명령을 조회한다.
3. SyncPlanner가 Create/Edit/Delete/Unchanged를 계산한다.
4. SyncExecutor가 해당 범위의 SyncCommand 정책에 허용된 작업만 실행한다.
5. 결과에 대상, 요청, 성공/실패를 기록한다. 원격 전용 삭제 후보는 다른 범위로 번지지 않는다.

### 인터랙션 처리

1. Gateway 또는 HTTP 어댑터가 Discord payload를 수신한다.
2. 공통 해석기가 상호작용 유형, 원본 payload, 메타데이터와 resolved 데이터를 보존한다.
3. Dispatcher가 등록된 콜백과 검사 함수를 실행한다.
4. Response 상태 객체가 유효한 callback 또는 후속 webhook 요청을 결정한다.
5. InteractionApi가 실제 전송을 수행한다.

### 컴포넌트 왕복

1. 공개 컴포넌트 객체는 순수 데이터와 제약 조건을 가진다.
2. Component codec이 중첩 구조를 직렬화한다.
3. 수신 시 유형 등록표로 복원하고 모르는 유형은 원본 데이터를 보존한다.
4. 컴포넌트 응답의 values/value와 resolved 데이터는 별도 resolver가 연결한다.

## 단계적 이전 규칙

- 먼저 테스트로 기존 동작을 고정하고, 한 책임씩 새 모듈로 옮긴다.
- 기존 공개 파일은 새 구현을 재노출하되 이미 제공 중인 공개 이름과 import 경로를 유지한다.
- 네트워크가 필요한 어댑터와 순수 비교·직렬화 코드를 분리해 오프라인 검증을 가능하게 한다.
- 한 하위 작업에서 파일 이동과 새 기능을 동시에 크게 수행하지 않는다.
- 순환 import가 생기면 최상위 파일에 추가 분기를 쌓지 않고 모델/포트 경계를 조정한다.
- 독립적인 유형 추가는 해당 유형 모듈, codec 등록, 검증 테스트를 함께 커밋한다.

## 확정된 공개 정책

- 이미 개발된 공개 API 이름은 그대로 유지한다. 새 기능에만 Discord API 용어를 사용한다.
- `SyncCommand`가 명시되지 않은 범위에서는 자동 동기화를 수행하지 않는다.
- 기존 명시적 동기화 인자의 의미는 보존하고 새 정책과의 연결은 3-g에서 검증한다.
- 시작 전 작업 트리의 변경은 확인 후 기준선 커밋 `edd5ac9`에 포함했다.
