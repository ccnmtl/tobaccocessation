from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from pagetree.models import Hierarchy
from django.contrib.auth.decorators import login_required
from tobaccocessation_main.models import SiteState
import time

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

def unlocked(section,user,previous=None):
    """ if the user can proceed past this section """
    if section.is_root or SiteState.get_has_visited(user, section):
       return True
   
    if not previous:
        previous = section.get_previous()
        
    if previous.is_root:
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
    hview = HierarchyView(h)
    
    current_root = h.get_section_from_path(path)
    section = hview.get_first_leaf(current_root)
    ancestors = hview.get_ancestors(section)
    
    # Skip to the first leaf, make sure to mark these sections as visited
    if (current_root != section):
        SiteState.set_has_visited(request.user, ancestors)
        return HttpResponseRedirect(section.get_absolute_url())
    
    previous = hview.get_previous_leaf(section)
    next = hview.get_next(section)
    
    can_access = unlocked(section,request.user, previous)
    
    SiteState.save_last_location(request.user, request.path, section)
        
    module = None
    if not section.is_root:
        module = ancestors[1]
    
    return dict(section=section,
                accessible=can_access,
                module=module,
                root=hview.get_root(),
                previous=previous,
                next=next)

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


class HierarchyNode(object):
    def __init__(self, section, parent):
        self.section = section
        self.parent = parent
        self.children = []
       
    def append_child(self, newnode):
        self.children.append(newnode)


class HierarchyView:
    
    def __init__(self, h):
        self.hierarchy = h
        self.root = HierarchyNode(h.get_root(), None)
        self.depth_first_traversal = []
        
        tc1 = time.clock()
        self._build_tree(self.root)
        tc2 = time.clock()
        print '__init__ %s: ' % (tc2 - tc1)
    
        
    def get_root(self):
        return self.root.section
            
    def _build_tree(self, parent):
        self.depth_first_traversal.append(parent)
        for c in parent.section.get_children():
            child = HierarchyNode(c, parent)
            parent.append_child(child)
            self._build_tree(child)
            
    def _print_tree(self, node):
        print node.section
        for c in node.children:
            print c
            self._print_tree(c)
            
    def find_node(self, section):
        return self._find_node(section, self.root)
            
    def _find_node(self, section, parent):
        for c in parent.children:
            if (c.section == section):
                return c
            
            found = self._find_node(section, c)
            if found:
                return found
            
        return None
            
    def get_first_leaf(self, section):
        # skip to the specified section
        node = self.find_node(section)
        
        #traverse the node's kids until we find the first leaf
        while len(node.children) > 0:
            node = node.children[0]
        return node.section
    
    def get_previous_leaf(self, section):
        for (i,n) in enumerate(self.depth_first_traversal):
            if n.section.id == section.id:
                # first element is the root, so we don't want to
                # return that
                prev = None
                while i > 1 and not prev:
                    node = self.depth_first_traversal[i-1]
                    if node and len(node.children) > 0:
                        i -= 1
                    else:
                        prev = node
                if prev:
                    return prev.section
                else:
                    return None
        # made it through without finding ourselves? weird.
        return None

    def get_next(self, section):
        for (i,n) in enumerate(self.depth_first_traversal):
            if n.section.id == section.id:
                if i < len(self.depth_first_traversal) - 1:
                    return self.depth_first_traversal[i+1].section
                else:
                    return None
        # made it through without finding ourselves? weird.
        return None
                    
    def get_ancestors(self, section):
        return self._get_ancestors(section, self.root)
            
    def _get_ancestors(self, section, parent):
        if (parent.section == section):
            return [parent.section]

        for c in parent.children:
            found = self._get_ancestors(section, c)
            if found:
                found.insert(0, parent.section)
                return found
            
        return None