"""oppo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.lista_moviles, name='inicio'),
    path('carga/',views.carga, name='carga'),
    path('moviles_precio/', views.buscar_porprecio),
    path('moviles_fecha/', views.buscar_porfecha),
    path('moviles_modelo/', views.buscar_pormodelo),
    path('moviles_puntuacion/', views.buscar_porpuntuacion),
    path('moviles_capacidad/', views.buscar_porcapacidad),
    path('moviles_bateria/', views.buscar_porbateria),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name="login"),
    path('logout/', views.logout_request, name= "logout"),
    path('favoritos/', views.favoritos),
    path('recomendaciones/', views.recomendacion),
    path('toggle-favorito/<int:movil_id>/', views.toggle_favorito, name='toggle_favorito'),

]
