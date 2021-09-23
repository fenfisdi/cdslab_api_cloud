FROM python:3.7.10-slim
EXPOSE 8080

ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV /app/.venv
ENV APP_HOME /app
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"


RUN apt-get update \
    && apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl gnupg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-cloud-sdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists


WORKDIR $APP_HOME

COPY requirements.txt .

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY docker-entrypoint.sh .
COPY src src
COPY api.json /tmp/api_key.json

ENTRYPOINT ["/bin/bash"]
CMD ["./docker-entrypoint.sh"]
