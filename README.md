## Sustech Store 

An implement for CS309 Project. 

This is the back-end code of a second-hand trading platform. The platform supports buyers and sellers to communicate in real time, and designs a complete return and exchange process.

## Requirements

The backend is implemented using the Django framework. In order to improve performance, celery, redis and other techniques are used.

You can install all requirements by

```
pip install -r requirements.txt
```

## Quick Start 

You can start the server by

```
python run_uvicorn.py
```

You can also build a docker image by Dockerfile.