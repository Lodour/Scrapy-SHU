# -*- coding: utf-8 -*-
import urlparse

import scrapy

from ..items import ScoreItem
from ..mixins import CaptchaLoginSpiderMixin


class MyScoreSummarySpider(scrapy.Spider, CaptchaLoginSpiderMixin):
    name = 'my_score_summary'
    allowed_domains = ['cj.shu.edu.cn']
    start_urls = ['http://cj.shu.edu.cn/']
    fields_to_export = ScoreItem.fields_to_export[1:] + ScoreItem.fields_to_export[:1]

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.before_login)

    def after_login(self, response):
        # 获取成绩查询入口
        query_url = response.xpath(u'//a[text()="成绩查询"]/@href').extract()
        assert query_url, '获取成绩查询入口失败'
        query_url = response.urljoin(query_url[0])
        yield scrapy.Request(query_url, callback=self.parse_summary)

    def parse_summary(self, response):
        # 获取成绩大表查询入口
        query_url = response.xpath(u'//a[text()="成绩大表"]/@href').extract()
        assert query_url, '获取成绩大表查询入口失败'
        query_url = urlparse.urljoin(response.url, query_url[0])
        print query_url
        yield scrapy.Request(query_url, callback=self.parse_score)

    def parse_score(self, response):
        # 提取所有行
        rows = response.xpath('//tr[count(td)=12]')
        for row in rows:
            # 提取所有列(12)
            cols = row.xpath('td/text()').extract()
            # TODO "<B>以下空白</B>"所在行会产生13个text，考虑寻找更优雅的方式解决
            assert len(cols) in (12, 13), '行解析错误，获得%r列: %r' % (len(cols), cols)

            # 提取两门课程
            for fields in (cols[:6], cols[6:]):
                data = {k: fields[i] for i, k in enumerate(self.fields_to_export)}
                yield ScoreItem(**data)
