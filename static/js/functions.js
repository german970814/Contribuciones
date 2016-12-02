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
