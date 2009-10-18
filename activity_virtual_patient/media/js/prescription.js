function get_state()
{
   debug("get_state")
   
   doc = {}
   doc['medication_idx'] = $('medication_idx').value
   
   tag = $('medication_tag').value
   doc[tag] = {}
   doc[tag]['concentration'] = $('concentration').options[$('concentration').selectedIndex].value
   doc[tag]['dosage'] = $('dosage').options[$('dosage').selectedIndex].value
   doc[tag]['refill'] = $('refill').options[$('refill').selectedIndex].value
   
   if ($('concentration2'))
   {
      doc[tag]['concentration2'] = $('concentration2').options[$('concentration2').selectedIndex].value
      doc[tag]['dosage2'] = $('dosage2').options[$('dosage2').selectedIndex].value
      doc[tag]['refill2'] = $('refill2').options[$('refill2').selectedIndex].value
   }
   
   jsontxt = JSON.stringify(doc, null)
   return jsontxt   
}