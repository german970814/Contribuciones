from django import forms
from django.utils.translation import ugettext_lazy as _
from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse

import datetime
from collections import OrderedDict
from io import StringIO

from main.models import Sobre, Observacion, Persona, TipoIngreso
from main.mixins import CustomForm
from main.constants import DATE_FORMAT


__author__ = 'German Alzate'


LOG = []
FILA = 0
TIPOS_INGRESO = {}


class FormularioSubirExcel(CustomForm):
    """Formulario para subir un archivo de excel y migrar sobres."""

    archivo = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(FormularioSubirExcel, self).__init__(*args, **kwargs)
        self.accepts = ['xls', 'xlsx']
        self.fields['archivo'].widget.attrs.update({'class': 'form-control', 'accept': '.' + ', .'.join(self.accepts)})

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        file = cleaned_data.get('archivo', None)
        if file is not None:
            try:
                name, extension = file.name.strip().split('.')
                if extension.lower() not in self.accepts:
                    self.add_error('archivo', _('Formato de archivo no aceptado.'))
            except:
                self.add_error('archivo', _('Formato de archivo inválido.'))
        return cleaned_data


def importar_sobres_excel_view(request):
    """Vista para importar los sobres desde un archivo de excel."""

    if request.method == 'POST':
        form = FormularioSubirExcel(data=request.POST, files=request.FILES)

        if form.is_valid():
            excel = request.FILES['archivo']
            pages = excel.get_book_dict()
            for page in pages:
                first = True
                for row in pages[page]:
                    if not first:
                        excelt_to_python(row)
                    first = False

            # .save_to_database(
            #     model=Sobre, initializer=excelt_to_python,
            #     mapdict=[
            #         'fecha', 'diligenciado', 'tipo_ingreso',
            #         'valor', 'forma_pago', 'persona', 'observaciones'
            #     ]
            # )
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=logs.txt'

            file = StringIO()
            try:
                for line in LOG:
                    file.write(line)
            except:
                print("Se ha interrumpido la inscripcion del archivo.")

            response.write(file.getvalue())
            file.close()
            return response

    else:
        form = FormularioSubirExcel()

    return render(request, 'importar_sobres_excel.html', {'form': form})


def to_python(obj, boolean=True):
    if obj is not None:
        if getattr(str(obj), '__len__', lambda: None)() == 1:
            try:
                if boolean:
                    return bool(int(obj))
            except:
                pass
        try:
            return int(obj)
        except:
            if isinstance(obj, datetime.datetime):
                return obj
            return str(obj)
    return None


def format_value(obj, **kwargs):
    if obj is not None:
        if isinstance(obj, str):
            obj = obj.replace('.', '').replace(',', '').replace('$', '').replace('-', '')
            obj = obj.strip().title()
        native = to_python(obj, **kwargs)
        if type(native) in [int, bool]:
            return native
        try:
            return datetime.datetime.strptime(native, DATE_FORMAT)
        except:
            return native
    return ''


def excelt_to_python(row):
    global FILA, LOG
    table = OrderedDict()
    table[str(Persona._meta.verbose_name)] = {
        '3': 'nombre',
        '4': 'primer_apellido',
        '5': 'segundo_apellido',
        '6': 'cedula',
        '7': 'telefono',
    }
    table[str(Observacion._meta.verbose_name)] = {
        '2': 'texto',
    }
    table[str(Sobre._meta.verbose_name)] = {
        '0': 'fecha',
        '1': 'diligenciado',
        '8': 'valor',
        '9': 'tipo_ingreso',
        '10': 'forma_pago'
    }

    objects = []

    for reference in table:
        model = apps.get_model('main', reference)
        kwargs = {table[reference][x]: format_value(row[int(x)]) for x in table[reference]}
        if 'tipo_ingreso' in kwargs:
            pk = format_value(row[9], boolean=False)
            if str(pk) not in TIPOS_INGRESO:
                try:
                    kwargs['tipo_ingreso'] = TipoIngreso.objects.get(pk=pk)
                    TIPOS_INGRESO[str(pk)] = kwargs['tipo_ingreso']
                except:
                    LOG.append('* Sobre no agregado por tipo de ingreso con pk = {}, en fila: {}\n'.format(pk, FILA))
                    break
            else:
                kwargs['tipo_ingreso'] = TIPOS_INGRESO[str(pk)]
        if model == Persona:
            cedula = kwargs.pop('cedula')
            if cedula:
                kwargs['telefono'] = kwargs['telefono'] or None
                try:
                    obj, created = model.objects.get_or_create(cedula=cedula, defaults=kwargs)
                except Exception as e:
                    LOG.append('*{0} no agregada en fila #{1}, excepcion: {2}, dict: {3}\n'.format(reference, FILA, e, kwargs))
                    continue
            else:
                continue
        else:
            if model != Sobre:
                try:
                    obj, created = model.objects.get_or_create(**kwargs)
                except:
                    continue

        if model == Sobre:
            obj = model(**kwargs)
            for relation in objects:
                if isinstance(relation, Persona):
                    obj.persona = relation
                else:
                    obj.observaciones = relation
            try:
                obj.save()
            except Exception as e:
                LOG.append(
                    '*{0} no agregada en fila #{1}, excepcion: {2}, dict: {3}\n'.format(
                        reference, FILA, e, obj.__dict__
                    )
                )
                continue

        objects.append(obj)

    FILA += 1
    # print(row)
    return None
