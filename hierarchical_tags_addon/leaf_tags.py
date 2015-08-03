# -*- coding: utf-8 -*-
import re

from PyQt4.QtCore import QCoreApplication, SIGNAL
from PyQt4.QtGui import QAction, QProgressDialog

from anki.hooks import addHook
from anki.lang import _
from anki.template import template
from anki.utils import TimedLog # DELETE
from aqt import mw
from aqt.utils import showInfo

from hierarchical_tags import SEPARATOR

LEAF_TAGS_NAME = "LeafTags"

LEAF_TAG_RE = r"(?:{0})?([^{1}]+?$)".format(SEPARATOR, SEPARATOR[0])

# When False, {{LeafTags}} will be generated dynamically when you view cards
# with the desktop version of Anki. It will display "{unknown field LeafTags}"
# on AnkiWeb and mobile applications.
#
# When True, a new LeafTags field will be added to the end of every model, and
# its value will be updated when you change the tags on a note.
#
SAVE_LEAF_TAGS_TO_FIELD = True

ADD_LEAF_TAGS_TO_TEMPLATES = True

LEAF_TAGS_TEMPLATE = "<div class='tags'>tags: {0}</div>".format(LEAF_TAGS_NAME)

LOGGER = TimedLog() # DELETE

def _onTagsUpdated(note):
    model = note.model()

    # Add field to the note's model, if necessary.
    mm = note.col.models
    if not LEAF_TAGS_NAME in mm.fieldNames(model):
        showInfo("Adding {0} field to note type {1}".format(LEAF_TAGS_NAME, model["name"]))
        _add_field_to_model(mm, model)
        LOGGER.log(mm.fieldNames(model)) # DELETE

    # Set field based on updated tags.
    LOGGER.log(mm.fieldNames(note.model())) # DELETE
    note[LEAF_TAGS_NAME] = _format_tags(note.tags, _leafify_tag)
    note.flush()

    # TODO: Redraw browser/addcard UI.
    browser = mw.app.activeWindow()
    browser.editor.setNote(browser.card.note(reload=True))
    browser.editor.card = browser.card

def _my_get_or_attr(obj, name, default=None):
    # Intercept and dynamically generate leaf tags.
    if name == LEAF_TAGS_NAME:
        tags_str = original_get_or_attr(obj, "Tags", default)
        tags = tags_str.split(" ")
        return _format_tags(tags, _to_html)
    else:
        return original_get_or_attr(obj, name, default)


def _format_tags(tags, format_func):
    return " ".join([ format_func(tag) for tag in tags ])


def _to_html(tag):
    return "<span class='tag'>{0}</span>".format(_leafify_tag(tag))


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
    templates = sum([ model["tmpls"] for model in mm ], []) # flatten
    _add_field_to_templates(templates)
    mm.save(templates=True)
    mm.flush()

def _populate_field():
    mm = mw.col.models
    models = mm.all()
    nids = []
    for model in models:
        if not LEAF_TAGS_NAME in mm.fieldNames(model):
            _add_field_to_model(mm, model)
        nids.extend(mm.nids(model))

    for nid in _progress(nids, _(u"Adding leaf tags"), _(u"Stop")):
        note = mw.col.getNote(nid)
        note[LEAF_TAGS_NAME] = _format_tags(note.tags, _leafify_tag)

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


if ADD_LEAF_TAGS_TO_TEMPLATES:
    action = QAction("Add {0} to templates".format(LEAF_TAGS_NAME), mw)
    mw.connect(action, SIGNAL("triggered()"), _add_field_to_all_templates)
    mw.form.menuTools.addAction(action)

if SAVE_LEAF_TAGS_TO_FIELD:
    addHook("tagsUpdated", _onTagsUpdated)
    action = QAction("Update {0} fields".format(LEAF_TAGS_NAME), mw)
    mw.connect(action, SIGNAL("triggered()"), _populate_field)
    mw.form.menuTools.addAction(action)
else:
    original_get_or_attr = template.get_or_attr
    template.get_or_attr = _my_get_or_attr
