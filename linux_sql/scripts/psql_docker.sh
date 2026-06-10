#!/bin/bash

# CLI Args
cmd=$1
db_username=$2
db_password=$3

# Run docker if not running
sudo systemctl status docker || sudo systemctl start docker

# Check container status
docker container inspect jrvs-psql
container_status=$?

case $cmd in

  # Create container
  create)
  if [ $container_status -eq 0 ]; then
    echo 'Container already exists'
    exit 1
  fi

  if [ $# -ne 3 ]; then
    echo 'Username and Password required'
    exit 1
  fi

  echo 'Creating new Container'
  docker volume create pgdata
  docker run --name jrvs-psql -e POSTGRES_PASSWORD=$db_password  -d -v pgdata:/var/lib/postgresql/data -p 5432:5432 postgres:9.6-alpine
  exit $?
  ;;

  # Start or Stop container
  start|stop)
  if [ $container_status -eq 1 ]; then
    echo 'Container does not exist'
    exit 1
  fi

  docker container $cmd jrvs-psql
  exit $?
  ;;

  *)
  echo 'Illegal Command'
  echo 'Valid Commands Start|Stop|Create'
  exit 1

esac