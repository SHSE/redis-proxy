build:
	docker-compose build

clean:
	docker-compose down -v

test: build clean
	docker-compose run --rm tests
	docker-compose down -v
