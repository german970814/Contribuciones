# Django imports
from django import forms
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Locale imports
from . import constants


class CustomModelForm(forms.ModelForm):
    """Clase de base para trabajar con modelforms."""

    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': constants.INPUT_CLASS,
                'placeholder': self.fields[field].label
            })


class CustomForm(forms.Form):
    """Clase de base para trabajar con forms."""

    error_css_class = constants.CSS_ERROR_CLASS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': constants.INPUT_CLASS,
                'placeholder': self.fields[field].label
            })

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
            _(ERROR_FORM)
        )
