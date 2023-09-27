FROM python:3

WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/path/to/audio"
COPY ./audio /usr/local/lib/python3.11/site-packages/audio
RUN pip install /path/to/audio
VOLUME /path/to/audio

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]