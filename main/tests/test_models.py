# Django imports
from django.db.utils import IntegrityError, DataError

# Locale imports
from .base_test import CustomBaseTestCase, ModelTestCase
from ..models import Sobre, Persona, TipoIngreso, Observacion


class SobreModelTest(ModelTestCase):
    """Pruebas unitarias para el modelo de Sobre."""

    class Meta:
        model = Sobre

    def setUp(self):
        super().setUp()

    def test_required_fields(self):
        return super().required_fields()

    def test_to_json_method(self):
        return super().to_json_method(fail=True)

    def test_fields_with_ugettext(self):
        return super().fields_with_ugettext()


class PersonaModelTest(ModelTestCase):
    """Pruebas unitarias para el modelo de Sobre."""

    class Meta:
        model = Persona

    def setUp(self):
        super().setUp()

    def test_required_fields(self):
        return super().required_fields()

    def test_to_json_method(self):
        return super().to_json_method()

    def test_fields_with_ugettext(self):
        return super().fields_with_ugettext()


class TipoIngresoModelTest(ModelTestCase):
    """Pruebas unitarias para el modelo de Sobre."""

    class Meta:
        model = TipoIngreso

    def setUp(self):
        super().setUp()

    def test_required_fields(self):
        return super().required_fields()

    def test_to_json_method(self):
        return super().to_json_method(fail=True)

    def test_fields_with_ugettext(self):
        return super().fields_with_ugettext()


class ObservacionModelTest(ModelTestCase):
    """Pruebas unitarias para el modelo de Sobre."""

    class Meta:
        model = Observacion

    def setUp(self):
        super().setUp()

    def test_required_fields(self):
        return super().required_fields()

    def test_to_json_method(self):
        return super().to_json_method(fail=True)

    def test_fields_with_ugettext(self):
        return super().fields_with_ugettext()
