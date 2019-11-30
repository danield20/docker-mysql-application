.IGNORE:
.SILENT:

all: attach

attach: build run
	docker-compose run myclient && docker attach tema2_myclient_1 2>/dev/null

build:
	docker-compose build

run:
	docker-compose -p tema2 up -d mysql-dev myserver myadmin-app

restart_attach:
	docker-compose restart myclient && docker attach tema2_myclient_1

start_client:
	docker run -i --network host -p 8003:80 -p 8004:5000 client_py python main.py $(host)

start_service: run

stop:
	docker-compose down

exit_remove_volumes:
	docker-compose down -v