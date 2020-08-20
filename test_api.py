import requests
import json
import urllib.request
import sqlite3
import os
import glob
import wikipedia
from slug import slug

wikipedia.set_lang('ru')

# подключение базы данных Django проекта
conn_django = sqlite3.connect("Django_FilmsBD.sqlite3", check_same_thread=False, timeout=10)
cursor_django = conn_django.cursor()
# чистка базы данных перед заполнением
cursor_django.execute("DELETE FROM movies_movie_director")
cursor_django.execute("DELETE FROM movies_director")
cursor_django.execute("DELETE FROM movies_movie")
cursor_django.execute("DELETE FROM movies_genre")
cursor_django.execute("DELETE FROM movies_movie_genre")
cursor_django.execute("DELETE FROM movies_movieshots")
conn_django.commit()

# очистка папок с картинками

files = glob.glob('media/**/*.jpg', recursive=True)
for f in files:
    try:
        os.remove(f)
    except OSError:
        pass


def download_pic(name_file, url, name_dir):
    """Скачивание картинки по URL"""
    img = urllib.request.urlopen(url).read()
    out = open("media/" + name_dir + "/" + name_file + ".jpg", "wb")
    out.write(img)


def get_response(req, param, film_filter=""):
    url = ''
    if req == 'name':
        url = 'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword=' + param + '&page=1'
    elif req == 'id':
        url = 'https://kinopoiskapiunofficial.tech/api/v2.1/films/' + param + "?append_to_response=" + film_filter
    elif req == 'staff_id':
        url = 'https://kinopoiskapiunofficial.tech/api/v1/staff?filmId=' + param
    response = requests.get(
        url,
        headers={'Accept': 'application/json',
                 'X-API-KEY': '6a37b452-05e2-44b3-8337-82b4b68ba23d'
                 },
    )
    return json.loads(response.text)


class Film:

    def __init__(self, name_mov):
        self.filmId = str(get_response('name', name_mov)['films'][0]['filmId'])
        todos = get_response('id', self.filmId)
        self.nameRu = todos['data']['nameRu']
        self.nameEn = todos['data']['nameEn']
        self.year = str(todos['data']['year'])
        self.slogan = todos['data']['slogan']
        self.description = todos['data']['description']
        self.category_id = 1
        self.poster = 'movies/' + str(self.filmId) + '.jpg'
        download_pic(self.filmId, todos['data']['posterUrl'], 'movies')
        tod = get_response('id', self.filmId, 'BUDGET')
        self.budget = tod['budget']['budget']
        self.gross_usa = tod['budget']['grossUsa']
        self.gross_russia = tod['budget']['grossRu']
        self.gross_world = tod['budget']['grossWorld']
        todo = get_response('id', self.filmId, 'RATING')
        self.rating_kinopoisk = todo['rating']['rating']
        self.draft = 0

        self.url = slug(self.filmId)
        """ 
        
        """
        #self.url = slug(self.nameEn)

        self.film_class = todos['data']['type']
        self.film_detail_id = '1'
        self.genre = ','.join(self.get_genre())
        self.country = ','.join(self.get_country())

    def get_country(self):
        countries = get_response('id', self.filmId)['data']['countries']
        countr = []
        for c in countries:
            countr.append(c['country'])
        return countr

    def get_genre(self):
        genres = get_response('id', self.filmId)['data']['genres']
        genr = []
        for g in genres:
            genr.append(g['genre'])
        return genr


director = []
director_id = {}
director_descrip = {}
num_of_note = 1
num_of_genre = 1
num_of_dir = 1
all_films_id = []
all_genre = []
all_director = []


# Получаем информацию о режисcере
def director_inf(a):
    tod = get_response('staff_id', a.filmId)
    c = 0
    while str(tod[c]["professionKey"]) == "DIRECTOR":
        director.append(tod[c]['nameRu'])
        director_id[tod[c]['nameRu']] = tod[c]['staffId']
        try:
            director_descrip[tod[c]['nameRu']] = wikipedia.summary(tod[c]['nameRu'])
        except:
            director_descrip[tod[c]['nameRu']] = 'pass'
        download_pic(str(tod[c]['staffId']), (tod[c]['posterUrl']), 'directors')
        c += 1


def add_director(movie, num_of_movie):
    global num_of_dir
    director_inf(movie)
    for c in director:
        if not c in all_director:
            cursor_django.execute("""
                     INSERT INTO movies_movie_director
                     VALUES (?,?,?)
                    """, (
                num_of_dir, num_of_movie, director_id[c]
            ))

            conn_django.commit()

            pic_url = 'directors/' + str(director_id[c]) + '.jpg'
            cursor_django.execute("""
                INSERT INTO movies_director
                 VALUES (?,?,?,?,?)
                """, (
                director_id[c], c, 10, director_descrip[c], pic_url
            ))

            num_of_dir += 1

            all_director.append(c)

            conn_django.commit()


def add_genre(movie, num_of_movie):
    global num_of_genre
    genres = movie.get_genre()
    for genre in genres:
        if not genre in all_genre:
            cursor_django.execute("""
                         INSERT INTO movies_movie_genre
                         VALUES (?,?,?)
                        """, (
                num_of_genre, num_of_movie, num_of_genre
            ))
            conn_django.commit()
            cursor_django.execute("""
                         INSERT INTO movies_genre
                         VALUES (?,?,?,?)
                        """, (
                num_of_genre, genre, wikipedia.summary(str(genre) + '(жанр)'), num_of_genre
            ))
            num_of_genre += 1
            conn_django.commit()

            all_genre.append(genre)


# добавление в БД
def add_notes(movie_name, detail_id):
    global num_of_note
    movie = Film(movie_name)
    if not movie.filmId in all_films_id:
        movie.film_detail_id = detail_id
        sql = """
                        INSERT OR REPLACE INTO movies_movie 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                       """
        cursor_django.execute(sql, (
            num_of_note, movie.nameRu, movie.slogan, movie.description, movie.poster, movie.year, movie.country,
            movie.budget, movie.gross_usa, movie.gross_world, movie.gross_russia, movie.film_class,
            movie.film_detail_id, movie.url, movie.draft, movie.category_id, movie.rating_kinopoisk
        ))
        conn_django.commit()

        add_director(movie, num_of_note)
        add_genre(movie, num_of_note)

        director.clear()
        director_id.clear()
        director_descrip.clear()

        all_films_id.append(movie.filmId)
        num_of_note += 1


# подключение базы данных с фильмами
conn = sqlite3.connect("files.db", check_same_thread=False, timeout=10)
cursor = conn.cursor()

cursor.execute("SELECT DETAIL_ID,NAME FROM OBJECTS WHERE CLASS=:Id",
               {"Id": "item.videoItem"})
while True:
    row = cursor.fetchone()
    if row == None:
        break
    else:
        try:
            print(row[1])
            add_notes(row[1], row[0])
        except IndexError:
            pass
        conn.commit()
