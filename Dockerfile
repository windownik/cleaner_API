FROM python:3.10

WORKDIR /main/

COPY . /main/

ENV TZ=Europe/Moscow
RUN apt-get update && apt-get install -yy tzdata
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip3 install aiohttp
RUN pip3 install uvicorn fastapi
RUN pip3 install fastapi-asyncpg
RUN pip3 install python-multipart
RUN pip3 install firebase-admin


CMD ["python3", "main.py"]
