from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from pagetree.models import Hierarchy
from pagetree.helpers import get_hierarchy, get_section_from_path,get_module, needs_submit
from main.models import UserProfile

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
    
@user_passes_test(lambda u: u.is_staff)
@rendered_with('main/edit_page.html')
def edit_page(request,path):
    section = get_section_from_path(path)
    h = get_hierarchy()
    return dict(section=section,
                module=get_module(section),
                root=h.get_root())    

@rendered_with('main/page.html')
def page(request,path):
    h = get_hierarchy()
    section = get_section_from_path(path)
    return _response(request, h, section, path)

@login_required
@rendered_with('main/page.html')
def page(request,path):
    h = Hierarchy.get_hierarchy('main')
    current_root = get_section_from_path(path)
    section = h.get_first_leaf(current_root)
    ancestors = section.get_ancestors()
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    # Skip to the first leaf, make sure to mark these sections as visited
    if (current_root != section):
        profile.set_has_visited(ancestors)
        return HttpResponseRedirect(section.get_absolute_url())
    
    # the previous node is the last leaf, if one exists.
    prev = _get_previous_leaf(section)
    next = section.get_next()
    
    # Is this section unlocked now?
    can_access = _unlocked(section, request.user, prev, profile)
    if can_access:
        profile.save_last_location(request.path, section)
        
    module = None
    if not section.is_root() and len(ancestors) > 1:
        module = ancestors[1]
        
    # construct the subnav up here. it's too heavy on the client side
    subnav = _construct_menu(request, module, section, profile)
        
    # construct the left nav up here too.
    parent = section
    if section.depth == 4:
        parent = section.get_parent()
    elif section.depth == 5:
        parent = section.get_parent().get_parent()
    leftnav = _construct_menu(request, parent, section, profile)
    
    return dict(section=section,
                accessible=can_access,
                module=module,
                root=ancestors[0],
                previous=prev,
                next=next,
                subnav=subnav,
                depth=section.depth,
                leftnav=leftnav)
    
@login_required
def index(request):
    try:
        profile = request.user.get_profile()
        url = profile.last_location
    except UserProfile.DoesNotExist:
        url = "welcome"
        
    return HttpResponseRedirect(url)

def accessible(section, user):
    previous = section.get_previous()
    return _unlocked(section, user, previous, user.get_profile())

#####################################################################
## View Utility Methods

def _get_previous_leaf(section):
    depth_first_traversal = section.get_root().get_annotated_list()
    for (i,(s,ai)) in enumerate(depth_first_traversal):
        if s.id == section.id:
            # first element is the root, so we don't want to return that
            prev = None
            while i > 1 and not prev:
                (node, x) = depth_first_traversal[i-1]
                if node and len(node.get_children()) > 0:
                    i -= 1
                else:
                    prev = node
            return prev
    # made it through without finding ourselves? weird.
    return None

def _construct_menu(request, parent, section, profile):
    menu = []
    if parent:
        for s in parent.get_children():
            entry = {'section': s, 'selected': False, 'descended': False, 'accessible': False}
            if s.id == section.id:
                entry['selected'] = True
            
            if section in s.get_descendants():
                entry['descended'] = True
                
            previous = _get_previous_leaf(s)
                
            if _unlocked(s, request.user, previous, profile):
                entry['accessible'] = True
                
            menu.append(entry)
        
    return menu

UNLOCKED = [ 'welcome', 'resources' ]

def _unlocked(section,user,previous,profile):
    """ if the user can proceed past this section """
    if not section or section.is_root() or profile.get_has_visited(section) or section.slug in UNLOCKED:
       return True
    
    if not previous or previous.is_root() or previous.slug in UNLOCKED:
        return True
    
    for p in previous.pageblock_set.all():
        if hasattr(p.block(),'unlocked'):
           if p.block().unlocked(user) == False:
              return False
    
    return profile.get_has_visited(previous)



