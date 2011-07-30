function validate()
{
   getElement('next').style.display = "block"; 
   return true;
}

MochiKit.Signal.connect(window, "onload", validate)