FROM python:3.10

RUN apt-get update && apt-get install -y supervisor

WORKDIR /app

COPY axon-python-synapse/requirements.txt axon-python-synapse/
RUN pip install --no-cache -r ./axon-python-synapse/requirements.txt

COPY axon-python-tictactoe/requirements.txt axon-python-tictactoe/
RUN pip install --no-cache -r ./axon-python-tictactoe/requirements.txt

# RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisord.conf

COPY axon-python-synapse axon-python-synapse
COPY axon-python-tictactoe axon-python-tictactoe

RUN ls -l
RUN pip install --no-cache -e ./axon-python-synapse
RUN pip install --no-cache -e ./axon-python-tictactoe

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

# backend
EXPOSE 8888
# frontend
EXPOSE 8881
