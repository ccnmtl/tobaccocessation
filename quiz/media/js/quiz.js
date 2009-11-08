function debug(string)
{
   if (true)
      log("DEBUG " + string)
}

function onChooseAnswer(ctrl)
{
   debug('onChooseAnswer: ' + ctrl.name)
   setStyle(ctrl.name + "_answer", {'display':'block'})
   
   maybeEnableNext()
}

function maybeEnableNext()
{
   debug('maybeEnableNext')
   
   questions = getElementsByTagAndClassName(null, 'casequestion')
   selectedvalues = filter(itemgetter('checked'), $$('input'))
   
   forEach(selectedvalues,
         function(elem) {
            setStyle(elem.name + "_answer", {'display':'block'})
         })
   
   if (selectedvalues.length < questions.length)
   {
      // if the user has answered all the questions, enable the "next" buttons
      setStyle('span_' + $('next_section_slug').value, {'display': 'inline'})
      setStyle($('next_section_slug').value, {'display': 'none'})
      setStyle('next', {'display': 'none'})
   }
   else
   {
      // if the user has answered all the questions, enable the "next" buttons
      setStyle('span_' + $('next_section_slug').value, {'display': 'none'})
      setStyle($('next_section_slug').value, {'display': 'inline'})
      setStyle('next', {'display': 'inline'})
   }
}

MochiKit.Signal.connect(window, "onload", maybeEnableNext)
