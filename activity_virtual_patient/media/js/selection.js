function get_state()
{
   debug("get_state")
   doc = {}
   
   doc['prescribe'] = ""
   elem = getFirstElementByTagAndClassName("*", "highlight", 'best_treatment')
   if (elem)
      doc['prescribe'] = elem.id
           
   elems = getElementsByTagAndClassName("*", 'highlight', 'available_treatments')
   doc['combination'] = []
   forEach(elems,
           function(elem)
           {
              idx = elem.id.lastIndexOf('_')
              doc['combination'].push(elem.id.slice(0, idx))
           })
           
   jsontxt = JSON.stringify(doc, null)
   return jsontxt
}

function validate()
{
   debug('validate')
   var combination = false
   elem = getFirstElementByTagAndClassName("*", "highlight", 'best_treatment')
   if (elem)
      combination = elem.id == 'combination'

   maxHighlight = combination ? 3 : 1;
   highlightCount = getElementsByTagAndClassName("*", "highlight").length
   debug("highlightCount: " + highlightCount)
   if (highlightCount == maxHighlight)
   {
      return true
   }
   else if (combination)
   {
      alert('Please select two treatments to combine.')
      return false
   }
   else
   {
      alert('Please select a best treatment choice.')
      return false
   }
}


///////////////////////////////////////////////////////////////////////////////////////////

function setupPage()
{
   debug("setupPage")
   checkMaxHighlighted()
}

MochiKit.Signal.connect(window, "onload", setupPage)

///////////////////////////////////////////////////////////////////////////////////
// controlling the combination eccentricities here

MAX_COMBOTREATMENT_COUNT = 2
MAX_TREATMENT_COUNT = 1

function onSelectBestTreatment(elem)
{
   debug("onSelectBestTreatment " + elem.id)
   
   if (!hasElementClass(elem, 'highlight'))
   {
      // untoggle all classes that may be highlighted
      highlighted = getElementsByTagAndClassName("*", "highlight")
      forEach(highlighted,
           function(item)
           {
               toggleElementClass('highlight', item)
               if (item.id == 'combination')
                  hideCombinationView()         
           })
      
      // highlight the selected treatment
      toggleElementClass('highlight', elem)
      if (elem.id == "combination")
      {
         showCombinationView()
      }
      else
      {
         setStyle('combination_directions', {'display':'none'})
         setStyle('singletreatment_directions', {'display':'block'})
         
      }
   }
}

function onSelectCombinationTreatment(elem)
{
   debug("onSelectCombinationTreatment")
   // are we at the maximum treatments allowed? max treatments varies based
   // on whether we're dealing with a combination situation or not
   
   highlightCount = getElementsByTagAndClassName("*", "highlight", $('available_treatments')).length
   if (highlightCount >= MAX_COMBOTREATMENT_COUNT && !hasElementClass(elem, 'highlight'))
   {
      alert("You've already chosen two treatments to combine. Please deselect one of your choices and reselect this choice.")
      return
   }
   
   // nope, highlight the treatment
   toggleElementClass('highlight', elem)

   // are we at the maximum treatments allowed now?
   newHighlightCount = getElementsByTagAndClassName("*", "highlight", $('available_treatments')).length
   $('treatments_to_combine').innerHTML = 2 - newHighlightCount

}

function checkMaxHighlighted()
{
   var combination = false
   elem = getFirstElementByTagAndClassName("*", "highlight", 'best_treatment')
   if (elem)
      combination = elem.id == 'combination'

   maxHighlight = combination ? 3 : 1;
   highlightCount = getElementsByTagAndClassName("*", "highlight").length
           
}

function showCombinationView()
{
   debug('showCombinationView')
   
   // show the treatments box
   setStyle($('available_treatments_box'), {'display':'block'})
   
   setStyle($('combination_directions'), {'display':'block'})
   setStyle($('singletreatment_directions'), {'display':'none'})
}
   
function hideCombinationView()
{
   debug('hideCombinationView')
   
   setStyle($('available_treatments_box'), {'display':'none'})
   
   setStyle($('combination_directions'), {'display':'none'})
   setStyle($('singletreatment_directions'), {'display':'block'})
      
   
   elems = getElementsByTagAndClassName("*", "treatment_draggable")
   forEach(elems,
           function(elem)
           {
               removeElementClass(elem, 'highlight')
           })
}