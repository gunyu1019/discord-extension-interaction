# Discord API 지원 표 (0-b 기준선)

이 표는 현재 작업 트리의 `discord.ext.interaction` 자체 공개 API를 평가한다.
`discord.py`를 직접 호출해 우회하는 기능은 지원으로 세지 않는다. `지원`은 생성·전송·수신·해석
경로가 있는 경우, `일부`는 해당 경로 중 하나 이상이 누락되거나 알려진 오류가 있는 경우다.
실제 Discord 서버와의 통합 검증 여부는 별도 추적한다.

## 공식 문서

- [Interactions Overview](https://docs.discord.com/developers/interactions/overview)
- [Receiving and Responding](https://docs.discord.com/developers/interactions/receiving-and-responding)
- [Application Commands](https://docs.discord.com/developers/interactions/application-commands)
- [Components Overview](https://docs.discord.com/developers/components/overview)
- [Component Reference](https://docs.discord.com/developers/components/reference)
- [Using Message Components](https://docs.discord.com/developers/components/using-message-components)
- [Using Modal Components](https://docs.discord.com/developers/components/using-modal-components)

## 애플리케이션 명령

| 기능 | 상태 | 현재 근거 및 후속 작업 |
| --- | --- | --- |
| CHAT_INPUT(1) 전역 명령 | 일부 | `core.py:Command`, `client.py:register_command`; 그룹 실행과 옵션 해석 오류는 1-b/1-d. |
| USER(2) 전역 명령 | 지원 | `core.py:MemberCommand`, `commands.py:UserCommand`; 실서버 검증은 9-f. |
| MESSAGE(3) 전역 명령 | 지원 | `core.py:ContextMenuCommand`, `commands.py:ContextMenu`; 실서버 검증은 9-f. |
| PRIMARY_ENTRY_POINT(4) | 미지원 | `enums.py:ApplicationCommandType`에 없음; 9-d. |
| 전역 생성·목록·조회·수정·삭제 | 일부 | `client.py`에 API가 있으나 캐시 조회 오류는 1-e. |
| 서버별 생성·목록·조회·수정·삭제 | 미지원 | `guild_id`를 저장하지만 호출은 전역 endpoint; 2-a/2-e. |
| 전역·서버별 일괄 덮어쓰기 | 미지원 | 직접 API 없음; 3-c/3-d에서 계획 적용 방식 결정. |
| 범위별 동기화 정책 | 미지원 | `global_sync_command` 단일 boolean; 3-a~3-h. |
| 명령·하위 명령 그룹·하위 명령 | 일부 | 모델 존재, 그룹 실행 경로 오류; 1-b. |
| 옵션 유형 STRING(3), INTEGER(4), BOOLEAN(5) | 지원 | `commands.py:CommandOption`, `interaction.py:ApplicationContext`. |
| 옵션 유형 USER(6), CHANNEL(7), ROLE(8), NUMBER(10) | 일부 | 변환 경로 존재하나 캐시/부분 객체 상황은 검증 필요; 4-b. |
| 옵션 유형 MENTIONABLE(9), ATTACHMENT(11) | 일부 | 유형 선언 가능, 수신 해석이 부정확함; 1-d. |
| 옵션 choices·범위·길이·autocomplete | 일부 | `CommandOption`에 필드가 있으나 검증·수신 범위는 2-c/2-g. |
| 이름·설명 현지화: 명령/하위 명령/옵션/선택지 | 미지원 | 각 모델에 localization 필드 없음; 2-d. |
| default_member_permissions | 일부 | 모델 및 payload에 있으나 기본 데코레이터에 노출되지 않음; 2-c/2-g. |
| integration_types·contexts | 일부 | 모델 및 payload에 있으나 기본 데코레이터에 노출되지 않음; 2-c/2-g. |
| nsfw | 일부 | 모델에는 있으나 등록 payload에 누락; 2-c. |
| 서버별 명령 권한 조회·수정 | 미지원 | 별도 인증과 endpoint 필요; 9-e. |

## 인터랙션 수신·응답

| 기능 | 상태 | 현재 근거 및 후속 작업 |
| --- | --- | --- |
| Gateway INTERACTION_CREATE | 지원 | `client.py:_install_interaction_parsers`; 4-c에서 어댑터로 분리. |
| HTTP outgoing webhook 수신 | 미지원 | 서버, 요청 서명 검증, PING 응답 없음; 9-a/9-b. |
| APPLICATION_COMMAND(2) | 일부 | 디스패치 구현, 명령 옵션 오류는 1-b/1-d. |
| MESSAGE_COMPONENT(3) | 일부 | 디스패치 구현, 유형 필터와 Select 해석 오류; 1-c/7-e. |
| AUTOCOMPLETE(4) | 지원 | `AutocompleteContext.autocomplete`; 실서버 검증은 9-f. |
| MODAL_SUBMIT(5) | 일부 | Label/Text Input 해석, 새 입력 유형 누락; 8-b~8-g. |
| 공통 메타데이터 | 일부 | id/token/user/locale 등은 보존; app_permissions, entitlements, 설치 주체, 호출 context, attachment_size_limit 누락; 4-a. |
| resolved 데이터 | 일부 | 명령 대상 일부만 해석; 옵션·컴포넌트·모달용 공통 resolver 없음; 4-b. |
| 초기 메시지 응답(4) | 지원 | `InteractionContext.send`; 파일은 지연 후 원본 편집; 4-e/4-f에서 경계 검증. |
| 지연 메시지 응답(5) | 지원 | `InteractionContext.defer`; 4-d에서 상태 통합. |
| 컴포넌트 지연·즉시 업데이트(6/7) | 일부 | `ComponentsContext.defer_update/update`; 상태와 첨부 파일 경계 검증 필요; 4-d/4-f. |
| 자동완성 결과(8) | 지원 | `AutocompleteContext.autocomplete`. |
| 모달 응답(9) | 일부 | Action Row/Label 전송 가능, 새 모달 입력 미지원; 8-a~8-h. |
| LAUNCH_ACTIVITY 응답(12) | 미지원 | Activity 명령 및 응답 API 없음; 9-d. |
| 원본·후속 응답 조회/수정/삭제 | 일부 | HTTP 경로가 있으나 응답 상태 통합 및 경계 검증 필요; 4-d~4-f. |
| 3초 초기 응답·15분 토큰 수명 안내 | 일부 | Discord 제약을 자동 추적하지 않음; 4-f 및 문서 9-g. |

## 컴포넌트 유형

| 유형 | 용도 | 상태 | 현재 근거 및 후속 작업 |
| --- | --- | --- | --- |
| 1 Action Row | 메시지/기존 모달 컨테이너 | 일부 | 모델 있음, 공통 id·배치 검증 없음; 5-a/5-e. |
| 2 Button | 메시지 상호작용 | 일부 | 일반/링크 가능, 프리미엄 sku_id 없음; 7-a. |
| 3 String Select | 메시지/모달 선택 | 일부 | `Selection` 모델, 모달 required·제출 values 누락; 7-b/8-f. |
| 4 Text Input | 모달 텍스트 | 일부 | 모델 있음, 공통 id 및 Label 중심 검증 필요; 5-d/8-a. |
| 5 User Select | 메시지/모달 선택 | 미지원 | 모델·파서·resolved 해석 없음; 7-c/7-e. |
| 6 Role Select | 메시지/모달 선택 | 미지원 | 모델·파서·resolved 해석 없음; 7-c/7-e. |
| 7 Mentionable Select | 메시지/모달 선택 | 미지원 | 모델·파서·resolved 해석 없음; 7-c/7-e. |
| 8 Channel Select | 메시지/모달 선택 | 미지원 | 모델·파서·resolved 해석 없음; 7-c/7-d. |
| 9 Section | V2 레이아웃 | 미지원 | 6-a. |
| 10 Text Display | V2 텍스트 | 미지원 | 6-a. |
| 11 Thumbnail | V2 미디어 | 미지원 | 6-b. |
| 12 Media Gallery | V2 미디어 | 미지원 | 6-b. |
| 13 File | V2 첨부 파일 표시 | 미지원 | 6-b/6-f. |
| 14 Separator | V2 레이아웃 | 미지원 | 6-a. |
| 17 Container | V2 레이아웃 | 미지원 | 6-a. |
| 18 Label | 모달 컨테이너 | 일부 | 모델 있음, 자식 유형 확대와 공통 id 필요; 8-a. |
| 19 File Upload | 모달 파일 입력 | 미지원 | 8-b. |
| 21 Radio Group | 모달 단일 선택 | 미지원 | 8-c. |
| 22 Checkbox Group | 모달 복수 선택 | 미지원 | 8-d. |
| 23 Checkbox | 모달 boolean | 미지원 | 8-e. |

## 공통 컴포넌트·메시지 동작

| 기능 | 상태 | 현재 근거 및 후속 작업 |
| --- | --- | --- |
| 공통 component `id` | 미지원 | 기존 모델에 공통 id 없음; 5-a. |
| 알 수 없는 component 보존 | 미지원 | `components.py:from_payload`가 무시함; 5-c. |
| 부모·자식 배치 및 필드 검증 | 일부 | 개별 생성자는 있으나 문서의 구조 규칙을 통합 검증하지 않음; 5-e. |
| IS_COMPONENTS_V2 플래그 | 미지원 | 공개 전송 API에 V2 모드 없음; 6-c. |
| V2에서 content/embeds/poll/stickers 배제 | 미지원 | V2 메시지 모드 자체가 없음; 6-d. |
| V2 첨부 파일 표시와 attachment:// 참조 | 미지원 | 일반 파일 첨부는 가능, V2 File/미디어 연결 없음; 6-f. |
| 레거시 Action Row 메시지 | 지원 | `parser.py:handle_message_parameter`; 6-g에서 회귀 검증. |
| 버튼/선택 메뉴 custom_id 콜백 | 일부 | `DetectComponent` 및 wait_for 존재, 유형 필터 오류; 1-c/7-f. |

## 검증 현황

기존 오프라인 pytest 34개는 이전 조사에서 통과했다. 새로운 유형, 서버별 명령,
HTTP webhook, 실제 Discord 서버와의 상호 운용성은 아직 검증되지 않았다.
