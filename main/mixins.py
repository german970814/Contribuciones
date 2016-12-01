# Django imports
from django import forms
from django.contrib import messajes
from django.utils.translation import ugetext_lazy as _

from . import constants


class CustomModelForm(forms.ModelForm):
    """Clase de base para trabajar con modelforms."""

    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': constants.INPUT_CLASS
            })


class CustomForm(forms.Form):
    """Clase de base para trabajar con forms."""

    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': constants.INPUT_CLASS
            })

class CustomMixinView(object):
    """Mixin para las vistas basadas en clases"""

    def form_valid(self, form):
        messages.success(
            self.request,
            _('Se ha completado el formulario exitosamente')
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            _(ERROR_FORM)
        )
