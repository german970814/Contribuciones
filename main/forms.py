# Django imports
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

# Locale imports
from .models import Sobre, Persona, TipoIngreso, Observacion
from .mixins import CustomForm, CustomModelForm
from . import constants


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

    hidden = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)

    DILIGENCIADO_CHOICES = (
        (True, _('Si')),
        (False, _('No')),
    )

    diligenciado = forms.TypedChoiceField(
        coerce=lambda x: x == 'True', choices=DILIGENCIADO_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Sobre
        fields = (
            'fecha', 'diligenciado',
            'observaciones', 'valor',
            'tipo_ingreso', 'forma_pago',
        )

    def __init__(self, *args, **kwargs):
        self.persona_cache = None
        self.persona = kwargs.pop('persona', None)
        super().__init__(*args, **kwargs)
        if self.persona is not None:
            self.initial.update(self.persona.to_json())
            self.initial['hidden'] = self.persona.id.__str__()
        self.formulario_crear_persona_class = FormularioCrearPersona
        for name, field in self.formulario_crear_persona_class().fields.items():
            self.fields[name] = field
            self.fields[name].required = False

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        diligenciado = cleaned_data.get('diligenciado', False)
        observaciones = cleaned_data.get('observaciones', None)
        hidden = cleaned_data.get('hidden', None) or None

        if not diligenciado and observaciones is None:
            self.add_error(
                'observaciones',
                _('Este campo es obligatorio')
            )

        try:
            self.persona_cache = Persona.objects.get(id=hidden)
        except (Persona.DoesNotExist, ValueError):
            self.persona_cache = self._get_persona()

        return cleaned_data

    def _get_persona(self):
        """wrapper que retorna la persona en cache."""
        if self.persona_cache is None and self.cleaned_data.get('nombre') == '':
            return None
        elif not isinstance(self.persona_cache, Persona):
            form = self.formulario_crear_persona_class(data=self.cleaned_data)  # self.data
            if not form.is_valid():
                # si entra aca, se supone que el formulario actual de la clase no tiene errores
                if self.errors:
                    self._errors.update(form.errors)
                else:
                    self._errors = form.errors
            else:
                self.persona_cache = form.save()
        return self.persona_cache

    def get_persona(self):
        """Retorna la persona en cache."""
        return self._get_persona()


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
            'texto',
        )
