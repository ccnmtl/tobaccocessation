_light_smoker_options = ['patch', 'gum', 'lozenge', 'inhaler', 'nasalspray']
_moderate_smoker_options = ['patch', 'chantix', 'bupropion']
_heavy_smoker_options = ['combination', 'chantix']
                            
function debug(string)
{
   if (false)
      log("DEBUG " + string)
}

function validate()
{
   debug('validate')
   if (checkForSuccess())
   {
      window.location = $('next').href
      return true
   }
   else
   {
      alert("Please complete the exercise before continuing")
      return false
   }
}

function removeClassFromAcceptList(element, node)
{
   clazzName = String(element.className.split(' ', 1))
   
   for (i=0; i < _droppables.length; i++)
   {
      if (_droppables[i].element.id == node.id)
      {
         // find the index
         idx = -1
         for (j=0; j < _droppables[i].options.accept.length; j++)
         {
            if (_droppables[i].options.accept[j] == clazzName)
               idx = j
         }
         _droppables[i].options.accept.splice(idx, 1)
         
         debug("removeClassFromAcceptList " + clazzName + " [" + _droppables[i].options.accept + "]")
      }
   }
}

function addClassToAcceptList(element, node)
{
   clazzName = element.className.split(' ', 1)
   
   for (i=0; i < _droppables.length; i++)
   {
      if (_droppables[i].element.id == node.id)
      {
         _droppables[i].options.accept.push(clazzName)
         
         debug("addClassToAcceptList " + clazzName + " [" + _droppables[i].options.accept + "]")
      }
   }   
}

function checkForSuccess()
{
   debug("checkForSuccess") 
  
   // If each smoker quantity div has an empty accept list, then the answers are correct. 
   smoker_quantity_divs = ['treatment_light_smoker', 'treatment_moderate_smoker', 'treatment_heavy_smoker'] 
                           
   for (i=0; i < _droppables.length; i++) 
   { 
      for(j=0; j < smoker_quantity_divs.length; j++) 
      { 
         if (_droppables[i].element.id == smoker_quantity_divs[j] && _droppables[i].options.accept.length > 0) 
         { 
            return false 
         } 
      } 
   } 
  
   setStyle('success_overlay', {'display': 'inline'})
   setStyle('span_' + $('next_section_slug').value, {'display': 'none'})
   setStyle($('next_section_slug').value, {'display': 'inline'})
   return true 
}

_dropped = false
_counter = 5
_droppables = []

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

// On successful drop, copy the source node to the destination
function treatmentDropHandler(element, onto, event)
{
   debug("treatmentDropHandler")
   
   var newnode = element.cloneNode(true)
   id = _counter++
   newnode.id = "treatment_" + id
   
   onto.appendChild(newnode)
   
   // clear the styles that were picked up from drag/drop & the specific background styling
   setStyle(newnode, {'position': 'relative', 'left': '', 'top': '', 'zindex': '', 'opacity': '1'})
   removeElementClass(newnode, 'treatment_draggable')
      addElementClass(newnode, 'treatment_trashable')
   
   // remove the elements' class from the destination's accept list
   removeClassFromAcceptList(element, onto)
   
   checkForSuccess()
   _dropped = true
   setCounters()
}

function setupTreatmentDropZones()
{
   debug("setupTreatmentDropZones")
   
   var draggables = getElementsByTagAndClassName(null, 'treatment_draggable')
   
   forEach(draggables,
         function(elem) {
            draggable = new Draggable(elem, { 
               revert: true,
               reverteffect: reverteffect
               })
         })
   
   _droppables = new Array()
   
   _droppables[0] = new Droppable('treatment_light_smoker', { 
      accept: _light_smoker_options.slice(), // Array of CSS classes
      ondrop: treatmentDropHandler
   })
   
   _droppables[1] = new Droppable('treatment_moderate_smoker', {
      accept: _moderate_smoker_options.slice(),
      ondrop: treatmentDropHandler
   })
   
   _droppables[2] = new Droppable('treatment_heavy_smoker', { 
      accept: _heavy_smoker_options.slice(),
      ondrop: treatmentDropHandler
   })
   
   $('next').onclick = validate
}

function loadStateSuccess(doc)
{
      // add each element to the correct div
      // remove the element from the "accept" list
      forEach(doc.smoker_quantity_state,
              function(state)
              {
                 div = getElement(state.id)
                 
                 // create a child for each treatment listed
                 forEach(state.treatments, 
                      function(treatment) 
                      {
                          // clone the template node
                          var newnode = $('treatment_template').cloneNode(true)
                          newnode.id = "treatment_" + _counter++
                          setStyle(newnode, {'display': 'inline'})
                          addElementClass(newnode, treatment)
                          addElementClass(newnode, "treatment_trashable")
                          
                          // fix the src on the image
                          image = getFirstElementByTagAndClassName("img", "", newnode)
                          image.src = image.src + treatment + ".jpg"
                          
                          // This item is also draggable, and can be trashed in the treatments window
                          new Draggable(newnode, { 
                             revert: true, 
                             reverteffect: reverteffect
                          })
                          
                          removeClassFromAcceptList(newnode, div)
                          
                          div.appendChild(newnode)
                      })
              })

   
   checkForSuccess()
   setCounters()
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
   url = 'http://' + location.hostname + ':' + location.port + "/activity/treatment/load/"
   deferred = loadJSONDoc(url)
   deferred.addCallbacks(loadStateSuccess, loadStateError)
}

MochiKit.Signal.connect(window, "onload", setupTreatmentDropZones)
MochiKit.Signal.connect(window, "onload", loadState)

function saveState()
{
   debug("saveState")
 
   doc = 
   {
      'smoker_quantity_state': [],
      'complete': checkForSuccess()
   }

   smoker_quantity_divs = ['treatment_light_smoker', 'treatment_moderate_smoker', 'treatment_heavy_smoker']
              
   forEach(smoker_quantity_divs,
           function(div) {
              state = {}
              state['id'] = div
              state['treatments'] = []
	      children = getElementsByTagAndClassName('*', 'treatment_trashable', div)
              forEach(children, 
                      function(child) 
                      {
                         clazzName = child.className.split(' ', 1)
                         state['treatments'].push(clazzName)
                      })
              doc['smoker_quantity_state'].push(state)
           })

   // save state via a synchronous request. 
   url = 'http://' + location.hostname + ':' + location.port + "/activity/treatment/save/"
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':JSON.stringify(doc, null)}));
}

MochiKit.Signal.connect(window, "onbeforeunload", saveState)

function saveStateSuccess()
{
   debug("saveStateSuccess")
   
   _droppables[0].options.accept = _light_smoker_options.slice()
   
   _droppables[1].options.accept = _moderate_smoker_options.slice()
   
   _droppables[2].options.accept = _heavy_smoker_options.slice()
   
   setStyle('span_' + $('next_section_slug').value, {'display': 'inline'})
   setStyle($('next_section_slug').value, {'display': 'none'})
   setStyle('success_overlay', {'display': 'none'})
   setCounters()
}

function saveStateError()
{
   debug("saveStateError")
}

function clearState()
{
   debug("saveState")
   url = 'http://' + location.hostname + ':' + location.port + "/activity/treatment/save/"
 
   doc = 
   {
      'smoker_quantity_state': []
   }

   smoker_quantity_divs = ['treatment_light_smoker', 'treatment_moderate_smoker', 'treatment_heavy_smoker']
              
   forEach(smoker_quantity_divs,
           function(div) {
              children = getElementsByTagAndClassName('*', 'treatment_trashable', div)
              forEach(children, 
                      function(child) 
                      {
                         removeElement(child)
                      })
           })
           
   // contact the server and save the clearedstate
  deferred = doXHR(url, 
        { 
           method: 'POST', 
           sendContent: queryString({'json': JSON.stringify(doc, null)})
        });
  deferred.addCallbacks(saveStateSuccess, saveStateError);
}

function setCounters()
{
   debug('setCounters')
   for (i=0; i < _droppables.length; i++) 
   { 
      if (_droppables[i].element.id == 'treatment_light_smoker')
      {
         $("light_smoker_countdown").innerHTML = _droppables[i].options.accept.length
      }
      else if (_droppables[i].element.id == 'treatment_moderate_smoker')
      {
         $('moderate_smoker_countdown').innerHTML = _droppables[i].options.accept.length
      }
      else if (_droppables[i].element.id == 'treatment_heavy_smoker')
      {
         $('heavy_smoker_countdown').innerHTML = _droppables[i].options.accept.length
      }
   } 
}

