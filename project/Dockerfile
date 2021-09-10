FROM python:2.7-alpine

LABEL vendor="Noha Salah El-Tohamy"

COPY ./techtrends/ /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN python init_db.py

EXPOSE 3111

CMD ["python","app.py"]
