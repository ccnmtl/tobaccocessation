function get_state()
{
   debug("get_state");
   doc = {};
   
   doc.prescribe = "";
   elem = getFirstElementByTagAndClassName("*", "highlight", 'best_treatment');
   if (elem)
      doc.prescribe = elem.id;
           
   elems = getElementsByTagAndClassName("*", 'highlight', 'available_treatments');
   doc.combination = [];
   forEach(elems,
           function(elem)
           {
              idx = elem.id.lastIndexOf('_');
              doc.combination.push(elem.id.slice(0, idx));
           });
           
   jsontxt = JSON.stringify(doc, null);
   return jsontxt;
}

function validate()
{
   var combination = false;
   var elem = getFirstElementByTagAndClassName("*", "highlight", 'best_treatment');
   if (elem) {
      combination = elem.id == 'combination';
   }

   var maxHighlight = combination ? 3 : 1;
   var highlightCount = getElementsByTagAndClassName("*", "highlight").length;
   
   if (highlightCount == maxHighlight) {
       getElement('next').style.display = "block";
       getElement('next_disabled').style.display = "none";
       return true;
   } else {
       getElement('next').style.display = "none";
       getElement('next_disabled').style.display = "block";
       return false;
   } 
}

///////////////////////////////////////////////////////////////////////////////////////////

function setupPage()
{
   validate();
}

MochiKit.Signal.connect(window, "onload", setupPage);

///////////////////////////////////////////////////////////////////////////////////
// controlling the combination eccentricities here

MAX_COMBOTREATMENT_COUNT = 2;
MAX_TREATMENT_COUNT = 1;

function onSelectBestTreatment(elem)
{
   debug("onSelectBestTreatment " + elem.id);
   
   if (!hasElementClass(elem, 'highlight'))
   {
      // untoggle all classes that may be highlighted
      var highlighted = getElementsByTagAndClassName("*", "highlight");
      for (i = 0; i < highlighted.length; i++) {
          var item = highlighted[i];
          removeElementClass(item, 'highlight');
          if (item.id == 'combination')
              hideCombinationView();         
       }
      
      // highlight the selected treatment
      addElementClass(elem, 'highlight');
      if (elem.id == "combination") {
         showCombinationView();
      } else {
         setStyle('combination_directions', {'display':'none'});
         setStyle('singletreatment_directions', {'display':'block'});
      }
   }
   
   validate();
}

function onSelectCombinationTreatment(elem)
{
   debug("onSelectCombinationTreatment");
   // are we at the maximum treatments allowed? max treatments varies based
   // on whether we're dealing with a combination situation or not
   
   highlightCount = getElementsByTagAndClassName("*", "highlight", $('available_treatments')).length;
   if (highlightCount >= MAX_COMBOTREATMENT_COUNT && !hasElementClass(elem, 'highlight'))
   {
      alert("You've already chosen two treatments to combine. Please deselect one of your choices and reselect this choice.");
      return;
   }
   
   // nope, highlight the treatment
   toggleElementClass('highlight', elem);

   // are we at the maximum treatments allowed now?
   newHighlightCount = getElementsByTagAndClassName("*", "highlight", $('available_treatments')).length;
   $('treatments_to_combine').innerHTML = 2 - newHighlightCount;
   
   validate();
}

function showCombinationView()
{
   debug('showCombinationView');
   
   // show the treatments box
   setStyle($('available_treatments_box'), {'display':'block'});
   
   setStyle($('combination_directions'), {'display':'block'});
   setStyle($('singletreatment_directions'), {'display':'none'});
}
   
function hideCombinationView()
{
   debug('hideCombinationView');
   
   setStyle($('available_treatments_box'), {'display':'none'});
   
   setStyle($('combination_directions'), {'display':'none'});
   setStyle($('singletreatment_directions'), {'display':'block'});
      
   
   elems = getElementsByTagAndClassName("*", "treatment_draggable");
   forEach(elems,
           function(elem)
           {
               removeElementClass(elem, 'highlight');
           });
}