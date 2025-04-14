FROM python:3.12-alpine

ENV TIMEZONE=UTC

RUN cp /usr/share/zoneinfo/$TIMEZONE /etc/localtime && \
  echo $TIMEZONE > /etc/timezone

ENV TZDIR=/usr/share/zoneinfo

WORKDIR /app

ADD . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 3000

CMD ["fastapi", "run", "main.py", "--port", "3000","--proxy-headers"]
