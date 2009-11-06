function debug(string)
{
   if (true)
      log("DEBUG " + string)
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
   vertical_line(getElement('dosage_callout'), getElement('dosage'))
   vertical_line(getElement('disp_callout'), getElement('disp'))
   vertical_line(getElement('refills_callout'), getElement('refills'))
}

function connectCalloutsSingle()
{
   vertical_line(getElement('dosage_callout'), getElement('dosage'))
   vertical_line(getElement('disp_callout'), getElement('disp'))
   vertical_line(getElement('refills_callout'), getElement('refills'))
   
}

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

function setBackgroundColor(ctrl)
{
   if (ctrl.value.length > 0)
   {
      setStyle(ctrl.id, { 'background-color': 'white' })
   }
   else
   {
      setStyle(ctrl.id, { 'background-color': '#F8F5E1' })
   }
}

function onEditChange(ctrl)
{
   setBackgroundColor(ctrl)
   maybeEnableNext()
}

function maybeEnableNext()
{
   if (!$('dosage_correct'))
   {
      // is there content in all 3 fields or all 6 in case of double prescriptions
      // enable the next button, otherwise, hide it.
      gonext = false
      
      gonext = $('dosage').value && $('dosage').value.length > 0 &&
               $('disp').value && $('disp').value.length > 0 && 
               $('sig').value && $('sig').value.length > 0 &&
               $('refills').value && $('refills').value.length > 0 
      
      if ($('dosage_2'))
      {
         gonext = gonext &&
               $('dosage_2').value && $('dosage_2').value.length > 0 &&
               $('disp_2').value && $('disp_2').value.length > 0 && 
               $('sig_2').value && $('sig_2').value.length > 0 &&
               $('refills_2').value && $('refills_2').value.length > 0
      }
      
      if (gonext)
      {
         setStyle('next', {'display': 'inline'}) 
         return true 
      }
      else
      {
         setStyle('next', {'display': 'none'}) 
         return false
      }
   }
}

function loadStateSuccess(doc)
{
   debug('loadStateSuccess')
   
   if (doc && doc[$('medication_name').value])
   {
      rx = doc[$('medication_name').value]
      $('dosage').value = rx['dosage']
      $('disp').value = rx['disp']
      $('sig').value = rx['sig']
      $('refills').value = rx['refills']
                              
      if ($('dosage_2'))
      {
         $('dosage_2').value = rx['dosage_2']
         
         $('disp_2').value = rx['disp_2']
         
         $('sig_2').value = rx['sig_2']
         
         $('refills_2').value = rx['refills_2']
      }
   }
                                                                                                                                                                       
   setBackgroundColor($('dosage'))
   setBackgroundColor($('disp'))
   setBackgroundColor($('sig'))
   setBackgroundColor($('refills'))
   
   if ($('dosage_2'))
   {
      setBackgroundColor($('dosage_2'))
      setBackgroundColor($('disp_2'))
      setBackgroundColor($('sig_2'))
      setBackgroundColor($('refills_2'))
   }
   
  if ($('dosage_correct'))
     connectCallouts()
     
  maybeEnableNext()
}

function loadStateError(err)
{
   debug("loadStateError")
   // @todo: Find a spot to display an error or decide just to fail gracefully
   // $('errorMsg').innerHTML = "An error occurred loading your state (" + err + "). Please start again."
}

function loadState()
{
   debug("loadState")
   if (!$('dosage_correct'))
   {
      setStyle('next', {'display': 'none'})
   }
   url = 'http://' + location.hostname + ':' + location.port + "/activity/prescription/load/"
   deferred = loadJSONDoc(url)
   deferred.addCallbacks(loadStateSuccess, loadStateError)
}

function setfocus()
{
   if (!$('dosage_correct'))
      $("dosage").focus()
}

MochiKit.Signal.connect(window, "onload", loadState)
MochiKit.Signal.connect(window, "onload", setfocus)

function numeric(field) {
    var regExpr = new RegExp("^[0-9]$");
    if (!regExpr.test(field.value)) 
    {
      // Case of error
      field.value = "";
    }
}

function saveState()
{
   if (!$('dosage_correct'))
   {
      debug("saveState")
      url = 'http://' + location.hostname + ':' + location.port + "/activity/prescription/save/"
    
      rx = 
      {
         'dosage' : $('dosage').value,
         'disp' : $('disp').value,
         'sig' : $('sig').value,
         'refills' : $('refills').value,
      }
      
      if ($('dosage_2'))
      {
         rx['dosage_2'] = $('dosage_2').value
         rx['disp_2'] = $('disp_2').value
         rx['sig_2'] = $('sig_2').value
         rx['refills_2'] = $('refills_2').value
      }
      
      doc = {}
      doc[$('medication_name').value] = rx
      
      // save state via a synchronous request. 
      var sync_req = new XMLHttpRequest();  
      sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
      sync_req.open("POST", url, false);
      sync_req.send(queryString({'json':JSON.stringify(doc, null)}));
   }
}

MochiKit.Signal.connect(window, "onbeforeunload", saveState)

