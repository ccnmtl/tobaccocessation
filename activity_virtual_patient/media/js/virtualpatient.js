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

//////////////////////////////////////////////////////////////////////////////

function saveStateSuccess(response)
{
   debug("saveStateSuccess")
   doc = JSON.parse(response.responseText, null)
   window.location = doc.redirect 
}

function saveStateError(err)
{
   debug("saveStateError")
}

function saveStateAsynch()
{
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/post/" + $('page_id').value + "/" + $('patient_id').value + "/"

   jsontxt = get_state() // defined by page
   
   deferred = doXHR(url, 
         { 
            method: 'POST', 
            sendContent: queryString({'json': jsontxt})
         });
   deferred.addCallbacks(saveStateSuccess, saveStateError);
}

function saveStateSynch()
{
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/post/" + $('page_id').value + "/" + $('patient_id').value + "/"

   jsontxt = get_state() // defined by page
      
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':jsontxt}));
}

MochiKit.Signal.connect(window, "onbeforeunload", saveStateSynch)


///////////////////////////////////////////////////////////////////////////////////////////

function loadStateSuccess(doc)
{
   debug("loadStateSuccess")
   
   set_state(doc) // defined in the per page view
   
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
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/load/" + $('page_id').value + "/" + $('patient_id').value + "/"
   
   deferred = loadJSONDoc(url, {'url': location.pathname});
   deferred.addCallbacks(loadStateSuccess, loadStateError);
}

MochiKit.Signal.connect(window, "onload", loadState)


