odoo.define('msc.basic_fields', function (require) {
'use strict';


const { FieldBinaryImage } = require('web.basic_fields');


FieldBinaryImage.include({
    events: _.extend({}, FieldBinaryImage.prototype.events,
    {
        'click img': function ()
        {
            if (this.mode === 'readonly')
            {
                this.trigger_up('bounce_edit');

                const unique = this.recordData.__last_update;
                const url = this._getImageUrl(this.model, this.res_id, 'image_1920', unique);
                window.open(url, '_blank').focus();
            }
        },
    }),

});


});
