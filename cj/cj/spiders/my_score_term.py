# -*- coding: utf-8 -*-
import scrapy

from ..items import ScoreItem
from ..mixins import CaptchaLoginSpiderMixin


class MyScoreTermSpider(scrapy.Spider, CaptchaLoginSpiderMixin):
    name = 'my_score_term'
    allowed_domains = ['cj.shu.edu.cn']
    start_urls = ['http://cj.shu.edu.cn/']
    fields_to_export = ScoreItem.fields_to_export

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.before_login)

    def after_login(self, response):
        # 获取成绩查询入口
        query_url = response.xpath(u'//a[text()="成绩查询"]/@href').extract()
        assert query_url, '获取成绩查询入口失败'
        query_url = response.urljoin(query_url[0])
        yield scrapy.Request(query_url, callback=self.parse_term)

    def parse_term(self, response):
        # 获取所有可选学期
        terms = response.xpath('//option/@value').extract()
        url = response.url.replace('ScoreQuery', 'CtrlScoreQuery')

        for term_id in terms:
            data = {'academicTermID': term_id}
            yield scrapy.FormRequest(url, formdata=data, meta={'term_id': term_id},
                                     callback=self.parse_score)

    def parse_score(self, response):
        courses = response.xpath('//table/tr[3 <= position() and position() < last()]')
        for course in courses:
            term_id = response.meta['term_id']
            fields = course.xpath('td[1 < position()]/text()').extract()
            data = {k: fields[i] for i, k in enumerate(self.fields_to_export[1:])}
            yield ScoreItem(term_id=term_id, **data)
