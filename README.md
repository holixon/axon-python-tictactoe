# Self-learning TicTacToe with Axon and Python

_(This is a work in progress repo. Do not use it in production.)_


Requirements 

- Python>=3.10
- [axon-python-synapse](https://github.com/holixon/axon-python-synapse) 

To install the app, first clone this repository.


```sh
git clone https://github.com/holixon/axon-python-tictactoe.git
```

Next install the dependencies. (Assuming in a venv where axon-python-synapse is installed)

```sh
cd axon-python-tictactoe
pip install .
```


To start the backend app.

```sh
python -m backend
```

Likewise for the frontend app.

```sh
python -m frontend
```


Configure the axon synapse server endpoint for frontend and backend apps with the environment variable `AXON_SYNAPSE_API`.

```sh
# default is http://localhost:8080/v1
AXON_SYNAPSE_API=http://axon-synapse:8080/v1 python -m frontend
```

The backend app registers its callback handlers using the host as defined in `CALLBACK_HOST`.

```sh
# default is system hostname
CALLBACK_HOST=tictactoe AXON_SYNAPSE_API=... python -m backend
```

