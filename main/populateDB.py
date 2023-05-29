#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import re, os, shutil, locale
from datetime import datetime
import json
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from main.models import Movil

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

f = urllib.request.urlopen("https://www.movilzona.es/moviles/oppo/")
s = BeautifulSoup(f, "lxml")

def populateDB():
    populate_movil()
    
def populate_movil():

    #borramos todas las tablas de la BD
    Movil.objects.all().delete()
    
    link=""
    precio=0.0
    imagen="Sin imagen"
    items = s.find("div",attrs={"class": "reviews-result wrap-content"})
    
    for item in items:
        if len(item.findAll("a")) == 2:
            link = item.findAll("a")[1]['href']
            precio = item.find("span",class_="price").text.replace(".","").replace(",",".")
            imagen = item.find_all("img")[1]['src']
        else:
            link = item.findAll("a")[0]['href']
            imagen = item.find_all("img")[0]['src']
            
        extraer_link(link,precio,imagen)

    return Movil.objects.count()
    
def extraer_link(link,precio,imagen):
    
    f = urllib.request.urlopen(link)
    s = BeautifulSoup(f, "lxml")
        
    #FECHA Y MODELO
    texts = [t.text.strip() for t in s.findAll("div",class_="spec-head-data")]
    fecha_string = texts[2]
    modelo = texts[0].upper()+" "+texts[1]
    print("Fecha " + fecha_string)
    print("Modelo " + modelo)
    
    #ROM Y RAM
    almacenamientos = [t.text.strip() for t in s.findAll("div",class_="summary summary-storage")]
    ram = []
    rom = []
    for e in almacenamientos:
        if 'Almacenamiento interno' in e:
            rom = [int(num) for num in re.findall(r'\d+', e)]
            
        if 'Memoria RAM' in e:
            ram = [int(num) for num in re.findall(r'\d+', e)]
  
    roms_json = json.dumps(rom)
    rams_json = json.dumps(ram)
    
    print("ROM" + roms_json)
    print("RAM" + rams_json)
    
    #BATERIA
    baterias = [t.text.strip() for t in s.findAll("div",class_="summary summary-battery")]
    bateria =0
    for e in baterias:
        if 'Capacidad de batería' in e:
            bateria = re.search(r'[1-9]\d*', e).group()
    #print("Bateria " + bateria)
    
    #PUNTUACION
    puntuacion = 0.0
    if s.find("div", class_="global-score"):
        puntuacion_string = s.find("div", class_="global-score").text.strip()
        puntuacion = re.search(r'\d+(\.\d+)?', puntuacion_string).group()
    elif s.find("span", class_="review-points"):
        puntuacion_string = s.find("span", class_="review-points").text.strip()
        puntuacion = re.search(r'\d+(\.\d+)?', puntuacion_string).group()   
    #print("Puntuacion "+puntuacion)
        
    #PRECIO
    #print("Precio "+precio)
    
    #IMAGEN
    print(imagen)

     #almacenamos en la BD
    Movil.objects.create(fecha=fecha_string, modelo=modelo, rom=roms_json, ram=rams_json, bateria=int(bateria), puntuacion=float(puntuacion), precio=float(precio), imagen=imagen)

     

