FROM python:3.9.13-slim

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENV VERSION="BLUE"
ENV CONTEXT_PATH=""
ENV PORT="5001"

CMD ["python3", "-m", "main", "run", "--host=0.0.0.0"]
