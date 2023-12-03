#!/bin/bash

#USAGE Example bash .autodevops/quick_build_deploy.sh dev auth

ENVIRONMENT=$1
COMPONENT_NAME=$2

echo Start CD process to $ENVIRONMENT environment

source .autodevops/service.properties

cz bump -ch

SERVICE_VERSION=$(cz version -p)
IMAGE_NAME=shkedia-photo-${COMPONENT_NAME}-service:${SERVICE_VERSION}
IMAGE_FULL_NAME=public.ecr.aws/q2n5r5e8/ozrnds/${IMAGE_NAME}

echo BUILD IMAGE $IMAGE_FULL_NAME
docker build . -t ${IMAGE_FULL_NAME}

ENVIRONMENT=dev
DEPLOYMENT_ENV=.local/${COMPONENT_NAME}_service_${ENVIRONMENT}.env
export ${COMPONENT_NAME^^}_SERVICE_VERSION=$SERVICE_VERSION

echo Deploy with env file $DEPLOYMENT_ENV

docker compose --env-file ${DEPLOYMENT_ENV} up -d