from django import template
from tobaccocessation.activity_virtual_patient.models import ActivityState
register = template.Library()


class GetUserState(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        u = context['request'].user
        context[self.var_name] = ActivityState.get_for_user(u)
        return ''


@register.tag('getuserstate')
def get_user_state(parser, token):
    var_name = token.split_contents()[1:][1]
    return GetUserState(var_name)


class GetAvailableTreatments(template.Node):
    def __init__(self, block, var_name):
        self.block = block
        self.var_name = var_name

    def render(self, context):
        b = context[self.block]
        u = context['request'].user
        context[self.var_name] = b.available_treatments(u)
        return ''


@register.tag('gettreatments')
def get_available_treatments(parser, token):
    block = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetAvailableTreatments(block, var_name)


class GetMedications(template.Node):
    def __init__(self, block, var_name):
        self.block = block
        self.var_name = var_name

    def render(self, context):
        b = context[self.block]
        u = context['request'].user

        context[self.var_name] = b.medications(u)
        return ''


@register.tag('getmedications')
def get_medications(parser, token):
    block = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetMedications(block, var_name)


class GetResults(template.Node):
    def __init__(self, block, var_name):
        self.block = block
        self.var_name = var_name

    def render(self, context):
        b = context[self.block]
        u = context['request'].user

        context[self.var_name] = b.feedback(u)
        return ''


@register.tag('getresults')
def get_results(parser, token):
    block = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetResults(block, var_name)
