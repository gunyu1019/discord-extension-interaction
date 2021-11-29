<h1 align="center">Discord(Py)-Extension-Cog</h1>
<p align="center">
    <img src="https://img.shields.io/badge/release_version-0.0.6%20alpha-0080aa?style=flat" alt="Release" >
</p>

# Introduce
[discord.py](https://github.com/Rapptz/discord.py)의 [ext.commands](https://github.com/Rapptz/discord.py/tree/master/discord/ext/commands)와 비슷한 구조를 갖고 있으며, 빗금 명령어(Slash Command)와 일반 명령어(Message Command)를 한 번에 사용할 수 있도록 만들어 주는 확장 모듈입니다.

# Enviroment
디스코드 봇은 아래의 환경에서 개발하고 있습니다.
<table>
    <thead>
        <tr>
            <th>NAME</th>
            <th>VERSION</th>
            <th>TESTED</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Windows</td>
            <td>Windows 11 21H2</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Development)</td>
        </tr>
        <tr>
            <td>Python</td>
            <td>v3.8.6</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Development)</td>
        </tr>
        <tr>
            <td>MariaDB</td>
                <td>10.3.23-MariaDB</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji></td>
        </tr>
    </tbody>
</table>

# Function Process
아래 항목에는 현재 작업 중인 기능 목록을 나열합니다.
> **♣**: 신규 기능<br/>
> **⊙**: 리메이크 기능 (P1 - Add Component)<br/>
> **◐**: 리메이크 기능 (P2 - Remake Service)<br/>
* 검색
    * 코로나 정보 ◐
    * 날씨 정보 ◐
    * 택배 운송 정보 ⊙
    * 스팀 게임 정보 ⊙
    * 학교 급식 정보 ⊙
    * 한강 수온 정보
    * 번역 기능
    * 애니메이션 검색 ⊙
* 전적 검색
    * 리그오브레전드 ⊙
    * 배틀그라운드 - PUBG BOT v1.3 (T)
    * 레인보우식스 ◐
    * 오버워치 ⊙
    * 하이픽셀 ◐
    * 마인크래프트 ⊙
    * 포트나이트 ⊙
* 미니 게임 기능
    * 타자 연습 게임 ⊙
    * O/X 게임♣
    * 5x5 오셀로 게임 ♣
    * 5x5 오목(3줄 승리) ♣
    * 레벨링 기능 ♣
        * 메시지 (+1)
        * [미니게임] 게임 우승 (+20)
        * 포럼 커뮤니티 채팅 (+5)
        * 파트너 커뮤니티 채팅 (+2)
        * Top.gg / KoreanBots / UniqueBots 하트 및 좋아요 (+10)
    * 레벨 기반  / 도박 기능 ♣
* 음악 기능 ♣
    * Powered By [Music Bot](https://github.com/gunyu1019/Music-Bot)
* 관리자 전용 기능
    * Python Console Debug - debug v2 
    * Shell Debug ♣
    * MySQL Command Debug ♣
* 이모지 (밈) 기능 ♣
* 대시보드 (v4.1:+)
    * 계정 연동 기능 (Oauth2)
        * 배틀넷 - 오버워치 
