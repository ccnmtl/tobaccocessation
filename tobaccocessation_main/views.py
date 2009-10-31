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

def unlocked(section,user):
#    """ if the user can proceed past this section """
#    if section is None:
#        return True
#    if section.is_root:
#        # root can't be locked
#        return True
#    previous = unlocked(section.get_previous(),user)
#    if previous == False:
#        # a previous section is blocking
#        return False
#    for p in section.pageblock_set.all():
#        if hasattr(p.block(),'unlocked'):
#            if p.block().unlocked(user) == False:
#                return False
    return True

def accessible(section,user):
#    """ can the user even see this section? """
#    if unlocked(section,user):
#        # if it's unlocked, they can definitely see it
#        return True
#    # if it's locked though, we want to know if the 
#    # one before it is unlocked. if it is, that means that
#    # the lock is on the current section, which means that
#    # they are proceeding properly. If the one before it isn't
#    # unlocked, we know they're trying to skip ahead
#    return unlocked(section.get_previous(),user)

    return True

@login_required
@rendered_with('tobaccocessation_main/page.html')
def page(request,path):
    SiteState.save_last_location(request.user, request.path)
    
    h = get_hierarchy()
    section = h.get_section_from_path(path)
    if request.method == "POST":
        # user has submitted a form. deal with it
        for p in section.pageblock_set.all():
            if hasattr(p.block(),'needs_submit'):
                if p.block().needs_submit():
                    prefix = "pageblock-%d-" % p.id
                    data = dict()
                    for k in request.POST.keys():
                        if k.startswith(prefix):
                            data[k[len(prefix):]] = request.POST[k]
                    p.block().submit(request.user,data)
        return HttpResponseRedirect(section.get_next().get_absolute_url())
    else:
        return dict(section=section,
    #                unlocked=unlocked(section,request.user))
    #                accessible=accessible(section,request.user),
                    module=get_module(section),
                    needs_submit=needs_submit(section),
                    root=h.get_root())

@login_required
@rendered_with('tobaccocessation_main/edit_page.html')
def edit_page(request,path):
    h = get_hierarchy()
    section = h.get_section_from_path(path)
    return dict(section=section,
                module=get_module(section),
                root=h.get_root())

@login_required
def index(request):
    try:
        ss = SiteState.objects.get(user=request.user)
        url = ss.last_location
    except SiteState.DoesNotExist:
        h = get_hierarchy()
        first_leaf = h.get_first_leaf(h.get_root())
        url = first_leaf.get_absolute_url()
    return HttpResponseRedirect(url)