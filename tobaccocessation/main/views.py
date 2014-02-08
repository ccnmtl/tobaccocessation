from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils import simplejson
from pagetree.helpers import get_section_from_path, get_module, get_hierarchy
from pagetree.models import Section, UserLocation, UserPageVisit
from tobaccocessation.activity_prescription_writing.models import \
    ActivityState as PrescriptionWritingActivityState
from tobaccocessation.activity_virtual_patient.models import \
    ActivityState as VirtualPatientActivityState
from tobaccocessation.main.models import QuickFixProfileForm, UserProfile
UNLOCKED = ['resources']  # special cases


class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if isinstance(items, type({})):
                ctx = RequestContext(request)
                return render_to_response(self.template_name,
                                          items,
                                          context_instance=ctx)
            else:
                return items

        return rendered_func


@login_required
@rendered_with('main/index.html')
def index(request):
    """Need to determine here whether to redirect
    to profile creation or registraion and profile creation"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    if profile is not None and profile.has_consented():
        profile = UserProfile.objects.get(user=request.user)
        h = get_hierarchy(name=profile.role())
        return {'user': request.user,
                'profile': profile,
                'hierarchy': h,
                'root': h.get_root()}
    else:
        return HttpResponseRedirect(reverse('create_profile'))


def _edit_response(request, section):
    return dict(section=section,
                hierarchy=section.hierarchy,
                module=get_module(section),
                root=section.hierarchy.get_root())


@user_passes_test(lambda u: u.is_staff)
@rendered_with('main/edit_page.html')
def edit_page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _edit_response(request, section)


@user_passes_test(lambda u: u.is_staff)
def edit_page_by_id(request, hierarchy, section_id):
    section = Section.objects.get(id=section_id)
    return HttpResponseRedirect(section.get_edit_url())


@user_passes_test(lambda u: u.is_staff)
@rendered_with('main/edit_page.html')
def edit_resources(request, path):
    section = get_section_from_path(path, "resources")
    return _edit_response(request, section, path)


@login_required
@rendered_with('main/page.html')
def page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _response(request, section)


@login_required
@rendered_with('main/page.html')
def page_by_id(request, hierarchy, section_id):
    section = Section.objects.get(id=section_id)
    return HttpResponseRedirect(section.get_absolute_url())


@login_required
@rendered_with('main/page.html')
def resources(request, path):
    section = get_section_from_path(path, "resources")
    return _response(request, section, path)


def _get_left_parent(first_leaf):
    leftnav = first_leaf
    if first_leaf.depth == 4:
        leftnav = first_leaf.get_parent()
    elif first_leaf.depth == 5:
        leftnav = first_leaf.get_parent().get_parent()
    return leftnav


@rendered_with('main/page.html')
def _response(request, section):
    h = section.hierarchy
    if request.method == "POST":
        # user has submitted a form. deal with it
        proceed = True
        for p in section.pageblock_set.all():
            if request.POST.get('action', '') == 'reset':
                section.reset(request.user)
                return HttpResponseRedirect(section.get_absolute_url())

            if hasattr(p.block(), 'needs_submit') and p.block().needs_submit():
                proceed = section.submit(request.POST, request.user)

        if request.is_ajax():
            json = simplejson.dumps({'submitted': 'True'})
            return HttpResponse(json, 'application/json')
        elif proceed:
            return HttpResponseRedirect(section.get_next().get_absolute_url())
        else:
            # giving them feedback before they proceed
            return HttpResponseRedirect(section.get_absolute_url())
    else:
        first_leaf = h.get_first_leaf(section)
        ancestors = first_leaf.get_ancestors()
        profile = UserProfile.objects.filter(user=request.user)[0]

        # Skip to the first leaf, make sure to mark these sections as visited
        if (section != first_leaf):
            profile.set_has_visited(ancestors)
            return HttpResponseRedirect(first_leaf.get_absolute_url())

        # the previous node is the last leaf, if one exists.
        prev_page = _get_previous_leaf(first_leaf)
        next_page = first_leaf.get_next()

        # Is this section unlocked now?
        can_access = _unlocked(first_leaf, request.user, prev_page, profile)
        if can_access:
            profile.set_has_visited([section])

        module = None
        if not first_leaf.is_root() and len(ancestors) > 1:
            module = ancestors[1]

        allow_redo = False
        needs_submit = first_leaf.needs_submit()
        if needs_submit:
            allow_redo = first_leaf.allow_redo()

        return dict(request=request,
                    hierarchy=h,
                    section=first_leaf,
                    accessible=can_access,
                    module=module,
                    root=ancestors[0],
                    previous=prev_page,
                    next=next_page,
                    needs_submit=needs_submit,
                    allow_redo=allow_redo,
                    is_submitted=first_leaf.submitted(request.user))


def create_profile(request):
    """We actually dont need two views - can just return
    a registration form for non Columbia ppl and a
    QuickFixProfileForm for the Columbia ppl"""

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)

    form = QuickFixProfileForm()
    if request.method == 'POST':
        form = QuickFixProfileForm(request.POST)
        if form.is_valid():
            user_profile.institute = form.data['institute']
            user_profile.consent = True
            user_profile.is_faculty = form.data['is_faculty']
            user_profile.year_of_graduation = form.data['year_of_graduation']
            user_profile.specialty = form.data['specialty']
            user_profile.gender = form.data['gender']
            user_profile.hispanic_latino = form.data['hispanic_latino']
            user_profile.race = form.data['race']
            user_profile.age = form.data['age']
            user_profile.save()
            return HttpResponseRedirect('/')
    else:
        form = QuickFixProfileForm()

    return render(request, 'main/create_profile.html', {
        'form': form
    })


def accessible(section, user):
    try:
        previous = section.get_previous()
        return _unlocked(section, user, previous, user.get_profile())
    except AttributeError:
        return False


@login_required
def is_accessible(request, section_slug):
    section = Section.objects.get(slug=section_slug)
    previous = section.get_previous()
    response = {}

    if _unlocked(section, request.user, previous, request.user.get_profile()):
        response[section_slug] = "True"

    json = simplejson.dumps(response)
    return HttpResponse(json, 'application/json')


@login_required
def clear_state(request):
    try:
        request.user.get_profile().delete()
    except UserProfile.DoesNotExist:
        pass

    # clear visits & saved locations
    UserLocation.objects.filter(user=request.user).delete()
    UserPageVisit.objects.filter(user=request.user).delete()

    # clear quiz
    import quizblock
    quizblock.models.Submission.objects.filter(user=request.user).delete()

    # clear prescription writing
    PrescriptionWritingActivityState.objects.filter(user=request.user).delete()

    # clear virtual patient
    VirtualPatientActivityState.objects.filter(user=request.user).delete()

    return HttpResponseRedirect(reverse("index"))

#####################################################################
## View Utility Methods


def _get_previous_leaf(section):
    depth_first_traversal = section.get_root().get_annotated_list()
    for (i, (s, ai)) in enumerate(depth_first_traversal):
        if s.id == section.id:
            # first element is the root, so we don't want to return that
            prev = None
            while i > 1 and not prev:
                (node, x) = depth_first_traversal[i - 1]
                if node and len(node.get_children()) > 0:
                    i -= 1
                else:
                    prev = node
            return prev
    # made it through without finding ourselves? weird.
    return None

UNLOCKED = ['resources']  # special cases


def _unlocked(section, user, previous, profile):
    """ if the user can proceed past this section """
    if (not section or
        section.is_root() or
        profile.get_has_visited(section) or
        section.slug in UNLOCKED or
            section.hierarchy.name in UNLOCKED):
        return True

    if not previous or previous.is_root():
        return True

    for p in previous.pageblock_set.all():
        if hasattr(p.block(), 'unlocked'):
            if not p.block().unlocked(user):
                return False

    if previous.slug in UNLOCKED:
        return True

    # Special case for virtual patient as this activity was too big to fit
    # into a "block"
    if (previous.label == "Virtual Patient" and
            not VirtualPatientActivityState.is_complete(user)):
        return False

    return profile.get_has_visited(previous)
