class RatingDistribution(dict):
    def __init__(self):
        self.total_vote_count = 0

    def __setitem__(self, key, value):
        assert key >= 1 and key <= 10
        assert value >= 0
        if key in self:
            self.total_vote_count -= self[key]
        super().__setitem__(key, value)
        self.total_vote_count += value

    def __add__(self, other):
        tmp = self.copy() # we don't need a deep copy
        for key, value in tmp.items():
            tmp[key] += other[key]
        return tmp


class Media:
    def __init__(self, rank, title, rating_str, vote_count, directors, 
                 writers, stars, year, genres, description, rating_dist):
        self.rank = rank
        self.title = title
        self.rating_str = rating_str
        self.vote_count = vote_count
        self.directors = directors
        self.writers = writers
        self.stars = stars
        self.year = year
        self.genres = genres
        self.description = description
        self.rating_dist = rating_dist

    def __str__(self):
        return (
            f'rank = {self.rank}\n'
            f'title = {self.title}\n'
            f'rating = {self.rating_str}\n'
            f'vote count = {self.vote_count}\n'
            f'director(s) = {self.directors}\n'
            f'writer(s) = {self.writers}\n'
            f'star(s) = {self.stars}\n'
            f'year = {self.year}\n'
            f'genres = {self.genres}\n'
            f'description = {self.description}'
        )


class Movie(Media):
    def __init__(self, rank, title, rating_str, vote_count, directors,
                 writers, stars, year, genres, description, rating_dist, duration):
        super().__init__(rank, title, rating_str, vote_count, directors,
                 writers, stars, year, genres, description, rating_dist)
        self.duration = duration

    def __str__(self):
        return super().__str__() + f'\nduration = {self.duration}'
