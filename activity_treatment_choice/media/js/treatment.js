function debug(string)
{
   if (true)
      log("DEBUG " + string)
}

function removeClassFromAcceptList(element, node)
{
   clazzName = String(element.className.split(' ', 1))
   
   for (i=0; i < _droppables.length; i++)
   {
      if (_droppables[i].element.id == node.id)
      {
         _droppables[i].options.accept.splice(_droppables[i].options.accept.indexOf(clazzName), 1);
         
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
         _droppables[i].options.accept.push(clazzName);
         
         debug("addClassToAcceptList " + clazzName + " [" + _droppables[i].options.accept + "]")
      }
   }   
}

_dropped = false;
_counter = 5;
_droppables = null;


//On successful drop, "snap" the element back into place immediately, 
//otherwise, use the MochiKit "move" function to animate the
//element's journey back to its resting spot. Copied code partially
//from default MochiKit revert function -- DragAndDrop.js
function reverteffect(innerelement, top_offset, left_offset)
{
   debug("reverteffect");

   var dur = 0
   if (!_dropped)            
      dur = Math.sqrt(Math.abs(top_offset ^ 2) + Math.abs(left_offset ^ 2)) * 0.02; 
    
   _dropped = false
    
   return new (MochiKit.Visual.Move)(innerelement, {x: - left_offset, y: - top_offset, duration: dur});
}

// On successful drop, copy the source node to the destination
function treatmentDropHandler(element, onto, event)
{
   debug("treatmentDropHandler");
   
   if (hasElementClass(element, "treatment_trashable"))
   {
      debug("dropping a trashable element. just copy from source to destination")
      
      source = element.parentNode
      addClassToAcceptList(element, source)
      
      onto.appendChild(element)
      //source.removeChild(element)
   }
   else
   {
      debug("dropping an element directly from the toolbox.")
      var newnode = element.cloneNode(true)
      id = _counter++
      newnode.id = "treatment_" + id
      
      onto.appendChild(newnode)
      
      // clear the styles that were picked up from drag/drop & the specific background styling
      setStyle(newnode, {'position': 'relative', 'left': '', 'top': '', 'zindex': '', 'opacity': '1'})
      removeElementClass(newnode, 'treatment_draggable')
      addElementClass(newnode, 'treatment_trashable')
      
      // This item is also draggable, and can be trashed in the treatments window
      new Draggable(newnode, { 
         revert: true, 
         reverteffect: reverteffect
      });
   }
   
   // remove the elements' class from the destination's accept list
   removeClassFromAcceptList(element, onto)
   
   _dropped = true;
}

//On successful drop, copy the source node to the destination
function treatmentTrashHandler(element, onto, event)
{
   debug("treatmentTrashHandler: dropping " + element.id + " onto " + onto.id );

   // readd this item from the accept list
   for (i=0; i < _droppables.length; i++)
   {
      if (_droppables[i].element.id == element.parentNode.id)
      {
         clazz = element.className.slice(0, element.className.indexOf(' '));
         _droppables[i].options.accept.push(clazz);
      }
   }
   
   removeElement(element);
   
   _dropped = true;
}

function setupTreatmentDropZones()
{
   debug("setupTreatmentDropZones");
   
   var draggables = getElementsByTagAndClassName(null, 'treatment_draggable');
   
   forEach(draggables,
         function(elem) {
            draggable = new Draggable(elem, { 
               revert: true,
               reverteffect: reverteffect
               });
         });
   
   _droppables = new Array();
   
   _droppables[0] = new Droppable('treatment_light_smoker', { 
      accept: ['patch', 'gum', 'lozenge', 'inhaler', 'nasalspray'], // Array of CSS classes
      ondrop: treatmentDropHandler
   });
   
   _droppables[1] = new Droppable('treatment_moderate_smoker', {
      accept: ['patch', 'chantix', 'bupropion'],
      ondrop: treatmentDropHandler
   });
   
   _droppables[2] = new Droppable('treatment_heavy_smoker', { 
      accept: ['combination', 'chantix'],
      ondrop: treatmentDropHandler
   });
   
   new Droppable('treatments', { 
      accept: [ 'treatment_trashable' ],
      ondrop: treatmentTrashHandler
   });
}
MochiKit.Signal.connect(window, "onload", setupTreatmentDropZones);

