# Django imports
# from django.views.generic import View
# from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

# Locale imports
from .base_test import ViewTestCase
from .. import constants
from ..forms import FormularioLogearUsuario
from ..views import (
    login_view, home_view, logout_view, listar_sobres, reporte_contribuciones,
    SobreCreate
)
from ..models import Sobre

# Python imports
import datetime


class LoginViewTest(ViewTestCase):
    """Pruebas para la vista de login."""

    class Meta:
        view = login_view

    def setUp(self):
        super().setUp()
        self.template = self.template_base.format('login.html')

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_home_if_user_is_logged_in(self):
        """Verifica que redireccione al login en caso que el usuario este logeado."""

        # logea el usuario
        self.login_usuario()
        # crea la respuesta
        response = self.GET()
        # verifica que sea redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que redireccione a home
        self.assertIn(reverse(self.url_base.format('home')), response['Location'])

    def test_log_user_with_post_data(self):
        """Verifica que sea logeado el usuario con los datos del post."""

        # form_class = FormularioLogearUsuario
        # istance = form_class()
        # fields = {(field, instance.fields[field]) for field in instance.fields if instance[field].required}
        # data = self.get_initial(fields)
        # crea el usuario
        user = self.get_user()
        # pasa los datos
        data = {
            'email': user.email,
            'password': self.RAW_STRING
        }
        # envia la peticion
        response = self.POST(data=data)
        # verifica que sea una redireccion a home
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        self.assertIn(reverse(self.url_base.format('home')), response['Location'])

    def test_next_work_with_user_login(self):
        """Verifica que el parametro next este haciendo la redireccion adecuadamente."""

        # crea el usuario
        user = self.get_user()

        # crea los datos
        data = {
            'email': user.email,
            'password': self.RAW_STRING
        }
        # agrega el parametro next a la peticion
        response = self.POST(url=self.get_url() + '?next=/admin/', data=data)

        # verifica la redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que redireccione admin
        self.assertIn('/admin/', response['Location'])

    def test_next_work_with_user_loggedin(self):
        """Verifica que el parametro next funcione en GET."""

        # logea el usuario
        self.login_usuario()
        # hace la peticion get con el parametro next
        response = self.GET(url=self.get_url() + '?next=/admin/')

        # verifica la redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que redireccione al admin
        self.assertIn('/admin/', response['Location'])


class HomeViewTest(ViewTestCase):
    """Pruebas para la vista de home_view."""

    class Meta:
        view = home_view

    def setUp(self):
        super().setUp()
        self.template = self.template_base.format('home.html')

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()


class LogoutViewTest(ViewTestCase):
    """Pruebas para la vista de logout_view."""

    class Meta:
        view = logout_view

    def test_get_redirect_to_home(self):
        """Verifica que a un GET lo redireccione a /login/."""

        response = self.GET()

        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        self.assertIn(reverse(self.url_base.format('login')), response['Location'])


class ListarSobresTest(ViewTestCase):
    """Pruebas para la vista de listar_sobres."""

    class Meta:
        view = listar_sobres

    def setUp(self):
        super().setUp()
        self.template = self.template_base.format('listar_sobres.html')

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_get_with_form_and_not_sobre_list(self):
        """Verifica que esté llegando el formulario y no los sobres"""
        # se crea la peticion GET
        response = self.GET()
        # se verifica que el formulario este en las respuestas
        self.assertIn('form', response.context)
        # se verifica que no se envien los sobres con el GET
        self.assertNotIn('sobre_list', response.context)

    def test_post_response_sobre_list(self):
        """Verifica que la respuesta tenga la lista de sobres."""
        # se crean los datos iniciales
        hoy = datetime.date.today().strftime(constants.DATE_FORMAT)
        # se crea la peticion de POST
        response = self.POST(data={
            'fecha_inicial': hoy,
            'fecha_final': hoy
        })

        # se verifica que la respuesta sea 200
        self.assertEqual(response.status_code, constants.RESPONSE_SUCCESS)
        # se verifica que los datos esten en el contexto
        self.assertIn('sobre_list', response.context)
        self.assertIn('form', response.context)
        # se verifica que los mensajes tengan el success
        self.assertEqual([x.tags for x in response.context['messages']], ['success'])

    def test_sobre_returned_in_view(self):
        """Verifica que retorne los sobres adecuadamente la respuesta."""
        # se crea el sobre
        sobre = self.create_object(Sobre)

        # se crean los datos
        hoy = datetime.date.today().strftime(constants.DATE_FORMAT)
        # se crea la peticion POST
        response = self.POST(data={
            'fecha_inicial': hoy,
            'fecha_final': hoy
        })
        # se verifica que el sobre este en el contexto
        self.assertIn(sobre, response.context['sobre_list'])


class ReporteContribuciones(ViewTestCase):
    """Pruebas para la vista de reportes de contribuciones."""

    class Meta:
        view = reporte_contribuciones

    def setUp(self):
        super().setUp()
        self.template = self.template_base.format('reporte_contribuciones.html')

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()


class SobreCreateTest(ViewTestCase):
    """Pruebas para la vista de SobreCreate."""

    class Meta:
        view = SobreCreate

    def setUp(self):
        super().setUp()

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()
