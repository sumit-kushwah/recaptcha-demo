FROM golang:latest
WORKDIR /app
COPY go.mod .
RUN go mod tidy
COPY . .
RUN mkdir -p /data
ENV PORT=3000
EXPOSE 3000
RUN go build -o main .
CMD ["./main"]