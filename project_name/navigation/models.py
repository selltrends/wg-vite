from django.db import models
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock

from {{ project_name }}.utils.blocks import LinkStreamBlock, InternalLinkBlock
from {{ project_name }}.navigation.blocks import MainMenuSectionBlock
from wagtail.snippets.models import register_snippet


@register_snippet
class MainMenu(ClusterableModel):
    name = models.CharField(max_length=255)
    menu_sections = StreamField([("menu_section", MainMenuSectionBlock())])

    panels = [
        FieldPanel("name"),
        FieldPanel("menu_sections", classname="collapsible"),
    ]

    class Meta:
        verbose_name = "Main menu"

    def __str__(self) -> str:
        return f"Main menu: {self.name}"

    def save(self, **kwargs):
        super().save(**kwargs)

        for nav in NavigationSettings.objects.filter(primary_navigation=self):
            nav.save(fragment_to_clear="primarynav")

@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    primary_navigation = models.ForeignKey(
        "navigation.MainMenu",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_navigation = StreamField(
        [("link_section", blocks.StructBlock([
                ("section_heading", blocks.CharBlock()),
                ("links", LinkStreamBlock(
                    label = "Links", 
                    max_num = None
                )),
            ])) 
        ],
        blank=True,
    )

    panels = [
        FieldPanel("primary_navigation"),
        FieldPanel("footer_navigation"),
    ]

