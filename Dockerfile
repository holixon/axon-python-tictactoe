FROM --platform=linux/amd64 python:3.10

WORKDIR /app
# COPY ./axon-python-tictactoe/requirements.txt /app
COPY ./axon-python-synapse .
COPY ./axon-python-tictactoe .
RUN pip install --no-cache -e ./axon-python-synapse
RUN pip install --no-cache -e ./axon-python-tictactoe

# backend
EXPOSE 8888
# frontend
EXPOSE 8881

# docker run -d -p 8024:8024 -p 8124:8124 axoniq/axonserver
# docker run -d -p 8080:8080 --entrypoint=java axoniq/synapse -Dsynapse.axon-server.server-list=host.docker.internal -jar ./synapse.jar
