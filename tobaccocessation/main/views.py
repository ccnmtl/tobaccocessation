from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils import simplejson
from pagetree.helpers import get_section_from_path, get_module
from pagetree.models import Section
from tobaccocessation.activity_prescription_writing.models import \
    ActivityState as PrescriptionWritingActivityState
from tobaccocessation.activity_treatment_choice.models import \
    ActivityState as TreatmentChoiceActivityState
from tobaccocessation.activity_virtual_patient.models import \
    ActivityState as VirtualPatientActivityState
from tobaccocessation.main.models import QuickFixProfileForm, UserProfile
import django.core.exceptions
from django.db import DatabaseError
from django.core.exceptions import MultipleObjectsReturned


INDEX_URL = "/welcome/"
UNLOCKED = ['welcome', 'resources']  # special cases
CREATE_COL_PROFILE = "c_profile/" # says form referenced before assignment
CREATE_NOCOL_PROFILE = "nonc_profile/"


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


def _edit_response(request, section, path):
    first_leaf = section.hierarchy.get_first_leaf(section)

    return dict(section=section,
                module=get_module(section),
                root=section.hierarchy.get_root(),
                leftnav=_get_left_parent(first_leaf),
                prev=_get_previous_leaf(first_leaf),
                next=first_leaf.get_next())


@user_passes_test(lambda u: u.is_staff)
@rendered_with('main/edit_page.html')
def edit_page(request, path):
    section = get_section_from_path(path, "main")
    return _edit_response(request, section, path)


@user_passes_test(lambda u: u.is_staff)
@rendered_with('main/edit_page.html')
def edit_resources(request, path):
    section = get_section_from_path(path, "resources")
    return _edit_response(request, section, path)


@login_required
@rendered_with('main/page.html')
def resources(request, path):
    section = get_section_from_path(path, "resources")
    return _response(request, section, path)


@login_required
@rendered_with('main/page.html')
def page(request, path):
    section = get_section_from_path(path, "main")
    return _response(request, section, path)


def _get_left_parent(first_leaf):
    leftnav = first_leaf
    if first_leaf.depth == 4:
        leftnav = first_leaf.get_parent()
    elif first_leaf.depth == 5:
        leftnav = first_leaf.get_parent().get_parent()
    return leftnav


@rendered_with('main/page.html')
def _response(request, section, path):
    h = section.hierarchy
    if request.method == "POST":
        # user has submitted a form. deal with it
        proceed = True
        for p in section.pageblock_set.all():
            if hasattr(p.block(), 'needs_submit'):
                if p.block().needs_submit():
                    prefix = "pageblock-%d-" % p.id
                    data = dict()
                    for k in request.POST.keys():
                        if k.startswith(prefix):
                            data[k[len(prefix):]] = request.POST[k]
                    p.block().submit(request.user, data)
                    if hasattr(p.block(), 'redirect_to_self_on_submit'):
                        proceed = not p.block().redirect_to_self_on_submit()

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
        profile = UserProfile.objects.get_or_create(user=request.user)[0]

        # Skip to the first leaf, make sure to mark these sections as visited
        if (section != first_leaf):
            profile.set_has_visited(ancestors)
            return HttpResponseRedirect(first_leaf.get_absolute_url())

        # the previous node is the last leaf, if one exists.
        prev = _get_previous_leaf(first_leaf)
        next_page = first_leaf.get_next()

        # Is this section unlocked now?
        can_access = _unlocked(first_leaf, request.user, prev, profile)
        if can_access:
            profile.save_last_location(request.path, first_leaf)

        module = None
        if not first_leaf.is_root() and len(ancestors) > 1:
            module = ancestors[1]

        # specify the leftnav parent up here.
        leftnav = _get_left_parent(first_leaf)

        return dict(section=first_leaf,
                    accessible=can_access,
                    module=module,
                    root=ancestors[0],
                    previous=prev,
                    next=next_page,
                    depth=first_leaf.depth,
                    request=request,
                    leftnav=leftnav)


@login_required
def non_columbia_create_profile(request):
    """Redirect Profileless User to create a profile."""
    user =request.user
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=user)
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.save()
        user_profile.gender = form.data['gender']
        user_profile.year_of_graduation = form.data['year_of_graduation']
        user_profile.race = form.data['race']
        user_profile.age = form.data['age']
        user_profile.is_faculty = form.data['is_faculty']
        user_profile.specialty = form.data['specialty']
        user_profile.institute = form.data['institute']
        user_profile.user = user # not sure how this goes
        user_profile.save()
        return HttpResponseRedirect('/')
    else:
        form = QuickFixProfileForm()  # An unbound form

    return render(request, 'main/non_columbia_create_profile.html', {
        'form': form,
    })

def columbia_create_profile(request):
    """Redirect Columbia User with no profile to create a profile
    - we already have their username, first_name, last_name,
    and email."""
    user =request.user
    if request.method == 'POST':
        form = QuickFixProfileForm()
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=user)

        user_profile.gender = form.data['gender']
        user_profile.year_of_graduation = form.data['year_of_graduation']
        user_profile.race = form.data['race']
        user_profile.age = form.data['age']
        user_profile.is_faculty = form.data['is_faculty']
        user_profile.specialty = form.data['specialty']
        user_profile.institute = 'I1'
        user_profile.save()
        return HttpResponseRedirect('/')
    else:
        form = QuickFixProfileForm()  # An unbound form

    return render(request, 'main/columbia_create_profile.html', {
        'form': form,
    })


def update_profile(request):
    user =request.user
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # should probably have something else since they shouldn't be updating a profile they dont have...
            user_profile = UserProfile(user=user)
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.username = form.data['username']
        user.email = form.data['email']
        user.save()
        user_profile.gender = form.data['gender']
        user_profile.year_of_graduation = form.data['year_of_graduation']
        user_profile.race = form.data['race']
        user_profile.age = form.data['age']
        user_profile.is_faculty = form.data['is_faculty']
        user_profile.specialty = form.data['specialty']
        user_profile.institute = form.data['institute']
        user_profile.user = user # not sure how this goes
        user_profile.save()
        return HttpResponseRedirect('/')
    else:
        form = QuickFixProfileForm()  # An unbound form

    return render(request, 'main/update_profile.html', {
        'form': form,
    })




@login_required
def index(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        url = INDEX_URL#url = profile.last_location - why did I do this again?
    except django.core.exceptions.MultipleObjectsReturned:
        profile = UserProfile.objects.filter(user=request.user)[0]
        url = profile.last_location
    except UserProfile.DoesNotExist:
        url = CREATE_COL_PROFILE
    return HttpResponseRedirect(url)
    # CREATE_NOCOL_PROFILE - we need to account for columbia vs non columbia users



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

    # clear quiz
    import quizblock
    quizblock.models.Submission.objects.filter(user=request.user).delete()

    # clear prescription writing
    PrescriptionWritingActivityState.objects.filter(user=request.user).delete()

    # clear treatment choices
    TreatmentChoiceActivityState.objects.filter(user=request.user).delete()

    # clear virtual patient
    VirtualPatientActivityState.objects.filter(user=request.user).delete()

    return HttpResponseRedirect(INDEX_URL)

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

#UNLOCKED = ['welcome', 'resources']  # special cases


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
            if p.block().unlocked(user) is False:
                return False

    if previous.slug in UNLOCKED:
        return True

    # Special case for virtual patient as this activity was too big to fit
    # into a "block"
    if (previous.label == "Virtual Patient" and
            not VirtualPatientActivityState.is_complete(user)):
        return False

    return profile.get_has_visited(previous)


def ajax_consent(request):
    if request.is_ajax():
        test = "TRUE"

    if request.method == 'POST':
        form = DonateForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = DonateForm()
        test = "FALSE"

    return render_to_response('donate_form.html', {'form':form,'test':test}, context_instance=RequestContext(request))

