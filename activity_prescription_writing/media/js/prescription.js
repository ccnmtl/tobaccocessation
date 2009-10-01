function numeric(field) {
    var regExpr = new RegExp("^[0-9]$");
    if (!regExpr.test(field.value)) 
    {
      // Case of error
      field.value = "";
    }
}

function setfocus()
{
   $("dosage").focus()
}

function connectCallouts()
{
   // dosage
   var elemPos = getElementPosition('dosage_correct')
   var elemDim = getElementDimensions('dosage_correct')
   
   x = elemPos.x + elemDim.w
   y = elemPos.y + elemDim.h/2
   x2 = getElementPosition('dosage_callout').x
   log(x2)
   drawlines(x, y, x2, y, 700)
   
   // disp
   elemPos = getElementPosition('disp')
   elemDim = getElementDimensions('disp')
   
   x = elemPos.x
   y = elemPos.y + elemDim.h/2
   x2 = getElementPosition('disp_callout').x + getElementDimensions('disp_callout').w
   drawlines(x2, y, x, y, 250)
   
   // refills
   elemPos = getElementPosition('refills_correct')
   elemDim = getElementDimensions('refills_correct')
   
   x = elemPos.x + elemDim.w
   y = elemPos.y + elemDim.h/2
   x2 = getElementPosition('refills_callout').x
   drawlines(x, y, x2, y, 500)
}

MochiKit.Signal.connect(window, "onload", setfocus)
MochiKit.Signal.connect(window, "onload", connectCallouts)

function drawlines (from_x, from_y, to_x, to_y, x_break) {
    // make the left hline go all the way to the right edge of the center vline. Add 2 pixels, if necessary.
    var extra = ( from_y > to_y )? 2 : 0; 
    hline (from_x, x_break + extra, from_y);
    vline (from_y, to_y, x_break);
    hline (x_break, to_x, to_y );
}

function hline (from, to, y) {
    if (from > to) { var temp = to; to = from; from = temp; }
    var newdiv = DIV ( {"class":"connecting_line" });
    appendChildNodes(currentDocument().body, newdiv);
    setStyle( newdiv , { "left": from + 'px', "top" : y + 'px' , "width" : (to - from) + "px", "height" : "2px"});
}

function vline (from, to, x) {
    if (from > to) { var temp = to; to = from; from = temp; }
    var newdiv = DIV ( {"class":"connecting_line" });
    appendChildNodes(currentDocument().body, newdiv);
    setStyle( newdiv , { "left": x + 'px', "top" : from + 'px' , "height" : (to - from) + "px", "width" : "2px"});
}

