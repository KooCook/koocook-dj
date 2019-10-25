FROM python:3.7.5-slim-stretch
WORKDIR /usr/src/app
COPY . .

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install psycopg2~=2.6
# Remove after configuring Psycopg2
RUN apt-get autoremove -y gcc

RUN pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
