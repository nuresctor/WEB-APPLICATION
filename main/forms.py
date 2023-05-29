#encoding:utf-8
from django import forms
from main.models import Movil, User
from django.contrib.auth.forms import UserCreationForm

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class BusquedaPorFechaForm(forms.Form):
    meses = [('N/A','N/A'),('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'), ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'), ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'), ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre', 'Diciembre')]
    años = [('N/A','N/A'),(2020, '2020'), (2021, '2021'), (2022, '2022'), (2023, '2023')]
    mes = forms.ChoiceField(label="Month", choices=meses, initial=meses[0][0])
    año= forms.ChoiceField(label="Year", choices=años, initial=años[0][0])

class BusquedaPorModeloForm(forms.Form):
    modelo=forms.CharField(label="Model", widget=forms.TextInput())

class BusquedaPorPrecioForm(forms.Form):
    precio=forms.FloatField(label="Maximum price", widget=forms.NumberInput(attrs={'style': 'width: 50px;'}))

class BusquedaPorPuntuacionForm(forms.Form):
    puntuacion=forms.FloatField(label="Minimum score", widget=forms.NumberInput(attrs={'style': 'width: 50px;'}))

class BusquedaPorBateriaForm(forms.Form):
    bateria=forms.FloatField(label="Minimum battery", widget=forms.NumberInput(attrs={'style': 'width: 50px;'}))

class BusquedaPorCapacidadForm(forms.Form):
    rams = [('N/A','N/A'),
        (4, '4 GB'),
        (6, '6 GB'),
        (8, '8 GB'),
        (12, '12 GB'),
        (16, '16 GB'),]
    roms=[('N/A','N/A'),
        (16, '16 GB'),
        (32, '32 GB'),
        (64, '64 GB'),
        (128, '128 GB'),
        (256, '256 GB'),
        (512, '512 GB'),]
    rom = forms.ChoiceField(label='ROM',choices=roms, initial=roms[0][0])
    ram = forms.ChoiceField(label='RAM',choices=rams, initial=rams[0][0])