FROM postgres:15

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-15-cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo "shared_preload_libraries = 'pg_cron'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "cron.database_name = 'shopdb'" >> /usr/share/postgresql/postgresql.conf.sample

CMD ["postgres"]