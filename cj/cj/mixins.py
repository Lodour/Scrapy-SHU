# -*- coding: utf-8 -*-
from StringIO import StringIO
from getpass import getpass

import scrapy
from PIL import Image


class CaptchaLoginSpiderMixin(object):
    """
    带验证码的登录爬虫组件，仅适用于本项目。

    入口: self.before_login
    出口: self.after_login
    """

    logger = None

    def before_login(self, response):
        # 获取登录字段名
        login_fields = response.xpath('//input[@type!="hidden" and @type!="submit"]/@name').extract()
        assert len(login_fields) == 3, '登录字段异常: %r' % login_fields

        # 获取验证码URL
        captcha_url = response.xpath('//img[@id="Img1"]/@src').extract()
        assert len(captcha_url) == 1, '获取验证码URL异常: %r' % captcha_url
        captcha_url = response.urljoin(captcha_url[0])

        # 访问验证码，进行登陆操作
        yield scrapy.Request(captcha_url, callback=self.login,
                             meta={'fields': login_fields, 'response': response})

    def login(self, response):
        # 获取验证码
        Image.open(StringIO(response.body)).show()
        captcha = raw_input('请输入验证码: ')

        # 设置登录数据
        fields = response.meta['fields']
        data = (raw_input('请输入学号: '), getpass('请输入密码: '), captcha)
        login_data = dict(zip(fields, data))

        # 执行登录操作，检测登录状态
        yield scrapy.FormRequest.from_response(response.meta['response'], formdata=login_data,
                                               callback=self.check_login)

    def check_login(self, response):
        # 检测登录结果
        error_msg = response.xpath('normalize-space(//div[@id="divLoginAlert"])').extract()
        assert self.logger is not None, '`logger`未重载，请检查继承顺序'
        if error_msg and error_msg[0]:
            self.logger.error(u'登录失败: <%s>', error_msg[0])
            return
        self.logger.info(u'登录成功')

        return self.after_login(response)

    def after_login(self, response):
        raise Exception('未重载登录出口after_login')
