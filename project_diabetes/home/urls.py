from django.urls import path
from home import views
urlpatterns = [
    path('', views.index, name='index'),
    path('prediction', views.prediction, name='prediction'),
    path('faq', views.faq, name='FAQs'),
    path('contact', views.contact, name='contact'),
    path('prediction/', views.prediction_view, name='prediction'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('doctor', views.doctor, name='doctor'),
    
]