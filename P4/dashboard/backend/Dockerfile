FROM python:3.13-slim-trixie AS builder

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install --target=./lib -r requirements.txt

FROM gcr.io/distroless/python3-debian13:nonroot-amd64

EXPOSE 8080

WORKDIR /app

ENV PYTHONPATH=/app/lib

COPY --chown=nonroot:nonroot --from=builder /app/lib ./lib

COPY --chown=nonroot:nonroot ./ ./

CMD ["-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
