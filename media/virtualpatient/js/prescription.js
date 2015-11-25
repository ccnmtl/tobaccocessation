function get_state() {
    debug('get_state');

    var doc = {};
    doc.medication_idx = $('medication_idx').value;

    var tag = $('medication_tag').value;
    doc[tag] = {};
    doc[tag].concentration = $('concentration')
        .options[$('concentration').selectedIndex].value;
    doc[tag].dosage = $('dosage').options[$('dosage').selectedIndex].value;

    if ($('concentration2')) {
        doc[tag].concentration2 = $('concentration2')
            .options[$('concentration2').selectedIndex].value;
        doc[tag].dosage2 = $('dosage2')
            .options[$('dosage2').selectedIndex].value;
    }

    var jsontxt = JSON.stringify(doc, null);
    return jsontxt;
}

function validate() {
    var valid = true;
    var children = jQuery('div#content').find('select');
    jQuery.each(children, function() {
        if (valid && jQuery(this).is(':visible')) {
            if (this.tagName === 'SELECT') {
                var value = jQuery(this).val();
                valid = value !== undefined && value.length > 0 &&
                    jQuery(this).val().trim() !== '-----';
            }
        }
    });

    if (!valid) {
        getElement('next_disabled').style.display = 'block';
        getElement('next').style.display = 'none';
        return false;
    } else {
        getElement('next_disabled').style.display = 'none';
        getElement('next').style.display = 'block';
    }
    return true;
}

function setupGender() {
    debug('setupGender: ' + $('patient_id').value);
    if ($('patient_id').value === 4) {
        // move over the gender to the left
        setStyle($('gender'), {'margin-left': '285px'});

        if ($('gender2')) {
            setStyle($('gender2'), {'margin-left': '288px'});
        }
    }

    MochiKit.Signal.connect('concentration', 'onchange', validate);
    MochiKit.Signal.connect('dosage', 'onchange', validate);
    if (getElement('concentration2') !== null) {
        MochiKit.Signal.connect('concentration2', 'onchange', validate);
    }
    if (getElement('dosage2') !== null) {
        MochiKit.Signal.connect('dosage2', 'onchange', validate);
    }

    validate();
}

MochiKit.Signal.connect(window, 'onload', setupGender);
