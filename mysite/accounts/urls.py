from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register_view,
    my_profile_view,
    member_profile_view,
    following_view,
    follow_unfollow_view,
    follower_view,
)

app_name="accounts"
urlpatterns = [
    path('register/', register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path('my_profile/', my_profile_view, name="my-profile"),
    path('<int:id>/', member_profile_view, name="member-profile"),
    path('following/<int:id>/', following_view, name="following"),
    path('followers/<int:id>/', follower_view, name="followers"),
    path('follow_unfollow/<int:id>/', follow_unfollow_view, name="unfollow"),
]