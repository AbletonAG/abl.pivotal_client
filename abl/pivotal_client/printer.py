"""
Print A6 cards based on stories retrieved from Pivotal Tracker.

Install `reportlab` if you want to use this.
"""

from reportlab.lib import pagesizes
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
    )
from reportlab.lib.units import (
    cm,
    mm,
    )

from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    )



class StoryCardStyle(object):
    def __init__(self):
        self.styles = getSampleStyleSheet()

        self.styles.add(
            ParagraphStyle(
                name='StoryTitle',
                alignment=TA_CENTER,
                fontSize=14,
                spaceAfter=5 * mm))

        self.styles.add(
            ParagraphStyle(
                name='StoryDescription',
                fontSize=8,
                spaceAfter=1.5 * mm))

        self.styles.add(
            ParagraphStyle(
                name='StoryMetaData',
                fontSize=7,
                spaceAfter=0))


class A6CardFormat(object):
    PAGE_HEIGHT, PAGE_WIDTH = pagesizes.A6
    PAGE_MARGINS = 5 * mm


class StoryCardPrinter(object):
    def __init__(self, card_formatter_cls=A6CardFormat, stylesheet_cls=StoryCardStyle):
        self.card_formatter = card_formatter_cls
        self.styles = stylesheet_cls().styles


    def create_pdf(self, stories, file_name):
        """
        Create a PDF containing one page for each story.
        """
        doc = SimpleDocTemplate(
            file_name,
            bottomMargin=self.card_formatter.PAGE_MARGINS,
            leftMargin=self.card_formatter.PAGE_MARGINS,
            pagesize=(self.card_formatter.PAGE_WIDTH,
                      self.card_formatter.PAGE_HEIGHT),
            rightMargin=self.card_formatter.PAGE_MARGINS,
            topMargin=self.card_formatter.PAGE_MARGINS,)
        doc_parts = []
        for story in stories:
            header_text = '%s (%s)' % (story['title'],
                                       story['points'] or story['story_type'])
            header = Paragraph(header_text, style=self.styles['StoryTitle'])

            doc_parts.append(header)

            if story['description']:
                lines = story['description'].split('\n')
                paragraphs = [Paragraph(l, style=self.styles['StoryDescription']) for l in lines]

                for paragraph in paragraphs:
                    doc_parts.append(paragraph)

                doc_parts.append(Spacer(self.card_formatter.PAGE_WIDTH, 1 * cm))

            # TODO-mlp: Look into adding story ID and story labels
            # sections to the bottom of the card.

            story_id = Paragraph(
                'Story ID: %s' % story['story_id'],
                style=self.styles['StoryMetaData'])
            doc_parts.append(story_id)

            if story['labels']:
                labels = Paragraph(
                    'Labeled with: %s' % story['labels'],
                    style=self.styles['StoryMetaData'])
                doc_parts.append(labels)

            doc_parts.append(PageBreak())
        doc.build(doc_parts)

