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

    # crea los campos que seran usados
    email = forms.EmailField(label=_('Email'))
    password = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        # crea un usuario en cache que luego será devuelto
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        # obtiene los valores del formulario
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # autentifica el usuario, con el backend de autentificacion por email
        self.user_cache = authenticate(email=email, password=password)

        # verifica, para retornar los errores, en caso de haberlos
        if self.user_cache is None:
            raise forms.ValidationError(_('Usuario no encontrado'))
        elif self.user_cache.is_active is None:
            raise forms.ValidationError(_('Usuario Inactivo'))

        # retorna los datos
        return cleaned_data

    def get_user(self):
        """Retorna el usuario creado en memoria por el formulario."""
        # retorna el usuario
        return self.user_cache


class FormularioCrearSobre(CustomModelForm):
    """Formulario para la creacion de sobres."""

    # crea las opciones de diligenciado
    DILIGENCIADO_CHOICES = (
        (True, _('Si')),
        (False, _('No')),
    )

    # crea un campo para guardar el id de la persona que hizo un sobre, para recuperarlo facilmente
    hidden = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)
    diligenciado = forms.TypedChoiceField(
        coerce=lambda x: x == 'True', choices=DILIGENCIADO_CHOICES,
        widget=forms.RadioSelect
    )  # se agrega le widget a el campo diligenciado

    class Meta:
        model = Sobre
        fields = (
            'fecha', 'diligenciado',
            'observaciones', 'valor',
            'tipo_ingreso', 'forma_pago',
        )  # se definen los campos iniciales del formulario

    def __init__(self, *args, **kwargs):
        self.persona_cache = None  # crea la persona en chaché
        self.persona = kwargs.pop('persona', None)  # intenta obtener una persona de las kwargs
        # asigna la clase del formulario de persona
        self.formulario_crear_persona_class = FormularioCrearPersona

        # llama el __init__ de el padre
        super().__init__(*args, **kwargs)

        if self.persona is not None:  # si encuentra la persona de las kwargs
            self.initial.update(self.persona.to_json())  # actualiza el formulario inicial, con el json
            self.initial['hidden'] = self.persona.id.__str__()  # actualiza el campo hidden con el id

        for name, field in self.formulario_crear_persona_class().fields.items():  # recorre los campos
            # agrega los campos del formulario crear persona a el formulario actual
            self.fields[name] = field
            self.fields[name].required = False  # no los requiere

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        # de obtienen las posibles opciones
        diligenciado = cleaned_data.get('diligenciado', False)
        observaciones = cleaned_data.get('observaciones', None)
        hidden = cleaned_data.get('hidden', None) or None

        # se agregan validaciones
        if not diligenciado and observaciones is None:
            self.add_error(
                'observaciones',
                _('Este campo es obligatorio')
            )

        try:
            # intenta sacar la persona por el campo invisible
            self.persona_cache = Persona.objects.get(id=hidden)
        except (Persona.DoesNotExist, ValueError):
            # la obtiene a partir del formulario
            self.persona_cache = self._get_persona()

        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        # intenta sacar una persona
        persona = self.get_persona()
        if persona is not None:  # si encuentra la persona
            self.instance.persona = persona  # le asigna a la instancia, una persona
        return super().save(commit=commit, *args, **kwargs)

    def _get_persona(self):
        """wrapper que retorna la persona en cache."""
        # si no encuentra la persona en el campo hidden y no hay nombre
        if self.persona_cache is None and self.cleaned_data.get('nombre') == '':
            # no hay persona
            return None
        elif not isinstance(self.persona_cache, Persona):  # si es None (basicamente)
            # crea un formulario de crear persona, le pasa los datos limpios
            form = self.formulario_crear_persona_class(data=self.cleaned_data)  # self.data
            if not form.is_valid():
                # si entra aca, se supone que el formulario actual de la clase no tiene errores
                if self.errors:
                    # si hay errores, actualiza los errores con los del formulario nuevo
                    self._errors.update(form.errors)
                else:
                    # asigna los errores de un formulario a otro
                    self._errors = form.errors
            else:
                # crea la persona
                self.persona_cache = form.save()
        # retorna la persona
        return self.persona_cache

    def get_persona(self):
        """Retorna la persona en cache."""
        # retorna la funcion para obtener la persona
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
