# config.py
# These values MUST match what's in docker-compose.yml exactly.

DB_CONFIG = {
    "host":     "localhost",      # Docker maps the container to your localhost
    "database": "phonebook_db",   # POSTGRES_DB in docker-compose.yml
    "user":     "postgres",       # POSTGRES_USER in docker-compose.yml
    "password": "1234",           # POSTGRES_PASSWORD in docker-compose.yml
    "port":     "5432"            # The left side of "5432:5432" in ports
}