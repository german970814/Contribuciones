# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

# Locale imports
from .constants import MAIN, ERROR_FORM
from .models import Sobre, Persona, Observacion, TipoIngreso
from .mixins import CustomMixinView
from .forms import (
    FormularioLogearUsuario, FormularioCrearSobre, FormularioCrearPersona,
    FormularioCrearTipoIngreso, FormularioCrearObservacion
)


def login_view(request):
    """Vista de login."""

    # primero verifica si existe un usuario
    if request.user.is_authenticated():
        # de ser asi, lo redirecciona a /home/
        return redirect('home')

    # busca la pagina siguiente en caso de que sea por redireccion
    next_page = request.GET.get('next', None)

    if request.method == 'POST':
        # se crea el formulario con los datos del POST
        form = FormularioLogearUsuario(data=request.POST)

        if form.is_valid():
            # se logea el usuario apra el request, en caso de ser valido
            login(request, form.get_user())

            # si hay una pagina siguiente, se redirecciona a ella
            if next_page is not None:
                return redirect(next_page)
            # de lo contrario va a /home/
            return redirect('main:home')
        else:
            # lanza el error
            messages.error(
                request,
                _(ERROR_FORM)
            )
    else:
        # crea el formulario en GET
        form = FormularioLogearUsuario()

    return render(request, MAIN.format('login.html'), {'form': form})


@login_required
def home_view(request):
    """Vista que retorna el inicio."""

    return render(request, MAIN.format('home.html'), {})


def logout_view(request):
    """Vista para el logout."""
    logout(request)
    return redirect('main:login')


class SobreCreate(CustomMixinView, CreateView):
    """Clase para crear los sobres"""

    model = Sobre
    form_class = FormularioCrearSobre
    success_url = reverse_lazy('main:crear_sobre')
    template_name = MAIN.format('crear_sobre.html')

    def render_to_response(self, context, **response_kwargs):
        context['personas'] = Persona.objects.all()
        return super().render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.get_persona() is not None:
            # nueva_persona = Persona.objects.create(**form.cleaned_data)
            # self.object = form.save()
            # self.object.persona = nueva_persona
            persona = form.get_persona()
            self.object.persona = persona
            self.object.save()
        return response


class SobreUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar sobres."""

    model = Sobre
    form_class = FormularioCrearSobre
    success_url = reverse_lazy('main:editar_sobre')
    template_name = MAIN.format('crear_sobre.html')


class PersonaCreate(CustomMixinView, CreateView):
    """Clase para crear los personas"""

    model = Persona
    form_class = FormularioCrearPersona
    success_url = reverse_lazy('main:crear_persona')
    template_name = MAIN.format('crear_persona.html')


class PersonaUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar personas."""

    model = Persona
    form_class = FormularioCrearPersona
    success_url = reverse_lazy('main:editar_persona')
    template_name = MAIN.format('crear_persona.html')


class TipoIngresoCreate(CustomMixinView, CreateView):
    """Clase para crear los tipos de ingreso"""

    model = TipoIngreso
    form_class = FormularioCrearTipoIngreso
    success_url = reverse_lazy('main:crear_tipo_ingreso')
    template_name = MAIN.format('crear_tipo_ingreso.html')


class TipoIngresoUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar tipos de ingreso."""

    model = TipoIngreso
    form_class = FormularioCrearTipoIngreso
    success_url = reverse_lazy('main:editar_tipo_ingreso')
    template_name = MAIN.format('crear_tipo_ingreso.html')


class ObservacionCreate(CustomMixinView, CreateView):
    """Clase para crear los observaciones"""

    model = Observacion
    form_class = FormularioCrearObservacion
    success_url = reverse_lazy('main:crear_observacion')
    template_name = MAIN.format('crear_observacion.html')


class ObservacionUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar observaciones."""

    model = Observacion
    form_class = FormularioCrearObservacion
    success_url = reverse_lazy('main:editar_observacion')
    template_name = MAIN.format('crear_observacion.html')
