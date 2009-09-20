from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from pagetree.models import Hierarchy
from pageblocks.models import TextBlock, PullQuoteBlock, HTMLBlock, ImageBlock, ImagePullQuoteBlock
from pageblocks.forms import AddTextBlockForm, AddImageBlockForm, AddImagePullQuoteBlockForm, AddHTMLBlockForm

# copied(labs.views)
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

# copied(labs.views)
def get_hierarchy():
    try:
        return Hierarchy.objects.get(name="main")
    except Hierarchy.DoesNotExist:
        return Hierarchy.objects.create(name="main",base_url="/")

# copied(labs.views)
def get_section_from_path(path):
    h = get_hierarchy()
    return h.get_section_from_path(path)

# copied(labs.views)
def get_module(section):
    """ get the top level module that the section is in"""
    if section.is_root:
        return None
    return section.get_ancestors()[1]

#copied(labs.views)
def needs_submit(section):
    """ if any blocks on the page need to be submitted """
    for p in section.pageblock_set.all():
        if hasattr(p.block(),'needs_submit'):
            if p.block().needs_submit():
                return True
    return False

# copied(labs.views)
@login_required
@rendered_with('siteeditor/page.html')
def page(request,path):
    section = get_section_from_path(path)
    h = get_hierarchy()
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
                    module=get_module(section),
                    needs_submit=needs_submit(section),
                    root=h.get_root())
        
@rendered_with('siteeditor/edit_page.html')
def edit_page(request,path):
    section = get_section_from_path(path)
    h = get_hierarchy()
    return dict(section=section,
                add_text_block_form=AddTextBlockForm(),
                add_image_block_form=AddImageBlockForm(),
                add_image_pullquote_block_form=AddImagePullQuoteBlockForm(),
                add_html_block_form=AddHTMLBlockForm(),
                module=get_module(section),
                root=h.get_root())
    
def add_child_section(request,path):
    section = get_section_from_path(path)
    child = section.append_child(request.POST.get('label','unnamed'),
                                 request.POST.get('slug','unknown'))
    return HttpResponseRedirect("/edit" + section.get_absolute_url())

def add_textblock(request,path):
    section = get_section_from_path(path)
    tb = TextBlock.objects.create(body=request.POST.get('body',''))
    pageblock = section.append_pageblock(label=request.POST.get('label',''),content_object=tb)
    return HttpResponseRedirect("/edit" + section.get_absolute_url())

def add_htmlblock(request,path):
    section = get_section_from_path(path)
    tb = HTMLBlock.objects.create(html=request.POST.get('html',''))
    pageblock = section.append_pageblock(label=request.POST.get('label',''),content_object=tb)
    return HttpResponseRedirect("/edit" + section.get_absolute_url())

def add_pullquoteblock(request,path):
    section = get_section_from_path(path)
    tb = PullQuoteBlock.objects.create(body=request.POST.get('body',''))
    pageblock = section.append_pageblock(label=request.POST.get('label',''),content_object=tb)
    return HttpResponseRedirect("/edit" + section.get_absolute_url())

def add_quizblock(request,path):
    section = get_section_from_path(path)
    qb = Quiz.objects.create(description=request.POST.get('description',''),
                             rhetorical=request.POST.get('rhetorical',''))
    pageblock = section.append_pageblock(label=request.POST.get('label',''),
                                         content_object=qb)
    return HttpResponseRedirect("/edit" + section.get_absolute_url())

def add_imageblock(request,path):
    section = get_section_from_path(path)
    if 'image' in request.FILES:
        ib = ImageBlock.objects.create(caption=request.POST.get('caption',''),
                                       image="")
        ib.save_image(request.FILES['image'])
        pageblock = section.append_pageblock(label=request.POST.get('label',''),
                                             content_object=ib)

    return HttpResponseRedirect("/edit" + section.get_absolute_url())

def add_imagepullquoteblock(request,path):
    section = get_section_from_path(path)
    if 'image' in request.FILES:
        ib = ImagePullQuoteBlock.objects.create(caption=request.POST.get('caption',''),
                                       image="")
        ib.save_image(request.FILES['image'])
        pageblock = section.append_pageblock(label=request.POST.get('label',''),
                                             content_object=ib)

    return HttpResponseRedirect("/edit" + section.get_absolute_url())

# should add this to Hierarchy.
def get_first_leaf(section):
    if (section.is_leaf()):
        return section
    
    return get_first_leaf(section.get_children()[0])
    
def index(request):
    #determine the first page in the tree & navigate to it
    h = get_hierarchy()
    s = h.get_root()
    path = "/"
    
    first_leaf = get_first_leaf(s)
    if (first_leaf == s):
        # the tree is not yet setup, direct the site to edit
        return HttpResponseRedirect("/edit/")
    else:
        return HttpResponseRedirect(first_leaf.get_absolute_url())