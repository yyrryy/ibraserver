from django.urls import path, include
from . import checkviews
from . import views

urlpatterns = [
    path('notifyadmin', views.notifyadmin, name='notifyadmin'),
    path('disablenotif', views.disablenotif, name='disablenotif'),
    path('getconnectedusers', views.getconnectedusers, name='getconnectedusers'),
    # path('notifyadmin', views.notifyadmin, name='notifyadmin'),
    # path('notifyadmin', views.notifyadmin, name='notifyadmin'),
    # path('notifyadmin', views.notifyadmin, name='notifyadmin'),
]