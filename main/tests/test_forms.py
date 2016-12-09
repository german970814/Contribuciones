# Django imports
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

# Locale imports
from .base_test import FormTestCase
from ..forms import (
    FormularioLogearUsuario, FormularioCrearSobre, FormularioCrearPersona,
    FormularioCrearTipoIngreso, FormularioCrearObservacion,
    FormularioReporteContribuciones, FormularioCrearUsuario,
    CambiarContrasenaForm
)
from ..models import Persona, Sobre


class FormularioLogearUsuarioTest(FormTestCase):
    """Clase de pruebas para el formulario de logear usuario."""

    class Meta:
        form = FormularioLogearUsuario

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values()

    def test_error_css_class(self):
        super().error_class_form_invalid()

    def test_get_user_is_none_with_empty_data(self):
        """Verifica que el usuario este retornando vacio, cuando el formulario no tiene datos."""

        form = self.form(data={})
        # se verifica que el usuario sea None antes del valid
        self.assertIs(form.get_user(), None)
        form.is_valid()
        # se verifica que el usuario sea None despues del valid
        self.assertIs(form.get_user(), None)

    def test_error_with_fake_user(self):
        """
        Verifica que el formulario arroje error cuando tiene todos los campos requeridos
        y el usuario no existe.
        """

        # se crea un formulario inicial con los campos necesarios
        form = self.form(data=self.get_initial(self.required_fields))
        # se verifica que aun asi no es valido, porque no existe usuario
        self.assertFalse(form.is_valid())

    def test_get_user_backend_with_form(self):
        """Verifica que se retorne un usuario desde el backend con el formulario."""

        # se crea el usuario
        user = self.get_user()
        # se setea la contraseña
        user.set_password(self.RAW_STRING)
        # se guarda el usuario
        user.save()

        # se crea el usuario con los datos iniciales
        form = self.form(data={'email': user.email, 'password': self.RAW_STRING})

        # se verifica que sea valido el formulario
        self.assertTrue(form.is_valid())
        # verifica que retorne el mismo id del usuario creado
        self.assertEqual(form.get_user().id, user.id)
        # se verifica que el usuario haya sido autentificado por el backend
        self.assertTrue(hasattr(form.get_user(), 'backend'))
        # se asegura que devuelva una instancia de usuario
        self.assertIsInstance(form.get_user(), user.__class__)


class FormularioCrearSobreTest(FormTestCase):
    """Clase de pruebas para el formulario de crear sobres."""

    class Meta:
        form = FormularioCrearSobre

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values(excludes=['diligenciado'])

    def test_error_css_class(self):
        super().error_class_form_invalid()

    def test_fields_formulario_crear_persona_in_form(self):
        """Verifica que los campos del formulario para crear personas esten en el formulario."""

        form = self.form()  # se hace una instancia del formulario, de lo contrario no funciona

        for field in FormularioCrearPersona._meta.fields:
            # se verifica que el campo, este entre los campos de el formulario
            self.assertIn(field, form.fields)

    def test_get_persona_without_clean_method(self):
        """Verifica que levante una excepcion intentar sacar la persona sin haber usado el metodo clean."""

        # se prueba con form.is_bound = False
        form = self.form()

        with self.assertRaises(AttributeError):
            form.get_persona()

        # se prueba con form.is_bound = True
        form = self.form(data={})

        with self.assertRaises(AttributeError):
            form.get_persona()

    def test_get_persona_without_persona_data(self):
        """Verifica que la persona esté retornando None si no hay datos de persona."""

        # se sacan los campos solo del formulario, sin persona
        fields = self.form._meta.fields
        # por cada campo
        campos = {
            (field, self.form().fields[field]) for field in \
                ({'hidden'} ^ set(fields)) if self.form().fields[field].required
                # se saca el campo hidden para que no sea puesto con cualquier valor
        }
        # se crean datos iniciales
        data = self.get_initial(campos)
        # se actualiza a diligenciado =  True
        data.update({'diligenciado': True})  # , 'tipo_ingreso': data['tipo_ingreso'].id})
        # se llena el formulario
        form = self.form(data=data)
        # se verifica que sea valido
        self.assertTrue(form.is_valid())
        # se intenta obtener la persona
        self.assertIs(form.get_persona(), None)

    def test_form_invalid_if_diligenciado_is_false_and_not_observaciones(self):
        """Verifica que el formulario sea invalido si no hay observaciones y el campo diligenciado es falso."""

        # se sacan los campos obligatorios
        campos = self.required_fields
        # se sacan los campos iniciales
        data = self.get_initial(campos)
        # se actualiza, diligenciado a false
        data.update({'diligenciado': False})
        # se llena el formulario
        form = self.form(data=data)

        # se verifica que el formulario no sea valido
        self.assertFalse(form.is_valid())
        # se verifica que observaciones este en los errores
        self.assertIn('observaciones', form.errors)

        # se agrega el campo de observacion a los campos
        campos = campos | {('observaciones', form.fields['observaciones'])}
        # se vuelven a obtener los datos iniciales
        data = self.get_initial(campos)
        # se setea nuevamente diligenciado a false
        data.update({'diligenciado': False})
        # se lleva el formulario
        form = self.form(data=data)
        # se verifica que el formulario ahora sea valido
        self.assertTrue(form.is_valid())

    def test_get_person_via_hidden_input(self):
        """Verifica que se pueda obtener la persona a travez del campo hidden."""

        # se sacan los campos
        fields = self.required_fields  # | {('hidden', self.form().fields['hidden'])}
        # se crea una persona
        persona = self.create_object(Persona)
        # se sacan crean los datos iniciales
        data = self.get_initial(fields)
        # se actualizan los datos para que el formulario pase sin errores
        data.update({'diligenciado': True, 'hidden': persona.id})  # se agrega el id de la persona

        # se le pasan los datos al formulario
        form = self.form(data=data)

        # se verifica que el formulario sea valido
        self.assertTrue(form.is_valid())
        # se verifica que la instancia de la persona devuelta por el formulario, sea la misma de la persona
        self.assertIsInstance(form.get_persona(), persona.__class__)
        # se verifica que tengan el mismo id
        self.assertEqual(form.get_persona().id, persona.id)

    def test_form_invalid_if_nombre_is_bound(self):
        """Verifica que el formulario arroje error si el nombre no está vacio."""

        # se sacan los campos requeridos
        fields = self.required_fields
        # se generan los datos
        data = self.get_initial(fields)
        # se agrega el campo de nombre
        data.update({'nombre': self.RAW_STRING, 'diligenciado': True})
        # se envian los datos al formulario
        form = self.form(data=data)

        # se sacan los campos de las personas
        fields_personas = FormularioCrearPersona().fields

        # se sacan los campos obligatorios del formulario de personas
        fields_personas = {
            field for field in fields_personas if fields_personas[field].required
        } ^ {'nombre'}  # se excluye el campo de nombre

        self.assertFalse(form.is_valid())  # debe arrojar error

        for field in fields_personas:
            # se verifica que cada campo este en la lista de errores
            self.assertIn(field, form.errors)

    def test_create_person_via_form_field(self):
        """Verifica que se pueda crear una persona a partir del formulario."""

        # se sacan todos los campos del formulario
        _fields = self.form().fields
        # se crean las tuplas
        fields = {(field, _fields[field]) for field in _fields}
        # se saca la tupla de el campo hidden
        fields = {('hidden', _fields['hidden'])} ^ fields
        # se crean los datos iniciales
        data = self.get_initial(fields)

        # se envian los datos al formulario
        form = self.form(data=data)

        # formulario debe ser valido
        self.assertTrue(form.is_valid())
        # se obtiene la persona
        persona_formulario = form.get_persona()
        # se verifica que retorne una persona
        self.assertIsInstance(persona_formulario, Persona)
        # se hace una consulta a la base de datos por una persona
        persona = Persona.objects.first()
        # se verifica que sea la misma persona, por el id
        self.assertEqual(persona.id, persona_formulario.id)
        # se crea el sobre
        sobre = form.save()
        # se verifica que cree un sobre
        self.assertIsInstance(sobre, Sobre)
        # se verifica que se le haya asignado la persona al sobre
        self.assertEqual(sobre.persona, persona)
        # se verifica que sea la misma persona del formulario
        self.assertEqual(sobre.persona, persona_formulario)

    def test_form_bound_with_instances(self):
        """Verifiica que el formulario este correctamente lleno con las instancias."""

        # se crea un objeto sobre
        sobre = self.create_object(Sobre)

        # se envia la instancia y la persona al formulario
        form = self.form(instance=sobre, persona=sobre.persona)

        # se verifica que los campos con init sean los mismos la persona en el json
        self.assertEqual(set(form.initial) & set(sobre.persona.to_json()), set(sobre.persona.to_json()))
        # verifica que el id sea el mismo
        self.assertEqual(form.initial['hidden'].__str__(), sobre.persona.id.__str__())


class FormularioCrearPersonaTest(FormTestCase):
    """Clase para las pruebas unitarias de el formulario para crear personas."""

    class Meta:
        form = FormularioCrearPersona

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values()

    def test_error_css_class(self):
        super().error_class_form_invalid()


class FormularioCrearTipoIngresoTest(FormTestCase):
    """Clase para las pruebas unitarias de el formulario para crear personas."""

    class Meta:
        form = FormularioCrearTipoIngreso

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values()

    def test_error_css_class(self):
        super().error_class_form_invalid()


class FormularioCrearObservacionTest(FormTestCase):
    """Clase para las pruebas unitarias de el formulario para crear personas."""

    class Meta:
        form = FormularioCrearObservacion

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values()

    def test_error_css_class(self):
        super().error_class_form_invalid()


class FormularioReporteContribucionesTest(FormTestCase):
    """Pruebas para el formulario de reporte de contribuciones."""

    class Meta:
        form = FormularioReporteContribuciones

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        with self.assertRaises(AssertionError):
            super().default_values(excludes=['totalizado'])

    def test_error_css_class(self):
        super().error_class_form_invalid()

    def test_persona_is_required_if_totalizado_is_false(self):
        """Verifica que el campo de persona sea requerido si el campo de totalizado es False."""

        data = self.get_initial(self.required_fields)
        data['totalizado'] = False
        form = self.form(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('persona', form.errors)


class FormularioCrearUsuarioTest(FormTestCase):
    """Pruebas para el formulario de crear usuarios."""

    class Meta:
        form = FormularioCrearUsuario

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values(excludes=['totalizado'])

    def test_error_css_class(self):
        super().error_class_form_invalid()

    def test_password_confirmation_have_input_password(self):
        """Verifica que el campo de la contraseña tenga el widget PasswordInput."""

        from django.forms import PasswordInput  # se importa el widget

        form = self.form()

        # se verifica que ambos campos tengan el widget, para proteger la contraseña
        self.assertIsInstance(form.fields['password_confirmation'].widget, PasswordInput)
        self.assertIsInstance(form.fields['password'].widget, PasswordInput)

    def test_email_fields_required(self):
        """Verifica que el campo de email sea un campo requerido."""

        form = self.form()
        # se verifica que el email, sea requerido
        self.assertTrue(form.fields['email'].required)

    def test_password_unique(self):
        """Verifica que las contraseñas escritas por el usuario, sean las mismas."""

        # se crean los datos
        data = self.get_initial(self.required_fields)
        # se cambia la contraseña 2
        data['password_confirmation'] = self.RAW_STRING_2

        # se crea el formulario con los datos
        form = self.form(data=data)

        # se verifica que no sea valido
        self.assertFalse(form.is_valid())
        # se mira si el error es de contraseña
        self.assertIn('password', form.errors)

        # se cambia la contraseña por una igual a la de data
        data['password_confirmation'] = data['password']

        # se vuelve a llenar el formulario
        form = self.form(data=data)
        # ahora es valido
        self.assertTrue(form.is_valid())

    def test_create_user_with_group(self):
        """Verifica que se cree el usuario adecuadamente con el grupo escogido."""

        # se crean los datos iniciales
        data = self.get_initial(self.required_fields)

        # se envian los datos al formulario
        form = self.form(data=data)

        # se verifica que sea valido
        self.assertTrue(form.is_valid())

        # se obtiene el modelo de usuario
        User = get_user_model()
        user_form = form.save()  # se obtiene el usuario de el formulario
        grupo = Group.objects.first()  # se obtiene el grupo creado por los datos

        # se verifica que la instancia devuelta por el formulario sea un usuario
        self.assertIsInstance(user_form, User)
        # se verifica la contraseña de el usuario
        self.assertTrue(user_form.check_password(data['password']))
        self.assertTrue(user_form.check_password(data['password_confirmation']))
        # se verifica que el grupo, haya sido correctamente asignado al usuario
        self.assertEqual(user_form.groups.first().id, grupo.id)


class CambiarContrasenaFormTest(FormTestCase):
    """Pruebas para el formulario de cambio de contraseña."""

    class Meta:
        form = CambiarContrasenaForm

    def setUp(self):
        super().setUp()

    def test_error_form_with_empty_data(self):
        super().error_form_with_empty_data()

    def test_labels_with_ugettext(self):
        super().labels_with_ugettext()

    def test_required_fields(self):
        super().required_fields()

    def test_default_values(self):
        super().default_values()

    def test_error_css_class(self):
        super().error_class_form_invalid()

    def test_passwords_have_input_password(self):
        """Verifica que el campo de la contraseña tenga el widget PasswordInput."""

        from django.forms import PasswordInput  # se importa el widget

        form = self.form()

        # se verifica que ambos campos tengan el widget, para proteger la contraseña
        self.assertIsInstance(form.fields['password_1'].widget, PasswordInput)
        self.assertIsInstance(form.fields['password_2'].widget, PasswordInput)

    def test_password_unique(self):
        """Verifica que las contraseñas escritas por el usuario, sean las mismas."""

        # se crean los datos
        data = self.get_initial(self.required_fields)
        # se cambia la contraseña 2
        data['password_2'] = self.RAW_STRING_2

        # se crea el formulario con los datos
        form = self.form(data=data)

        # se verifica que no sea valido
        self.assertFalse(form.is_valid())
        # se mira si el error es de contraseña
        self.assertIn('password_1', form.errors)

        # se cambia la contraseña por una igual a la de data
        data['password_2'] = data['password_1']

        # se vuelve a llenar el formulario
        form = self.form(data=data)
        # ahora es valido
        self.assertTrue(form.is_valid())

    def test_form_return_authenticated_user(self):
        """Verifica que el formulario retorne un usuario autentificado."""

        # se crea u obtiene el usuario
        user = self.get_user()

        # se crean las contraseñas nuevas
        data = {
            'password_1': self.RAW_STRING,
            'password_2': self.RAW_STRING
        }

        # se crea el formulario con el atributo user
        form = self.form(data=data, usuario=user)

        # se verifica que sea valido
        self.assertTrue(form.is_valid())

        # se guarda el usuario
        user_form = form.save()

        # se verifica que el usuario retornado sea el mismo
        self.assertEqual(user.id, user_form.id)
        # se verifica que tenga un backend, lo que quiere decir que fue autentificado
        self.assertTrue(hasattr(user_form, 'backend'))
        # se verifica la contraseña
        self.assertTrue(user.check_password(data['password_1']))

    def test_raise_error_if_usuario_keyword_not_provided(self):
        """Verifica que el formulario arroje error si no hay usuario."""

        # se crea el formulario con los datos iniciales
        data = self.get_initial(self.required_fields)
        form = self.form(data=data)

        # se valida el formulario
        self.assertTrue(form.is_valid())

        # se verifica el error
        with self.assertRaises(NotImplementedError):
            form.save()
