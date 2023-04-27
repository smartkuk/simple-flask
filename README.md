
# simple-flask

쿠버네티스 환경에 동작 상태를 확인하기 위해 단순하게 개발된 Flask 프로젝트이다. REST API 및 Html 화면을 통해서 기능 점검을 제공한다.

## API List

사용할 수 있는 REST API 목록은 다음과 같다. 사용한 포트는 기본 포트이고 변경이 가능하다.

* 화면 접속

  ```sh
  curl http://localhost:5001
  ```

  아래와 같이 마지막에 '/'가 설정이 되어도 화면에 진입 가능하다.

  ```sh
  curl http://localhost:5001/
  ```

* 헬스체크

  애플리케이션에 생존을 검사하는 헬스체크 API를 제공한다.

  ```sh
  curl http://localhost:5001/health
  {
    "status": "OK"
  }
  ```

* Header 설정의 검증

  애플리케이션에 헤더를 설정해서 요청하면 그 정보를 응답하는 API로 Istio VirtualService 설정을 검증하는 기능이다.

  ```sh
  curl http://localhost:5001/header
  {
    "Accept": "*/*",
    "Host": "localhost:5001",
    "User-Agent": "curl/7.58.0"
  }
  ```

  ```sh
  curl -H "username:smartkuk" http://localhost:5001/header
  {
    "Accept": "*/*",
    "Host": "localhost:5001",
    "User-Agent": "curl/7.58.0",
    "Username": "smartkuk"
  }
  ```

* POST 메소드로 데이터 저장

  애플리케이션에 사용자 정보 데이터를 저장하는 API이다. 기본적으로 사용자 데이터는 미국 대통령 이름으로 5개가 초기 설정이 된다.

  ```sh
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"user_id": "1", "user_name": "Trump"}' \
    http://localhost:5001/users
  ```

  ```sh
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"user_id": "2", "user_name": "Obama"}' \
    http://localhost:5001/users
  ```

  ```sh
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"user_id": "3", "user_name": "Biden"}' \
    http://localhost:5001/users
  ```

* GET 메소드로 데이터 조회

  애플리케이션에 저장된 사용자 데이터를 조회하는 API이다. 다양한 방식으로 데이터를 조회가 가능하다.

  ```sh
  curl http://localhost:5001/users
  [
    {
      "country": "US",
      "user_id": "1",
      "user_name": "Trump"
    },
    {
      "country": "US",
      "user_id": "2",
      "user_name": "Obama"
    },
    {
      "country": "US",
      "user_id": "3",
      "user_name": "Biden"
    },
    {
      "country": "US",
      "user_id": "4",
      "user_name": "Jefferson"
    },
    {
      "country": "US",
      "user_id": "5",
      "user_name": "Kennedy"
    }
  ]
  ```

  사용자 ID 정보로 조회하는 예시는 아래와 같다.

  ```sh
  curl http://localhost:5001/users/2
  {
    "country": "US",
    "user_id": "2",
    "user_name": "Obama"
  }
  ```

  사용자 이름을 쿼리 파라미터를 사용해서 조회하는 예시가 아래와 같다.

  ```sh
  curl http://localhost:5001/users?user_name=Trump
  {
    "country": "US",
    "user_id": "1",
    "user_name": "Trump"
  }
  ```

* DELETE 메소드로 사용자 데이터 삭제

  ```sh
  curl -X DELETE http://localhost:5001/users/2
  {
    "country": "US",
    "user_id": "2",
    "user_name": "Obama"
  }
  curl http://localhost:5001/users/2
  {
    "message": "Not found user by user_id=2"
  }
  ```

---

## OS별 환경변수 설정법

  아래는 OS 환경별로 simple-flask 프로젝트에서 사용하는 환경변수를 설정하는 방법을 작성했다.

  ```cmd
  set PORT=8888
  set VERSION=GREEN
  set CONTEXT_PATH=/green
  set VERBOSE=True
  ```

  > Windows cmd

  ```sh
  export PORT=8888
  export VERSION=GREEN
  export CONTEXT_PATH=/green
  export VERBOSE=True
  ```

  > 리눅스 기반 OS

  |변수명|설명|
  |---|---|
  |PORT|애플리케이션이 시작할때 사용하는 Listen 포트번호(기본값: 5001)|
  |VERSION|화면 또는 응답 헤더에 지정하는 버전 값(기본값: BLUE) GREEN을 설정하면 화면에서는 색상이 변경되는 효과도 있음|
  |CONTEXT_PATH|요청을 수신시 / 대신에 다른 형태로 시작하고 싶다면 설정하는 컨텍스트 경로(기본값: '/')|
  |VERBOSE|요청 객체를 출력하려면 True 설정|

---

## Docker 빌드

본 프로젝트에는 Dockerfile 파일을 제공하고 있고 이것을 이용해서 컨테이너 이미지를 생성하고 기동할 수 있다.

```sh
docker build -t simple-flask:v1 .
```

---

## Docker 이미지 실행

```sh
docker run -d -p 5001:5001 --name simple-flask simple-flask:v1
```

아래는 환경변수 주입을 통해서 이미지를 실행하는 예시이다.

```sh
HOST_PORT=5001
EXPOSE_PORT=8888

docker run -d -p $HOST_PORT:$EXPOSE_PORT \
  -e VERSION=GREEN \
  -e CONTEXT_PATH=/green \
  -e PORT=$EXPOSE_PORT \
  -e VERBOSE=True \
  --name simple-flask \
  simple-flask:v1
```

---

## Docker 리소스 정리

```sh
docker stop simple-flask
docker rm simple-flask
docker rmi simple-flask:v1
```
