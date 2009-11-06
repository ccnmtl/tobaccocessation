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

def unlocked_by_default(section):
    if section is None:
        return True
    
    if section.is_root:
        # root can't be locked
        return True
    
    return False

def unlocked(section,user):
    """ if the user can proceed past this section """
    if unlocked_by_default(section):
        return True
    
    if SiteState.get_has_visited(user, section):
       return True
   
    previous = section.get_previous()
    if unlocked_by_default(previous):
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
    
    # Skip to the first leaf, make sure to mark these sections as visited
    if (current_root != section):
        SiteState.set_has_visited(request.user, section.get_ancestors())
        return HttpResponseRedirect(section.get_absolute_url())
    
    # Is this section unlocked now?
    can_access = unlocked(section,request.user)
    if can_access:
        SiteState.save_last_location(request.user, request.path, section)
        
    # the previous node is the last leaf, if one exists.
    prev = None
    depth_first_traversal = _get_descendent_leaves(section.get_root())
    for (i,s) in enumerate(depth_first_traversal):
        if s.id == section.id:
            # first element is the root, so we don't want to
            # return that
            if i >= 1:
                prev = depth_first_traversal[i-1]
    
    return dict(section=section,
                accessible=can_access,
                module=get_module(section),
                root=h.get_root(),
                previous=prev,
                next=section.get_next())

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

def _get_descendent_leaves(section):
    l = []
    for c in section.get_children():
        if (c.is_leaf()):
            l.append(c)
        else:
            l.extend(_get_descendent_leaves(c))
    return l

