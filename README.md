Hierarchical Tags for Anki
==========================

This addon adds hierarchical tags to the browser in [Anki][]. The addon is
[published on Ankiweb](https://ankiweb.net/shared/info/1089921461).

To create hierarchies use double-colons in the tag names, for example
"learning::anki" or "language::japanese".

This addon is licensed under the same license as Anki itself (GNU Affero
General Public License 3).

## LeafTags

This addon also makes a new field available: `{{LeafTags}`, which is like
the built-in [{{Tags}}](http://ankisrs.net/docs/manual.html#special-fields)
except that it only displays that last portion of hierarchical tags. For
example, the tag "language::japanese" would appear as just "japanese".

If you edit the addon's source code, you can control the name of this tag via
the constant `LEAF_TAGS_NAME`.

You can also control whether leaf tags are dynamically created or stored in a
new "LeafTags" field via the constant `SAVE_LEAF_TAGS_TO_FIELD`.

When `False`, leaf tags will be generated dynamically when you view cards
with the desktop version of Anki. It will display "{unknown field LeafTags}"
on AnkiWeb and mobile applications.

When `True`, a new "LeafTags" field will be added to the end of every model, and
its value will be updated when you change the tags on a note.

If `ADD_LEAF_TAGS_TO_TEMPLATES` is `True`, it will also add the leaf tags to the
bottom of each note type's templates.


## Known Issues

When clicking on a tag in the hierarchy, an asterisk is added to the search
term. The effect of that is that all notes with that tag and all subtags are
searched for.

But a side-effect is, that all tags with the same prefix are matched. For
example if you have a tag ``it`` and a tag ``italian``, clicking on the tag
``it`` would also show content from ``italian``. Let me know if this affects
you and I'll try to work around this.


## Support

The add-on was written by [Patrice Neff][]. I try to monitor threads in the
[Anki Support forum][]. To be safe you may also want to open a ticket on the
plugin's [GitHub issues][] page.


[Anki]: http://ankisrs.net/
[Patrice Neff]: http://patrice.ch/
[Anki support forum]: https://anki.tenderapp.com/discussions/add-ons
[GitHub issues]: https://github.com/pneff/anki-hierarchical-tags/issues
