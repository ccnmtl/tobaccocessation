import csv
from json import dumps
from zipfile import ZipFile
from StringIO import StringIO

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils.encoding import smart_str

from pagetree.helpers import get_section_from_path, get_module, get_hierarchy
from pagetree.models import Section, UserLocation, UserPageVisit, Hierarchy

from tobaccocessation.activity_prescription_writing.models import \
    ActivityState as PrescriptionWritingState, PrescriptionColumn
from tobaccocessation.activity_virtual_patient.models import \
    ActivityState as VirtualPatientActivityState, VirtualPatientColumn
from tobaccocessation.main.choices import RACE_CHOICES, SPECIALTY_CHOICES, \
    INSTITUTION_CHOICES, HISPANIC_LATINO_CHOICES, GENDER_CHOICES, choices_key
from tobaccocessation.main.models import QuickFixProfileForm, UserProfile, \
    QuestionColumn


UNLOCKED = ['resources', 'faculty']  # special cases


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
        hierarchy = get_hierarchy(name=profile.role())
        return {'user': request.user,
                'profile': profile,
                'hierarchy': hierarchy,
                'root': hierarchy.get_root()}
    else:
        return HttpResponseRedirect(reverse('create_profile'))


@user_passes_test(lambda u: u.is_staff)
@rendered_with('main/edit_page.html')
def edit_page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return dict(section=section,
                hierarchy=section.hierarchy,
                module=get_module(section),
                root=section.hierarchy.get_root())


def page_post(request, section):
    proceed = True
    for p in section.pageblock_set.all():
        if request.POST.get('action', '') == 'reset':
            section.reset(request.user)
            return HttpResponseRedirect(section.get_absolute_url())

        if hasattr(p.block(), 'needs_submit') and p.block().needs_submit():
            proceed = section.submit(request.POST, request.user)

    if request.is_ajax():
        json = dumps({'submitted': 'True'})
        return HttpResponse(json, 'application/json')
    elif request.POST.get('proceed', False) or proceed:
        return HttpResponseRedirect(section.get_next().get_absolute_url())
    else:
        # giving them feedback before they proceed
        return HttpResponseRedirect(section.get_absolute_url())


@login_required
@rendered_with('main/page.html')
def page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    h = section.hierarchy
    if request.method == "POST":
        # user has submitted a form. deal with it
        return page_post(request, section)
    first_leaf = h.get_first_leaf(section)
    ancestors = first_leaf.get_ancestors()
    profile = UserProfile.objects.filter(user=request.user)[0]

    # Skip to the first leaf, make sure to mark these sections as visited
    if (section != first_leaf):
        profile.set_has_visited(ancestors)
        return HttpResponseRedirect(first_leaf.get_absolute_url())

    # the previous node is the last leaf, if one exists.
    prev_page = _get_previous_leaf(first_leaf)
    next_page = _get_next(first_leaf)

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
                ancestors=ancestors,
                profile=profile,
                hierarchy=h,
                section=first_leaf,
                can_access=can_access,
                module=module,
                root=ancestors[0],
                previous=prev_page,
                next=next_page,
                needs_submit=needs_submit,
                allow_redo=allow_redo,
                is_submitted=first_leaf.submitted(request.user))


def create_profile(request):
    """We actually don't need two views - can just return
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
            user_profile.consent_participant = \
                form.data.get('consent_participant', False)
            user_profile.consent_not_participant = \
                form.data.get('consent_not_participant', False)
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
        return _unlocked(section, user, previous, user.profile)
    except AttributeError:
        return False


@login_required
def is_accessible(request, section_slug):
    section = Section.objects.get(slug=section_slug)
    previous = section.get_previous()
    response = {}

    if _unlocked(section, request.user, previous, request.user.profile):
        response[section_slug] = "True"

    json = dumps(response)
    return HttpResponse(json, 'application/json')


@login_required
def clear_state(request):
    try:
        request.user.profile.delete()
    except UserProfile.DoesNotExist:
        pass

    # clear visits & saved locations
    UserLocation.objects.filter(user=request.user).delete()
    UserPageVisit.objects.filter(user=request.user).delete()

    # clear quiz
    import quizblock
    quizblock.models.Submission.objects.filter(user=request.user).delete()

    # clear prescription writing
    PrescriptionWritingState.objects.filter(user=request.user).delete()

    # clear virtual patient
    VirtualPatientActivityState.objects.filter(user=request.user).delete()

    return HttpResponseRedirect(reverse("index"))


# ####################################################################
# View Utility Methods

def _get_next(section):
    # next node in the depth-first traversal
    depth_first_traversal = Section.get_annotated_list(section.get_root())
    for (i, (s, ai)) in enumerate(depth_first_traversal):
        if s.id == section.id:
            if i < len(depth_first_traversal) - 1:
                return depth_first_traversal[i + 1][0]
            else:
                return None
    # made it through without finding ourselves? weird.
    return None


def _get_previous_leaf(section):
    depth_first_traversal = Section.get_annotated_list(section.get_root())
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


def _unlocked(section, user, previous, profile):
    if (section.hierarchy.name == 'faculty' and (
            not profile.is_role_faculty() and not user.is_staff)):
        return False

    # if the user can proceed past this section
    if (not section or
        section.is_root() or
        profile.get_has_visited(section) or
        section.slug in UNLOCKED or
            section.hierarchy.name in UNLOCKED):
        return True

    if not previous or previous.is_root():
        return True

    for pbl in previous.pageblock_set.all():
        if hasattr(pbl.block(), 'unlocked'):
            if not pbl.block().unlocked(user):
                return False

    if previous.slug in UNLOCKED:
        return True

    return profile.get_has_visited(previous)


# ####################################################################
# Reporting


def _get_columns(key, hierarchy):
    columns = []
    for section in hierarchy.get_root().get_descendants():
        columns += QuestionColumn.all(hierarchy, section, key)
        columns += PrescriptionColumn.all(hierarchy, section, key)
        columns += VirtualPatientColumn.all(hierarchy, section, key)
    return columns


def _all_results_key(output, hierarchy):
    """
        A "key" for all questions and answers in the system.
        * One row for short/long text questions
        * Multiple rows for single/multiple-choice questions.
        Each question/answer pair get a row
        itemIdentifier - unique system identifier,
            concatenates hierarchy id, item type string,
            page block id (if necessary) and item id
        hierarchy - first child label in the hierarchy
        section description - ['', 'Prescription Writing Exercise', 'Quiz'...]
        itemType - ['single choice', 'multiple choice', 'short text', 'bool']
        itemText - identifying text for the item
        answerIdentifier - for single/multiple-choice questions. an answer id
        answerText
    """
    writer = csv.writer(output)
    headers = ['itemIdentifier', 'hierarchy', 'exercise type',
               'itemType', 'itemText', 'answerIdentifier', 'answerText']
    writer.writerow(headers)

    # key to profile choices / values
    # username, e-mail, gender, is_faculty, institution, specialty
    #    hispanic/latino, race, year_of_graduation, consent, % complete
    writer.writerow(['username', 'profile', '', 'string', 'Username'])
    writer.writerow(['email', 'profile', '', 'string', 'User E-mail'])
    choices_key(writer, GENDER_CHOICES, 'gender', 'single_choice')
    writer.writerow(['faculty', 'profile', '', 'boolean', 'Is Faculty'])
    choices_key(writer, INSTITUTION_CHOICES, 'institution', 'single_choice')
    choices_key(writer, SPECIALTY_CHOICES, 'specialty', 'single_choice')
    choices_key(writer, HISPANIC_LATINO_CHOICES,
                'hispanic_latino', 'single_choice')
    choices_key(writer, RACE_CHOICES, 'race', 'single_choice')
    writer.writerow(['year_of_graduation',
                     'profile', '', 'number', 'Graduation Year'])
    writer.writerow(['consent', 'profile', '', 'boolean', 'Has Consented'])
    writer.writerow(['complete', 'profile', '', 'percent', 'Percent Complete'])

    # quizzes, prescription writing, virtual patient keys -- data / values
    for column in _get_columns(True, hierarchy):
        writer.writerow(column.key_row())

    return writer


def _all_results(output, hierarchy, include_superusers):
    """
    All system results
    * One or more column for each question in system.
        ** 1 column for short/long text. label = itemIdentifier from key
        ** 1 column for single choice. label = itemIdentifier from key
        ** n columns for multiple choice: 1 column for each possible answer
           *** column labeled as itemIdentifer_answer.id

        * One row for each user in the system.
            1. username
            2 - n: answers
                * short/long text. text value
                * single choice. answer.id
                * multiple choice.
                    ** answer id is listed in each question/answer
                    column the user selected
                * Unanswered fields represented as an empty cell
    """
    writer = csv.writer(output)

    columns = _get_columns(False, hierarchy)

    headers = ['username', 'email', 'gender', 'faculty', 'institution',
               'specialty', 'hispanic_latino', 'race', 'year_of_graduation',
               'consent', 'percent_complete']
    for column in columns:
        headers += [column.identifier()]
    writer.writerow(headers)

    # Only look at users who have create a profile + consented
    profiles = UserProfile.objects.filter(consent=True)
    if not include_superusers:
        profiles = profiles.filter(user__is_superuser=False)

    for profile in profiles:
        row = [profile.user.username, profile.user.email, profile.gender,
               profile.is_role_faculty(), profile.institute,
               profile.specialty, profile.hispanic_latino, profile.race,
               profile.year_of_graduation, profile.has_consented(),
               profile.percent_complete()]

        for column in columns:
            v = smart_str(column.user_value(profile.user))
            row.append(v)

        writer.writerow(row)

    return writer


@user_passes_test(lambda u: u.is_superuser)
@rendered_with("main/report.html")
def report(request):
    if request.method == "GET":
        exclusions = ['faculty', 'resources']
        hierarchies = Hierarchy.objects.all().exclude(
            name__in=exclusions).order_by("id")
        return {'hierarchies': hierarchies}
    else:
        hierarchy_id = request.POST.get('hierarchy-id', None)
        hierarchy = Hierarchy.objects.get(id=hierarchy_id)

        include_superusers = request.POST.get('include-superusers', False)

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename=tobacco.zip'

        z = ZipFile(response, 'w')

        output = StringIO()  # temp output file
        _all_results_key(output, hierarchy)
        z.writestr("tobacco_%s_key.csv" % hierarchy.name, output.getvalue())

        output.truncate(0)
        output.seek(0)
        _all_results(output, hierarchy, include_superusers)
        z.writestr("tobacco_%s_values.csv" % hierarchy.name, output.getvalue())

        return response
