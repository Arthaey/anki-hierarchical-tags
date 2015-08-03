import re
from anki.template import template
from hierarchical_tags import SEPARATOR

LEAF_TAG_RE = r"(?:{0})?([^{1}]+?$)".format(SEPARATOR, SEPARATOR[0])


def _my_get_or_attr(obj, name, default=None):
    if name == "LeafTags":
        tags_str = original_get_or_attr(obj, "Tags", default)
        tags = tags_str.split(" ")
        tags_html = [_format_tag(tag) for tag in tags]
        return " ".join(tags_html)
    else:
        return original_get_or_attr(obj, name, default)


def _format_tag(tag):
    match = re.search(LEAF_TAG_RE, tag)
    if match:
        tag = match.group(1)
    return "<span class='tag'>{0}</span>".format(tag)


original_get_or_attr = template.get_or_attr
template.get_or_attr = _my_get_or_attr
