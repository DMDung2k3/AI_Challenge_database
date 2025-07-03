# Build PostgreSQL 15 with pgvector extension from source
FROM postgres:15

USER root

# Cài các package cần thiết để clone, build và verify SSL
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
       build-essential \
       postgresql-server-dev-15 \
  && rm -rf /var/lib/apt/lists/*

# Clone và build pgvector cho Postgres 15
RUN git clone https://github.com/pgvector/pgvector.git /pgvector \
  && cd /pgvector \
  && make \
  && make install \
  && cd / \
  && rm -rf /pgvector

# Gỡ các package build-time không cần thiết
RUN apt-get purge -y --auto-remove \
       git \
       build-essential \
       postgresql-server-dev-15 \
  && rm -rf /var/lib/apt/lists/*

USER postgres