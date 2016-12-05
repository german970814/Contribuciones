# Django imports
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import format_html_join
from django.shortcuts import redirect

# Locale imports
from . import constants


class CustomModel(object):
    """Custom class for models instances."""

    def to_json(self, *args):
        """Retorna los datos de la persona en formato JSON."""

        # se buscan los argumentos, o el parametro de json_fields
        fields = args or getattr(self, 'json_fields', None)

        # si no hay fields retorna la excepcion
        if fields is None:
            return NotImplementedError(
                _('No se ha definido método .to_json para la clase %s' % self.__class__.__name__)
            )

        # crea el diccionario
        JSON = {}
        for field in fields:
            # si los campos no estan en self.__dir__()
            if field not in self.__dir__():  # self.__dict__
                # levanta la excepcion
                return ValueError('Field "%s" not found in "%s"' % (field, self.__class__.__name__))
            # agrega el campo en mayúscula
            JSON[field] = getattr(self, field).__str__().upper()
        # retorna el diccionario
        return JSON


class CustomErrorList(ErrorList):
    """Clase para hacer los errores de los formularios."""

    def __str__(self):
        # retorna en el string la nueva funcion
        return self.as_material()

    def as_material(self):
        # se define la funcion
        VOID = ''
        # si no hay datos, retorna vacio
        if not self.data:
            return VOID

        # de lo contrario retorna el error
        return format_html_join(
            VOID,
            '<li class="parsley-required">{}</li>',
            ((force_text(e), ) for e in self)
        )


class FormMixin(object):
    """Clase Mixin para trabajar con los formularios"""

    # agrega la clase general de css, definida en las constantes
    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        # agrega la clase de error a todos los formularios
        super().__init__(error_class=CustomErrorList, *args, **kwargs)
        for field in self.fields:
            # agrega a todos los campos el placeholder con el label, y la clase
            if hasattr(self.fields[field], 'choices'):
                self.fields[field].widget.attrs.update({
                    'class': constants.SELECT_CLASS,
                    'placeholder': self.fields[field].label,
                    'tabindex': '-1'
                })
            else:
                self.fields[field].widget.attrs.update({
                    'class': constants.INPUT_CLASS,
                    'placeholder': self.fields[field].label
                })

    def add_class_error_to_input(self):
        """Agrega una clase de error de css al input."""
        for field in self.fields:
            if getattr(self, '_errors', None) is not None and field in self._errors:
                # si la clase está en los errores, le asigan la clase al input
                if hasattr(self.fields[field], 'choices'):
                    self.fields[field].widget.attrs.update({
                        'class': constants.CSS_ERROR_CLASS + ' ' + constants.SELECT_CLASS
                    })
                else:
                    self.fields[field].widget.attrs.update({
                        'class': constants.CSS_ERROR_CLASS + ' ' + constants.INPUT_CLASS
                    })

    def is_valid(self, *args, **kwargs):
        # se sobreescribe el metodo is_valid
        valid = super().is_valid(*args, **kwargs)

        # si no esta valido
        if not valid:
            # llama a la funcion para agrega errores al input
            self.add_class_error_to_input()
        # retorna el valido
        return valid


class CustomModelForm(FormMixin, forms.ModelForm):
    """Clase de base para trabajar con modelforms."""
    pass


class CustomForm(FormMixin, forms.Form):
    """Clase de base para trabajar con forms."""
    pass


class FechasRangoFormMixin(CustomForm):
    """Clase de base para trabajar un formulario con fecha inicial y fecha final."""

    fecha_inicial = forms.DateField(label=_('Fecha Inicial'))
    fecha_final = forms.DateField(label=_('Fecha Final'))

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        fecha_inicial = cleaned_data.get('fecha_inicial', None)
        fecha_final = cleaned_data.get('fecha_final', None)

        if fecha_final is not None and fecha_inicial is not None:
            # se valida el campo
            if fecha_inicial > fecha_final:
                self.add_error(
                    'fecha_inicial', _('Fecha inicial no puede ser mayor que la Fecha final')
                )

        return cleaned_data


class CustomMixinView(object):
    """Mixin para las vistas basadas en clases"""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # si existe el grupo requerido
        if getattr(self, 'group_required', None) is not None:
            # saca los grupos
            grupos = self.group_required
            # saca el usuario
            user = request.user
            # si el usuario no tiene los grupos, y ademas no es superusuario
            if not user.groups.filter(name__in=grupos).exists() and not user.is_staff and not user.is_superuser:
                # lo redirecciona al login
                return redirect(settings.LOGIN_URL)
        # retorna el metodo dispatch
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # agrega el mensaje de success al formulario
        messages.success(
            self.request,
            _(constants.SUCCESS_FORM)
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        # agrega el mensaje de error al formulario
        messages.error(
            self.request,
            _(constants.ERROR_FORM)
        )
        return super().form_invalid(form)

    def get_success_url(self):
        # sobreescribe el metodo get_success_url para las instancias de UpdateView
        if isinstance(self.success_url, str):
            # si es un string, retorna la url del string, mas el id del objeto
            return reverse_lazy(self.success_url, args=(self.object.id, ))
        # de lo contrario, retorna la url
        return super().get_success_url()
