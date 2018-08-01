#!/bin/bash
git pull &&
export RELEASE=$(git rev-parse --short HEAD)  &&
docker-compose -f prod.yml build &&
docker-compose -f prod.yml push &&
docker stack deploy -c prod.yml manager_production &&
exit 0