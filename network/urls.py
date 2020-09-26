
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("post", views.post, name="post"),
    path("post/edit/<int:post_id>", views.edit_post, name="edit"),
    path("post/like/<int:post_id>", views.like_post, name="like")
]
