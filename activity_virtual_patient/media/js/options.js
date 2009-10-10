function get_state()
{
   debug("options: get_state")
   
   // setup a post block with the relevant information & send it up to the server
   doc = {}
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

function set_state(doc)
{
   debug("options: set_state")

   for (item in doc)
   {
      template = getElement('medication_template')
      forEach(doc[item], 
              function(med) {
                 // create elements for each of the meds
                 newnode = template.cloneNode(true)
                 newnode.id = med
                 setStyle(newnode, {'display': 'inline'})
                 addElementClass(newnode, med)
                 
                 // fix the src on the image
                 image = getFirstElementByTagAndClassName("img", "", parent=newnode)
                 image.src = image.src + med + ".jpg"
                 
                 $(item).appendChild(newnode)
                 
                 // remove from the available treatments
                 node = getFirstElementByTagAndClassName(null, med, parent=$('available_treatments'))
                 removeElement(node)
              })
   }
}