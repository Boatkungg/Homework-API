FROM python:3.11.6-slim-bookworm as base

FROM base as builder

RUN apt-get update

RUN apt-get install -y --no-install-recommends gcc build-essential

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml /install/
COPY README.md /install/
COPY .python-version /install/

WORKDIR /install

RUN pip install .

FROM base

COPY --from=builder /opt/venv /opt/venv

COPY src/homework_api /app/homework_api

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 5000

CMD ["uvicorn", "homework_api.main:app", "--host", "0.0.0.0", "--port", "5000"]
