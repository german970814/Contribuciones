# Django imports
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import format_html_join

# Locale imports
from . import constants


class CustomModel(object):
    """Custom class for models instances."""

    def to_json(self, *args, **kwargs):
        """Retorna los datos de la persona en formato JSON."""

        fields = args or self.json_fields
        _fields = kwargs.get('fields', None)

        if _fields:
            fields = _fields

        if fields is None:
            return NotImplementedError(
                _('No se ha definido método .to_json para la clase %s' % self.__class__.__name__)
            )

        JSON = {}
        for field in fields:
            if field not in self.__dir__():
                return ValueError('Field "%s" not found in "%s"' % (field, self.__class__.__name__))
            JSON[field] = getattr(self, field)
        return JSON

class CustomErrorList(ErrorList):
    """Clase para hacer los errores de los formularios."""

    def __str__(self):
        return self.as_material()

    def as_material(self):
        VOID = ''
        if not self.data:
            return VOID

        return format_html_join(
            VOID,
            '<li class="parsley-required">{}</li>',
            ((force_text(e), ) for e in self)
        )

class FormMixin(object):
    """Clase Mixin para trabajar con los formularios"""

    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        super().__init__(error_class=CustomErrorList, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': constants.INPUT_CLASS,
                'placeholder': self.fields[field].label
            })

    def add_class_error_to_input(self):
        """Agrega una clase de error de css al input."""
        for field in self.fields:
            if field in self._errors:
                self.fields[field].widget.attrs.update({
                    'class': constants.CSS_ERROR_CLASS + ' ' + constants.INPUT_CLASS
                })

    def is_valid(self, *args, **kwargs):
        valid = super().is_valid(*args, **kwargs)

        if not valid:
            self.add_class_error_to_input()

        return valid


class CustomModelForm(FormMixin, forms.ModelForm):
    """Clase de base para trabajar con modelforms."""
    pass


class CustomForm(FormMixin, forms.Form):
    """Clase de base para trabajar con forms."""
    pass


class CustomMixinView(object):
    """Mixin para las vistas basadas en clases"""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(
            self.request,
            _('Se ha completado el formulario exitosamente')
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            _(constants.ERROR_FORM)
        )
        return super().form_invalid(form)
