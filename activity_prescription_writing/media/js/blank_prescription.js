function numeric(field) {
    var regExpr = new RegExp("^[0-9]$");
    if (!regExpr.test(field.value)) 
    {
      // Case of error
      field.value = "";
    }
}

function setfocus()
{
   $("dosage").focus()
}

function saveState()
{
   debug("saveState")
   url = 'http://' + location.hostname + ':' + location.port + "/activity/prescription/save/"
 
   rx = 
   {
      'dosage' : $('dosage'),
      'disp' : $('disp'),
      'sig' : $('sig'),
      'refills' : $('refills'),
      'dosage_2' : $('dosage_2'),
      'disp_2' : $('disp_2'),
      'sig_2' : $('sig_2'),
      'refills_2' : $('refills_2'),
   }
   
   doc = 
   {
      $('medication_name'): rx
   }


   // save state via a synchronous request. 
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':JSON.stringify(doc, null)}));
}

MochiKit.Signal.connect(window, "onload", setfocus)
MochiKit.Signal.connect(window, "onbeforeunload", saveState)
