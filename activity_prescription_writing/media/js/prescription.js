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
   if (getElement("dosage_2"))
   {
      connectCalloutsDouble()
   }
   else
   {  
      connectCalloutsSingle()
   }
}

function connectCalloutsDouble()
{
   horizontal_line(getElement('dosage_callout'), getElement('dosage'))  
   horizontal_line(getElement('refills_2'), getElement('refills_callout'))
   horizontal_line(getElement('disp_callout'), getElement('disp_2'))
   
}

function connectCalloutsSingle()
{
   vertical_line(getElement('dosage_callout'), getElement('dosage'))
   vertical_line(getElement('disp_correct'), getElement('disp_callout'))
   vertical_line(getElement('refills_callout'), getElement('refills'))
}

MochiKit.Signal.connect(window, "onload", setfocus)
MochiKit.Signal.connect(window, "onload", connectCallouts)

function horizontal_line(topElement, bottomElement)
{
   bottomPos = getElementPosition(bottomElement)
   bottomDim = getElementDimensions(bottomElement)
   
   topPos = getElementPosition(topElement)
   topDim = getElementDimensions(topElement)
   
   fromx = topPos.x + topDim.w/2
   fromy = topPos.y + topDim.h
   tox = bottomPos.x + bottomDim.w/2
   toy = bottomPos.y
   drawlines(fromx, fromy, tox, toy, fromx)

}

function vertical_line(leftElement, rightElement)
{
   x = getElementPosition(leftElement).x + getElementDimensions(leftElement).w
   x2 = getElementPosition(rightElement).x
   y = getElementPosition(rightElement).y + getElementDimensions(rightElement).h/2
   
   drawlines(x, y, x2, y, x2)
}

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

