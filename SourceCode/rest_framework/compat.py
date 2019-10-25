"""
`compat`模块支持与旧版本的向后兼容性版本的Django / Python，以及围绕可选软件包的兼容性包装。
"""
import sys

from django.conf import settings
from django.views.generic import View

try:
    from django.urls import (  # noqa
        URLPattern,
        URLResolver,
    )
except ImportError:
    # Will be removed in Django 2.0
    from django.urls import (  # noqa
        RegexURLPattern as URLPattern,
        RegexURLResolver as URLResolver,
    )

try:
    from django.core.validators import ProhibitNullCharactersValidator  # noqa
except ImportError:
    ProhibitNullCharactersValidator = None


def get_original_route(urlpattern):
    """
    获取用户在path（），re_path（）或url（）指令中输入的原始路由/正则表达式。
    这与下面的get_regex_pattern相反，后者针对RoutePattern返回从path（）生成的原始正则表达式。
    """
    if hasattr(urlpattern, 'pattern'):
        # Django 2.0
        return str(urlpattern.pattern)
    else:
        # Django < 2.0
        return urlpattern.regex.pattern


def get_regex_pattern(urlpattern):
    """
    从urlpattern的RegexPattern或RoutePattern中获取原始正则表达式。与上面的get_original_route不同，这始终是一个正则表达式。
    """
    if hasattr(urlpattern, 'pattern'):
        # Django 2.0
        return urlpattern.pattern.regex.pattern
    else:
        # Django < 2.0
        return urlpattern.regex.pattern


def is_route_pattern(urlpattern):
    if hasattr(urlpattern, 'pattern'):
        # Django 2.0
        from django.urls.resolvers import RoutePattern
        return isinstance(urlpattern.pattern, RoutePattern)
    else:
        # Django < 2.0
        return False


def make_url_resolver(regex, urlpatterns):
    try:
        # Django 2.0
        from django.urls.resolvers import RegexPattern
        return URLResolver(RegexPattern(regex), urlpatterns)

    except ImportError:
        # Django < 2.0
        return URLResolver(regex, urlpatterns)


def unicode_http_header(value):
    # 将HTTP标头值强制转换为unicode。
    if isinstance(value, bytes):
        return value.decode('iso-8859-1')
    return value


def distinct(queryset, base):
    if settings.DATABASES[queryset.db]["ENGINE"] == "django.db.backends.oracle":
        # 针对Oracle用户的独特模拟
        return base.filter(pk__in=set(queryset.values_list('pk', flat=True)))
    return queryset.distinct()


# django.contrib.postgres requires psycopg2
try:
    from django.contrib.postgres import fields as postgres_fields
except ImportError:
    postgres_fields = None


# coreapi is required for CoreAPI schema generation
try:
    import coreapi
except ImportError:
    coreapi = None

# uritemplate is required for OpenAPI and CoreAPI schema generation
try:
    import uritemplate
except ImportError:
    uritemplate = None


# coreschema is optional
try:
    import coreschema
except ImportError:
    coreschema = None


# pyyaml is optional
try:
    import yaml
except ImportError:
    yaml = None


# requests is optional
try:
    import requests
except ImportError:
    requests = None


# PATCH method is not implemented by Django
if 'patch' not in View.http_method_names:
    View.http_method_names = View.http_method_names + ['patch']


# Markdown is optional (version 3.0+ required)
try:
    import markdown

    HEADERID_EXT_PATH = 'markdown.extensions.toc'
    LEVEL_PARAM = 'baselevel'

    def apply_markdown(text):
        """
        Simple wrapper around :func:`markdown.markdown` to set the base level
        of '#' style headers to <h2>.
        """
        extensions = [HEADERID_EXT_PATH]
        extension_configs = {
            HEADERID_EXT_PATH: {
                LEVEL_PARAM: '2'
            }
        }
        md = markdown.Markdown(
            extensions=extensions, extension_configs=extension_configs
        )
        md_filter_add_syntax_highlight(md)
        return md.convert(text)
except ImportError:
    apply_markdown = None
    markdown = None


try:
    import pygments
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter

    def pygments_highlight(text, lang, style):
        lexer = get_lexer_by_name(lang, stripall=False)
        formatter = HtmlFormatter(nowrap=True, style=style)
        return pygments.highlight(text, lexer, formatter)

    def pygments_css(style):
        formatter = HtmlFormatter(style=style)
        return formatter.get_style_defs('.highlight')

except ImportError:
    pygments = None

    def pygments_highlight(text, lang, style):
        return text

    def pygments_css(style):
        return None

if markdown is not None and pygments is not None:
    # starting from this blogpost and modified to support current markdown extensions API
    # https://zerokspot.com/weblog/2008/06/18/syntax-highlighting-in-markdown-with-pygments/

    from markdown.preprocessors import Preprocessor
    import re

    class CodeBlockPreprocessor(Preprocessor):
        pattern = re.compile(
            r'^\s*``` *([^\n]+)\n(.+?)^\s*```', re.M | re.S)

        formatter = HtmlFormatter()

        def run(self, lines):
            def repl(m):
                try:
                    lexer = get_lexer_by_name(m.group(1))
                except (ValueError, NameError):
                    lexer = TextLexer()
                code = m.group(2).replace('\t', '    ')
                code = pygments.highlight(code, lexer, self.formatter)
                code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />').replace('\\@', '@')
                return '\n\n%s\n\n' % code
            ret = self.pattern.sub(repl, "\n".join(lines))
            return ret.split("\n")

    def md_filter_add_syntax_highlight(md):
        md.preprocessors.register(CodeBlockPreprocessor(), 'highlight', 40)
        return True
else:
    def md_filter_add_syntax_highlight(md):
        return False


# Django 1.x url routing syntax. Remove when dropping Django 1.11 support.
try:
    from django.urls import include, path, re_path, register_converter  # noqa
except ImportError:
    from django.conf.urls import include, url # noqa
    path = None
    register_converter = None
    re_path = url


# `separators` argument to `json.dumps()` differs between 2.x and 3.x
# See: https://bugs.python.org/issue22767
SHORT_SEPARATORS = (',', ':')
LONG_SEPARATORS = (', ', ': ')
INDENT_SEPARATORS = (',', ': ')


# Version Constants.
PY36 = sys.version_info >= (3, 6)
