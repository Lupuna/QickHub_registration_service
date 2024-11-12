FROM nginx:alpine3.20

RUN apk update && \
    apk add --no-cache \
    ca-certificates \
    openssl \
    && update-ca-certificates

COPY ../../certs/nginx-selfsigned.crt /etc/nginx/certs/nginx-selfsigned.crt
COPY ../../certs/nginx-selfsigned.key /etc/nginx/certs/nginx-selfsigned.key
COPY ../../certs/nginx-selfsigned.crt /usr/local/share/ca-certificates/nginx-selfsigned.crt

RUN update-ca-certificates
