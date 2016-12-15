# Django imports
# from django.views.generic import View
# from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

# Locale imports
from .base_test import ViewTestCase
from .. import constants
from ..forms import FormularioLogearUsuario, FormularioReporteContribuciones
from ..views import (
    login_view, home_view, logout_view, listar_sobres, reporte_contribuciones,
    SobreCreate, SobreUpdate, PersonaCreate, PersonaUpdate, TipoIngresoCreate,
    TipoIngresoUpdate, ObservacionCreate, ObservacionUpdate, UserCreate,
    PersonaList, TipoIngresoList, ObservacionList, UserList,
    SetPasswordView
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
        manana = (datetime.date.today() + datetime.timedelta(days=1)).strftime(constants.DATE_FORMAT)
        # se crea la peticion POST
        response = self.POST(data={
            'fecha_inicial': hoy,
            'fecha_final': manana
        })

        # se verifica que el sobre este en el contexto
        self.assertContains(response, sobre.valor)
        self.assertContains(response, sobre.persona.nombre)
        self.assertContains(response, reverse(self.url_base.format('editar_sobre'), args=(sobre.id, )))


class ReporteContribuciones(ViewTestCase):
    """Pruebas para la vista de reportes de contribuciones."""

    class Meta:
        view = reporte_contribuciones
        form = FormularioReporteContribuciones

    def setUp(self):
        super().setUp()
        self.template = self.template_base.format('reporte_contribuciones.html')

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_get_totales_by_persona(self):
        """Verifica que se pueda ver los totales de las contribuciones por persona."""

        # se crea una instancia del formulario
        form_instance = self.form()
        # se sacan los campos obligatorios
        required_fields = {(field, form_instance.fields[field]) for field in form_instance.fields}

        # se crea un sobre
        sobre = self.create_object(Sobre)

        # se crean los datos iniciales
        data = self.get_initial(required_fields)
        # se marca que no hay totalizado
        data['totalizado'] = False

        # se genera la respuesta
        response = self.POST(data=data)

        # se verifica que retorne 200
        self.assertEqual(response.status_code, constants.RESPONSE_SUCCESS)
        # se espera que venga la tabla en la respuesta
        self.assertIn('tabla', response.context)
        # se saca la tabla
        tabla = response.context['tabla']
        # se verifica que el total, sea igual al total de lo que ha dado una persona
        self.assertEqual(tabla['TOTAL']['total'].__str__(), str(sobre.valor))
        # se verifica el total por forma de pago
        self.assertEqual(
            tabla['TOTAL'][sobre.get_forma_pago_display().upper()].__str__(),
            sobre.valor.__str__()
        )

    def test_form_with_totalizado(self):
        """Verifica que se envien los resultados adecuadamente por totales generales en la iglesia."""

        # se crea una instancia del formulario
        form_instance = self.form()
        # se sacan los campos obligatorios
        required_fields = {(field, form_instance.fields[field]) for field in form_instance.fields}

        # se crean varios sobres
        sobre_1 = self.create_object(Sobre)
        sobre_2 = self.create_object(Sobre, diff=True)
        sobre_3 = self.create_object(Sobre, diff=True)

        # se crean los datos iniciales
        data = self.get_initial(required_fields)
        # se marca que si hay totalizado
        data['totalizado'] = True

        # se genera la respuesta
        response = self.POST(data=data)

        # se verifica que retorne 200
        self.assertEqual(response.status_code, constants.RESPONSE_SUCCESS)
        # se espera que venga la tabla en la respuesta
        self.assertIn('tabla', response.context)
        # se saca la tabla
        tabla = response.context['tabla']
        # se verifica que el total no sea igual a de un solo sobre
        self.assertNotEqual(tabla['TOTAL']['total'].__str__(), str(sobre_1.valor))
        self.assertNotEqual(tabla['TOTAL']['total'].__str__(), str(sobre_2.valor))
        self.assertNotEqual(tabla['TOTAL']['total'].__str__(), str(sobre_3.valor))
        # se verifica que el total sea igual a la suma de los 3 sobres
        self.assertEqual(
            tabla['TOTAL']['total'].__str__(),
            str(sobre_1.valor + sobre_2.valor + sobre_3.valor)
        )

    def test_table_response_structure(self):
        """Verifica la estructura de la tabla que llega como respuesta."""

        # se crea una instancia del formulario
        form_instance = self.form()
        # se sacan los campos obligatorios
        required_fields = {(field, form_instance.fields[field]) for field in form_instance.fields}

        # se crea un sobre
        sobre = self.create_object(Sobre)

        # se crean los datos iniciales
        data = self.get_initial(required_fields)
        # se marca que no hay totalizado
        data['totalizado'] = False

        # se genera la respuesta
        response = self.POST(data=data)

        # se verifica que retorne 200
        self.assertEqual(response.status_code, constants.RESPONSE_SUCCESS)
        # se espera que venga la tabla en la respuesta
        self.assertIn('tabla', response.context)
        # se saca la tabla
        tabla = response.context['tabla']
        # se verifica que el TOTAL este en la tabla principal
        self.assertIn('TOTAL', tabla)
        # se verifica que ese total tenga un total
        self.assertIn('total', tabla['TOTAL'])
        # se saca el tipo de ingreso, de acuerdo al sobre
        tipo_ingreso = str(sobre.tipo_ingreso.nombre).upper()
        # se verifica que el tipo de ingreso salga en la tabla
        self.assertIn(tipo_ingreso, tabla)
        # se verifica que el tipo de ingreso tenga un total
        self.assertIn('total', tabla[tipo_ingreso])

        # se recorren las formas de pago del sobre
        for forma in Sobre.FORMAS_PAGO:
            # se verifica que cada forma de pago, este contenido en el total
            self.assertIn(forma[1], tabla['TOTAL'])
            # se verifica que cada forma de pago este contenido en el tipo de ingreso
            self.assertIn(forma[1], tabla[tipo_ingreso])


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

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # marca diligenciado a True
        data['diligenciado'] = True
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(Sobre.objects.all().count(), 1)
        # verifica a donde redirecciona
        url = self.view.success_url.__str__()
        url += '?{}={}'.format('date', data['fecha'].strftime(constants.DATE_FORMAT))
        self.assertRedirects(response, url)

    def test_form_bound_with_date_from_url(self):
        """Prueba que el formulario esté lleno con los datos del GET."""

        # crea la fecha de hoy
        hoy = datetime.date.today().strftime(constants.DATE_FORMAT)

        # hace un GET
        response = self.GET(url=self.get_url() + '?{}={}'.format('date', hoy))

        # verifica que la fecha esté en la vista
        self.assertContains(response, hoy)

    def test_personas_in_context(self):
        """Verifica que las personas esten en el contexto."""

        # hace un GET
        response = self.GET()
        # verifica que este las personas dentro del contexto
        self.assertIn('personas', response.context)
        # hace un POST
        response = self.POST()
        # verifica que este las personas dentro del contexto
        self.assertIn('personas', response.context)


class SobreUpdateTest(ViewTestCase):
    """Pruebas para la vista de SobreUpdate."""

    class Meta:
        view = SobreUpdate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # marca diligenciado a True
        data['diligenciado'] = True
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica que el sobre es la instancia
        self.assertEqual(self.model.objects.first(), self.instance)
        # verifica a donde redirecciona
        url = self.view.success_url
        self.assertRedirects(response, reverse(url, args=(self.instance.id, )).__str__())

    def test_personas_in_context(self):
        """Verifica que las personas esten en el contexto."""

        # hace un GET
        response = self.GET()
        # verifica que este las personas dentro del contexto
        self.assertIn('personas', response.context)
        # hace un POST
        response = self.POST()
        # verifica que este las personas dentro del contexto
        self.assertIn('personas', response.context)


class PersonaCreateTest(ViewTestCase):
    """Pruebas para la vista de PersonaCreate."""

    class Meta:
        view = PersonaCreate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica a donde redirecciona
        self.assertRedirects(response, self.view.success_url.__str__())


class PersonaUpdateTest(ViewTestCase):
    """Pruebas para la vista de PersonaUpdate."""

    class Meta:
        view = PersonaUpdate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica que el sobre es la instancia
        self.assertEqual(self.model.objects.first(), self.instance)
        # verifica a donde redirecciona
        url = self.view.success_url
        self.assertRedirects(response, reverse(url, args=(self.instance.id, )).__str__())


class TipoIngresoCreateTest(ViewTestCase):
    """Pruebas para la vista de TipoIngresoCreate."""

    class Meta:
        view = TipoIngresoCreate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica a donde redirecciona
        self.assertRedirects(response, self.view.success_url.__str__())


class TipoIngresoUpdateTest(ViewTestCase):
    """Pruebas para la vista de TipoIngresoUpdate."""

    class Meta:
        view = TipoIngresoUpdate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica que el sobre es la instancia
        self.assertEqual(self.model.objects.first(), self.instance)
        # verifica a donde redirecciona
        url = self.view.success_url
        self.assertRedirects(response, reverse(url, args=(self.instance.id, )).__str__())


class ObservacionCreateTest(ViewTestCase):
    """Pruebas para la vista de ObservacionCreate."""

    class Meta:
        view = ObservacionCreate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica a donde redirecciona
        self.assertRedirects(response, self.view.success_url.__str__())


class ObservacionUpdateTest(ViewTestCase):
    """Pruebas para la vista de ObservacionUpdate."""

    class Meta:
        view = ObservacionUpdate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el sobre
        self.assertEqual(self.model.objects.all().count(), 1)
        # verifica que el sobre es la instancia
        self.assertEqual(self.model.objects.first(), self.instance)
        # verifica a donde redirecciona
        url = self.view.success_url
        self.assertRedirects(response, reverse(url, args=(self.instance.id, )).__str__())


class UserCreateTest(ViewTestCase):
    """Pruebas para la vista de UserCreate."""

    class Meta:
        view = UserCreate

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica que crea el usuario
        self.assertEqual(self.model.objects.all().count(), 2)
        # verifica a donde redirecciona
        self.assertRedirects(response, self.view.success_url.__str__())


class PersonaListTest(ViewTestCase):
    """Pruebas para la vista de PersonaList."""

    class Meta:
        view = PersonaList

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()


class TipoIngresoListTest(ViewTestCase):
    """Pruebas para la vista de TipoIngresoList."""

    class Meta:
        view = TipoIngresoList

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()


class SetPasswordViewTest(ViewTestCase):
    """Pruebas para la vista de SetPasswordView."""

    class Meta:
        view = SetPasswordView

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()

    def test_post_error(self):
        super().post_error()

    def test_redirect_to_url(self):
        """verifica que redireccione a la url seleccionada si el formulario está correcto."""

        # crea los datos iniciales
        data = self.get_initial(self.required_fields)
        # crea la peticion/respuesta
        response = self.POST(data=data)

        # verifica que retorne una redireccion
        self.assertEqual(response.status_code, constants.RESPONSE_REDIRECT)
        # verifica a donde redirecciona
        self.assertRedirects(response, self.view.success_url.__str__())


class ObservacionListTest(ViewTestCase):
    """Pruebas para la vista de ObservacionList."""

    class Meta:
        view = ObservacionList

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()


class UserListTest(ViewTestCase):
    """Pruebas para la vista de UserList."""

    class Meta:
        view = UserList

    def test_get_response_is_200(self):
        super().response_is_200()

    def test_get_response_is_template(self):
        super().response_is_template()
