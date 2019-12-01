.IGNORE:
.SILENT:

# make run to start all containers using docker-compose, in the same network
all: attach

attach: build run
	docker-compose run myclient && docker attach tema2_myclient_1

# make build if you want to build the images
build:
	docker-compose build

# make restart if you want to restart all the services, without the database beeing deleted
# this should be given after make stop
restart: run restart_attach

run:
	docker-compose -p tema2 up -d mysql-dev myserver myadmin-app

restart_attach:
	docker-compose run myclient && docker attach tema2_myclient_1

# make start_client host=(your host for other services)
# this should be given when the client is located on another network then the other 2 services
start_client:
	docker run -i --network host -p 8003:80 -p 8004:5000 client_py python main.py $(host)

# start the other 3 services
start_service: run

# stop without losing databse content
stop:
	docker-compose down

# stop and remove database content
exit_remove_volumes:
	docker-compose down -v