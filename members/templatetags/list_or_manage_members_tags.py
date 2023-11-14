from django import template

register = template.Library()


@register.simple_tag(name="should_show_leave_btn", takes_context=True)
def should_show_leave_btn(context, member):
    project = context.get("project")
    user_can_manage_members = context.get("can_manage_members")
    member_is_creator = member.user.id == project.user.id

    return user_can_manage_members and not member_is_creator
