function debug(string)
{
   if (false)
      log("DEBUG " + string)
}

function onChooseAnswer(ctrl)
{
   debug('onChooseAnswer: ' + ctrl.name)
   a = ctrl.id.split('_')
   setStyle(a[0] + "_answer", {'display':'block'})
}

function loadStateSuccess(doc)
{
   debug('loadStateSuccess')
   // add each element to the correct div
   // remove the element from the "accept" list
   forEach(doc.question,
           function(question)
           {
              $(question.id + "_" + question.answer).checked = true
              setStyle(question.id + "_answer", {'display':'block'})
           })
   
   maybeEnableNext()
}

function loadStateError(err)
{
   debug("loadStateError")
   // @todo: Find a spot to display an error or decide just to fail gracefully
   // $('errorMsg').innerHTML = "An error occurred loading your state (" + err + "). Please start again."
}

function loadState()
{
   debug("loadState")
   url = 'http://' + location.hostname + ':' + location.port + "/activity/quiz/load/"
   deferred = loadJSONDoc(url)
   deferred.addCallbacks(loadStateSuccess, loadStateError)
}

MochiKit.Signal.connect(window, "onload", loadState)

function saveState()
{
   debug("saveState")
   url = 'http://' + location.hostname + ':' + location.port + "/activity/quiz/save/"
 
   doc = 
   {
      'question': []
   }
   
   questions = getElementsByTagAndClassName('*', 'question')
              
   forEach(questions,
           function(question) {
              if (question.checked)
              {
                 a = question.id.split('_')
                 q = {}
                 
                 q['id'] = a[0]
                 q['answer'] = a[1]
                 doc['question'].push(q)
              }
           })

   // save state via a synchronous request. 
   var sync_req = new XMLHttpRequest();  
   sync_req.onreadystatechange= function() { if (sync_req.readyState!=4) return false; }         
   sync_req.open("POST", url, false);
   sync_req.send(queryString({'json':JSON.stringify(doc, null)}));
}

MochiKit.Signal.connect(window, "onbeforeunload", saveState)

