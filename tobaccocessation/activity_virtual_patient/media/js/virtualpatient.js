jQuery(document).ready(function () {
    
    var elts = jQuery("input[type='radio']:checked");
    if (elts.length > 0) {
        jQuery("input[type='radio']").prop("disabled", true);
    }
    elts = jQuery("div.virtualpatient.treatment-selection").find("input[type='checkbox']:checked");
    if (elts.length > 0) {
        jQuery("input[type='checkbox']").prop("disabled", true);
        jQuery("div.combination-therapy").show();
    }

    jQuery("div.virtualpatient.treatment-options").parents("form").submit(function(evt) {
        evt.stopImmediatePropagation();
        
        if (!is_form_complete(this)) {
            alert('Please classify all treatment options. Select at least one treatment as "appropriate".');
            return false;
        }
        
        selector = "div.treatment-type input[type='radio'][value='appropriate']:checked";    
        if (jQuery(selector).length === 0) {
            alert('Please classify at least one treatment as "appropriate".');
            return false;
        } else {
            return true;
        }
    });
    
    jQuery("div.virtualpatient.treatment-selection").find("input[type='radio']").click(function(evt) {
        if (jQuery(this).val() == "combination") {
            jQuery("div.combination-therapy").show();
        } else {
            jQuery("div.combination-therapy").hide();
        }
    });
    
    jQuery("div.virtualpatient.treatment-selection").parents("form").submit(function(evt) {
        evt.stopImmediatePropagation();
        
        if (!is_form_complete(this)) {
            alert('Please select the best treatment option for your patient.');
            return false;
        }
        
        selector = "div.treatment-type input[type='checkbox']:checked";    
        if (jQuery(selector).length !== 2) {
            alert('Please select two therapies to combine.');
            return false;
        } else {
            return true;
        }
    });    

});