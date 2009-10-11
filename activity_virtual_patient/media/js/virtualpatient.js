function debug(string)
{
   if (true)
      log("DEBUG " + string)
}

//////////////////////////////////////////////////////////////////////////////

function saveStateSynch()
{
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/save/" + $('page_id').value + "/" + $('patient_id').value + "/"

   jsontxt = get_state() // defined by page
      
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':jsontxt}));
}

MochiKit.Signal.connect(window, "onbeforeunload", saveStateSynch)

///////////////////////////////////////////////////////////////////////////////////////////

function loadState()
{
   debug("loadState")
   url = 'http://' + location.hostname + ':' + location.port + "/activity/virtualpatient/load/" + $('page_id').value + "/" + $('patient_id').value + "/"
   
   deferred = loadJSONDoc(url, {'url': location.pathname});
   deferred.addCallbacks(loadStateSuccess, loadStateError); // handlers defined by each page
}

MochiKit.Signal.connect(window, "onload", loadState)


