#!/bin/bash
docker run --rm -it \
    -e AWS_PROFILE=lego-worker \
    -e CLOUDWATCH_LOG_GROUP=lego-catalog-pipeline-dev \
    -e S3_BUCKET_NAME=lego-catalog-storage \
    -e SQS_QUEUE_URL=https://sqs.eu-west-3.amazonaws.com/730335557058/lego-catalog-queue \
    -e LDRAW_PATH=/tmp/ldraw.zip \
    -e OUTPUT_PATH=/tmp/output \
    -e MAX_EMPTY_POLLS=3 \
    -v ~/.aws:/root/.aws \
    lego-converter
    