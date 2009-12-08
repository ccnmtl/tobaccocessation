function get_state()
{
   debug("get_state")
   
   doc = {}
   doc['medication_idx'] = $('medication_idx').value
   
   tag = $('medication_tag').value
   doc[tag] = {}
   doc[tag]['concentration'] = $('concentration').options[$('concentration').selectedIndex].value
   doc[tag]['dosage'] = $('dosage').options[$('dosage').selectedIndex].value
   
   if ($('concentration2'))
   {
      doc[tag]['concentration2'] = $('concentration2').options[$('concentration2').selectedIndex].value
      doc[tag]['dosage2'] = $('dosage2').options[$('dosage2').selectedIndex].value
   }
   
   jsontxt = JSON.stringify(doc, null)
   return jsontxt   
}

function validate()
{
   return true;
}

function setupGender()
{
   debug('setupGender: ' + $('patient_id').value)
   if ($('patient_id').value == 4)
   {
      // move over the gender to the left
      setStyle($('gender'), {'margin-left': '285px'})
      
      if ($('gender2'))
      {
         setStyle($('gender2'), {'margin-left': '288px'})
      }
   }
}

MochiKit.Signal.connect(window, "onload", setupGender)