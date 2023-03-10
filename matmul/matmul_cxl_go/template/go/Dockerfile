FROM --platform=${TARGETPLATFORM:-linux/amd64} ghcr.io/openfaas/classic-watchdog:0.2.1 as watchdog
FROM --platform=${TARGETPLATFORM:-linux/amd64} golang:1.18

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH

# Required to enable Go modules
RUN apt-get update \
    && apt-get install -y git
# RUN apk add --no-cache git

# Allows you to add additional packages via build-arg
ARG ADDITIONAL_PACKAGE
ARG CGO_ENABLED=0
ARG GO111MODULE="off"
ARG GOPROXY=""
ARG GOFLAGS=""

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ENV CGO_ENABLED=0

WORKDIR /go/src/handler
COPY . .

# Run a gofmt and exclude all vendored code.
# RUN test -z "$(gofmt -l $(find . -type f -name '*.go' -not -path "./vendor/*" -not -path "./function/vendor/*"))" || { echo "Run \"gofmt -s -w\" on your Golang code"; exit 1; }

WORKDIR /go/src/handler/function
RUN mkdir -p /go/src/handler/function/static
RUN go get gonum.org/v1/gonum/mat

RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} CGO_ENABLED=${CGO_ENABLED} go test ./... -cover

WORKDIR /go/src/handler


RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} CGO_ENABLED=${CGO_ENABLED} \
    go build --ldflags "-s -w" -a -installsuffix cgo -o handler .

# FROM --platform=${TARGETPLATFORM:-linux/amd64} alpine:3.15 as ship

RUN apt-get install -y ca-certificates numactl
# RUN addgroup -S app && adduser -S -g app app
RUN groupadd app && useradd -r -g app app



# WORKDIR /home/app
# RUN chown -R app /home/app 

# COPY --from=build --chown=app /usr/bin/fwatchdog                  .
# COPY --from=build --chown=app /go/src/handler/handler             .
# COPY --from=build --chown=app /go/src/handler/function/static   static

USER app

ENV fprocess="/go/src/handler/handler"
EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD numactl --cpunodebind 0 --membind 1 -- fwatchdog
