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
   
   getElement('next').disabled = elems.length > 0
   
   if (elems.length < 1)
   {
      setStyle(getElement('next'), {'display': 'inline'})
      pulsate(getElement('next'))
   }
   else
   {
      setStyle(getElement('next'), {'display': 'none'})
   }
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

///////////////////////////////////////////////////////////////////////////////////////////

function setupPage(doc)
{
   debug("setupPage")
   
   setupDragDrop()
   maybeAllowUserToContinue()
}
MochiKit.Signal.connect(window, "onload", setupPage)

///////////////////////////////////////////////////////////////////////////////////////////

function get_state()
{
   debug("options: get_state")
   
   // setup a post block with the relevant information & send it up to the server
   doc = { "prescribe": {}, "combination": {} }
   divs = ['best_treatment', 'reasonable_treatment', 'ineffective_treatment', 'harmful_treatment', 'available_treatments']
   forEach(divs,
           function(div) {
              medications = []
              elements = getElementsByTagAndClassName("*", "treatment_draggable", parent=div)
              forEach(elements,
                      function(element) {
                 
                         medications.push(element.id)
                      })
              doc[div] = medications
            })
   jsontxt = JSON.stringify(doc, null)
   return jsontxt
}