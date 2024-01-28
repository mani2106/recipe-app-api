"""
Mappings for user api
"""
from django.urls import path

# from user import views
from .views import CreateUserView

app_name = 'user'

urlpatterns = [
    path('create/', view=CreateUserView.as_view(),
         # name is used in reverse lookup, check test_user_api.py
         name='create')
]
