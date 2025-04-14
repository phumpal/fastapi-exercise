FROM python:3.12-alpine

ENV TIMEZONE=UTC
ENV TZDIR=/usr/share/zoneinfo

RUN cp /usr/share/zoneinfo/$TIMEZONE /etc/localtime && \
  echo $TIMEZONE > /etc/timezone

WORKDIR /app

ADD ./app /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

EXPOSE 3000

CMD ["fastapi", "run", "main.py", "--port", "3000","--proxy-headers"]
