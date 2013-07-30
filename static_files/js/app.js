/**
 * User: PervinenkoVN
 * Date: 18.07.13
 * Time: 10:43
 * To change this template use File | Settings | File Templates.
 */

var app = (function(){
    var log;
    var enable_logging = false;

    if(typeof console != "undefined") log = function(msg) {
        if(enable_logging) console.log(msg);
    };
    else log = function(msg) {

    };

    return {
        log : log,
        error: function(msg){
            log('Error: ' + msg);
        },
        loggerActive : function(state){
            enable_logging = state;
        },
        genUuid : function genUuid() {
            var uuid = "";
            for (var i=0; i < 10; i++) {
                uuid += Math.floor(Math.random() * 16).toString(16);
            }
            return 'id' + uuid;
        }
    };
})();
