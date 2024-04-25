FROM python:3.11

RUN pip install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "python", "main.py"]