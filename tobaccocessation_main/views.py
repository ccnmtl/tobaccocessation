from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from pagetree.models import Hierarchy
from django.contrib.auth.decorators import login_required
from tobaccocessation_main.models import SiteState
import time
from django.core.cache import cache

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
    depth_first_traversal = get_descendents(ancestors[0]) 
    prev = get_previous(section, depth_first_traversal)
    next = get_next(section, depth_first_traversal)
    
    # Is this section unlocked now?
    can_access = _unlocked(section, request.user, prev, ss)
    if can_access:
        ss.save_last_location(request.path, section)
        
    module = None
    if not section.is_root:
        module = ancestors[1]
        
    # construct the subnav up here. it's too heavy on the client side
    subnav = _construct_menu(request, module, section, depth_first_traversal, ss)
        
    # construct the left nav up here too.
    depth = section.depth()
    parent = section
    if depth == 3:
        parent = section.get_parent()
    elif depth == 4:
        parent = section.get_parent().get_parent()
    leftnav = _construct_menu(request, parent, section, depth_first_traversal, ss)
    
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
@rendered_with('tobaccocessation_main/edit_page.html')
def edit_page(request,path):
    h = Hierarchy.get_hierarchy('main')
    section = h.get_section_from_path(path)
    return dict(section=section,
                module=section.get_module(),
                root=h.get_root())
    
@login_required
def index(request):
    try:
        ss = SiteState.objects.get(user=request.user)
        url = ss.last_location
    except SiteState.DoesNotExist:
        url = "welcome"
        
    return HttpResponseRedirect(url)

###############################################################
## Optimized Hierachy Methods

def get_previous(section, depth_first_traversal):
    for (i,s) in enumerate(depth_first_traversal):
        if s.id == section.id:
            # first element is the root, so we don't want to
            # return that
            prev = None
            while i > 1 and not prev:
                node = depth_first_traversal[i-1]
                if node and len(node.get_children()) > 0:
                    i -= 1
                else:
                    prev = node
            return prev
    # made it through without finding ourselves? weird.
    return None

def get_next(section, depth_first_traversal):
    length = len(depth_first_traversal) - 1
    for (i,s) in enumerate(depth_first_traversal):
        if s.id == section.id:
            if i < length:
                return depth_first_traversal[i+1]
            else:
                return None
    # made it through without finding ourselves? weird.
    return None

def get_descendents(section):
    desc = _get_cached_value(section, 'descendents')
    if not desc:
        desc = section.get_descendents()
        _set_cached_value(section, 'descendents', desc)
    return desc

#####################################################################
## View Utility Methods
    
def _construct_menu(request, parent, section, depth_first_traversal, ss):
    menu = []
    for s in parent.get_children():
        entry = {'section': s, 'selected': False, 'descended': False, 'accessible': False}
        if s.id == section.id:
            entry['selected'] = True
        
        if section in get_descendents(s):
            entry['descended'] = True
            
        previous = get_previous(s, depth_first_traversal)
            
        if _unlocked(s, request.user, previous, ss):
            entry['accessible'] = True
            
        menu.append(entry)
        
    return menu

def _unlocked(section,user,previous,sitestate):
    """ if the user can proceed past this section """
    if not section or section.is_root or sitestate.get_has_visited(section):
       return True
    
    if not previous or previous.is_root:
        return True
    
    for p in previous.pageblock_set.all():
        if hasattr(p.block(),'unlocked'):
           if p.block().unlocked(user) == False:
              return False
    
    return sitestate.get_has_visited(previous)

def _get_cached_value(section, key):
    d = cache.get(section)
    if not d or not d.has_key(key):
        return None
    
    return d[key] 

def _set_cached_value(section, key, value):
    d = cache.get(section)
    if not d:
        d = {}
        
    d[key] = value
    cache.set(section, d)
    



