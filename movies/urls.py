from django.urls import path
from . import views

urlpatterns = [
    path("", views.MoviesView.as_view()),
    path("filter/", views.FilterMoviesView.as_view(), name='filter'),
    path("search/", views.Search.as_view(), name='search'),
    path("<slug:slug>/", views.MovieDetailView.as_view(), name="movie_detail"),
    path("director/<str:slug>/", views.DirectorView.as_view(), name="director_detail"),
]
