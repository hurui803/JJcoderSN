import logging
from functools import update_wrapper

from django.core.exceptions import ImproperlyConfigured
from django.http import (
    HttpResponse, HttpResponseGone, HttpResponseNotAllowed,
    HttpResponsePermanentRedirect, HttpResponseRedirect,
)
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import classonlymethod

logger = logging.getLogger('django.request')


class ContextMixin:
    """
    一个默认的上下文混合，它将get_context_data（）接收到的关键字参数作为模板上下文传递。
    """
    extra_context = None

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs


class View:
    """
    故意为所有视图提供简单的父类。仅实现按方法调度和简单的健全性检查。
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        """
        构造函数。在URLconf中调用；可以包含有用的额外关键字参数以及其他内容。
        """
        # 遍历关键字参数，然后将其值保存到我们的实例中，或者引发错误。
        for key, value in kwargs.items():
            setattr(self, key, value)  # 将键和值保存到self中

    @classonlymethod
    def as_view(cls, **initkwargs):
        """请求-响应过程的主要入口点。"""
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))  # 上面这两个报错还不太懂

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.setup(request, *args, **kwargs)
            if not hasattr(self, 'request'):
                raise AttributeError(
                    "%s instance has no 'request' attribute. Did you override "
                    "setup() and forget to call super()?" % cls.__name__
                )
            return self.dispatch(request, *args, **kwargs)  # 这里调用了dispatch方法

        view.view_class = cls
        view.view_initkwargs = initkwargs

        # 从类中获取名称和文档字符串
        update_wrapper(view, cls, updated=())

        # 以及由装饰器设置的可能属性，例如csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view  # 返回一个view

    def setup(self, request, *args, **kwargs):
        """初始化所有视图方法共享的属性。"""
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def dispatch(self, request, *args, **kwargs):
        # 尝试调度正确的方法；如果不存在方法，则转到错误处理程序。如果request方法不在批准列表中，则也应遵循错误处理程序。
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        # 看self中是否有http_method_names中的属性，如果有则handler=request.method.lower(),否则调用self.http_method_not_allowed
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(
            'Method Not Allowed (%s): %s', request.method, request.path,
            extra={'status_code': 405, 'request': request}
        )  # 打印日志报错信息，级别是warning，status_code是405：方法禁用 禁用请求中指定的方法。
        return HttpResponseNotAllowed(self._allowed_methods())

    def options(self, request, *args, **kwargs):
        """处理对OPTIONS HTTP动词的请求的响应。"""
        response = HttpResponse()
        response['Allow'] = ', '.join(self._allowed_methods())
        response['Content-Length'] = '0'
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class TemplateResponseMixin:
    """可用于渲染模板的mixin。"""
    template_name = None
    template_engine = None
    response_class = TemplateResponse
    content_type = None

    def render_to_response(self, context, **response_kwargs):
        """
        使用此视图的`response_class`返回响应，并使用给定上下文渲染模板。

       将response_kwargs传递给响应类的构造函数。
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )

    def get_template_names(self):
        """
        返回用于请求的模板名称列表。必须返回一个列表。如果render_to_response（）被覆盖，则可能不会被调用。
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name]  # 必须返回一个列表


class TemplateView(TemplateResponseMixin, ContextMixin, View):
    """
    渲染模板。将关键字参数从URLconf传递到上下文。
    """

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class RedirectView(View):
    """提供任何GET请求的重定向。"""
    permanent = False
    url = None
    pattern_name = None
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        """
       返回URL重定向到。 URL模式匹配中生成重定向请求的关键字参数作为kwargs提供给此方法。
        """
        if self.url:
            url = self.url % kwargs
        elif self.pattern_name:
            url = reverse(self.pattern_name, args=args, kwargs=kwargs)
        else:
            return None

        args = self.request.META.get('QUERY_STRING', '')
        if args and self.query_string:
            url = "%s?%s" % (url, args)
        return url

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if url:
            if self.permanent:
                return HttpResponsePermanentRedirect(url)
            else:
                return HttpResponseRedirect(url)
        else:
            logger.warning(
                'Gone: %s', request.path,
                extra={'status_code': 410, 'request': request}
            )
            return HttpResponseGone()

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
