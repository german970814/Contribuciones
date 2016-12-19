# Django imports
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, FormView
from django.utils import timezone

# Locale imports
from .constants import MAIN, ERROR_FORM, INFO_FORM, DATE_FORMAT
from .decorators import group_required
from .mixins import CustomMixinView, FechasRangoFormMixin
from .models import Sobre, Persona, Observacion, TipoIngreso
from .forms import (
    FormularioLogearUsuario, FormularioCrearSobre, FormularioCrearPersona,
    FormularioCrearTipoIngreso, FormularioCrearObservacion,
    FormularioReporteContribuciones, FormularioCrearUsuario,
    CambiarContrasenaForm
)

# Python imports
from collections import OrderedDict
import datetime

import calendar
from django.utils.translation import activate
from django.template.defaultfilters import date as date_name
import json

def login_view(request):
    """Vista de login."""

    # busca la pagina siguiente en caso de que sea por redireccion
    next_page = request.GET.get('next', None)

    # luego verifica si existe un usuario
    if request.user.is_authenticated():
        # si hay next page
        if next_page is not None:
            # redirecciona a next_page
            return redirect(next_page)
        # de no ser asi, lo redirecciona a /home/
        return redirect('main:home')

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

    user = request.user
    data = {}

    if group_required('administrador')(user):
        _hoy = timezone.now().date()
        hoy = _hoy
        inicio_mes = datetime.date(year=hoy.year, month=hoy.month, day=1)

        hoy += datetime.timedelta(days=1)

        rango_mes = (inicio_mes, hoy)

        sobres = Sobre.objects.filter(
            fecha__range=rango_mes
        )

        total = sobres.aggregate(total=Sum('valor'))['total'] or 0
        data['total_mes'] = total
        data['numero_sobres_mes'] = sobres.count()
        data['total_sin_diligenciar'] = sobres.filter(diligenciado=False).count()

        totales = {}

        _tipos = TipoIngreso.objects.all().values_list('nombre', flat=True)

        start = hoy.month - 5
        end = hoy.month + 1
        year = hoy.year

        if start < 5:
            start = 12 - 5 + hoy.month
        if end < start:
            end = 12 + end

        for month in range(start, end):
            if end >= 14:
                if month >= 13:
                    year = hoy.year
                else:
                    year = hoy.year - 1

            if month > 12:
                month -= 12

            sobres = Sobre.objects.filter(
                fecha__month=month, fecha__year=year
            ).values('tipo_ingreso__nombre').annotate(total=Sum('valor'))

            mes = date_name(datetime.date(year=year, month=month, day=1), 'F')

            tipos = [x for x in _tipos]

            for tipo in sobres:
                if tipo['tipo_ingreso__nombre'] not in totales:
                    totales[tipo['tipo_ingreso__nombre']] = OrderedDict(
                        {mes: tipo['total']}
                    )
                else:
                    totales[tipo['tipo_ingreso__nombre']][mes] = tipo['total']

                tipos.remove(tipo['tipo_ingreso__nombre'])

            for tipo in tipos:
                totales[tipo][mes] = 0

        data['totales'] = json.dumps(totales)

    return render(request, MAIN.format('home.html'), data)  # retorna al home


def logout_view(request):
    """Vista para el logout."""
    logout(request)  # deslogea de la sesion
    return redirect('main:login')  # redirecciona al login


@group_required('administrador')
def listar_sobres(request):
    """Vista para listar los sobres, de acuerdo a un rango de fecha."""

    data = {}

    if request.method == 'POST':
        form = FechasRangoFormMixin(data=request.POST)

        if form.is_valid():
            fecha_inicial = form.cleaned_data.get('fecha_inicial')
            fecha_final = form.cleaned_data.get('fecha_final') + datetime.timedelta(days=1)

            sobres = Sobre.objects.filter(
                fecha__range=(fecha_inicial, fecha_final)
            ).select_related('persona', 'tipo_ingreso', 'observaciones').only(
                'fecha', 'diligenciado', 'valor', 'forma_pago', 'persona', 'tipo_ingreso',
                'observaciones'
            )

            sobres = sobres.iterator()
            data['sobre_list'] = sobres

            messages.success(
                request,
                _(INFO_FORM)
            )
        else:
            messages.error(
                request,
                _(ERROR_FORM)
            )
    else:
        form = FechasRangoFormMixin()

    data['form'] = form

    return render(request, MAIN.format('listar_sobres.html'), data)


@group_required('consultas', 'administrador')
def reporte_contribuciones(request):
    """Reporte de personas totalizada por contribuciones"""

    data = {}  # se crean los datos que seran enviados al template

    if request.method == 'POST':
        form = FormularioReporteContribuciones(data=request.POST)

        if form.is_valid():
            # si el formulario es valido, se sacan los campos necesarios
            totalizado = form.cleaned_data.get('totalizado')
            fecha_inicial = form.cleaned_data.get('fecha_inicial')
            fecha_final = form.cleaned_data.get('fecha_final') + datetime.timedelta(days=1)

            # se crea un diccionario para pasar como argumentos de llave valor
            queryset_kwargs = {
                'fecha__range': (fecha_inicial, fecha_final)
            }

            if not totalizado:
                # si no hay totalizado, busca la persona del formulario
                persona = form.cleaned_data.get('persona')
                # lo añade a los argumentos
                queryset_kwargs['persona'] = persona

            # se crea la tabla, de forma ordenada, para que sea a menera cola
            tabla = OrderedDict({'TOTAL': {'total': 0}})

            # se recorren todos los tipos de ingresos
            queryset = TipoIngreso.objects.prefetch_related('sobres').all()
            for tipo in queryset.iterator():
                total = 0
                # se crea una variable temporal, para guardar los totales por tipo de ingreso
                _totales = {'total': 0}  # se inicializa un total a 0

                # se filtra con los argumentos de llave valor, creados antes
                sobres = tipo.sobres.filter(**queryset_kwargs)

                # se recorren las formas de pago que tienen los sobres
                for forma in Sobre.FORMAS_PAGO:
                    # forma = ('FO', 'FORMA DE PAGO'), representacion de forma de pago
                    _sobres = sobres.filter(forma_pago=forma[0])  # se filtra por el primer valor de la tupla
                    # se crea una variable temporal, para guardar los totales por forma de pago
                    totales = _sobres.aggregate(
                        **{forma[1]: Sum('valor')}  # seria la forma de pago con la suma de los valores
                    )

                    # si no hay valores, lo asigna a 0
                    totales[forma[1]] = totales[forma[1]] or 0
                    # actualiza el total de el diccionario de tipo de ingreso
                    _totales['total'] += totales[forma[1]]
                    _totales.update(totales)

                    # agrega los totales por forma de pago valores a la tabla principal
                    if forma[1] in tabla['TOTAL']:
                        tabla['TOTAL'][forma[1]] += totales[forma[1]]
                    else:
                        tabla['TOTAL'][forma[1]] = totales[forma[1]]

                # agrega los totales por tipo de ingreso a la tabla
                tabla['TOTAL']['total'] += _totales['total']

                # agrega los datos a la tabla
                tabla.update({str(tipo): _totales})
            # se vuelve a ordenar la tabla de manera inversa para que el total salga de ultimo
            data['tabla'] = OrderedDict(reversed(list(tabla.items())))
            # se muestra el mensaje
            messages.success(
                request,
                _(INFO_FORM)
            )

        else:
            # se muestra el mensaje de error
            messages.error(
                request,
                _(ERROR_FORM)
            )
    else:
        form = FormularioReporteContribuciones()

    # se envia el formulario de vuelta
    data['form'] = form

    return render(request, MAIN.format('reporte_contribuciones.html'), data)


class SobreCreate(CustomMixinView, CreateView):
    """Clase para crear los sobres"""

    model = Sobre
    form_class = FormularioCrearSobre
    success_url = reverse_lazy('main:crear_sobre')
    template_name = MAIN.format('crear_sobre.html')
    group_required = ('administrador', 'digitador', )

    def render_to_response(self, context, **response_kwargs):
        persona_queryset = Persona.objects.all().only('nombre', 'primer_apellido', 'cedula')
        context['personas'] = persona_queryset.iterator()  # agrega el queryset de personas
        return super().render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        self._valid_form = form  # se guarda el formulario valido
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        # si existe el formulario valido
        if hasattr(self, '_valid_form'):
            form = self._valid_form
            # obtiene del formulario la fecha
            date = form.cleaned_data.get('fecha')
            # lo convierte a string
            date = date.strftime(DATE_FORMAT)
            # lo inserta en la url
            return url + '?{}={}'.format('date', date)
        return url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  # se sacan las kwargs
        get_data = self.request.GET  # se obtienen los datos del GET
        if 'date' in get_data:  # se verifica que date este en el GET
            date = get_data['date']  # obtiene la fecha
            kwargs['initial'] = {'fecha': date}  # se crea el diccionario inicial
        # retorna las llaves
        return kwargs


class SobreUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar sobres."""

    model = Sobre
    form_class = FormularioCrearSobre
    success_url = 'main:editar_sobre'
    template_name = MAIN.format('crear_sobre.html')
    group_required = ('administrador', )

    def render_to_response(self, context, **response_kwargs):
        persona_queryset = Persona.objects.all().only('nombre', 'primer_apellido', 'cedula')
        context['personas'] = persona_queryset.iterator()  # agrega el queryset de personas
        return super().render_to_response(context, **response_kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  # obtiene las llaves/valor de el formulario
        if self.object.persona is not None:
            kwargs.update({'persona': self.object.persona})  # agrega una persona
        return kwargs  # retorna el diccionario


class SobreList(CustomMixinView, ListView):  # actualmente sin uso
    """Vista para listar los sobres ingresados."""

    model = Sobre
    template_name = MAIN.format('listar_sobres.html')
    group_required = ('administrador', )


class PersonaCreate(CustomMixinView, CreateView):
    """Clase para crear los personas"""

    model = Persona
    form_class = FormularioCrearPersona
    success_url = reverse_lazy('main:crear_persona')
    template_name = MAIN.format('crear_persona.html')
    group_required = ('administrador', )


class PersonaUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar personas."""

    model = Persona
    form_class = FormularioCrearPersona
    success_url = 'main:editar_persona'
    template_name = MAIN.format('crear_persona.html')
    group_required = ('administrador', )


class PersonaList(CustomMixinView, ListView):
    """Vista para listar las personas ingresadas."""

    model = Persona
    template_name = MAIN.format('listar_personas.html')
    group_required = ('administrador', )


class TipoIngresoCreate(CustomMixinView, CreateView):
    """Clase para crear los tipos de ingreso"""

    model = TipoIngreso
    form_class = FormularioCrearTipoIngreso
    success_url = reverse_lazy('main:crear_tipo_ingreso')
    template_name = MAIN.format('crear_tipo_ingreso.html')
    group_required = ('administrador', )


class TipoIngresoUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar tipos de ingreso."""

    model = TipoIngreso
    form_class = FormularioCrearTipoIngreso
    success_url = 'main:editar_tipo_ingreso'
    template_name = MAIN.format('crear_tipo_ingreso.html')
    group_required = ('administrador', )


class TipoIngresoList(CustomMixinView, ListView):
    """Vista para listar los tipos de ingreso ingresados."""

    model = TipoIngreso
    template_name = MAIN.format('listar_tipo_ingresos.html')
    group_required = ('administrador', )


class ObservacionCreate(CustomMixinView, CreateView):
    """Clase para crear los observaciones"""

    model = Observacion
    form_class = FormularioCrearObservacion
    success_url = reverse_lazy('main:crear_observacion')
    template_name = MAIN.format('crear_observacion.html')
    group_required = ('administrador', )


class ObservacionUpdate(CustomMixinView, UpdateView):
    """Clase para actualizar observaciones."""

    model = Observacion
    form_class = FormularioCrearObservacion
    success_url = 'main:editar_observacion'
    template_name = MAIN.format('crear_observacion.html')
    group_required = ('administrador', )


class ObservacionList(CustomMixinView, ListView):
    """Vista para listar las observaciones ingresadas."""

    model = Observacion
    template_name = MAIN.format('listar_observaciones.html')
    group_required = ('administrador', )


class UserCreate(CustomMixinView, CreateView):
    """Clase para crear usuarios."""

    model = get_user_model()
    form_class = FormularioCrearUsuario
    success_url = reverse_lazy('main:crear_usuario')
    template_name = MAIN.format('crear_usuario.html')
    group_required = ('administrador', )


class UserList(CustomMixinView, ListView):
    """Clase para listar usuarios."""

    model = get_user_model()
    template_name = MAIN.format('listar_usuarios.html')
    group_required = ('administrador', )

    def get_queryset(self):
        return super().get_queryset().exclude(is_staff=True).exclude(is_superuser=True)


class SetPasswordView(CustomMixinView, FormView):
    """Clase para cambiar la contraseña."""

    template_name = MAIN.format('cambiar_contraseña.html')
    form_class = CambiarContrasenaForm
    success_url = reverse_lazy('main:cambiar_contraseña')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  # obtiene las llaves/valor de el formulario
        kwargs.update({'usuario': self.request.user})  # agrega un usuario
        return kwargs  # retorna el diccionario

    def form_valid(self, form):
        user = form.save()  # se obtiene el usuario del formulario
        login(self.request, user)  # se logea el usuario
        return super().form_valid(form)
