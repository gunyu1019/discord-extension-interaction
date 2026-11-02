# 0.6.x → 0.8.0 마이그레이션 가이드

0.6.2 이후 공개 이름 일부가 바뀌었고 요구 사항이 올라갔다. 이 문서는 기존 코드를 고칠 때
필요한 항목만 정리한다. 추가된 기능은 [CHANGELOG](../CHANGELOG.md)와
[새 기능 예제](new-feature-examples.md)를 본다.

## 먼저 확인할 것

| 영역 | 0.6.x | 0.8.0 | 조치 |
| --- | --- | --- | --- |
| discord.py | 선택 extra(`[discordpy]`), 버전 제한 없음 | 필수 의존성 `>=2.7.1,<3` | discord.py를 2.7.1 이상으로 올린다. |
| Python | 3.10 이상 | 3.10 이상 | 변경 없음. |
| 상호작용 수신 | `enable_debug_events=True`를 강제하고 `on_socket_raw_receive`에서 직접 압축 해제 | `ConnectionState` 파서 훅 | 아래 "수신 방식" 참고. |

## 이름 변경과 제거

| 0.6.x | 0.8.0 |
| --- | --- |
| `interaction.ModalContext` | `interaction.ModalSubmitContext` |
| `interaction.message.MessageSendable` | `interaction.MessageTransferable` |
| `interaction.message.MessageCommand` | 제거됨(0.1부터 deprecated). `interaction.Message`를 쓴다. |
| `interaction.http.handler_message_parameter` | `interaction.parser.handle_message_parameter` |
| `interaction.http.MultipartParameters` | `discord.http.MultipartParameters` |
| `ClientBase.on_socket_raw_receive` | 제거됨. 필요하면 discord.py의 `on_socket_raw_receive`를 직접 사용한다. |

별칭은 남기지 않았다. 모듈 경로는 `discord.ext.interaction` 바로 아래이다.

## 동작이 달라진 부분

### 수신 방식

이전에는 클라이언트가 `enable_debug_events=True`를 강제로 켜고 원시 소켓 데이터를 직접
해석했다. 지금은 discord.py가 이미 디코딩한 `INTERACTION_CREATE`를 받으므로 이 옵션이
필요 없다. 다만 다른 용도로 `enable_debug_events`(예: `on_socket_raw_receive`)에
기대고 있었다면 `interaction.Client(..., enable_debug_events=True)`로 직접 지정한다.

### 길드 범위 명령

이전에는 `guild_id`를 저장해도 등록·수정·삭제 요청이 항상 전역 endpoint로 갔다. 이제
길드 endpoint로 간다. 길드 전용 명령은 `scope`로 선언한다.

```python
guild = interaction.GuildScope(123456789)

@interaction.command(name="hello", description="Greet", scope=guild)
async def hello(ctx): ...
```

기존에 `guild_id`를 넘겼던 명령은 전역 목록에 남아 있을 수 있으므로 한 번 확인한다.

### 자동 동기화

`global_sync_command`와 `add_interaction(sync_command=...)`는 그대로 동작한다. 같은 범위에
`Client.set_sync_command(scope, SyncCommand(...))` 정책을 지정하면 그 정책이 우선한다.
정책을 지정하지 않은 범위에는 새 자동 동기화가 적용되지 않는다.

### 응답

- `ctx.send()`는 첫 응답에서 `GET @original`을 추가로 보내지 않고 콜백 응답의 메시지를
  쓴다. 콜백 응답은 `ctx.callback_response`에 남는다.
- `ctx.launch_activity()`는 `None` 대신 콜백 응답을 반환한다.
- `send()`는 `silent`, `poll`을, `edit()`는 `poll`을 키워드 인자로 받는다. 기존 호출은 그대로다.

### 컴포넌트와 모달

- `TextInput(label=...)`은 선택 인자이다. `Label` 안에서는 생략한다.
- 모르는 컴포넌트 유형은 버리지 않고 `UnknownComponent`로 보존한다.
- 모달 제출에서 새 입력 유형(select, File Upload, Radio Group 등)도 `ctx.components`에
  포함된다. 값은 `ctx.get_component(custom_id)`로 읽는다.
- 모달에서는 `ActionRow` + `TextInput` 대신 `Label`을 권장한다(Discord에서 deprecated).

### 컨텍스트

- 길드가 캐시에 없으면(HTTP 전용 수신, 봇이 없는 길드의 유저 설치 앱 등) `ctx.author`는
  `discord.Member`가 아니라 `discord.User`이다. 멤버 원본은 `ctx.envelope.member`에 있다.
  이전에는 이 경우 `TypeError`로 실패했다.
- 같은 경우 `ctx.channel`은 정수 `id`와 `guild_id`, 페이로드의 채널 유형을 가진
  `PartialMessageable`이다. 이전에는 `id`가 문자열이었다.

## HTTP 전용 수신으로 옮길 때

Gateway 대신 HTTP outgoing webhook으로 받으려면 `[http]` extra를 설치하고
`AiohttpInteractionAdapter`를 쓴다. Gateway에 연결하지 않으므로 `bot.run()` 대신
`await bot.login(token)`을 호출해야 한다. 자세한 예제는
[새 기능 예제의 aiohttp 수신](new-feature-examples.md#aiohttp-수신)을 본다.
