FROM --platform=linux/amd64 python:3.10

WORKDIR /app
COPY ./axon-python-tictactoe/requirements.txt /app
RUN pip install --no-cache -r /app/requirements.txt
COPY ./axon-python-tictactoe /app
COPY ./axon-python-demo/axon /app/axon

EXPOSE 8888
EXPOSE 8881

