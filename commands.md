
## Activate the Virtual Environment
1. python3 venv .venv
2. source .venv/bin/activate

## Redirect Libraries and Packages from the pip to the requirements.txt file
pip freeze > requirements.txt


## Docker Commands
1. docker compose build
2. docker compose up -d
3. docker exec -it docsign_api alembic upgrade head
4. docker exec -it docsign-backend-postgres-1 psql -U postgres -d docsign

docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=docsign \
  -p 5432:5432 \
  postgres


1. alembic init migrations


for postgres inside the docker container : postgresql+psycopg://postgres:postgres@postgres:5432/docsign
for postgres on the localhost : postgresql+psycopg://postgres:postgres@localhost:5432/docsign

Running Flask APP Locally
export FLASK_ENV=development
export FLASK_APP=main:create_app
flask run