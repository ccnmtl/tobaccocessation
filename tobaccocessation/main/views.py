from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils import simplejson
from pagetree.helpers import get_section_from_path, get_module
from pagetree.models import Section
from registration.forms import RegistrationForm
from tobaccocessation.activity_prescription_writing.models import \
    ActivityState as PrescriptionWritingActivityState
from tobaccocessation.activity_treatment_choice.models import \
    ActivityState as TreatmentChoiceActivityState
from tobaccocessation.activity_virtual_patient.models import \
    ActivityState as VirtualPatientActivityState
from tobaccocessation.main.models import QuickFixProfileForm, UserProfile
from registration.signals import user_registered
import django.dispatch

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
    profiles = UserProfile.objects.filter(user=request.user)
    if len(profiles) > 0 and profiles[0].has_consented():
        return {'user': request.user,
                'profile': profiles[0]}
    else:
        return HttpResponseRedirect(reverse('create_profile'))


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
def edit_page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _edit_response(request, section, path)


@login_required
@rendered_with('main/page.html')
def page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _response(request, section, path)


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
        profile = UserProfile.objects.filter(user=request.user)[0]

        # Skip to the first leaf, make sure to mark these sections as visited
        if (section != first_leaf):
            profile.set_has_visited(ancestors)
            url = "/%s%s" % ("pages", first_leaf.get_absolute_url())
            return HttpResponseRedirect(url)

        # the previous node is the last leaf, if one exists.
        prev = _get_previous_leaf(first_leaf)
        next_page = first_leaf.get_next()

        # Is this section unlocked now?
        can_access = _unlocked(first_leaf, request.user, prev, profile)
        if can_access:
            profile.set_has_visited([section])

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


"""Start of Horribly Wrong UserProfile Signals Attempt"""
"""Should sender be a signal object? do these arguments stay kwargs and sender?"""

def registration_reciever(user_registered, institute, is_faculty, year_of_graduation, specialty, gender, hispanic_latino, race, age, user_id):
    """something here"""
    UserProfile = User.objects.get(pk=user_id)
    user_profile.institute = institute
    user_profile.consent = True
    user_profile.is_faculty = is_faculty
    user_profile.year_of_graduation = year_of_graduation
    user_profile.specialty = specialty
    user_profile.gender = gender
    user_profile.hispanic_latino = hispanic_latino
    user_profile.race = race
    user_profile.age = age
    user_profile.save()


"""Not clear to me if this needs to be in a class and if so - where?
UserProfile? UserRegistration? does it even need to be done if it
is using a signal from the Registration Application?"""
#def signal_sender():

"""attempting to mannually connect reciever function to signal sender"""
user_registered.connect(registration_reciever)


"""Define args for new UserProfile - not sure if if lives here...."""
user_registered = django.dispatch.Signal(providing_args=["institute","is_faculty","year_of_graduation","specialty","gender","hispanic_latino","race","age","user_id"])

"""End of Feeble UserProfile Signal Attempt"""

"""We actually dont need two views - can just return a registration form for non Columbia ppl and a QuickFixProfileForm for the Columbia ppl"""
def create_profile(request):
    profiles = UserProfile.objects.filter(user=request.user)
    columbia_student = False
    if len(request.user.groups.filter(name='ALL_CU')) > 0:
        columbia_student = True
    user_profile = UserProfile(user=request.user)
    if request.method == 'POST':
        form = QuickFixProfileForm(request.POST)
        if columbia_student == False:
            userprofile.user.username = form.data['username']
            userprofile.user.email = form.data['email']
            userprofile.user.first_name = form.data['first_name']
            userprofile.user.last_name = form.data['last_name']
            userprofile.user.save()
            user_profile.institute = form.data['institute']
        elif columbia_student == True:
            user_profile.institute = 'I1'
        user_profile.consent = True
        """I think we are assuming if they could fill out
        the form that they indeed consented?"""
        #form.data['consent']
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
        'form': form, 'columbia_student': columbia_student
    })


def update_profile(request):
    profiles = UserProfile.objects.filter(user=request.user)
    columbia_student = False
    if len(request.user.groups.filter(name='ALL_CU')) > 0:
        columbia_student = True
    user_profile = UserProfile(user=request.user)
    if request.method == 'POST':
        form = QuickFixProfileForm(request.POST)
        if columbia_student==False:
            userprofile.user.username = form.data['username']
            userprofile.user.email = form.data['email']
            userprofile.user.first_name = form.data['first_name']
            userprofile.user.last_name = form.data['last_name']
            userprofile.user.save()
            user_profile.institute = form.data['institute']
        elif columbia_student==True:
            # institution should have already been saved
            user_profile.institute = 'I1'
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
        form = QuickFixProfileForm()  # An unbound form

    return render(request, 'main/create_profile.html', {
        'form': form, 'columbia_student': columbia_student
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

    # clear quiz
    import quizblock
    quizblock.models.Submission.objects.filter(user=request.user).delete()

    # clear prescription writing
    PrescriptionWritingActivityState.objects.filter(user=request.user).delete()

    # clear treatment choices
    TreatmentChoiceActivityState.objects.filter(user=request.user).delete()

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



