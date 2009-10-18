function debug(string)
{
   if (false)
      log("DEBUG " + string)
}

//////////////////////////////////////////////////////////////////////////////

function onXHRSuccess(response)
{
   doc = JSON.parse(response.responseText, null)
   window.location = doc.redirect 
}

function onXHRError(err)
{

}

function navigate()
{
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/navigate/" + $('page_id').value + "/" + $('patient_id').value + "/"

   jsontxt = get_state() // defined by individual pages
   
   deferred = doXHR(url, 
         { 
            method: 'POST', 
            sendContent: queryString({'json': jsontxt})
         });
   deferred.addCallbacks(onXHRSuccess, onXHRError);
}

//////////////////////////////////////////////////////////////////////////////

function saveStateSynch()
{
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/save/" + $('patient_id').value + "/"

   jsontxt = get_state() // defined by page
      
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':jsontxt}));
}

MochiKit.Signal.connect(window, "onbeforeunload", saveStateSynch)

//////////////////////////////////////////////////////////////////////////////