function get_state()
{
   debug("get_state")
   doc = {}
   
   doc['prescribe'] = ""
   elem = getFirstElementByTagAndClassName("*", "highlight", parent='best_treatment')
   if (elem)
      doc['prescribe'] = elem.id
           
   elems = getElementsByTagAndClassName("*", 'highlight', parent='available_treatments')
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
   
   // are we at the maximum treatments allowed? max treatments varies based
   // on whether we're dealing with a combination situation or not
   highlightCount = getElementsByTagAndClassName("*", "highlight").length
   debug(highlightCount)
   if (highlightCount >= MAX_TREATMENT_COUNT && !hasElementClass(elem, 'highlight'))
      return
      
   debug('1')
   // nope, highlight the treatment
   toggleElementClass('highlight', elem)
   debug('2')
   if (elem.id == "combination")
   {
      if (hasElementClass(elem, 'highlight'))
         showCombinationView()
      else
         hideCombinationView()
   }
   else
   {
      setStyle('combination_directions', {'display':'none'})
      setStyle('singletreatment_directions', {'display':'block'})
      
      elements = getElementsByTagAndClassName("*", "treatment_draggable", parent='best_treatment')
      forEach(elements,
              function(element) {
                 if (element.id != elem.id)
                 {
                    if (hasElementClass(elem, 'highlight'))
                       setOpacity(element, .5)
                    else
                       setOpacity(element, 1.0)
                 }
              })
   }
   checkMaxHighlighted()
}

function onSelectCombinationTreatment(elem)
{
   debug("onSelectCombinationTreatment")
   // are we at the maximum treatments allowed? max treatments varies based
   // on whether we're dealing with a combination situation or not
   highlightCount = getElementsByTagAndClassName("*", "highlight", parent=$('available_treatments')).length
   if (highlightCount >= MAX_COMBOTREATMENT_COUNT && !hasElementClass(elem, 'highlight'))
      return
      
   // nope, highlight the treatment
   toggleElementClass('highlight', elem)

   // are we at the maximum treatments allowed now?
   newHighlightCount = getElementsByTagAndClassName("*", "highlight", parent=$('available_treatments')).length

   // make sure that all the treatments are correctly enabled/disabled 
   // as the user clicks various treatment options
   comboTreatments = getElementsByTagAndClassName("*", "treatment_draggable", parent=$('available_treatments'))
   forEach(comboTreatments,
           function(med)
           {
               if (!hasElementClass(med, 'highlight'))
               {
                  if (newHighlightCount >= MAX_COMBOTREATMENT_COUNT)
                  {
                     setOpacity(med, .5)
                  }
                  else
                  {
                     setOpacity(med, 1.0)
                  }
               }
           })
   checkMaxHighlighted()
}

function checkMaxHighlighted()
{
   combination = getStyle('available_treatments_box', 'display') != 'none'
   maxHighlight = combination ? 3 : 1;
   highlightCount = getElementsByTagAndClassName("*", "highlight").length
           
   if (highlightCount == maxHighlight)
   {
      setStyle('next', {'display':'inline'})
      pulsate('next')
   }
   else
   {
      setStyle('next', {'display':'none'})
   }
}

function showCombinationView()
{
   debug('showCombinationView')
   
   // show the treatments box
   setStyle($('available_treatments_box'), {'display':'block'})
   
   setStyle($('combination_directions'), {'display':'block'})
   setStyle($('singletreatment_directions'), {'display':'none'})
   
   // gray all other best treatments
   elems = getElementsByTagAndClassName("*", "treatment_draggable", parent=$('best_treatment'))
   forEach(elems,
           function(elem)
           {
              if (elem.id == 'combination')
              {
                 setOpacity(elem, 1.0)
              }
              else
              {
                 setOpacity(elem, .5)
              }
           })
   
   // gray all unselected available treatments if we're at the max count 
   highlightCount = getElementsByTagAndClassName("*", "highlight", parent=$('available_treatments')).length
   elems = getElementsByTagAndClassName("*", "treatment_draggable", parent=$('available_treatments'))
   forEach(elems,
           function(elem)
           {
               if (!hasElementClass(elem, 'highlight'))
               {
                  if (highlightCount >= MAX_COMBOTREATMENT_COUNT)
                  {
                     setOpacity(elem, .5);
                  }
                  else
                  {
                     setOpacity(elem, 1.0);
                  }
               }
           })
   
}
   
function hideCombinationView()
{
   debug('hideCombinationView')
   
   setStyle($('available_treatments_box'), {'display':'none'})
   
   setStyle($('combination_directions'), {'display':'none'})
   setStyle($('singletreatment_directions'), {'display':'block'})
      
   
   // unhighlight any selected combination treatments, and put the opacity back to 1.0
   // for all best treatments: reset opacity to 1.0 
   elems = getElementsByTagAndClassName("*", "treatment_draggable")
   forEach(elems,
           function(elem)
           {
               removeElementClass(elem, 'highlight')
               setOpacity(elem, 1.0)
           })
}