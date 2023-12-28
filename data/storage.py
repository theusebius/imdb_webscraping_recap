import errno
import os
import sqlite3
from movie_info import RatingDistribution

DB_NAME = "data/movie.db"

class Storage:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Storage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.path_exists = os.path.exists(DB_NAME)
        if not self.path_exists:
            raise FileNotFoundError(
                errno.ENOENT, 
                os.strerror(errno.ENOENT), 
                DB_NAME
            )
        
        self.conn = sqlite3.connect(DB_NAME) 
        self.cur = self.conn.cursor()
        self.rating_dist = None

    def __del__(self):
        if self.path_exists:
            self.conn.close()
    
    def __get__query_res(self, query):
        return self.cur.execute(query).fetchall()

    def get_movie_ids_names(self):
        query = '''
            SELECT id, title
            FROM Movie
        '''
        return self.__get__query_res(query)

    def get_genre_ids_names(self):
        query = '''
            SELECT id, name
            FROM Genre
        '''
        return self.__get__query_res(query)
            
    def get_director_ids_names(self):
        query = '''
            SELECT DISTINCT Person.id, name
            FROM Person JOIN MovieDirector
            ON Person.id = MovieDirector.director_id
        '''
        return self.__get__query_res(query)

    def get_writer_ids_names(self):
        query = '''
            SELECT DISTINCT Person.id, name
            FROM Person JOIN MovieWriter
            ON Person.id = MovieWriter.writer_id
        '''
        return self.__get__query_res(query)

    def get_movie_scores(self):
        query = '''
            SELECT rank, title, rating from Movie
        '''
        return self.__get__query_res(query)

    def get_star_ids_names(self):
        query = '''
            SELECT DISTINCT Person.id, name
            FROM Person JOIN MovieStar
            ON Person.id = MovieStar.star_id
        '''
        return self.__get__query_res(query)

    def get_person_page_info(self, activity_type, person_id):
        name_query = f'''
            SELECT name from Person
            WHERE id == {person_id}
        '''
        name = self.__get__query_res(name_query)[0][0]

        conj_table = f'Movie{activity_type.capitalize()}'
        movie_query = f'''
            SELECT title, rating, year
            FROM Movie JOIN {conj_table}
            ON Movie.id = {conj_table}.movie_id
            JOIN Person ON Person.id = {conj_table}.{activity_type}_id
            WHERE Person.id == {person_id}
            ORDER BY rating DESC
        '''

        movies = self.__get__query_res(movie_query)
        return name, movies
    
    def get_genre_data(self):
        query = f'''
            SELECT name, rating
            FROM Genre JOIN MovieGenre
            ON Genre.id = MovieGenre.genre_id
            JOIN Movie ON MovieGenre.movie_id = Movie.id
        '''
        return self.__get__query_res(query)
        
    def get_unweighted_scores(self):
        query = '''
            SELECT Movie.title,
            CAST(SUM(MovieRatingDist.rating * MovieRatingDist.vote_count) AS FLOAT)
            / SUM(MovieRatingDist.vote_count) as Average_Rating
            FROM MovieRatingDist
            JOIN Movie ON MovieRatingDist.movie_id = Movie.id
            GROUP BY Movie.id
            ORDER BY Average_Rating DESC
        '''
        return self.__get__query_res(query)
        
    def get_full_movie_info(self):
        query = '''
            SELECT Movie.title,
            CAST(SUM(MovieRatingDist.rating * MovieRatingDist.vote_count) AS FLOAT)
            / SUM(MovieRatingDist.vote_count) as Average_Rating
            FROM MovieRatingDist
            JOIN Movie ON MovieRatingDist.movie_id = Movie.id
            GROUP BY Movie.id
            ORDER BY Average_Rating DESC
        '''
        return self.__get__query_res(query)

    def get_movie_id_to_rating_dist(self):
        query = 'SELECT * FROM RatingDist'
        movie_id_to_rating_dist = {}
        query_res = self.__get__query_res(query)
        for movie_id, rating, vote_count  in query_res:
            if not movie_id in movie_id_to_rating_dist:
                movie_id_to_rating_dist[movie_id] = RatingDistribution()
            movie_id_to_rating_dist[movie_id][rating] = vote_count
        return movie_id_to_rating_dist