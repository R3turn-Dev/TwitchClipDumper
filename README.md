# TwitchClipDumper

안녕하세요 청소년 프로그래머 이은학입니다.

도네이션용 팬영상을 만들기 위해 클립은 매우 좋은 소스가 되는데요,

채널에 클립이 한두개가 아니라 한 번에 다운받기 힘들어서 프로그램을 만들어봤습니다

Twitch clips are great for creating montages of epic moments.

But it usually takes wasteful amount of time trying to download each and individual clips.

This simple python tool allows you to download all clips from any Twitch channel. 



## 모듈설치 (Prerequisite)
```
$ pip -r requirements.txt
```

## 사용방식 (Usage)

```
$ python run.py <channel_id> --client-id=<client_id> --token=<authorization_token>
```

전체 기간 클립들을 핫클립 순으로 다운받으며, 채널 이름으로 서브폴더를 만들고 다운받습니다.

각죵 이슈는 깃허브를 통해서 부탁드립니다

It downloads all clips in descending order of popularity into a subfolder with the same name as the channel id.

Please use the Github Issues for any problems. Thank you.
