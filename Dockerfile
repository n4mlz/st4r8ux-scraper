FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY main.py ./

RUN pip install -e .

CMD ["python", "main.py"]