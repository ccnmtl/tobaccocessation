_dropped = false


//Deal with a Safari repaint issue. If the element is "inline", a bad repaint problem crops up. 
onStart = function (draggable) {
   if (navigator.userAgent.indexOf('Safari') > 0)
   {
      draggable.element.style.display = 'inline-block';
   }
};

connect(Draggables, 'start', onStart);

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

function validate()
{
    // check if the "available" treatments block is now empty. if yes
    // light up the "next" button, otherwise, hide it or disable it.
    var elems = getElementsByTagAndClassName('*', 'treatment_draggable', 'available_treatments');
    var best = getElementsByTagAndClassName('*', 'treatment_draggable', 'best_treatment');

    if (elems.length == 0 && best.length > 0) {
        getElement('next').style.display = "block";
        getElement('next_disabled').style.display = "none";
        return true;
    } else {
        getElement('next').style.display = "none";
        getElement('next_disabled').style.display = "block";
        return false;
    } 
}

// On successful drop, copy the source node to the destination
function treatmentDropHandler(element, onto, event)
{
   debug("treatmentDropHandler")
   
   node = removeElement(element)
   setStyle(node, {'position': 'relative', 'left': '', 'top': '', 'zindex': '', 'opacity': '1', 'display': 'inline'})
   onto.appendChild(node)
   
   elems = getElementsByTagAndClassName('*', 'treatment_draggable', 'available_treatments')
   $('treatments_to_classify').innerHTML = "" + elems.length
   
   _dropped = true
   
   // @todo check to see if next should be enabled/disabled
   validate();
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
   
   validate();
}
MochiKit.Signal.connect(window, "onload", setupPage)

///////////////////////////////////////////////////////////////////////////////////////////

function get_state()
{
   debug("options: get_state")
   
   // setup a post block with the relevant information & send it up to the server
   doc = {}
   divs = ['best_treatment', 'reasonable_treatment', 'ineffective_treatment', 'harmful_treatment', 'available_treatments']
   forEach(divs,
           function(div) {
	      medications = []
              elements = getElementsByTagAndClassName("*", "treatment_draggable", div)
              forEach(elements,
                      function(element) {
                         medications.push(element.id)
                      })
              doc[div] = medications
            })
   jsontxt = JSON.stringify(doc, null)
   
   return jsontxt
}