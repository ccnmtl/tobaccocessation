/* exported onEditChange, getElementPosition, getElementDimensions */

function connectCallouts() {
    if (document.getElementById('dosage_2')) {
        connectCalloutsDouble();
    } else {
        connectCalloutsSingle();
    }
}

function connectCalloutsDouble() {
    vertical_line(document.getElementById('dosage_callout'),
        document.getElementById('dosage'));
    vertical_line(document.getElementById('disp_callout'),
        document.getElementById('disp'));
    vertical_line(document.getElementById('refills_callout'),
        document.getElementById('refills'));
}

function connectCalloutsSingle() {
    vertical_line(document.getElementById('dosage_callout'),
        document.getElementById('dosage'));
    vertical_line(document.getElementById('disp_callout'),
        document.getElementById('disp'));
    vertical_line(document.getElementById('refills_callout'),
        document.getElementById('refills'));
}

function vertical_line(leftElement, rightElement) {
    var $leftEl = jQuery(leftElement);
    var $rightEl = jQuery(rightElement);
    var x = $leftEl.offset().left + $leftEl.outerWidth();
    var x2 = $rightEl.offset().left;
    var y = $rightEl.offset().top + ($rightEl.outerHeight() / 2);

    drawlines(x, y, x2, y, x2);
}

function drawlines(from_x, from_y, to_x, to_y, x_break) {
    // make the left hline go all the way to the right
    // edge of the center vline. Add 2 pixels, if necessary.
    var extra = (from_y > to_y) ? 2 : 0;
    hline(from_x, x_break + extra, from_y);
    vline(from_y, to_y, x_break);
    hline(x_break, to_x, to_y);
}

function hline(from, to, y) {
    if (from > to) {
        var temp = to;
        to = from;
        from = temp;
    }
    var $newDiv = jQuery('<div class="connecting_line"></div>');
    jQuery('body').append($newDiv);
    $newDiv.css({
        'left': from + 'px',
        'top': y + 'px' ,
        'width': (to - from) + 'px',
        'height': '2px'
    });
}

function vline(from, to, x) {
    if (from > to) {
        var temp = to;
        to = from;
        from = temp;
    }
    var $newDiv = jQuery('<div class="connecting_line"></div>');
    jQuery('body').append($newDiv);
    $newDiv.css({
        'left': x + 'px',
        'top': from + 'px' ,
        'height': (to - from) + 'px',
        'width': '2px'
    });
}

function setBackgroundColor(id) {
    var $el = jQuery('#' + id);
    if ($el.length > 0 && $el.val().length > 0) {
        $el.css('background-color', 'white');
    } else {
        $el.css('background-color', '#f8db9f');
    }
}

// eslint-disable-next-line no-unused-vars
function onEditChange(ctrl) {
    setBackgroundColor(ctrl.id);
}

function initPage() {
    if (!document.getElementById('dosage_correct')) {
        jQuery('#dosage').focus();
    }

    setBackgroundColor('dosage');
    setBackgroundColor('disp');
    setBackgroundColor('sig');
    setBackgroundColor('refills');

    if (document.getElementById('dosage_2')) {
        setBackgroundColor('dosage_2');
        setBackgroundColor('disp_2');
        setBackgroundColor('sig_2');
        setBackgroundColor('refills_2');
    }

    if (document.getElementById('dosage_correct')) {
        connectCallouts();
    }
}

jQuery(document).ready(function() {
    initPage();
});
