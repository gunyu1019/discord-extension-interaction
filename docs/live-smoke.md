# Discord 실서버 점검 체크리스트

오프라인 테스트가 통과해도 Discord 서버와 실제 클라이언트에서의 동작을 확인해야 한다.
봇 토큰과 OAuth Bearer 토큰은 저장소 또는 이 문서에 기록하지 않는다.

- [ ] 테스트 앱의 전역·서버별 CHAT_INPUT, USER, MESSAGE 명령을 생성·수정·삭제한다.
- [ ] 동일한 이름의 전역·서버 명령과 다른 명령 유형을 각각 호출한다.
- [ ] V2 Text Display, Section, Container, Media Gallery, File 및 첨부 참조가 표시된다.
- [x] Button과 네 종류의 자동 Select를 눌러 `custom_id`, values, resolved 객체를 확인한다.
- [x] Modal의 String Select, Text Input, File Upload, Radio Group, Checkbox Group, Checkbox 제출값을 확인한다.
- [ ] HTTP 엔드포인트에서 유효 서명 PING은 200/PONG, 잘못된 서명은 401을 반환한다.
- [ ] HTTP callback 202와 inline 200 응답을 실제 Discord 클라이언트에서 확인한다.
- [ ] Activity 앱이 있다면 APP_HANDLER와 LAUNCH_ACTIVITY 응답을 확인한다.
- [ ] 사용자 OAuth Bearer 토큰으로 명령별 권한을 조회·수정하고 클라이언트 표시를 확인한다.
- [ ] 완료 시 앱/길드, 실행 날짜, 각 항목 결과와 Discord 응답 오류를 기록한다.

이 항목은 앱 자격 증명과 테스트 guild가 준비되어야 실행할 수 있다.

## 명령 REST 점검

저장소의 Git 제외 파일 `.env`에 `DISCORD_TEST_BOT_TOKEN`,
`DISCORD_TEST_APPLICATION_ID`, `DISCORD_TEST_GUILD_ID`를 설정한다.
기존 `DISCORD_GUILD_ID`도 읽는다. 비밀 값은 출력하거나 커밋하지 않는다.

```powershell
.venv\Scripts\python.exe examples\live_smoke_commands.py
.venv\Scripts\python.exe examples\live_smoke_commands.py --crud
```

첫 명령은 전역·테스트 guild의 명령 목록만 읽는다. `--crud`는 각 범위에 고유 이름의
CHAT_INPUT, USER, MESSAGE 명령을 만들고 조회한 다음 CHAT_INPUT을 수정한다. 마지막에는
이번 실행에서 생성한 ID만 삭제한다. 다른 명령을 정리하거나 전체 동기화를 실행하지 않는다.

## 2026-10-11 실서버 실행 결과

테스트 앱과 테스트 guild에서 읽기 전용 목록 조회가 성공했다. 실행 전 전역 명령은
9개, 테스트 guild 명령은 0개였다. `--crud`로 각 범위에 CHAT_INPUT, USER,
MESSAGE 명령을 한 개씩 생성하고 목록 및 ID 조회를 확인했다. 각 범위의 CHAT_INPUT
설명을 수정하고 다시 조회했으며, 생성한 6개 명령을 모두 ID 기준으로 삭제했다.
각 범위의 삭제 후 목록에서도 해당 이름이 사라진 것을 확인했다.

Discord 클라이언트에서의 실제 명령 호출, 컴포넌트·모달 표시와 입력, 공개 HTTPS 수신은
아직 수동 점검이 필요하다. 별도 OAuth Bearer 토큰이 없어 명령별 권한 점검은 보류했다.

## V2 메시지 점검

`.env`에 `DISCORD_TEST_CHANNEL_ID`를 추가한 뒤 아래를 실행한다. 기본 모드는
테스트 메시지를 전송·조회한 다음 바로 삭제한다. 화면에서 확인할 때만 `--keep`을
사용하고, 출력된 ID를 `--delete`로 정리한다. 삭제 명령은 봇이 작성한 smoke
메시지만 허용한다.

```powershell
.venv\Scripts\python.exe examples\live_smoke_message.py
.venv\Scripts\python.exe examples\live_smoke_message.py --keep
.venv\Scripts\python.exe examples\live_smoke_message.py --delete MESSAGE_ID
```

2026-10-11 실행에서 Container, Section, Thumbnail, Media Gallery, File,
Separator, Button, 네 종류의 자동 Select와 multipart 첨부 파일이 Discord 메시지
응답에 유지됐다. File 컴포넌트는 응답에서 HTTPS CDN URL과 `name`·`size`를
반환하고 일반 `attachments` 배열에는 나타나지 않았다. 이 차이로 드러난 수신 파서
오류를 고쳐 재실행에 성공했다. 실제 Discord 클라이언트의 표시·클릭은 별도 확인이 필요하다.

## Gateway 클라이언트 점검

테스트 앱의 Interactions Endpoint URL이 비어 있을 때 아래 도구를 실행한다.
봇이 테스트 채널에 V2 메시지를 올리고, 지정한 시간이 지나면 자동으로 삭제한다.
메시지에서 두 버튼과 네 자동 선택 메뉴를 조작하면 각 제출을 해석해 사용자에게
ephemeral 응답을 보낸다. 첫 버튼의 모달은 Text Input, File Upload, Radio Group,
Checkbox Group, Checkbox를 사용하고 두 번째 버튼은 String Select를 사용한다.

```powershell
.venv\Scripts\python.exe -u examples\live_smoke_gateway.py --duration 300
```

이 도구는 테스트 명령을 등록하거나 다른 메시지를 삭제하지 않는다.

2026-10-11 실행에서는 네 자동 선택 메뉴 모두 `values=1`, `resolved=1`로 수신했고
ephemeral 응답을 전송했다. 두 버튼에서 각 모달이 열렸으며 String Select 값 제출도
해석했다. 다섯 입력 모달은 텍스트, File Upload, Radio Group, Checkbox Group,
Checkbox의 제출값을 검사했고 업로드 파일 한 개가 첨부 객체로 해석됐다. 사용자가
실제 Discord 클라이언트에서 모든 조작을 완료했다고 확인했다. 두 임시 메시지는
검증 후 삭제했다.

## Gateway 명령 호출 점검

아래 도구는 테스트 guild에 `codex_smoke_chat`, `Codex Smoke User`,
`Codex Smoke Message`를 임시 등록한다. 세 유형을 실제 Discord 클라이언트에서
호출하면 각 콜백이 ephemeral 응답을 보내고, 세 호출이 끝나거나 시간이 만료되면
이번 실행에서 생성한 명령 ID만 삭제한다.

```powershell
.venv\Scripts\python.exe -u examples\live_smoke_command_dispatch.py --duration 300
```
