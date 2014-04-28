Hierarchical Tags for Anki
==========================

This addon adds hierarchical tags to the browser in [Anki][]. The addon is
[published on Ankiweb](https://ankiweb.net/shared/info/1089921461).

To create hierarchies use double-colons in the tag names, for example
"learning::anki" or "language::japanese".

This addon is licensed under the same license as Anki itself (GNU Affero
General Public License 3).


## Known Issues

When clicking on a tag in the hierarchy, an asterisk is added to the search
term. The effect of that is that all notes with that tag and all subtags are
searched for.

But a side-effect is, that all tags with the same prefix are matched. For
example if you have a tag ``it`` and a tag ``italian``, clicking on the tag
``it`` would also show content from ``italian``. Let me know if this affects
you and I'll try to work around this.


[Anki]: http://ankisrs.net/
