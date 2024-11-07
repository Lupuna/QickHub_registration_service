FROM nginx:latest

COPY ../../certs/nginx-selfsigned.crt /usr/local/share/ca-certificates/nginx-selfsigned.crt

RUN update-ca-certificates

COPY ../../conf/nginx.conf /etc/nginx/nginx.conf

COPY ../../core/static /static