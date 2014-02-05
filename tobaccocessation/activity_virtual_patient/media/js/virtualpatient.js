jQuery(document).ready(function () {
    // Disable checked radio buttons
    var elts = jQuery("input[type='radio']:checked");
    if (elts.length > 0) {
        jQuery("input[type='radio']").prop("disabled", true);
    }
        
    // Treatment Options
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
    
    // Treatment Selection
    elts = jQuery("div.virtualpatient.treatment-selection").find("input[type='checkbox']:checked");
    if (elts.length > 0) {
        jQuery("input[type='checkbox']").prop("disabled", true);
        jQuery("div.combination-therapy").show();
    }
    
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
        
        // Make sure combinations are selected if visible
        if (jQuery("div.combination-therapy").is(":visible")) {
            selector = "div.treatment-type input[type='checkbox']:checked";    
            if (jQuery(selector).length !== 2) {
                alert('Please select two therapies to combine.');
                return false;
            } else {
                return true;
            }
        }
    });  
    
    // Prescriptions
    var carousel = jQuery('div.prescribe .carousel');
    if (carousel.length > 0) {        
        jQuery("div.prescribe .carousel").carousel({interval: false});
        jQuery("div.prescribe a.btn.prescription-one").hide();
        
        var check_prescription_complete = function() {
            var form  = jQuery("div.virtualpatient.prescribe").parents("form")[0];
            var complete = true;
            
            var children = jQuery(form).find("select");
            jQuery.each(children, function() {
                if (complete) {
                    var value = jQuery(this).val();
                    complete = value !== undefined && value.length > 0 &&
                        jQuery(this).val().trim() !== '-----';
                }
            });
            
            if (complete) {
                jQuery(form).find("input[type='submit']").show();
            } else {
                jQuery(form).find("input[type='submit']").hide();
            }
            return complete;
        };
        
        if (check_prescription_complete()) {
            jQuery("div.prescribe select").attr("disabled", "disabled");
        }
        
        jQuery("div.prescribe a.btn.prescription-one").click(function() {
            jQuery(this).hide();
            jQuery("div.prescribe a.btn.prescription-two").show();
        });

        jQuery("div.prescribe a.btn.prescription-two").click(function() {
            jQuery(this).hide();
            jQuery("div.prescribe a.btn.prescription-one").show();
        });
        
        jQuery("div.prescribe select").change(function() {
            check_prescription_complete();
        });        
    }

});