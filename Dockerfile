FROM python:3.11.6

WORKDIR /app

COPY src/homework_api /app/src/homework_api
COPY pyproject.toml /app/
COPY README.md /app/
COPY .python-version /app/

RUN pip3 install .

CMD ["uvicorn", "src.homework_api.main:app", "--host", "0.0.0.0", "--port", "5000"]

EXPOSE 5000
