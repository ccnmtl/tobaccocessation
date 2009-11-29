// no IE support yet. it shouldn't be hard to add, but it will make the
// code harder to understand.

var dragging;

document.captureEvents(Event.MOUSEMOVE);

function doDown(e) {
  if (e.target.tagName == "TEXTAREA"
      || e.target.tagName == "INPUT") {
    return;
  }
    document.body.style.cursor='move';
    document.onmousemove = doDrag;
    var target = findDraggableParent(e.target);
    if (target == null) return;
    dragging = target;
    dragging.className += " dragging";
    dragging.style.fontWeight='bold';
    if (e.stopPropagation) e.stopPropagation();
    return false;
}

function findDraggableParent(el) {
    if (el == null) return null;
    else if (el.className && el.className.indexOf("draggable") != -1) return el;
    else return findDraggableParent(el.parentNode);
}

function doDrag(e) {
    if (!dragging) return;
    var target = findDraggableParent(e.target);
    if (target == null) return;
    if (target.id != dragging.id) {
        swapElements(target, dragging);
    }
    if (e.stopPropagation) e.stopPropagation();
    return false;
}

function swapElements(child1, child2) {
    // currently, this works by building a list of all the
    // children, swapping the elements in this list, then
    // removing all the children and replacing them with our
    // list. there must be a more efficient way, but other approaches
    // i tried were buggy.
    var parent = child1.parentNode;
    var children = parent.childNodes;
    var items = new Array();
    for (var i = 0; i < children.length; i++) {
        items[i] = children.item(i);
        if (children.item(i).id) {
            if (children.item(i).id == child1.id) items[i] = child2;
            if (children.item(i).id == child2.id) items[i] = child1;
        }
    }
    for (var i = 0; i < children.length; i++) {
        parent.removeChild(children.item(i));
    }
    for (var i = 0; i < items.length; i++) {
        parent.appendChild(items[i]);

    }
}

function doUp(e) {
    if (dragging)
    {
       dragging.className = dragging.className.replace(/ dragging/,"");
       dragging = null;
       document.onmousemove = null;
       saveOrder();
       if (e.stopPropagation) e.stopPropagation();
       document.body.style.cursor='auto'
    }
    return false;
}

function addLoadEvent(func) {
        var oldonload = window.onload;
        if (typeof window.onload != 'function') {
                window.onload = func;
        } else {
                window.onload = function() {
                        oldonload();
                        func();
                }
        }
}

function initDrags() {
	 trs = document.getElementsByTagName('tr');
	 for (var i = 0; i < trs.length; i++) {
	     tr = trs[i];
	     if (tr.className.indexOf("draggable") != -1) {
		tr.onmousedown = doDown;
		tr.onmouseup = doUp;
	     }
	 }
	 lis = document.getElementsByTagName('li');
	 for (var i = 0; i < lis.length; i++) {
	     li = lis[i];
	     if (li.className.indexOf("draggable") != -1) {
		li.onmousedown = doDown;
		li.onmouseup = doUp;
	     }
	 }

	 var divs = document.getElementsByTagName('div');
	 for (var i = 0; i < divs.length; i++) {
	     var div = divs[i];
	     if (div.className.indexOf("draggable") != -1) {
		div.onmousedown = doDown;
		div.onmouseup = doUp;
	     }
	 }
	 
	 document.body.onmouseup = doUp;

}

addLoadEvent(initDrags);
