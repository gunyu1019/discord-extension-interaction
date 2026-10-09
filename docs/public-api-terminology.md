# 공개 API 용어 계약 (0-c)

## 원칙

이미 출시된 Python 공개 이름과 `discord.ext.interaction` import 경로는 유지한다.
새 기능을 추가할 때는 Discord 개발자 문서의 명령, 컴포넌트, 인터랙션 및 응답 용어를
기준으로 이름을 정한다. 이름만 바꾸기 위한 기존 API의 별칭 추가나 사용 중단은 하지 않는다.

| Discord API 개념 | 현재 공개 API | 이후 작업에서의 처리 |
| --- | --- | --- |
| Application Command | `ApplicationCommand`, `SlashCommand`, `UserCommand`, `ContextMenu` | 기존 클래스와 데코레이터 유지; 새 명령 유형과 필드는 Discord 용어 사용 |
| Application Command Option | `CommandOption`, `CommandOptionChoice`, `option` | 기존 이름 유지; 새 옵션 필드에는 Discord payload 용어 사용 |
| Action Row | `ActionRow` | 유지 |
| Button | `Button` | 유지 |
| String Select | `Selection`, `SelectOption` | 기존 `Selection` 유지; 새 선택 메뉴 유형은 `User Select`, `Role Select` 등 Discord 유형에 맞춰 명명 |
| Text Input / Label | `TextInput`, `Label` | 유지; 새 모달 입력 유형에 Discord 용어 사용 |
| Interaction / response contexts | `InteractionContext`, `ApplicationContext`, `ComponentsContext`, `ModalSubmitContext` 등 | 기존 context 이름과 메서드 유지; 새 응답 유형은 Discord callback 용어 사용 |
| Command synchronization | `global_sync_command`, 개별 `sync_command` | 기존 인자 유지; 새 정책은 사용자가 정한 `SyncCommand(create, edit, delete)`로 분리 |

새 `SyncCommand` 정책을 설정하지 않은 범위에는 자동 동기화를 수행하지 않는다.
기존 `global_sync_command=True`와 개별 `sync_command=True`는 명시적 설정으로 취급하며,
정확한 연결과 우선순위는 3-g의 회귀 테스트로 확정한다. 새 정책의 저장 위치와 전송
형식은 3-b에서 구현과 함께 검증한다.

기존 이름의 동작을 교체해야 할 때는 먼저 회귀 테스트를 작성한다. 새 이름과 옛 이름이
동시에 필요한 경우에도 동일 객체를 재노출해 구현이 갈라지지 않게 한다.
