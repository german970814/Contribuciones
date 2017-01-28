"""Constantes usadas en la aplicacion."""

__author__ = 'German Alzate'

__all__ = [
    'RESPONSE_SUCCESS', 'RESPONSE_ERROR', 'RESPONSE_DENIED', 'RESPONSE_CODE', 'RESPONSE_NOT_FOUND', 'RESPONSE_REDIRECT'
]

# CSS
CSS_ERROR_CLASS = 'parsley-error'
INPUT_CLASS = 'form-control'
SELECT_CLASS = 'form-control select2_single'

# DIRECTORIES
MAIN = 'main/{}'

# MESSAGES
ERROR_FORM = 'Ha ocurrido un error al enviar el formulario, intentalo nuevamente'
SUCCESS_FORM = 'Se ha completado exitosamente el formulario'
INFO_FORM = 'Se muestran los resultados'

# API
RESPONSE_SUCCESS = 200
RESPONSE_ERROR = 400
RESPONSE_DENIED = 403
RESPONSE_NOT_FOUND = 404
RESPONSE_REDIRECT = 302
CONTENT_TYPE = 'application/json'
CONTENT_TYPE_HTML = 'text/html'
RESPONSE_CODE = 'response_code'

# FORMATS

DATE_FORMAT = '%d/%m/%Y'
