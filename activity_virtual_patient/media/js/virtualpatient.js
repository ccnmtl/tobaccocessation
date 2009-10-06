function debug(string)
{
   if (true)
      log("DEBUG " + string)
}

_dropped = false

//On successful drop, "snap" the element back into place immediately, 
//otherwise, use the MochiKit "move" function to animate the
//element's journey back to its resting spot. Copied code partially
//from default MochiKit revert function -- DragAndDrop.js
function reverteffect(innerelement, top_offset, left_offset)
{
   debug("reverteffect")

   var dur = 0
   if (!_dropped)            
      dur = Math.sqrt(Math.abs(top_offset ^ 2) + Math.abs(left_offset ^ 2)) * 0.02 
    
   _dropped = false
    
   return new (MochiKit.Visual.Move)(innerelement, {x: - left_offset, y: - top_offset, duration: dur})
}

function maybeAllowUserToContinue()
{
   // check if the "available" treatments block is now empty. if yes
   // light up the "next" button, otherwise, hide it or disable it.
   
   elems = getElementsByTagAndClassName('*', 'treatment_draggable', 'available_treatments')
   
   getElement('next_button').disabled = elems.length > 0
   
   if (elems.length < 1)
      pulsate(getElement('next_button'))
}

// On successful drop, copy the source node to the destination
function treatmentDropHandler(element, onto, event)
{
   debug("treatmentDropHandler")
   
   node = removeElement(element)
   setStyle(node, {'position': 'relative', 'left': '', 'top': '', 'zindex': '', 'opacity': '1'})
   onto.appendChild(node)
   
   maybeAllowUserToContinue()

   _dropped = true
}

function setupDragDrop()
{
   debug("setupDragDrop")
   
   var draggables = getElementsByTagAndClassName(null, 'treatment_draggable')
   
   forEach(draggables,
         function(elem) {
            draggable = new Draggable(elem, { 
               revert: true,
               reverteffect: reverteffect
               })
         })
         
   var droppables = getElementsByTagAndClassName(null, 'treatment_droppable')
   
   forEach(droppables,
         function(elem) {
            draggable = new Droppable(elem, { 
               accept: ['treatment_draggable'],
               ondrop: treatmentDropHandler
               })
         })
}

function setupSelection()
{
   saveStateAsynchronous()
   setStyle($('reasonable_treatment_box'), { 'display':'none' })
   setStyle($('ineffective_treatment_box'), { 'display':'none' })
   setStyle($('harmful_treatment_box'), { 'display':'none' })
   setStyle($('available_treatments_box'), { 'display':'none' })
}

MochiKit.Signal.connect(window, "onload", loadState)
MochiKit.Signal.connect(window, "onunload", saveStateSynchronous)

///////////////////////////////////////////////////////////////////////////////////////////

function loadStateSuccess(doc)
{
   debug("loadStateSuccess")
   
   if (doc.html != undefined)
   {
      $('content').innerHTML = doc.html
   }
   setupDragDrop()
   maybeAllowUserToContinue()
}

function loadStateError(err)
{
   debug("loadStateError")
   // ignore?
}

function loadState()
{
   debug("loadState")
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/load/"
   
   deferred = loadJSONDoc(url, {'url': location.pathname});
   deferred.addCallbacks(loadStateSuccess, loadStateError);
}

function saveStateAsynchronous()
{
   debug("saveStateAsynchronous")
   doc = get_state()
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/save/"
   deferred = doXHR(url, 
      { 
         method: 'POST', 
         sendContent: queryString({'json': doc})
      });
   deferred.addCallbacks(saveStateSuccess, saveStateError);
}

function saveStateSynchronous()
{
   debug("saveStateSynchronous")
   doc = get_state()
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/save/"

   // save state via a synchronous request. 
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':JSON.stringify(doc, null)}));
}

function saveStateSuccess(doc)
{
   debug("saveStateSuccess")
}

function saveStateError(err)
{
   debug('saveStateError')
}

function get_state()
{
   doc = 
   {
      'url': location.pathname,
      'html': strip($('content').innerHTML),
   }
   return JSON.stringify(doc, null)   
}