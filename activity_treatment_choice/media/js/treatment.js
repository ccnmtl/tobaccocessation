function debug(string)
{
   if (false)
      log("DEBUG " + string)
}

function removeClassFromAcceptList(element, node)
{
   clazzName = String(element.className.split(' ', 1))
   
   for (i=0; i < _droppables.length; i++)
   {
      if (_droppables[i].element.id == node.id)
      {
         _droppables[i].options.accept.splice(_droppables[i].options.accept.indexOf(clazzName), 1)
         
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
            setStyle('next', {'display': 'none'}) 
            return false 
         } 
      } 
   } 
  
   setStyle('next', {'display': 'inline'})

   setStyle('span_' + $('next_section_slug').value, {'display': 'none'})
   setStyle($('next_section_slug').value, {'display': 'inline'})
   return true 
}

_dropped = false
_counter = 5
_droppables = null

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
   
   if (hasElementClass(element, "treatment_trashable"))
   {
      source = element.parentNode
      addClassToAcceptList(element, source)
      
      onto.appendChild(element)
   }
   else
   {
      var newnode = element.cloneNode(true)
      id = _counter++
      newnode.id = "treatment_" + id
      
      onto.appendChild(newnode)
      
      // clear the styles that were picked up from drag/drop & the specific background styling
      setStyle(newnode, {'position': 'relative', 'left': '', 'top': '', 'zindex': '', 'opacity': '1'})
      removeElementClass(newnode, 'treatment_draggable')
      addElementClass(newnode, 'treatment_trashable')
   }
   
   // remove the elements' class from the destination's accept list
   removeClassFromAcceptList(element, onto)
   
   checkForSuccess()
   _dropped = true
}

//On successful drop, copy the source node to the destination
function treatmentTrashHandler(element, onto, event)
{
   debug("treatmentTrashHandler: dropping " + element.id + " onto " + onto.id )

   // readd this item from the accept list
   for (i=0; i < _droppables.length; i++)
   {
      if (_droppables[i].element.id == element.parentNode.id)
      {
         clazz = element.className.slice(0, element.className.indexOf(' '))
         _droppables[i].options.accept.push(clazz)
      }
   }
   
   removeElement(element)
   
   _dropped = true
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
      accept: ['patch', 'gum', 'lozenge', 'inhaler', 'nasalspray'], // Array of CSS classes
      ondrop: treatmentDropHandler
   })
   
   _droppables[1] = new Droppable('treatment_moderate_smoker', {
      accept: ['patch', 'chantix', 'bupropion'],
      ondrop: treatmentDropHandler
   })
   
   _droppables[2] = new Droppable('treatment_heavy_smoker', { 
      accept: ['combination', 'chantix'],
      ondrop: treatmentDropHandler
   })
}

function loadStateSuccess(doc)
{
   if (doc.version == 1)
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
                          image = getFirstElementByTagAndClassName("img", "", parent=newnode)
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
   }
   
   checkForSuccess()
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
   url = 'http://' + location.hostname + ':' + location.port + "/activity/treatment/save/"
 
   doc = 
   {
      'version': 1,
      'smoker_quantity_state': [],
      'complete': checkForSuccess()
   }

   smoker_quantity_divs = ['treatment_light_smoker', 'treatment_moderate_smoker', 'treatment_heavy_smoker']
              
   forEach(smoker_quantity_divs,
           function(div) {
              parent = getElement(div)
              state = {}
              state['id'] = parent.id
              state['treatments'] = []
              children = getElementsByTagAndClassName(null, 'treatment_trashable', parent)
              forEach(children, 
                      function(child) 
                      {
                         clazzName = child.className.split(' ', 1)
                         state['treatments'].push(clazzName)
                      })
              
              doc['smoker_quantity_state'].push(state)
           })

   // save state via a synchronous request. 
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':JSON.stringify(doc, null)}));
}

MochiKit.Signal.connect(window, "onbeforeunload", saveState)

function saveStateSuccess()
{
   debug("saveStateSuccess")
   
   _droppables[0].options.accept = ['patch', 'gum', 'lozenge', 'inhaler', 'nasalspray'], // Array of CSS classes
   
   _droppables[1].options.accept = ['patch', 'chantix', 'bupropion']
   
   _droppables[2].options.accept = ['combination', 'chantix']
                                    
   setStyle('next', {'display':'none'})
   
   setStyle('span_' + $('next_section_slug').value, {'display': 'inline'})
   setStyle($('next_section_slug').value, {'display': 'none'})

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
      'version': 1,
      'smoker_quantity_state': []
   }

   smoker_quantity_divs = ['treatment_light_smoker', 'treatment_moderate_smoker', 'treatment_heavy_smoker']
              
   forEach(smoker_quantity_divs,
           function(div) {
              // remove all the children
              parent = getElement(div)
              children = getElementsByTagAndClassName(null, 'treatment_trashable', parent)
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

