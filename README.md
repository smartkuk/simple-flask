
```sh
curl http://localhost:5001
```

```sh
curl http://localhost:5001/
```

```sh
curl http://localhost:5001/health
```

```sh
curl http://localhost:5001/header
```

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

```sh
curl http://localhost:5001/users
```

```sh
curl http://localhost:5001/users/2
```

```sh
curl http://localhost:5001/users?user_name=Trump
```

```sh
curl -X DELETE http://localhost:5001/users/2
```

```sh
docker build -t simple-flask:v1 .
```

```sh
docker run -d -p 5001:5001 --name simple-flask simple-flask:v1
```

```sh
docker rm simple-flask
```
