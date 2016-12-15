# Django imports
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

# Locale imports
from .models import Sobre, Persona, TipoIngreso, Observacion
from .mixins import CustomForm, CustomModelForm, FechasRangoFormMixin
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
        self.persona_cache = None  # crea la persona en caché
        self.persona = kwargs.pop('persona', None)  # intenta obtener una persona de las kwargs
        # asigna la clase del formulario de persona
        self.formulario_crear_persona_class = FormularioCrearPersona

        # llama el __init__ de el padre
        super().__init__(*args, **kwargs)

        # se agrega la clase de input a el radiobutton
        self.fields['diligenciado'].widget.attrs.update({'class': constants.INPUT_CLASS})

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


class FormularioReporteContribuciones(FechasRangoFormMixin):
    """Formulario para el reporte de contribuciones."""

    totalizado = forms.BooleanField(label=_('Toda la congregacion'), required=False)
    persona = forms.ModelChoiceField(
        queryset=Persona.objects.all().only('nombre', 'primer_apellido', 'cedula'),
        label=_('Persona'), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['totalizado'].widget.attrs.update({
            'class': 'flat'
        })

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        persona = cleaned_data.get('persona', None)
        totalizado = cleaned_data.get('totalizado', False)

        if persona is None and totalizado is False:
            self.add_error(
                'persona', _('Debe escoger una persona, o marcar la casilla de totalizado')
            )


class FormularioCrearUsuario(CustomModelForm):
    """Clase para crear usuarios en el sistema."""

    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('Permisos'))
    password_confirmation = forms.CharField(
        max_length=255, label=_('Repita contraseña'), widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = (
            'email', 'password', 'first_name', 'last_name'
        )
        widgets = {
            'password': forms.PasswordInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        password_1 = cleaned_data.get('password', None) or None
        password_2 = cleaned_data.get('password_confirmation', None) or None

        if password_1 is not None and password_2 is not None:
            if password_1 != password_2:
                self.add_error(
                    'password',
                    _('Contraseñas no coinciden, asegurate de que las contraseñas coincidan')
                )

    def save(self, commit=True, *args, **kwargs):
        self.instance.set_password(self.cleaned_data.get('password'))
        self.instance.username = self.instance.email[:30]
        user = super().save(commit=commit, *args, **kwargs)
        user.groups.add(self.cleaned_data.get('grupo'))
        return user


class CambiarContrasenaForm(CustomForm):
    """Formulario para cambiar la contraseña de un usuario."""

    password_1 = forms.CharField(max_length=255, label=_('Contraseña'), widget=forms.PasswordInput)
    password_2 = forms.CharField(max_length=255, label=_('Repita Contraseña'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        password_1 = cleaned_data.get('password_1', None) or None
        password_2 = cleaned_data.get('password_2', None) or None

        if password_1 is not None and password_2 is not None:
            if password_1 != password_2:
                self.add_error(
                    'password_1',
                    _('Contraseñas no coinciden, asegurate de que las contraseñas coincidan')
                )

    def save(self, commit=True):
        # si hay usuario
        if self.user is not None:
            # busca la contraseña ingresada
            password = self.cleaned_data.get('password_1')
            # setea la contraseña
            self.user.set_password(password)
            if commit:
                # guarda el usuario
                self.user.save()
                # autentifica el usuario, y retorna el usuario autenticado
                return authenticate(email=self.user.email, password=password)
            # retorna el usuario
            return self.user
        else:
            # levanta una excepcion
            raise NotImplementedError(_('Usuario no fue proveido'))
