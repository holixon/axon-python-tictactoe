FROM --platform=linux/amd64 python:3.10

WORKDIR /app
COPY ./axon-python-tictactoe /app
COPY ./axon-python-demo/axon /app/axon

