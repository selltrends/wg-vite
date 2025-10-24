from collections import defaultdict

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageBlock, ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from {{ project_name }}.utils.struct_values import CardStructValue, LinkStructValue
from {{ project_name }}.utils.choices import SVGIcon


class CTALinkStructValue(blocks.StructValue):
    def url(self):
        if cta_url := self.get("cta_url"):
            return cta_url

        if cta_page := self.get("cta_page"):
            return cta_page.url

        return ""


class CTALinkMixin(blocks.StructBlock):
    class Meta:
        value_class = CTALinkStructValue

    def clean(self, value):
        struct_value = super().clean(value)

        errors = {}
        url = value.get("cta_url")
        page = value.get("cta_page")
        if self.required and not page and not url:
            error = ErrorList(
                [ValidationError("You must specify CTA page or CTA URL.")]
            )
            errors["cta_url"] = errors["cta_page"] = error

        if page and url:
            error = ErrorList(
                [
                    ValidationError(
                        "You must specify CTA page or CTA URL. You can't use both."
                    )
                ]
            )
            errors["cta_url"] = errors["cta_page"] = error

        if not value.get("text") and (page or url):
            error = ErrorList([ValidationError("You must specify CTA text.")])
            errors["text"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value["cta_url"]:
            context["value"]["url"] = value["cta_url"]
        if value["cta_page"]:
            context["value"]["url"] = value["cta_page"].get_url
        return context


class CTABlock(CTALinkMixin):
    text = blocks.CharBlock(label="CTA text", max_length=255, required=False)
    cta_page = blocks.PageChooserBlock(label="CTA page", required=False)
    cta_url = blocks.URLBlock(label="CTA URL", required=False)

    @property
    def required(self):
        return True

    class Meta:
        icon = "bullhorn"
        template = "components/streamfields/cta/cta_block.html"
        label = "CTA"


class OptionalCTABlock(CTABlock):
    @property
    def required(self):
        return False


class CardBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=255)
    description = blocks.RichTextBlock(required=False, features=["bold", "italic"])
    meta_icon = blocks.ChoiceBlock(choices=SVGIcon.choices)
    meta_text = blocks.TextBlock(max_length=50)
    cta = OptionalCTABlock()

    class Meta:
        icon = "address-card"
        template = "components/streamfields/cards/card_block.html"
        label = "Card"


class LogoCardBlock(CTALinkMixin):
    text = blocks.CharBlock(label="Heading", max_length=255)
    description = blocks.RichTextBlock(required=False, features=["bold", "italic"])
    meta_icon = blocks.ChoiceBlock(choices=SVGIcon.choices)
    meta_text = blocks.TextBlock(max_length=50)
    logo = ImageBlock(required=False)
    cta_page = blocks.PageChooserBlock(label="CTA page", required=False)
    cta_url = blocks.URLBlock(label="CTA URL", required=False)

    class Meta:
        icon = "image"
        template = "components/streamfields/cards/logo_card_block.html"
        label = "Logo card"


class CardsBlock(blocks.StructBlock):
    cards = blocks.ListBlock(CardBlock())

    class Meta:
        template = "components/streamfields/cards/cards_list_block.html"
        label = "Cards"


class LogoCardsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=255, required=False)
    cards = blocks.ListBlock(LogoCardBlock())

    class Meta:
        template = "components/streamfields/cards/logo_cards_list_block.html"
        label = "Logo cards"


class LogoBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    logos = blocks.ListBlock(
        ImageBlock(),
    )

    class Meta:
        icon = "HEART"
        template = "components/streamfields/logo_block/logo_block.html"

class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    content = blocks.RichTextBlock()

    class Meta:
        label = "Section"
        icon = "title"


class AccordionBlock(blocks.StructBlock):
    heading = blocks.ListBlock(AccordionBlock())
    list = blocks.ListBlock(AccordionBlock())

    class Meta:
        icon = "list-ol"
        template = "components/accordion/accordion.html"


class CaptionedImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    image_alt_text = blocks.CharBlock(
        required=False,
        help_text="If left blank, the image's global alt text will be used.",
    )
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "components/streamfield/blocks/image_block.html"


class InternalLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    title = blocks.CharBlock(
        required=False,
        help_text="Leave blank to use page's listing title.",
    )

    class Meta:
        icon = "link"
        value_class = LinkStructValue


class ArticlePageLinkBlock(InternalLinkBlock):
    page = blocks.PageChooserBlock(
        page_type="news.ArticlePage",
    )


class ExternalLinkBlock(blocks.StructBlock):
    link = blocks.URLBlock()
    title = blocks.CharBlock()

    class Meta:
        icon = "link"
        value_class = LinkStructValue


class LinkStreamBlock(blocks.StreamBlock):
    """
    StreamBlock that allows editors to add a single link of type internal or external.
    """

    internal = InternalLinkBlock()
    external = ExternalLinkBlock()

    class Meta:
        icon = "link"
        label = "Link"
        min_num = 1
        max_num = 1


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(form_classname="title")
    attribution = blocks.CharBlock(required=False)

    class Meta:
        icon = "openquote"
        template = "components/streamfield/blocks/quote_block.html"


class CardBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=255)
    description = blocks.RichTextBlock(required=False, features=["bold", "italic"])
    link = LinkStreamBlock(required=False, min_num=0)

    class Meta:
        icon = "form"
        template = "components/streamfield/blocks/card_block.html"
        label = "Card"
        value_class = CardStructValue


class FeaturedArticleBlock(blocks.StructBlock):
    link = ArticlePageLinkBlock()
    image = ImageBlock(
        required=False,
        help_text="Set to override the image of the chosen article page.",
    )
    description = blocks.TextBlock(
        max_length=255,
        required=False,
        help_text="Choose to override a page's listing summary or introduction.",
    )
    cta_text = blocks.CharBlock(
        max_length=255,
        blank=False,
        help_text="This is the cta link text. This will automatically redirect to the article page.",
    )
    left_aligned = blocks.BooleanBlock(
        required=False,
        help_text="If checked, the text will be left-aligned.",
    )

    class Meta:
        icon = "doc-full"
        template = "components/streamfield/blocks/feature_block.html"


class BaseSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        required=True
    )  # Should use H2s only
    sr_only_label = blocks.BooleanBlock(
        required=False,
        label="Screen reader only label",
        help_text="If checked, the heading will be hidden from view and avaliable to screen-readers only.",
    )

    class Meta:
        abstract = True
        icon = "title"


class StatisticSectionBlock(BaseSectionBlock):
    statistics = blocks.ListBlock(
        SnippetChooserBlock(
            "utils.Statistic"
        ),
        max_num=3,
        min_num=3,
    )

    class Meta:
        icon = "snippet"
        template = "components/streamfield/blocks/stat_block.html"


class CTASectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        required=True
    )
    link = LinkStreamBlock()
    description = blocks.TextBlock(required=False)

    class Meta:
        icon = "link"
        label = "CTA"
        template = "components/streamfield/blocks/cta_block.html"


class BaseCardSectionBlock(BaseSectionBlock):
    cards = blocks.ListBlock(
        CardBlock(),
        max_num=6,
        min_num=3,
        label="Card",
    )
    class Meta:
        abstract = True
        icon = "form"


class CardSectionBlock(BaseCardSectionBlock):
    class Meta:
        template = "components/streamfield/blocks/card_section_block.html"


class PlainCardSectionBlock(BaseCardSectionBlock):
    class Meta:
        icon = "doc-full"
        template = "components/streamfield/blocks/plain_cards_block.html"


class SectionBlocks(blocks.StreamBlock):
    paragraph = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "h3"],
        template="components/streamfield/blocks/paragraph_block.html",
    )


class SectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="components/streamfield/blocks/heading2_block.html",
    )
    content = SectionBlocks()

    class Meta:
        icon = "doc-full"
        template = "components/streamfield/blocks/section_block.html"


class StoryBlock(blocks.StreamBlock):
    section = SectionBlock()
    cta = CTASectionBlock()
    statistics = StatisticSectionBlock()

    class Meta:
        template = "components/streamfield/stream_block.html"


class HomePageStoryBlock(blocks.StreamBlock):
    section = SectionBlock()
    cta = CTASectionBlock()
    statistics = StatisticSectionBlock()
    logos = LogoBlock()

    class Meta:
        template = "components/streamfield/stream_block.html"