# 새 Discord API 기능 사용 예시

기존 `Selection`, `TextInput`, `Label`, `Client` 이름은 유지한다. 새 컴포넌트는
Discord API의 유형 이름을 사용한다.

## Components V2 메시지

```python
from discord.ext import interaction

await ctx.send(components=[
    interaction.TextDisplay("## 설문"),
    interaction.Container([
        interaction.TextDisplay("아래에서 선택해 주세요."),
    ]),
])
```

V2 컴포넌트가 있으면 메시지 플래그 `IS_COMPONENTS_V2`가 자동 설정된다. 이 모드에서는
`content`, `embeds`, `poll`, `stickers`를 함께 보낼 수 없다. 로컬 첨부 파일을 V2
미디어에 표시할 때는 `attachment://파일명`과 업로드 파일명을 일치시킨다.

## 모달 입력과 제출값

```python
await ctx.modal("survey", "설문", [
    interaction.Label(
        interaction.RadioGroup("choice", [
            interaction.RadioGroupOption("a", "A"),
            interaction.RadioGroupOption("b", "B"),
        ]), label="하나 선택",
    ),
    interaction.Label(interaction.Checkbox("agree"), label="동의"),
])

# 모달 제출을 받은 ModalSubmitContext에서:
choice = modal_ctx.get_component("choice").value
agreed = modal_ctx.get_component("agree").value
```

파일 업로드 결과는 `modal_ctx.get_component("files").values`의 첨부 파일 ID와
`modal_ctx.file_uploads["files"]`의 `discord.Attachment` 객체로 볼 수 있다.
자동 선택 메뉴 결과는 `modal_ctx.get_resolved_values("users")`로 해석할 수 있다.

## aiohttp 수신

```python
from aiohttp import web
from discord.ext import interaction
from discord.ext.interaction.aiohttp_interactions import AiohttpInteractionAdapter

bot = interaction.Client()
app = web.Application()
AiohttpInteractionAdapter(bot, public_key="APPLICATION_PUBLIC_KEY").register(app)


async def start_http_client(app: web.Application):
    # Gateway에 연결하지 않고 REST 세션만 연다. 이 호출이 없으면 Context의
    # ``send()`` 같은 응답 요청이 AttributeError로 실패한다.
    await bot.login("BOT_TOKEN")


async def stop_http_client(app: web.Application):
    await bot.close()


app.on_startup.append(start_http_client)
app.on_cleanup.append(stop_http_client)
web.run_app(app, port=8080)
```

위 방식은 서명 검증 후 기존 디스패처에 전달하고 HTTP `202`를 반환한다. 콜백은 기존
Context 메서드가 Discord REST endpoint에 보낸다. Gateway 수신과 HTTP webhook
수신은 Discord 앱 설정에서 서로 배타적이다. HTTP 전용 실행에서 명령 콜백이 필요하면
클라이언트에 명령을 먼저 등록해야 한다. 앱의 공개 키는 Developer Portal에서 가져온다.

HTTP 전용 실행에는 다음 제약이 있다.

- `bot.login(token)`만 호출하고 `bot.run()`/`bot.start()`는 호출하지 않는다.
  Gateway에 연결하지 않으므로 `on_ready`가 오지 않고, 시작 시 자동 동기화도 실행되지
  않는다. 명령 동기화는 `plan_sync_commands`/`apply_sync_commands`를 직접 호출한다.
- 길드·채널·멤버 캐시가 비어 있다. 길드 상호작용의 `ctx.author`는 `discord.Member`가
  아니라 `discord.User`이고, 원본 멤버 데이터는 `ctx.envelope.member`에서 읽는다.

직접 JSON 응답을 반환하려면 `inline_handler`에 async 함수를 전달한다. 함수는
컨텍스트를 받고 `{"type": 4, "data": {"content": "hello"}}` 같은 Discord callback
payload를 반환한다. 이 경로는 기존 이벤트 콜백을 실행하지 않는다. 2.5초 안에 응답해야
하며 `ctx.send()` 같은 REST 초기 응답을 함께 호출하면 안 된다.

## 인터랙션 메타데이터

```python
@interaction.command(description="Show invocation details")
async def whereami(ctx: interaction.ApplicationContext):
    if ctx.context == interaction.ApplicationContextType.BOT_DM:
        return await ctx.send("DM에서 호출했습니다.")

    can_embed = ctx.app_permissions is not None and ctx.app_permissions.embed_links
    installs = ", ".join(t.name for t in ctx.authorizing_integration_owners)
    await ctx.send(
        f"설치 유형: {installs} / 임베드 가능: {can_embed} / "
        f"업로드 한도: {ctx.attachment_size_limit} bytes / 구독 {len(ctx.entitlements)}건"
    )
```

`ctx.envelope`는 받은 Interaction Object의 읽기 전용 스냅샷이다. 길드 캐시가 없는
환경에서는 `ctx.author`가 `discord.User`이므로 원본 멤버 데이터는
`ctx.envelope.member`에서 읽는다.

## Activity

```python
command = interaction.ActivityCommand(
    "launch", "Open the Activity",
    handler=interaction.ActivityHandler.APP_HANDLER,
)

async def launch(ctx):
    await ctx.launch_activity()

bot.add_activity_command(command, launch, sync_command=True)
```

`ctx.launch_activity()`는 Discord의 Interaction Callback Response를 반환하고 `ctx.callback_response`에도 보관한다. 실행된 인스턴스는 `result["resource"]["activity_instance"]["id"]`로 읽는다. `ctx.send()`도 첫 응답에서 같은 방식으로 콜백 응답의 메시지를 사용하므로 `GET @original` 요청을 추가로 보내지 않는다.

Activity가 Discord 앱에서 활성화되어 있어야 한다. Discord가 직접 실행하게 할 때는
`ActivityHandler.DISCORD_LAUNCH_ACTIVITY`를 사용하고 콜백을 생략한다.

## 범위별 명령 동기화

```python
from discord.ext import interaction

bot = interaction.Client()
guild = interaction.GuildScope(123456789)

@interaction.command(name="hello", description="Greet", scope=guild)
async def hello(ctx):
    await ctx.send("Hello")

bot.add_interaction(hello, sync_command=False)
bot.set_sync_command(guild, interaction.SyncCommand(
    create=True, edit=True, delete=False,
))

async def inspect_and_apply():
    # 필요할 때 Discord 원격 목록을 읽고 변경 후보를 확인한다.
    plan = await bot.plan_sync_commands(guild)
    for item in plan.items:
        print(item.key.name, item.operation.value)

    # 등록된 정책을 명시적으로 적용한다.
    result = await bot.apply_sync_commands(guild)
    for failed in result.failures:
        print(failed.item.key.name, failed.error)
```

전역은 `GlobalScope()`를 사용한다. 정책은 실행 중 메모리에만 저장된다.
정책을 지정하지 않은 범위에는 새 자동 동기화를 적용하지 않는다. 정책을 해제할 때는
`bot.remove_sync_command(guild)`를 호출한다. 생성·수정·삭제 기본값은 모두 `True`라서
삭제를 원하지 않는 범위에서는 `delete=False`를 명시해야 한다.

## 명령별 서버 권한

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    api = interaction.CommandPermissionsAPI(session, oauth_bearer_token)
    await api.edit_command_permissions(application_id, guild_id, command_id, [
        interaction.CommandPermission(
            role_id, interaction.CommandPermissionType.ROLE, True,
        ),
    ])
```

권한 수정에는 봇 토큰이 아니라 `applications.commands.permissions.update` 범위로
승인된 사용자 OAuth Bearer 토큰이 필요하다. 수정 요청은 해당 명령의 권한 목록 전체를
덮어쓴다.
