# Discord 실서버 점검 체크리스트

오프라인 테스트가 통과해도 Discord 서버와 실제 클라이언트에서의 동작을 확인해야 한다.
봇 토큰과 OAuth Bearer 토큰은 저장소 또는 이 문서에 기록하지 않는다.

- [ ] 테스트 앱의 전역·서버별 CHAT_INPUT, USER, MESSAGE 명령을 생성·수정·삭제한다.
- [ ] 동일한 이름의 전역·서버 명령과 다른 명령 유형을 각각 호출한다.
- [ ] V2 Text Display, Section, Container, Media Gallery, File 및 첨부 참조가 표시된다.
- [ ] Button과 네 종류의 자동 Select를 눌러 `custom_id`, values, resolved 객체를 확인한다.
- [ ] Modal의 String Select, Text Input, File Upload, Radio Group, Checkbox Group, Checkbox 제출값을 확인한다.
- [ ] HTTP 엔드포인트에서 유효 서명 PING은 200/PONG, 잘못된 서명은 401을 반환한다.
- [ ] HTTP callback 202와 inline 200 응답을 실제 Discord 클라이언트에서 확인한다.
- [ ] Activity 앱이 있다면 APP_HANDLER와 LAUNCH_ACTIVITY 응답을 확인한다.
- [ ] 사용자 OAuth Bearer 토큰으로 명령별 권한을 조회·수정하고 클라이언트 표시를 확인한다.
- [ ] 완료 시 앱/길드, 실행 날짜, 각 항목 결과와 Discord 응답 오류를 기록한다.

이 항목은 앱 자격 증명과 테스트 guild가 준비되어야 실행할 수 있다.
