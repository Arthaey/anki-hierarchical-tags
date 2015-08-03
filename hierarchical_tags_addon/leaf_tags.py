import re
from anki.hooks import addHook
from anki.template import template
from hierarchical_tags import SEPARATOR

LEAF_TAG_RE = r"(?:{0})?([^{1}]+?$)".format(SEPARATOR, SEPARATOR[0])

# When False, {{LeafTags}} will be generated dynamically when you view cards
# with the desktop version of Anki. It will display "{unknown field LeafTags}"
# on AnkiWeb and mobile applications.
#
# When True, a new LeafTags field will be added to the end of every model, and
# its value will be updated when you change the tags on a note.
#
SAVE_LEAF_TAGS_TO_FIELD = False

def _onTagsUpdated(note):
    # TODO: Add field to the note's model, if necessary.
    model = note.model()
    # TODO: Set field based on updated tags.
    note.flush()


def _my_get_or_attr(obj, name, default=None):
    if name == "LeafTags":
        tags_str = original_get_or_attr(obj, "Tags", default)
        tags = tags_str.split(" ")
        tags_html = [_to_html(tag) for tag in tags]
        return " ".join(tags_html)
    else:
        return original_get_or_attr(obj, name, default)


def _to_html(tag):
    return "<span class='tag'>{0}</span>".format(_leafify(tag))


def _leafify(tag):
    match = re.search(LEAF_TAG_RE, tag)
    if match:
        tag = match.group(1)
    return tag


original_get_or_attr = template.get_or_attr

if SAVE_LEAF_TAGS_TO_FIELD:
    addHook("tagsUpdated", _onTagsUpdated)
else:
    template.get_or_attr = _my_get_or_attr
