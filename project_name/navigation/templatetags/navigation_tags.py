from django import template


register = template.Library()



@register.inclusion_tag("includes/menu_main.html", takes_context=True)
def main_navigation(context):
    menus = []

    try:
        main_navigation = context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation

        for block in main_navigation.menu_sections:
            menus.append(
                {
                    "name": block.value.get("name"),
                    "nav_items": block.value.get("nav_items"),
                }
            )
    except (KeyError, AttributeError):
        return {}

    return {"menus": menus}

