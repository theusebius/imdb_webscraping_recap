import datetime
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict
from data.storage import Storage
from flask import Flask, render_template

matplotlib.use('agg')
colors = [
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
    "tab:cyan",
    "crimson",
    "darkorange",
    "limegreen",
    "darkviolet",
    "saddlebrown",
    "deeppink",
    "dimgray",
    "mediumaquamarine",
    "gold",
    "steelblue",
    "lime",
]

app = Flask(__name__)

@app.route('/')
def index():
    storage = Storage()
    movie_ids_names = storage.get_movie_ids_names()
    genre_ids_names = storage.get_genre_ids_names()
    director_ids_names = storage.get_director_ids_names()
    writer_ids_names = storage.get_writer_ids_names()
    star_ids_names = storage.get_star_ids_names()

    context = {
        'movie_ids_names' : movie_ids_names,
        'genre_ids_names' : genre_ids_names,
        'director_ids_names' : director_ids_names,
        'writer_ids_names' : writer_ids_names,
        'star_ids_names' : star_ids_names,
    }
    return render_template("index.html", **context)


def float_to_pretty_str(val):
    val = f"{val:.3f}".rstrip("0")
    if val[-1] == '.':
        val += '0'
    return val


@app.route('/<path:subpath>/<int:id>')
def get_page(subpath, id):
    storage = Storage()
    if subpath in ('director', 'writer', 'star'):
        activity_verb_past_tense = 'Directed'
        if subpath != 'director':
            activity_verb_past_tense = 'Wrote' if subpath == 'writer' else 'Starred'

        person_name, movies = storage.get_person_page_info(subpath, id)
        work_count = len(movies)

        print('movies:', movies)
        movie_ratings = [t[1] for t in movies]
        average_rating = sum(movie_ratings) / work_count
        average_rating = float_to_pretty_str(average_rating)

        movie_approx_sort = sorted(movies, key=lambda p: p[2])
        plot_titles = [t[0] for t in movie_approx_sort]
        plot_ratings = [t[1] for t in movie_approx_sort]
        plot_years = [t[2] for t in movie_approx_sort]
        plt.plot(plot_years, plot_ratings, color='black')
        for i in range(work_count):
            plt.scatter(
                plot_years[i],
                plot_ratings[i],
                color=colors[i],
                marker='o', label=f'{plot_titles[i]}'
            )
        plt.xticks(plot_years)
        plt.legend()
        plt.savefig('static/person_plot.svg')
        plt.clf()

        context = {
            'person_name' : person_name,
            'person_type' : subpath,
            'work_count' : work_count,
            'movies' : movies,
            'average_rating' : average_rating,
            'activity_verb_past_tense' : activity_verb_past_tense,
        }
        return render_template("person.html", svg_filename='person_plot.svg', **context)


def autopct_condition(value):
    return '%1.1f%%' % value if value >= 3 else ''


@app.route('/full_recap')
def get_full_recap():
    storage = Storage()

    weighted_rating_and_scores = storage.get_movie_scores()
    unweighted_scores = storage.get_unweighted_scores()
    # print('unweighted_scores:', unweighted_scores)
    unweighted_rating_and_scores = []
    for i in range(len(unweighted_scores)):
        unweighted_rating_and_scores.append(
            [i+1,
            unweighted_scores[i][0],
            float_to_pretty_str(unweighted_scores[i][1])
            ]
        )


    genre_data = storage.get_genre_data()
    genre_count = defaultdict(int)
    genre_acc_rating = defaultdict(float)
    for genre, rating in genre_data:
        genre_count[genre] += 1
        genre_acc_rating[genre] += rating

    plt.figure(figsize=(6, 8))
    plt.pie(genre_count.values(),
            autopct=autopct_condition
        )
    legend = plt.legend(genre_count.keys())
    legend.get_frame().set_alpha(0.5)
    plt.title('Genre Distribution')
    plt.savefig('static/genre_dist.svg')
    plt.clf()

    genre_avg_rating = {}
    for genre in genre_count:
        genre_avg_rating[genre] =  genre_acc_rating[genre] / genre_count[genre]
    # for i, (title, rating) in unweighted_rating_and_scores:
    #     print(i, title, rating)
    # print('unweighted_rating_and_scores:', list(unweighted_rating_and_scores))
    context = {
        'unweighted_rating_and_scores' : unweighted_rating_and_scores,
        'weighted_rating_and_scores' : weighted_rating_and_scores
        # 'person_type' : subpath,
        # 'work_count' : work_count,
        # 'movies' : movies,
        # 'average_rating' : average_rating,
        # 'activity_verb_past_tense' : activity_verb_past_tense,
    }
    genre_avg_rating

    genre_names = list(genre_avg_rating.keys())
    genre_ratings = list(genre_avg_rating.values())
    plt.plot(genre_ratings)
    for i in range(len(genre_ratings)):
        plt.scatter(
            genre_names[i],
            genre_ratings[i],
            color=colors[i],
            marker='o', label=f'{genre_names[i]}')
    plt.legend()
    plt.xticks([])
    plt.savefig('static/genre_rating.svg')
    plt.clf()


    return render_template("full_recap.html",
                           genre_dist_svg='genre_dist.svg',
                           genre_rating_svg='genre_rating.svg',
                           **context)


if __name__ == "__main__":
    app.run(
        host="localhost",
        debug=True
    )