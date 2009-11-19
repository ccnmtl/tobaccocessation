function debug(string)
{
   if (true)
      log("DEBUG " + string)
}

//////////////////////////////////////////////////////////////////////////////

function saveStateSynch()
{
   if (window.get_state)
   {
      jsontxt = get_state() // defined by page
      url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/save/" + $('patient_id').value + "/"   
      var sync_req = new XMLHttpRequest();  
      sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
      sync_req.open("POST", url, false);
      sync_req.send(queryString({'json':jsontxt}));
   }
}

_onbeforeunload = MochiKit.Signal.connect(window, "onbeforeunload", saveStateSynch)

//////////////////////////////////////////////////////////////////////////////

function onXHRSuccess(response)
{
   doc = JSON.parse(response.responseText, null)
   window.location = doc.redirect 
}

function onXHRError(err)
{
   // do something intelligent here
}

function navigate()
{
   MochiKit.Signal.disconnect(_onbeforeunload)
   
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

