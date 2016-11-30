# Django imports
from django.db import models
from django.utils.translation import ugetext_lazy as _


class TipoIngreso(models.Model):
    """Modelo para guardar el tipo de ingreso que se da en en los sobres."""

    nombre = models.CharField(max_length=255, verbose_name=_('nombre'))

    class Meta:
        verbose_name = _('Tipo Ingreso')
        verbose_name_plural = _('Tipos de Ingreso')

    def __str__(self):
        return self.nombre.upper()


class Persona(models.Model):
    """Modelo de personas, guarda la informacion de una persona para un sobre."""

    nombre = models.CharField(verbose_name=_('nombre'), max_length=255)
    primer_apellido = models.CharField(verbose_name=_('primer apellido'), max_length=255)
    segundo_apellido = models.CharField(verbose_name=_('segundo apellido'), max_length=255, blank=True)
    cedula = models.BigIntegerField(verbose_name=_('no. identificación'), unique=True)
    telefono = models.BigIntegerField(verbose_name=_('teléfono'), blank=True, null=True)

    class Meta:
        verbose_name = _('Persona')
        verbose_name_plural = _('Personas')

    def __str__(self):
        return '{0} {1}({2})'.format(
            self.nombre.upper(),
            self.primer_apellido.upper(),
            self.cedula
        )


class Observacion(models.Model):
    """Modelo para guardar las observaciones que se pueden hacer en un sobre"""

    texto = models.TextField(verbose_name=_('observacion'))

    class Meta:
        verbose_name = _('Observacion')
        verbose_name_plural = _('Observaciones')

    def __str__(self):
        return 'Observacion No.{}'.format(self.id)


class Sobre(models.Model):
    """Modelo para la creacion de sobres en el sistema de digitacion de sobres."""

    EFECTIVO = 'EF'
    CHEQUE = 'CH'
    ELECTRONICO = 'EL'

    FORMAS_PAGO = (
        (EFECTIVO, 'EFECTIVO'),
        (CHEQUE, 'CHEQUE'),
        (ELECTRONICO, 'ELECTRONICO'),
    )

    fecha = models.DateField(_('fecha'))
    diligenciado = models.BooleanField(verbose_name=_('sobre diligenciado'), default=True)
    tipo_ingreso = models.ForeignKey(TipoIngreso, verbose_name=_('tipo ingreso'))
    valor = models.BigIntegerField(verbose_name=_('valor'))
    forma_pago = models.CharField(max_length=2, verbose_name=_('forma de pago'), choices=FORMAS_PAGO)
    persona = models.ForeignKey(Persona, verbose_name='persona', blank=True, null=True)

    class Meta:
        verbose_name = _('Sobre')
        verbose_name_plural = _('Sobres')

    def __str__(self):
        return 'Sobre de {0}, valor=${1}'.format(
            self.persona.__str__(),
            self.valor
        )
