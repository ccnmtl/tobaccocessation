from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from pagetree.models import Hierarchy
from django.contrib.auth.decorators import login_required
from tobaccocessation_main.models import SiteState

class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if type(items) == type({}):
                return render_to_response(self.template_name, items, context_instance=RequestContext(request))
            else:
                return items

        return rendered_func

@login_required
@rendered_with('tobaccocessation_main/page.html')
def page(request,path):
    h = Hierarchy.get_hierarchy('main')
    current_root = h.get_section_from_path(path)
    section = h.get_first_leaf(current_root)
    ancestors = section.get_ancestors()
    ss = SiteState.objects.get_or_create(user=request.user)[0]
    
    # Skip to the first leaf, make sure to mark these sections as visited
    if (current_root != section):
        ss.set_has_visited(ancestors)
        return HttpResponseRedirect(section.get_absolute_url())
    
    # the previous node is the last leaf, if one exists.
    prev = section.get_previous_leaf()
    next = section.get_next()
    
    # Is this section unlocked now?
    can_access = _unlocked(section, request.user, prev, ss)
    if can_access:
        ss.save_last_location(request.path, section)
        
    module = None
    if not section.is_root:
        module = ancestors[1]
        
    # construct the subnav up here. it's too heavy on the client side
    subnav = _construct_menu(request, module, section, ss)
        
    # construct the left nav up here too.
    depth = section.depth()
    parent = section
    if depth == 3:
        parent = section.get_parent()
    elif depth == 4:
        parent = section.get_parent().get_parent()
    leftnav = _construct_menu(request, parent, section, ss)
    
    return dict(section=section,
                accessible=can_access,
                module=module,
                root=ancestors[0],
                previous=prev,
                next=next,
                subnav=subnav,
                depth=depth,
                leftnav=leftnav)
    
@login_required
def index(request):
    try:
        ss = SiteState.objects.get(user=request.user)
        url = ss.last_location
    except SiteState.DoesNotExist:
        url = "welcome"
        
    return HttpResponseRedirect(url)

#####################################################################
## View Utility Methods
    
def _construct_menu(request, parent, section, ss):
    menu = []
    for s in parent.get_children():
        entry = {'section': s, 'selected': False, 'descended': False, 'accessible': False}
        if s.id == section.id:
            entry['selected'] = True
        
        if section in s.get_descendents():
            entry['descended'] = True
            
        previous = s.get_previous_leaf()
            
        if _unlocked(s, request.user, previous, ss):
            entry['accessible'] = True
            
        menu.append(entry)
        
    return menu

UNLOCKED = [ 'resources', 'welcome' ]

def _unlocked(section,user,previous,sitestate):
    """ if the user can proceed past this section """
    if not section or section.is_root or sitestate.get_has_visited(section):
       return True
   
    if section.slug in UNLOCKED:
        return True
    
    if not previous or previous.is_root:
        return True
    
    for p in previous.pageblock_set.all():
        if hasattr(p.block(),'unlocked'):
           if p.block().unlocked(user) == False:
              return False
    
    return sitestate.get_has_visited(previous)



