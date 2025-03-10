import psycopg

connection = psycopg.connect("postgresql://postgres:password@localhost:5432")

pg_cursor = connection.cursor()
