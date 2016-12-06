# Django imports
from django import forms

# Locale imports
from .base_test import FormTestCase
from ..forms import FormularioLogearUsuario, FormularioCrearSobre, FormularioCrearPersona


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
