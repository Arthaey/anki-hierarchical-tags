# -*- coding: utf-8 -*-
import re

from PyQt4.QtCore import QCoreApplication, SIGNAL
from PyQt4.QtGui import QAction, QProgressDialog

from anki.hooks import addHook, wrap
from anki.lang import _
from anki.tags import TagManager
from anki.template import template
from aqt import mw
from aqt.addcards import AddCards
from aqt.browser import Browser
from aqt.editcurrent import EditCurrent
from aqt.utils import showInfo

from hierarchical_tags import SEPARATOR

LEAF_TAGS_NAME = u"LeafTags"

# Have to escape a single literal "{" as "{{". So many braces...
LEAF_TAGS_TEMPLATE = u"\n\n<div class=\"tags\">tags: {{{{{0}}}}}</div>".format(LEAF_TAGS_NAME)

# Whether to append the leaf tags to all models' templates.
ADD_LEAF_TAGS_TO_TEMPLATES = True

# Whether the tags should be returned as "tag" or wrapped in a <span>.
WRAP_TAGS_IN_HTML = True

# Which tags to ignore for LeafTag purposes.
IGNORE_TAGS_WITH_PREFIX = ["~",]

# Whether to save processed leaf tags to the note, or generate dynamically.
SAVE_LEAF_TAGS_TO_FIELD = True

LEAF_TAG_RE = r"(?:{0})?([^{1}]+?$)".format(SEPARATOR, SEPARATOR[0])

def _onTagsUpdated(note):
    model = note.model()

    # Add field to the note's model, if necessary.
    mm = note.col.models
    if not LEAF_TAGS_NAME in mm.fieldNames(model):
        showInfo(u"Adding {0} field to note type {1}".format(LEAF_TAGS_NAME, model["name"]))
        _add_field_to_model(mm, model)

    # Set field based on updated tags.
    #_populate_field(note.id)
    format_func = _to_html if WRAP_TAGS_IN_HTML else _leafify_tag
    note[LEAF_TAGS_NAME] = _format_tags(note.tags, format_func)
    note.flush()

    # Redraw card UI.
    window = mw.app.activeWindow()
    if isinstance(window, AddCards) or isinstance(window, EditCurrent):
        window.editor.setNote(note, focus=True)
    if isinstance(window, Browser):
        window.editor.setNote(window.card.note(reload=True))
        window.editor.card = window.card

def _my_get_or_attr(obj, name, default=None):
    # Intercept and dynamically generate leaf tags.
    if name == LEAF_TAGS_NAME:
        tags_str = original_get_or_attr(obj, "Tags", default)
        tags = tags_str.split(" ")
        return _format_tags(tags, _to_html)
    else:
        return original_get_or_attr(obj, name, default)


def _format_tags(tags, format_func):
    ignore = "^(marked|leech)$"
    if len(IGNORE_TAGS_WITH_PREFIX):
        ignore += "|" + "|^".join(IGNORE_TAGS_WITH_PREFIX)
    return " ".join([ format_func(tag) for tag in tags if not re.match(ignore, tag) ])


def _to_html(tag):
    return u"<span class='tag'>{0}</span>".format(_leafify_tag(tag))


def _leafify_tag(tag):
    match = re.search(LEAF_TAG_RE, tag)
    if match:
        tag = match.group(1)
    return tag


def _add_field_to_model(mm, model):
    field = mm.newField(_(LEAF_TAGS_NAME))
    mm.addField(model, field)
    if ADD_LEAF_TAGS_TO_TEMPLATES:
        _add_field_to_templates(model["tmpls"])
    mm.save(model, templates=True)
    mm.flush()

def _add_field_to_templates(templates):
    for t in templates:
        if not LEAF_TAGS_NAME in t["qfmt"]:
            t["qfmt"] = t["qfmt"] + LEAF_TAGS_TEMPLATE
        if not LEAF_TAGS_NAME in t["afmt"]:
            t["afmt"] = t["afmt"] + LEAF_TAGS_TEMPLATE

def _add_field_to_all_templates():
    mm = mw.col.models
    templates = sum([ model["tmpls"] for model in mm.all() ], []) # flatten
    _add_field_to_templates(templates)
    mm.save(templates=True)
    mm.flush()
    showInfo("Templates updated.")

def _populate_fields_for_all_cards():
    mm = mw.col.models
    models = mm.all()
    nids = []

    for model in models:
        if not LEAF_TAGS_NAME in mm.fieldNames(model):
            _add_field_to_model(mm, model)
        nids.extend(mm.nids(model))

    for nid in _progress(nids, _(u"Adding leaf tags"), _(u"Stop")):
        _populate_field(nid)

    mw.reset()

def _populate_field(nid):
    note = mw.col.getNote(nid)
    format_func = _to_html if WRAP_TAGS_IN_HTML else _leafify_tag
    note[LEAF_TAGS_NAME] = _format_tags(note.tags, format_func)
    note.flush()

def _bulkAdd(self, ids, tags, add=True):
    for nid in ids:
        _populate_field(nid)
    mw.reset()

def _progress(data, *args):
    # From http://lateral.netmanagers.com.ar/weblog/posts/BB917.html
    # © 2000-2012 Roberto Alsina
    # Creative Commons Attribution-NonCommercial-ShareAlike 2.5 licence
    # http://creativecommons.org/licenses/by-nc-sa/2.5/
    it = iter(data)
    widget = QProgressDialog(*args + (0, it.__length_hint__()))
    c = 0
    for v in it:
        QCoreApplication.instance().processEvents()
        if widget.wasCanceled():
            raise StopIteration
        c += 1
        widget.setValue(c)
        yield(v)

def _add_menu_item(textTemplate, func):
    action = QAction(textTemplate.format(LEAF_TAGS_NAME), mw)
    mw.connect(action, SIGNAL("triggered()"), func)
    mw.form.menuTools.addAction(action)


if ADD_LEAF_TAGS_TO_TEMPLATES:
    _add_menu_item(u"Add {0} to templates", _add_field_to_all_templates)

if SAVE_LEAF_TAGS_TO_FIELD:
    addHook("tagsUpdated", _onTagsUpdated)
    TagManager.bulkAdd = wrap(TagManager.bulkAdd, _bulkAdd, "after")
    _add_menu_item(u"Update {0} fields", _populate_fields_for_all_cards)
else:
    original_get_or_attr = template.get_or_attr
    template.get_or_attr = _my_get_or_attr
