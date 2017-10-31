FROM tiangolo/uwsgi-nginx-flask:python3.6

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install uwsgi
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn","-b 0.0.0.0:8000","server:app"]
