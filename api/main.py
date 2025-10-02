import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Instrument the app with Prometheus
Instrumentator().instrument(app).expose(app)

# Database connection details from environment variables
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Pydantic model for Movie
class Movie(BaseModel):
    id: int
    title: str
    director: str
    year: int

@app.on_event("startup")
def startup_event():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            director VARCHAR(255) NOT NULL,
            year INT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/movies/", response_model=Movie)
def create_movie(movie: Movie):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO movies (title, director, year) VALUES (%s, %s, %s) RETURNING id, title, director, year",
        (movie.title, movie.director, movie.year)
    )
    new_movie = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_movie

@app.get("/movies/", response_model=list[Movie])
def read_movies():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, director, year FROM movies")
    movies = cur.fetchall()
    cur.close()
    conn.close()
    return movies

@app.get("/movies/{movie_id}", response_model=Movie)
def read_movie(movie_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, director, year FROM movies WHERE id = %s", (movie_id,))
    movie = cur.fetchone()
    cur.close()
    conn.close()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie: Movie):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "UPDATE movies SET title = %s, director = %s, year = %s WHERE id = %s RETURNING id, title, director, year",
        (movie.title, movie.director, movie.year, movie_id)
    )
    updated_movie = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if updated_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated_movie

@app.delete("/movies/{movie_id}", response_model=Movie)
def delete_movie(movie_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("DELETE FROM movies WHERE id = %s RETURNING id, title, director, year", (movie_id,))
    deleted_movie = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if deleted_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return deleted_movie