/*
 * Funciones generales de JavaScript y jQuery
*/

// csrfmiddlewaretoken
const $CSRF = $('input[name="csrfmiddlewaretoken"]')

// prototype functions utils

if (!String.prototype.format) {
    String.prototype.format = function () {
        let self = this.toString();
        for (var i = 0; i < arguments.length; i++) {
            self = self.replace('{' + i.toString() + '}', arguments[i].toString());
        }
        return self;
    };
}

if (!Array.prototype.contains) {
    Array.prototype.contains = function (value) {
        for (var i in this) {
            if (this[i] == value) {
                return true;
            }
        }
        return false;
    };
}

$(document).ready(function () {
    $('#id_fecha_inicial, #id_fecha_final')
        .addClass('datetimepicker')
        .datetimepicker({
            format: 'DD/MM/YYYY',
            maxDate: moment(),
        });

    $('#id_fecha_inicial').on("dp.change",function(e){
        $('#id_fecha_final').data("DateTimePicker").minDate(e.date);
    });

    $('#id_fecha_final').on("dp.change",function(e){
        $('#id_fecha_inicial').data("DateTimePicker").maxDate(e.date);
    });

    $(".select2_single").select2({
        placeholder: "Selecciona una opción",
        allowClear: true
    });
});
