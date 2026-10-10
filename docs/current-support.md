# 현재 Discord API 지원 범위

이 표는 `discord.ext.interaction` 자체 API와 오프라인 테스트를 기준으로 한다.
실제 Discord 서버 점검은 [실서버 체크리스트](live-smoke.md)에서 별도로 추적한다.
초기 조사 결과는 [기준선 지원 표](support-matrix.md)에 보존했다.

| 영역 | 현재 상태 | 공개 진입점 / 제한 |
| --- | --- | --- |
| 전역 CHAT_INPUT, USER, MESSAGE 명령 | 지원 | 기존 `command`, `user`, `context` 데코레이터와 직접 명령 모델 |
| 명령 현지화, 메타데이터, 서버별 REST CRUD | 지원 | 명령 모델과 `transport.command_api`; 범위별 로컬 레지스트리는 진행 중 |
| 범위별 `SyncCommand` 자동 동기화 | 지원 | 정책·계획·적용·재연결 중복 방지 구현; 같은 범위의 기존 `global_sync_command`와 개별 `sync_command=True`보다 우선 |
| Gateway 수신과 기본 응답 | 지원 | `Client`, 기존 Context 클래스; 초기·지연·후속 응답 상태 검증 |
| HTTP outgoing webhook | 지원 | `AiohttpInteractionAdapter`, `[http]` extra, Ed25519 검증, PING/PONG, 202 callback 또는 inline JSON |
| Legacy Action Row, Button, String Select, Text Input | 지원 | 기존 공개 클래스와 호출 유지; 단독 Button/Selection은 전송 시 Action Row로 감쌈 |
| 자동 Select(5–8) | 지원 | `UserSelect`, `RoleSelect`, `MentionableSelect`, `ChannelSelect`; raw IDs 및 resolved 객체 |
| Components V2 레이아웃/미디어(9–14, 17) | 지원 | `Section`, `TextDisplay`, `Thumbnail`, `MediaGallery`, `File`, `Separator`, `Container`; 40개 제한과 V2 플래그 |
| 모달 Label 및 입력(19, 21–23) | 지원 | `FileUpload`, `RadioGroup`, `CheckboxGroup`, `Checkbox`; 제출값은 `ModalSubmitContext.get_component` |
| Activity Entry Point(4) / 응답(12) | 지원 | `ActivityCommand`, `Client.add_activity_command`, `ctx.launch_activity`; Discord의 Activities 활성화 필요 |
| 명령별 guild 권한 | 지원 | `CommandPermissionsAPI`; 사용자 OAuth Bearer 토큰과 별도 aiohttp session 필요 |
| 실서버 상호 운용성 | 미검증 | 앱 자격 증명과 테스트 guild가 필요함 |

공식 범위: [Interactions Overview](https://docs.discord.com/developers/interactions/overview),
[Receiving and Responding](https://docs.discord.com/developers/interactions/receiving-and-responding),
[Application Commands](https://docs.discord.com/developers/interactions/application-commands),
[Component Reference](https://docs.discord.com/developers/components/reference),
[Components Overview](https://docs.discord.com/developers/components/overview),
[Using Message Components](https://docs.discord.com/developers/components/using-message-components),
[Using Modal Components](https://docs.discord.com/developers/components/using-modal-components).
