from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('realtime',views.index,name='Mainpage'),
    path('home',views.home),
    path('prevent',views.prevent),
    path('info',views.info),
    path('travel',views.travelhome),
    path('traveldet',views.traveldet),
    path('dashboard',views.dashboard),
    path('comparitive_analytics',views.comparitive_analytics),
    path('cma',views.cma),
    path('india',views.india),
    path('localdash',views.localdash),
    path('login',views.login)
]