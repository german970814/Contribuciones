# Django imports
from django.test import TestCase
from django.test.client import Client
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.db.models.fields import (
    CharField, EmailField, IntegerField, DateField,
    BooleanField, AutoField, TextField
)

# Locale imports
from .. import constants

# Python imports
import datetime


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
            # verifica la instancia de cada campo para agregarlo al diccionario
            if isinstance(field, (CharField, TextField)):
                if field.choices:
                    # si tiene opciones, coge la primera
                    dicc[field.name] = field.choices[0][0]
                else:
                    dicc[field.name] = self.RAW_STRING
            elif isinstance(field, EmailField):
                dicc[field.name] = self.RAW_EMAIL
            elif isinstance(field, IntegerField):
                dicc[field.name] = self.RAW_INT
            elif isinstance(field, DateField):
                dicc[field.name] = self.RAW_DATE
            elif isinstance(field, BooleanField):
                dicc[field.name] = self.RAW_BOOLEAN
            elif isinstance(field, dict):
                # agrega el campo tal cual venga en el diccionario
                dicc.update(field)
            elif isinstance(field, AutoField):
                # no hace nada
                pass
            else:
                # levanta una excepcion
                raise NotImplementedError('{} not in choices'.format(field.name))
        # devuelve el diccionario
        return dicc

    @property
    def _meta(self):
        if hasattr(self, 'Meta'):
            return self.Meta
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
        self._configure_meta()
        self.required_fields = {
            x for x in self.model._meta.fields if \
                not x.blank and not x.null and not x.is_relation \
                and not x.get_internal_type() == 'AutoField'
        }

    def required_fields(self):
        """Verifica los campos requeridos"""

        # saca los campos que son requeridos
        required_fields = self.required_fields

        # saca todos los campos
        all_fields = {
            x for x in self.model._meta.fields if \
                not x.is_relation and not x.get_internal_type() == 'AutoField'
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
