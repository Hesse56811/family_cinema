from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Категории"""
    name = models.CharField("Категория", max_length=150)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Director(models.Model):
    """Режиссеры"""
    name = models.CharField("Имя", max_length=100)
    age = models.PositiveSmallIntegerField("Возраст", default=0)
    description = models.TextField("Описание")
    image = models.ImageField("Изображние", upload_to="directors/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Режиссер"
        verbose_name_plural = "Режиссеры"

    def get_absolute_url(self):
        return reverse('director_detail', kwargs={"slug": self.name})


class Genre(models.Model):
    """Жанры"""
    name = models.CharField("Имя", max_length=100)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Movie(models.Model):
    """Фильм"""
    title = models.CharField("Название", max_length=100)
    tagline = models.CharField("Слоган", max_length=100, default='', null=True)
    description = models.TextField("Описание", null=True)
    poster = models.ImageField("Постер", upload_to="movies/")
    year = models.PositiveSmallIntegerField("Дата выхода", default=2019, null=True)
    country = models.CharField("Страна", max_length=30, null=True)
    director = models.ManyToManyField(Director, verbose_name="режиссер", related_name="film_director")
    genre = models.ManyToManyField(Genre, verbose_name="жанры")
    budget = models.PositiveIntegerField("Бюджет", default=0,
                                         help_text="указывать сумму в долларах", null=True)
    fees_in_usa = models.PositiveIntegerField(
        "Сборы в США", default=0, help_text="указывать сумму в долларах", null=True
    )
    fees_in_world = models.PositiveIntegerField(
        "Сборы в мире", default=0, help_text="указывать сумму в долларах", null=True
    )
    fees_in_russia = models.PositiveIntegerField(
        "Сборы в России", default=0, help_text="указывать сумму в долларах", null=True
    )
    rating = models.TextField("Рейтинг на Кинопоиске", max_length=5, default=10, null=True)
    film_class = models.TextField(max_length=100, null=True)
    film_detail_id = models.TextField("Уникальный id на серваке", max_length=100)
    category = models.ForeignKey(
        Category, verbose_name="Категория", on_delete=models.SET_NULL, null=True
    )
    url = models.SlugField(max_length=130, unique=True)
    draft = models.BooleanField("Черновик", default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("movie_detail", kwargs={"slug": self.url})

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"


class MovieShots(models.Model):
    """Кадры из фильма"""
    title = models.CharField("Заголовок", max_length=100)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="movie_shots/")
    movie = models.ForeignKey(Movie, verbose_name="Фильм", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Кадр из фильма"
        verbose_name_plural = "Кадры из фильма"
