## Prerequisites

`docker`, `docker-compose` and `jq`  will need to be installed. On macOS

    brew install --cask docker
    brew install docker-compose
    brew install jq

Alternatively a naive `Brewfile` has been included to install dependencies

    brew bundle install

## Getting started

Running

    docker-compose up

will

- build the app image
- launch the db (Postgres) container with appropriate creds
- launch an haproxy reverse-proxy
- seed the database

## Manual verification

When `docker-compose.yml` completes `seed.sh` will run to populate the db. `./seed.sh` can be run again to verify the databases has been seeded

> Item "Arroz" already exists. Skipping

To manually verify endpoints through the reverse proxy you can try

Return a list of items

    curl -s http://localhost/items/ | jq

Adds a new item

    curl -s -XPOST \
      -H "Content-Type: application/json" \
      -d '{"content": "Duros"}' \
      http://localhost/items/

Getting the service health

    curl -s http://localhost/health | jq

## Operationalizing for prodution

Steps necessary before deploying this microservice to production

- Add a default/root route, appropriate redirects, TLS
- Add the ability to list items by id, prevent duplicate items
- Support async request handling
- Review and finalize [uvicorn](https://www.uvicorn.org/) config
- Improve validation and error handling
- Add tests - unit, integration, functional, etc
- Implement CI/CD for testing + deployments using GitHub Actions
- Add a `/metrics` endpoint for scraping (Prometheus)
- Ensure all logs are well structured and consumed (ELK, etc)
- Add a Helm chart (if deploying to k8s)


## Technical decisions

PostgreSQL was chosen as the persistence layer due to familiarity and its maturity. Most of the defaults work well out of the box until you need to scale. Alternatives I considered were

- MongoDB - Pros flexible schema, JSON-native storage. Cons: difficult to operationalize, can be resource intensive
- Redis - Pros: lightweight, fast, simple key-value storage. Cons: if we need complex queries later, this model may be better suited for a cache
- DuckDB - Pros: embedded. Cons - unfamiliar

Similarly, I wanted to stay consistent with the existing company stack. Other choices I made included

- FastAPI - great documentation and easy-to-follow examples (i.e., `items`)
- HAProxy - chosen due to familiarity and existing configs available to reuse. Nginx could have also worked

## Misc

A few other notes

- Used `psycopg2-binary` versus Alpine edge repos for `postgresql17-contrib` and `postgresql17-dev` to reduce image size
- Preferred environment variables to construct `DATABASE_URL` due to possible variable interpolation and YAML shortcomings in docker-compose
- Allowed use of `DATABASE_URL` _when_ developing outside of docker-compose
- Used GitHub Copilot to
    - improve maintainability - single responsibility, modular
    - add structured logging
