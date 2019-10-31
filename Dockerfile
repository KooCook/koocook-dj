FROM python:3.7.5-slim-stretch
WORKDIR /usr/src/app
COPY . .

ARG SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
ARG SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
ARG DJANGO_SECRET_KEY
ARG DJANGO_ALLOWED_HOSTS
ARG DEBUG

#ENV GCP_SKEYFILE=gcp/skey_deploy.json
ENV DEBUG=$DEBUG
ENV SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=$SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
ENV SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=$SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
ENV DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS


# Register gcloud to Debian package registry
#RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
#RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update -y

RUN apt-get install -y openssh-client git curl libpq-dev gcc
RUN pip install psycopg2~=2.6
# Remove after configuring Psycopg2
RUN apt-get autoremove -y gcc

RUN pip install -r requirements.txt

# Install GCP SDKs
#RUN apt-get install google-cloud-sdk -y
# Activate GCP Service Account credentials
#RUN gcloud auth activate-service-account --key-file config/$GCP_SKEYFILE
# Configure the target project for deployment
#RUN gcloud config set project koocook-deploy
RUN python manage.py migrate
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
