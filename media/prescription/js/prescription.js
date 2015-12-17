function connectCallouts() {
    if (getElement('dosage_2')) {
        connectCalloutsDouble();
    } else {
        connectCalloutsSingle();
    }
}

function connectCalloutsDouble() {
    vertical_line(getElement('dosage_callout'), getElement('dosage'));
    vertical_line(getElement('disp_callout'), getElement('disp'));
    vertical_line(getElement('refills_callout'), getElement('refills'));
}

function connectCalloutsSingle() {
    vertical_line(getElement('dosage_callout'), getElement('dosage'));
    vertical_line(getElement('disp_callout'), getElement('disp'));
    vertical_line(getElement('refills_callout'), getElement('refills'));
}

function horizontal_line(topElement, bottomElement) {
    var bottomPos = getElementPosition(bottomElement);
    var bottomDim = getElementDimensions(bottomElement);

    var topPos = getElementPosition(topElement);
    var topDim = getElementDimensions(topElement);

    var fromx = topPos.x + topDim.w / 2;
    var fromy = topPos.y + topDim.h;
    var tox = bottomPos.x + bottomDim.w / 2;
    var toy = bottomPos.y;
    drawlines(fromx, fromy, tox, toy, fromx);
}

function vertical_line(leftElement, rightElement) {
    var x = getElementPosition(leftElement).x +
        getElementDimensions(leftElement).w;
    var x2 = getElementPosition(rightElement).x;
    var y = getElementPosition(rightElement).y +
        getElementDimensions(rightElement).h / 2;

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
    if (from > to) { var temp = to; to = from; from = temp; }
    var newdiv = DIV({'class': 'connecting_line'});
    appendChildNodes(currentDocument().body, newdiv);
    setStyle(newdiv , {'left': from + 'px',
                       'top': y + 'px' ,
                       'width': (to - from) + 'px',
                       'height': '2px'});
}

function vline(from, to, x) {
    if (from > to) { var temp = to; to = from; from = temp; }
    var newdiv = DIV({'class': 'connecting_line'});
    appendChildNodes(currentDocument().body, newdiv);
    setStyle(newdiv ,
             {'left': x + 'px',
              'top': from + 'px' ,
              'height': (to - from) + 'px',
              'width': '2px'});
}

function setBackgroundColor(ctrl) {
    if (ctrl.value.length > 0) {
        setStyle(ctrl.id, {'background-color': 'white'});
    } else {
        setStyle(ctrl.id, {'background-color': '#f8db9f'});
    }
}

function onEditChange(ctrl) {
    setBackgroundColor(ctrl);
}

function initPage() {
    if (!$('dosage_correct')) {
        $('dosage').focus();
    }

    setBackgroundColor($('dosage'));
    setBackgroundColor($('disp'));
    setBackgroundColor($('sig'));
    setBackgroundColor($('refills'));

    if ($('dosage_2')) {
        setBackgroundColor($('dosage_2'));
        setBackgroundColor($('disp_2'));
        setBackgroundColor($('sig_2'));
        setBackgroundColor($('refills_2'));
    }

    if ($('dosage_correct')) {
        connectCallouts();
    }
}

MochiKit.Signal.connect(window, 'onload', initPage);
