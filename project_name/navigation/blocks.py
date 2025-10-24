from wagtail import blocks

from {{ project_name }}.utils.blocks import CTALinkMixin
from {{ project_name }}.utils.choices import SVGIcon


class NavItemBlock(CTALinkMixin):
    text = blocks.CharBlock(label="Nav item name", max_length=55)
    short_description = blocks.CharBlock(required=False, max_length=55)
    icon = blocks.ChoiceBlock(choices=SVGIcon.choices)
    cta_page = blocks.PageChooserBlock(label="Page", required=False)
    cta_url = blocks.URLBlock(label="External Link", required=False)

    @property
    def required(self):
        return True

    class Meta:
        icon = "link"
        label = "Nav item"

class MainMenuSectionBlock(blocks.StructBlock):
    name = blocks.CharBlock(max_length=255)
    nav_items = blocks.ListBlock(NavItemBlock())

    class Meta:
        icon = "bars"
        label = "Main menu section"