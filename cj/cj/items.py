# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScoreItem(scrapy.Item):
    term_id = scrapy.Field()
    course_number = scrapy.Field()
    course_name = scrapy.Field()
    credit = scrapy.Field()
    score = scrapy.Field()
    gpa = scrapy.Field()

    fields_to_export = ('term_id', 'course_number', 'course_name', 'credit', 'score', 'gpa')
