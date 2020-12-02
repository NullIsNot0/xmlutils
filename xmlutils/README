xmlutils provides a few commands for working with xml documents. xmlkv and xpath can accomplish most tasks, these are simply alternatives.

These commands will work on a field called "xml" if found, otherwise _raw.

xmlprettyprint
xmlprettyprint does what you would expect, pretty printing the xml.

xmlsplit
xmlsplit splits nodes into new events, copying other fields on the event to the new events.

Examples:
Given this xml:
<a><b>foo</b><b>bar</b></a>

xmlsplit field="b"
will create two events:
<b>foo</b> <b>bar</b>

xmlkvrecursive
xmlkvrecursive recursively builds fields from the tag and attribute names. The optional boolean flatten determines how repeated fields are treated. By default, repeated field names will be appended into a multi-value field. With flatten="true", new fields will be created.

Examples:
sourcetype=* | head 1 | eval _raw="<a la='sdf'><b>foo</b><b>bar</b></a>" | xmlkvrecursive
produces:
a-la = sdf a_b = [foo,bar]

sourcetype=* | head 1 | eval _raw="<a la='sdf'><b>foo</b><b>bar</b></a>" | xmlkvrecursive flatten=true
produces:
a-la = sdf a_b = foo a_b[2](http://splunkbase.splunk.com/wiki/2) = bar

Most of the time, xpath or xmlkv would be more appropriate. This command is useful if you need to extract multiple fields that are not extracted easily using one of those commands.

xmlstripdeclaration
xmlstripdeclaration removes the <?xml declaration from the beginning of the xml. This is needed if the declaration is incorrect and the parser used by the other commands would refuse to continue.
