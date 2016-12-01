# Django imports
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugetext_lazy as _

# Locale imports
from .models import Sobre, Persona, TipoIngreso, Observacion
from .mixins import CustomForm, CustomModelForm


class FormularioLogearUsuario(CustomForm):
    """Formulario para el login de usuarios en el sistema."""

    email = forms.EmailField(label=_('Email'))
    password = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        self.user_cache = authenticate(email=email, password=password)

        if self.user_cache is None:
            raise forms.ValidationError(_('Usuario no encontrado'))
        elif self.user_cache.is_active is None:
            raise forms.ValidationError(_('Usuario Inactivo'))

        return cleaned_data

    def get_user(self):
        """Retorna el usuario creado en memoria por el formulario."""
        return self.user_cache


class FormularioCrearSobre(CustomModelForm):
    """Formulario para la creacion de sobres."""

    class Meta:
        model = Sobre
        fields = (
            'fecha', 'diligenciado',
            'observaciones', 'valor',
            'tipo_ingreso', 'forma_pago',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        diligenciado = cleaned_data.get('diligenciado', False)
        observaciones = cleaned_data.get('observaciones', None)

        if not diligenciado and observaciones is None:
            self.add_error(
                'observaciones',
                _('Este campo es obligatorio')
            )

        return cleaned_data


class FormularioCrearPersona(CustomModelForm):
    """Formulario para crear personas."""

    class Meta:
        model = Persona
        fields = (
            'nombre', 'primer_apellido', 'segundo_apellido',
            'cedula', 'telefono'
        )


class FormularioCrearTipoIngreso(CustomModelForm):
    """Formulario para crear tipos de ingreso."""

    class Meta:
        model = TipoIngreso
        fields = (
            'nombre',
        )

class FormularioCrearObservacion(CustomModelForm):
    """Formulario para crear observaciones."""

    class Meta:
        model = Observacion
        fields = (
            'texto'
        )
