_combination = false
MAX_COMBOTREATMENT_COUNT = 2
MAX_TREATMENT_COUNT = 1

function loadStateSuccess(doc)
{
   debug("loadStateSuccess")
   
   set_state(doc) // defined in the per page view
}

function loadStateError(err)
{
   debug("loadStateError")
   // ignore?
}

function onXHRSuccess(response)
{
   doc = JSON.parse(response.responseText, null)
   window.location = doc.redirect 
}

function onXHRError(err)
{

}

function gotoPrescribe()
{
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/post/" + $('page_id').value + "/" + $('patient_id').value + "/"
   
   jsontxt = get_state()
      
   deferred = doXHR(url, 
         { 
            method: 'POST', 
            sendContent: queryString({'json': jsontxt})
         });
   deferred.addCallbacks(onXHRSuccess, onXHRError);
}

function onSelectBestTreatment(elem)
{
   debug("onSelectBestTreatment " + elem.id)
   
   // are we at the maximum treatments allowed? max treatments varies based
   // on whether we're dealing with a combination situation or not
   highlightCount = getElementsByTagAndClassName("*", "highlight").length
   if (highlightCount >= MAX_TREATMENT_COUNT && !hasElementClass(elem, 'highlight'))
      return
      
   // nope, highlight the treatment
   toggleElementClass('highlight', elem)
   
   if (elem.id == "combination")
   {
      if (hasElementClass(elem, 'highlight'))
         showCombinationView()
      else
         hideCombinationView()
   }
   else
   {
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

function get_state()
{
   debug("get_state")
   doc = {}
   
   doc['prescribe'] = {}
   elem = getFirstElementByTagAndClassName("*", "highlight", parent='best_treatment')
   if (elem)
      doc['prescribe'][elem.id] = {}
           
   elems = getElementsByTagAndClassName("*", 'highlight', parent='available_treatments')
   doc['combination'] = {}
   forEach(elems,
           function(elem)
           {
              doc['combination'][elem.id] = {}
           })
           
   jsontxt = JSON.stringify(doc, null)
   return jsontxt
}

function set_state(doc)
{
   debug("selection: set_state: ")
   
   selected = ""
   if (doc['prescribe'])
   {   
      for (x in doc['prescribe'])
         selected = x
   }

   template = getElement('medication_template')
   forEach(doc['best_treatment'], 
           function(med) {
              
              // create elements for each of the meds
              newnode = template.cloneNode(true)
              newnode.id = med
              setStyle(newnode, {'display': 'inline'})
              addElementClass(newnode, med)
              
              // fix the src on the image
              image = getFirstElementByTagAndClassName("img", "", parent=newnode)
              image.src = image.src + med + ".jpg"
              
              $('best_treatment').appendChild(newnode)
              
              if (med == selected)
                 addElementClass(med, 'highlight')
              else if (selected.length > 0)
                 setOpacity(med, .5)
            })
   
   if (selected == "combination")
   {
      for (med in doc['combination'])
         addElementClass(med, 'highlight')
      showCombinationView()
   }
   checkMaxHighlighted()
}

///////////////////////////////////////////////////////////////////////////////////
// controlling the combination eccentricities here


function checkMaxHighlighted()
{
   maxHighlight = _combination ? 3 : 1;
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
   _combination = true
   
   // show the treatments box
   setStyle($('available_treatments_box'), {'display':'block'})
   
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
   _combination = false
   
   setStyle($('available_treatments_box'), {'display':'none'})
   
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