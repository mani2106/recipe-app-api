"""
Mappings for user api
"""
from django.urls import path

# from user import views
from .views import CreateUserView, CreateTokenView, ManageUserView

app_name = 'user'

urlpatterns = [
    path('create/', view=CreateUserView.as_view(),
         # name is used in reverse lookup, check test_user_api.py
         name='create'),
    path('token/', view=CreateTokenView.as_view(), name='token'),
    path('me/', view=ManageUserView.as_view(), name='me')
]
