# API side

## Prepare env

```bash
> cd api
> poetry shell
> cd ..
```

## Launch locally

```bash
> python -m api.main
...
INFO:     Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
```

## Run tests

```bash
> python -m pytest --cov=api --cov-branch --cov-report term-missing
```
