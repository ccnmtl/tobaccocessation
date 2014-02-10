from django import template
from tobaccocessation.activity_prescription_writing.models import ActivityState
register = template.Library()


class GetPrescription(template.Node):
    def __init__(self, block, var_name):
        self.block = block
        self.var_name = var_name

    def render(self, context):
        b = context[self.block]
        u = context['request'].user

        state = ActivityState.get_for_user(u).loads()[b.medication_name]
        state['complete'] = b.unlocked(u)
        context[self.var_name] = state
        return ''


@register.tag('getprescription')
def get_prescription(parser, token):
    block = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetPrescription(block, var_name)
