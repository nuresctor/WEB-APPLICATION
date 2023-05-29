#encoding:utf-8
from main.models import Movil,Favorito
from main.populateDB import populateDB
from django.shortcuts import render, redirect,get_object_or_404
from main.forms import BusquedaPorFechaForm, BusquedaPorModeloForm, BusquedaPorPrecioForm, BusquedaPorPuntuacionForm, BusquedaPorCapacidadForm, BusquedaPorBateriaForm, NewUserForm
import urllib.request
import json
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def recomendacion(request):
    lista_favoritos = Movil.objects.filter(id__in=Favorito.objects.filter(user=request.user).values_list('movil', flat=True))
    lista_moviles_ids = Movil.objects.all()
    lista_no_favoritos = [elemento for elemento in lista_moviles_ids if elemento not in lista_favoritos]

    moviles_favoritos = Movil.objects.filter(id__in=lista_favoritos)
    moviles_recomendados = calcular_recomendaciones(lista_favoritos, lista_no_favoritos)[:3]

    context = {
        'moviles_favoritos': moviles_favoritos,
        'moviles_recomendados': moviles_recomendados,
    }

    return render(request, 'recomendacion.html', context)

def calcular_similitud(movil1, movil2):
    similitud = 0.0

    diferencia_precio = abs(movil1.precio - movil2.precio)
    diferencia_bateria = abs(movil1.bateria - movil2.bateria)
    diferencia_puntuacion = abs(movil1.puntuacion - movil2.puntuacion)

    peso_precio = 0.5
    peso_bateria = 0.3
    peso_puntuacion = 0.2

    similitud = (
        peso_precio * (1 - diferencia_precio) +
        peso_bateria * (1 - diferencia_bateria) +
        peso_puntuacion * (1 - diferencia_puntuacion)
    )

    return similitud

def calcular_recomendaciones(lista_favoritos, lista_no_favoritos):
    recomendaciones = []

    for movil_no_favorito in lista_no_favoritos:
        similitud_total = 0.0
        conteo_caracteristicas = 0

        for movil_favorito in lista_favoritos:
            similitud = calcular_similitud(movil_no_favorito, movil_favorito)
            similitud_total += similitud
            conteo_caracteristicas += 1

        similitud_promedio = similitud_total / conteo_caracteristicas

        recomendaciones.append({
            'movil': movil_no_favorito,
            'similitud': similitud_promedio
        })

    recomendaciones = sorted(recomendaciones, key=lambda x: x['similitud'], reverse=True)

    return recomendaciones

@login_required
def toggle_favorito(request, movil_id):
    movil = get_object_or_404(Movil, id=movil_id)
    user = request.user

    # Actualizar estado de favorito
    favorito, created = Favorito.objects.get_or_create(user=user, movil=movil)
    if created:
        is_favorito = True
    else:
        favorito.delete()
        is_favorito = False

    # Devolver estado de favorito como JSON
    response_data = {
        'is_favorito': is_favorito
    }
    return JsonResponse(response_data)

@login_required
def favoritos(request):
    user = request.user
    favoritos = Favorito.objects.filter(user=user).select_related('movil')
    moviles_favoritos = [favorito.movil for favorito in favoritos]
    return render(request, 'favoritos.html', {'moviles': moviles_favoritos})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("inicio")

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("carga")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request, "login.html",{"login_form":form})

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("login")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = NewUserForm()
    return render(request, "register.html", {"register_form": form})

def carga(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_moviles = populateDB()
            mensaje="Se han almacenado: " + str(num_moviles) +" moviles" 
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

def inicio(request):
    num_moviles=Movil.objects.all().count()
    return render(request,'inicio.html', {'num_moviles':num_moviles})

def lista_moviles(request):
    moviles=Movil.objects.all()
    return render(request,'moviles.html', {'moviles':moviles})

def buscar_porfecha(request):
    formulario = BusquedaPorFechaForm()
    moviles = Movil.objects.all()
    
    if request.method=='POST':
        formulario = BusquedaPorFechaForm(request.POST)

        if formulario.is_valid():
            mes = formulario.cleaned_data['mes']
            año = formulario.cleaned_data['año']

            if mes and not año or año=='N/A':
                moviles = filtrar_mes(moviles, mes)
            elif año and not mes or mes=='N/A':
                moviles = filtrar_año(moviles, año)
            elif mes and año:
                moviles = filtrar_mesaño(moviles, mes, año)

    # Obtener lista de favoritos del usuario
    favoritos = Favorito.objects.filter(user=request.user).values_list('movil', flat=True)
        
    return render(request, 'moviles_fecha.html', {'formulario':formulario, 'moviles':moviles, 'favoritos': favoritos})

def buscar_pormodelo(request):
    formulario = BusquedaPorModeloForm()
    moviles = Movil.objects.all()
    
    if request.method=='POST':
        formulario = BusquedaPorModeloForm(request.POST)

        if formulario.is_valid():
            moviles=Movil.objects.filter(modelo__icontains=formulario.cleaned_data['modelo'])

    # Obtener lista de favoritos del usuario
    favoritos = Favorito.objects.filter(user=request.user).values_list('movil', flat=True)

    return render(request, 'moviles_modelo.html', {'formulario':formulario, 'moviles':moviles, 'favoritos': favoritos})

def buscar_porprecio(request):
    formulario = BusquedaPorPrecioForm()
    moviles = Movil.objects.all()
    
    if request.method=='POST':
        formulario = BusquedaPorPrecioForm(request.POST)

        if formulario.is_valid():
            moviles=Movil.objects.filter(precio__lte=formulario.cleaned_data['precio'])

    # Obtener lista de favoritos del usuario
    favoritos = Favorito.objects.filter(user=request.user).values_list('movil', flat=True)

    return render(request, 'moviles_precio.html', {'formulario':formulario, 'moviles':moviles,'favoritos': favoritos})

def buscar_porpuntuacion(request):
    formulario = BusquedaPorPuntuacionForm()
    moviles = Movil.objects.all()
    
    if request.method=='POST':
        formulario = BusquedaPorPuntuacionForm(request.POST)

        if formulario.is_valid():
            moviles=Movil.objects.filter(puntuacion__gte=formulario.cleaned_data['puntuacion'])

    # Obtener lista de favoritos del usuario
    favoritos = Favorito.objects.filter(user=request.user).values_list('movil', flat=True)

    return render(request, 'moviles_puntuacion.html', {'formulario':formulario, 'moviles':moviles, 'favoritos': favoritos})

def buscar_porcapacidad(request):
    formulario = BusquedaPorCapacidadForm()
    moviles = Movil.objects.all()

    if request.method=='POST':
        formulario = BusquedaPorCapacidadForm(request.POST)

        if formulario.is_valid():
            rom = formulario.cleaned_data['rom']
            ram = formulario.cleaned_data['ram']
            
            
            if rom and not ram or ram=='N/A':
              moviles=buscar_por_rom(moviles, rom)
            elif ram and not rom or rom=='N/A':
               moviles=buscar_por_ram(moviles, ram)
            elif rom and ram:
                moviles=buscar_por_romram(moviles,rom, ram)

    # Obtener lista de favoritos del usuario
    favoritos = Favorito.objects.filter(user=request.user).values_list('movil', flat=True)

    return render(request, 'moviles_capacidad.html', {'formulario': formulario, 'moviles': moviles, 'favoritos': favoritos})

def buscar_porbateria(request):
    formulario = BusquedaPorBateriaForm()
    moviles = Movil.objects.all()
    
    if request.method=='POST':
        formulario = BusquedaPorBateriaForm(request.POST)

        if formulario.is_valid():
            moviles=Movil.objects.filter(bateria__gte=formulario.cleaned_data['bateria'])

    # Obtener lista de favoritos del usuario
    favoritos = Favorito.objects.filter(user=request.user).values_list('movil', flat=True)

    return render(request, 'moviles_bateria.html', {'formulario':formulario, 'moviles':moviles,'favoritos': favoritos})

def buscar_por_rom(moviles, rom):
    resultados = []
    for movil in moviles:
        if int(rom) in movil.rom:
            resultados.append(movil)
    return resultados

def buscar_por_ram(moviles, ram):
    resultados = []
    for movil in moviles:
        if int(ram) in movil.ram:
            resultados.append(movil)
    return resultados

def buscar_por_romram(moviles, rom,ram):
    resultados = []
    for movil in moviles:
        if int(rom) in movil.rom and int(ram) in movil.ram: 
            resultados.append(movil)
    return resultados


def filtrar_mes(mobiles, month):
    filtered_mobiles = []
    for mobile in mobiles:
        date_str = mobile.fecha
        date_parts = date_str.split()
        if len(date_parts) == 2:
            mobile_month = date_parts[0]
            mobile_year = date_parts[1]
            if mobile_month.lower() == month.lower():
                filtered_mobiles.append(mobile)
    return filtered_mobiles

def filtrar_año(mobiles, year):
    filtered_mobiles = []
    for mobile in mobiles:
        date_str = mobile.fecha
        date_parts = date_str.split()
        if len(date_parts) == 2:
            mobile_year = date_parts[1]
            if mobile_year == year:
                filtered_mobiles.append(mobile)
    return filtered_mobiles

def filtrar_mesaño(mobiles, month, year):
    filtered_mobiles = []
    for mobile in mobiles:
        date_str = mobile.fecha
        date_parts = date_str.split() 
        if len(date_parts) == 2:
            mobile_month = date_parts[0]
            mobile_year = date_parts[1]
            if mobile_month.lower() == month.lower() and mobile_year == year:
                filtered_mobiles.append(mobile)
    return filtered_mobiles

