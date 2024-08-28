FROM python:3.12.5-alpine3.19

WORKDIR /sandbox

ENV PYTHONPATH "${PYTHONPATH}:/.setup"

RUN apk --no-cache add build-base libmagic && \
    PYTHONDONTWRITEBYTECODE=1 pip3 install --no-cache-dir matplotlib==3.9.1 pandas==2.2.2 python-magic==0.4.27 japanize-matplotlib==1.1.3

ENTRYPOINT ["python3", "-c"]

CMD ["print('Hello, World!')"]
