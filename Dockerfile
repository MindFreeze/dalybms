ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

COPY requirements.txt /

RUN apk add --no-cache python3 && \
    rm /usr/lib/python3*/EXTERNALLY-MANAGED && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    python3 -m pip install -r requirements.txt && \
    rm -rf /root/.cache

COPY monitor.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]