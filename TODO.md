__author__ = 'German Alzate'

#######################################################################################################
Contribuciones

* Optimización de búsqueda de personas, cuando hay muchos registros, en la vista de 'ingresar_sobre', 'actualizar_sobre' y 'reporte_contribuciones'

* Mejora en la vista de 'home_view' al hacer consultas basadas en rangos de fechas, cambiar a consultas por mes con el lookup: '__month__'

* Cambio en la consulta en for, por esto, Sobre.objects.values('tipo_ingreso__nombre').annotate(s=Sum('valor'))
