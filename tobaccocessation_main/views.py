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

def get_hierarchy():
    return Hierarchy.objects.get_or_create(name="main",defaults=dict(base_url="/"))[0]

def get_module(section):
    """ get the top level module that the section is in"""
    if section.is_root:
        return None
    return section.get_ancestors()[1]

def needs_submit(section):
    """ if any blocks on the page need to be submitted """
    for p in section.pageblock_set.all():
        if hasattr(p.block(),'needs_submit'):
            if p.block().needs_submit():
                return True
    return False

def unlocked(section,user,previous):
    """ if the user can proceed past this section """
    if not section or section.is_root or SiteState.get_has_visited(user, section):
       return True
   
    
    if not previous or previous.is_root:
        return True
    
    for p in previous.pageblock_set.all():
        if hasattr(p.block(),'unlocked'):
           if p.block().unlocked(user) == False:
              return False
    
    return SiteState.get_has_visited(user, previous)

@login_required
@rendered_with('tobaccocessation_main/page.html')
def page(request,path):
    h = get_hierarchy()
    current_root = h.get_section_from_path(path)
    section = h.get_first_leaf(current_root)
    ancestors = section.get_ancestors()
    
    # Skip to the first leaf, make sure to mark these sections as visited
    if (current_root != section):
        SiteState.set_has_visited(request.user, ancestors)
        return HttpResponseRedirect(section.get_absolute_url())
    
    # the previous node is the last leaf, if one exists.
    depth_first_traversal = ancestors[0].get_descendents() 
    prev = _get_previous(section, depth_first_traversal)
    next = _get_next(section, depth_first_traversal)
    
    # Is this section unlocked now?
    can_access = unlocked(section, request.user, prev)
    if can_access:
        SiteState.save_last_location(request.user, request.path, section)
        
    module = None
    if not section.is_root:
        module = section.get_ancestors()[1]
        
    # construct the subnav up here. it's too heavy on the client side
    subnav = _construct_menu(request, module, section, depth_first_traversal)
        
    # construct the left nav up here too.
    depth = section.depth()
    parent = section
    if depth == 3:
        parent = section.get_parent()
    elif depth == 4:
        parent = section.get_parent().get_parent()
    leftnav = _construct_menu(request, parent, section, depth_first_traversal)
    
    return dict(section=section,
                accessible=can_access,
                module=module,
                root=ancestors[0],
                previous=prev,
                next=next,
                subnav=subnav,
                depth=depth,
                leftnav=leftnav)
    
def _construct_menu(request, parent, section, depth_first_traversal):
    menu = []
    for s in parent.get_children():
        entry = {'section': s, 'selected': False, 'descended': False, 'accessible': False}
        if s.id == section.id:
            entry['selected'] = True
        
        if section in s.get_descendents():
            entry['descended'] = True
            
        previous = _get_previous(s, depth_first_traversal)
            
        if unlocked(s, request.user, previous):
            entry['accessible'] = True
            
        menu.append(entry)
        
    return menu

@login_required
@rendered_with('tobaccocessation_main/edit_page.html')
def edit_page(request,path):
    h = get_hierarchy()
    section = h.get_section_from_path(path)
    return dict(section=section,
                module=get_module(section),
                root=h.get_root())
    
@login_required
@rendered_with('tobaccocessation_main/welcome.html')
def welcome(request):
    return dict()

@login_required
@rendered_with('tobaccocessation_main/resources.html')
def resources(request):
    return dict()

@login_required
def index(request):
    try:
        ss = SiteState.objects.get(user=request.user)
        url = ss.last_location
    except SiteState.DoesNotExist:
        url = "welcome"
        
    return HttpResponseRedirect(url)

def _get_previous(section, depth_first_traversal):
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

def _get_next(section, depth_first_traversal):
    for (i,s) in enumerate(depth_first_traversal):
        if s.id == section.id:
            if i < len(depth_first_traversal) - 1:
                return depth_first_traversal[i+1]
            else:
                return None
    # made it through without finding ourselves? weird.
    return None

