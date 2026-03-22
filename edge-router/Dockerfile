# syntax=docker/dockerfile:experimental

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/

RUN pip install --no-cache-dir --user -r requirements/dev.txt

COPY app/ app/


FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends dos2unix && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY app/ app/

COPY start.sh /start.sh
RUN dos2unix /start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]