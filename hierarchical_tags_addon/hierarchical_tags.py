import re

from aqt.browser import Browser
from aqt.qt import QIcon
from anki.hooks import wrap
from anki.template import template


# Separator used between hierarchies.
#
# NOTE: If you change this to more than one type of repeated character,
#       {{LeafTags}} will stop working. For example, "::" and "-" will both
#       work, but ":-" would not.
#
SEPARATOR = '::'

LEAF_TAG_RE = r"(?:{0})?([^{1}]+?$)".format(SEPARATOR, SEPARATOR[0])


def _userTagTree(self, root, _old):
    tags = sorted(self.col.tags.all())
    tags_tree = {}

    for t in tags:
        if t.lower() == "marked" or t.lower() == "leech":
            continue

        components = t.split(SEPARATOR)
        for idx, c in enumerate(components):
            partial_tag = SEPARATOR.join(components[0:idx + 1])
            if not tags_tree.get(partial_tag):
                if idx == 0:
                    parent = root
                else:
                    parent_tag = SEPARATOR.join(components[0:idx])
                    parent = tags_tree[parent_tag]

                item = self.CallbackItem(
                    parent, c,
                    lambda partial_tag=partial_tag: self.setFilter("tag", partial_tag + '*'))
                item.setIcon(0, QIcon(":/icons/anki-tag.png"))

                tags_tree[partial_tag] = item


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


Browser._userTagTree = wrap(Browser._userTagTree, _userTagTree, 'around')

original_get_or_attr = template.get_or_attr
template.get_or_attr = _my_get_or_attr
