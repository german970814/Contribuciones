# Django imports
from django.test import TestCase
from django.test.client import Client
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db.models.fields import (
    CharField, EmailField, IntegerField, DateField,
    BooleanField, AutoField, TextField
)
from django.forms import (
    CharField as CharFieldForm, EmailField as EmailFieldForm,
    IntegerField as IntegerFieldForm, DateField as DateFieldForm,
    BooleanField as BooleanFieldForm, TypedChoiceField,
    ModelChoiceField
)
# Locale imports
from .. import constants

# Python imports
import datetime


class MetaClassTest(object):
    """Clase Meta para las opciones de los tests."""

    def __init__(self, options=None):
        self.model = getattr(options, 'model', None)
        self.form = getattr(options, 'form', None)


class CustomBaseTestCase(TestCase):
    """Clase base para los test de la app."""

    # valores dummy, para crear objetos en la base de datos
    RAW_STRING = 'RAW_VALUE'
    RAW_EMAIL = 'RAW_EMAIL@MAIL.COM'
    RAW_STRING_2 = 'RAW VALUE 2'
    RAW_INT = 123456
    RAW_DATE = datetime.date.today()
    RAW_BOOLEAN = True

    @classmethod
    def get_response_code(cls, response):
        """
        Retorna el response_code de una respuesta JSON
        """
        try:
            return cls.get_response_data(response)[constants.RESPONSE_CODE]
        except KeyError:
            raise NameError("The '{}' key not found in data".format(constants.RESPONSE_CODE))

    @staticmethod
    def get_response_data(response):
        """
        Retorna el JSON de una respuesta como diccionario
        """
        # si es HttpResponse busca el contenido
        if isinstance(response, HttpResponse) and hasattr(response, 'content'):
            response = response.content
        if not isinstance(response, dict):
            # si no es un diccionario
            try:
                # se evalua la respuesta, debe ser estring, y se le quita el bytecode
                response = eval(response.decode('utf-8'))
                if not isinstance(response, dict):
                    # si no retorna un JSON o diccionario, levanta una excepcion
                    raise ValueError("Expected 'dict', found '%s'." % response.__class__.__name__)
            except Exception as exception:
                if isinstance(exception, ValueError):
                    raise exception
                raise ValueError("Cannot eval the give exception")
        return response

    @staticmethod
    def get_content_type(response):
        """
        Retorna el MimeType o ContentType de una respuesta http
        """
        if isinstance(response, HttpResponse):
            return response._headers['content-type'][1]
        elif isinstance(response, dict):
            return response['content-type'][1]
        elif isinstance(response, tuple):
            return response[1]
        raise ValueError("Cannot find 'content-type' in {}".format(response.__class__.__name__))

    def create_object(self, model_class):
        """Crea un objeto, con sus campos relacionados."""

        # inicializa una lista
        field_list = []
        # recorre cada campo
        for field in model_class._meta.fields:
            # siempre y cuando el campo no sea el id
            if field.get_internal_type() != 'AutoField':
                # si no es una relacion
                if not field.is_relation:
                    # si es obligatorio el campo
                    if not field.blank and not field.null:
                        # lo añade a la lista
                        field_list.append(field)
                else:
                    # si es una relacion
                    relation = self.create_object(field.related.model)  # recursividad
                    # agrega el objeto como diccionario
                    field_list.append({field.name: relation})
        # retorna la creacion del objeto con los valores predeterminados
        return model_class.objects.create(**self.get_initial(field_list))

    def get_initial(self, array):
        """Retorna un diccionario con valores iniciales, para la creacion de cualquier objeto."""
        dicc = dict()  # crea un diccionario
        # recorre el array inicial, debe ser un array de campos (Field)
        for field in array:
            if isinstance(field, tuple):
                field[1].name = field[0]
                field = field[1]
            # verifica la instancia de cada campo para agregarlo al diccionario
            if isinstance(field, (EmailField, EmailFieldForm)):
                dicc[field.name] = self.RAW_EMAIL
            elif isinstance(field, (CharField, TextField, CharFieldForm, TypedChoiceField)):
                if getattr(field, 'choices', None) or None is not None:
                    # si tiene opciones, coge la primera
                    dicc[field.name] = field.choices[1][0]
                else:
                    dicc[field.name] = self.RAW_STRING
            elif isinstance(field, (IntegerField, IntegerFieldForm)):
                dicc[field.name] = self.RAW_INT
            elif isinstance(field, (DateField, DateFieldForm)):
                dicc[field.name] = self.RAW_DATE
            elif isinstance(field, (BooleanField, BooleanFieldForm)):
                dicc[field.name] = self.RAW_BOOLEAN
            elif isinstance(field, dict):
                # agrega el campo tal cual venga en el diccionario
                dicc.update(field)
            elif isinstance(field, ModelChoiceField):
                dicc[field.name] = self.create_object(field.queryset.model).id
            elif isinstance(field, AutoField):
                # no hace nada
                pass
            else:
                print(field)
                # levanta una excepcion
                raise NotImplementedError('{} not in choices'.format(field.name))
        # devuelve el diccionario
        return dicc

    def get_user(self):
        """Metodo para devolver un usuario"""
        if hasattr(self, '_user'):
            # si hay usuario, lo retorna
            return self._user
        # crea los datos
        data = self.get_initial([x for x in get_user_model()._meta.fields])
        del data['last_login']  # elimina las fechas, para evitar los warnings
        del data['date_joined']
        # pasa los datos
        self._user = get_user_model().objects.create(**data)
        # retorna el usuario
        return self._user

    @property
    def _meta(self):
        if hasattr(self, 'Meta'):
            return MetaClassTest(getattr(self, 'Meta', None))
        raise NotImplementedError("Meta class is not availabe for this object yet")

    def _configure_meta(self):
        try:
            for field in self._meta.__dict__:
                if not field.startswith('_'):
                    setattr(self, field, getattr(self._meta, field))
        except (NotImplementedError):
            pass

    def setUp(self):
        self.client = Client()
        self._configure_meta()


class ModelTestCase(CustomBaseTestCase):
    """Clase de Pruebas aplicadas para modelos."""

    def setUp(self):
        super().setUp()
        # self._configure_meta()
        self.required_fields = {
            x for x in self.model._meta.fields
            if not x.blank and not x.null and not x.is_relation and not
            x.get_internal_type() == 'AutoField'
        }

    def required_fields(self):
        """Verifica los campos requeridos"""

        # saca los campos que son requeridos
        required_fields = self.required_fields

        # saca todos los campos
        all_fields = {
            x for x in self.model._meta.fields if not
            x.is_relation and not x.get_internal_type() == 'AutoField'
        }

        for field in required_fields:
            # para cada campo, verifica que levantara una excepcion
            with self.assertRaises(IntegrityError):
                # excluye el campo de todos los campos
                excludes = {field} ^ all_fields
                # se obtienen datos dummy a partir de los campos
                initial = self.get_initial(list(excludes))
                # intenta crear el objeto
                self.model.objects.create(**initial).save()

        # verifica que no se haya creado ningun objeto en la base de datos
        # objects = self.model.objects.all().count()
        # self.assertEqual(objects, 0)

    def to_json_method(self, fail=False):
        """Verifica que el methodo to_json de la clase esté retornando los valores adecuados."""

        # crea el objeto de acuerdo al modelo
        instance = self.create_object(self.model)

        if fail:
            with self.assertRaises(NotImplementedError):
                self.assertTrue(isinstance(instance.to_json(), dict))
        else:
            # recorre el metodo json
            for key, value in instance.to_json().items():
                # obtiene el objeto, hace los asserts
                self.assertIn(key, instance.__dict__)
                # se verifica que el valor sea en mayuscula
                self.assertEqual(str(value), str(getattr(instance, key, None)).upper())

        # retorna un objeto creado
        self.assertEqual(self.model.objects.all().count(), 1)

    def fields_with_ugettext(self):
        """Verifica que todos los campos tengan el verbose_name con ugettext_lazy."""

        for field in self.model._meta.fields:
            if field.get_internal_type() != 'AutoField':
                # verifica que no retorne un string
                self.assertFalse(isinstance(field.verbose_name, str))


class FormTestCase(CustomBaseTestCase):
    """Clase de base para pruebas de Formularios."""

    def setUp(self):
        super().setUp()
        form = self.form()
        self.required_fields = {
            (field, form.fields[field]) for field in form.fields if form.fields[field].required is True
        }

    def error_form_with_empty_data(self):
        """Prueba los errores del formularo con datos vacios."""

        form = self.form(data={})  # se envia el formulario con datos vacios

        self.assertFalse(form.is_valid())  # se verifica que no es falso

        for field in self.required_fields:
            self.assertIn(field[0], form.errors)  # se verifica que los campos esten en los errores

        # self.assertIn('__all__', form.errors)  # se verifica que ocurra un error desde el backend

    def labels_with_ugettext(self):
        """Prueba que todos los campos del formulario tengan el label con ugettext_lazy."""

        # solo se hace prueba de que si tiene label, que sea ugettext, si no tiene label no prueba

        form = self.form()

        for field in form.fields:
            if form.fields[field].label is not None:
                self.assertFalse(isinstance(form.fields[field].label, str))

    def required_fields(self):
        """Funcion para probar los campos requeridos de un formulario."""

        # se recorren los campos requeridos
        for field in self.required_fields:
            # se crea el formulario con datos de acuerdo a los campos
            # se saca un solo campo requerido
            form = self.form(data=self.get_initial({field} ^ self.required_fields))
            # se verifica que no sea valido
            self.assertFalse(form.is_valid())
            # se verifica que el campo que hace falta sea el que se saco
            self.assertIn(field[0], form.errors)

    def default_values(self, excludes=[]):
        """Funcion para verificar los valores por defecto que toma un formulario."""

        # verifica que la clase de css sea la de error
        self.assertEqual(self.form.error_css_class, constants.CSS_ERROR_CLASS)

        form = self.form()

        for field in form.fields:
            # por cada campo
            if hasattr(form.fields[field], 'choices'):
                # verifica la clase de css de select
                if field in excludes:
                    # se debe agregar al excludes el campo que no cumpla con la condicion
                    self.assertEqual(form.fields[field].widget.attrs['class'], constants.INPUT_CLASS)
                else:
                    self.assertEqual(form.fields[field].widget.attrs['class'], constants.SELECT_CLASS)
            else:
                # verifica la clase de css de input normal
                self.assertEqual(form.fields[field].widget.attrs['class'], constants.INPUT_CLASS)
            # verifica el placeholder de cada uno
            self.assertEqual(form.fields[field].widget.attrs['placeholder'], form.fields[field].label)

    def error_class_form_invalid(self):
        """Funcion para verificar las clases de error de css que son agregadas a los campos por el mixin"""

        form = self.form(data={})

        form.is_valid()  # se hace que el formulario genere los errores

        for field in form.fields:
            # si el campo esta en los errores
            if field in form._errors:
                if hasattr(form.fields[field], 'choices'):
                    # verifica cada error de acuerdo al tipo de campo
                    self.assertIn(constants.CSS_ERROR_CLASS, form.fields[field].widget.attrs['class'])
                    self.assertIn(constants.SELECT_CLASS, form.fields[field].widget.attrs['class'])
                else:
                    self.assertIn(constants.INPUT_CLASS, form.fields[field].widget.attrs['class'])
                    self.assertIn(constants.CSS_ERROR_CLASS, form.fields[field].widget.attrs['class'])
