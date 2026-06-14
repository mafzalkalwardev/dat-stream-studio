FROM alpine:3.24
WORKDIR /src
COPY . .
LABEL org.opencontainers.image.source="https://github.com/mafzalkalwardev/dat-stream-studio"
CMD ["sh", "-c", "echo 'dat-stream-studio source package' && ls -1"]
