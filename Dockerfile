FROM python:3

WORKDIR /usr/src/app

ENV PYTHONPATH="/path/to/audio:$PYTHONPATH"
ADD audio /app/audio

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]