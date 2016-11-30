# Django imports
from django import forms
from django.utils.translation import ugetext_lazy as _

# Locale imports
from . import constants
from .models import Sobre, Persona, TipoIngreso, Observacion


class CustomModelForm(forms.ModelForm):
    """Clase de base para trabajar con forms."""

    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': constants.INPUT_CLASS
            })


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
