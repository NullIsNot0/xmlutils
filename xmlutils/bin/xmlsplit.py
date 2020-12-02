# Copyright (C) 2010 Splunk Inc.  All Rights Reserved.  Version 4.0
import sys,splunk.Intersplunk
import re
import xml.sax
import xml.sax.saxutils as saxutils
from xml.sax.handler import ContentHandler
from xml.sax.handler import EntityResolver
from xml.sax.xmlreader import InputSource
import copy
import StringIO


class NullInputSource(InputSource):
    def getByteStream(self):
        return StringIO.StringIO("entity files not supported.")

class NullEntityResolver(EntityResolver):
    def resolveEntity(self,publicId,systemId):
        return NullInputSource()

class XmlHandler(ContentHandler):
    def __init__(self, field):
        self.field = field

    def reset(self , newResults):
        self.current_output = ''
        self.newResults = newResults

    def startElement(self, name, attrs):
        if name == field:
            self.current_output = ''
        self.current_output += '<' + name

        if attrs.getLength() > 0:
            for k in attrs.getNames():
                self.current_output += ' ' + k + '=' + saxutils.quoteattr(attrs.getValue(k))
        self.current_output += '>'

    def characters(self, content):
        self.current_output += saxutils.escape( content )

    def endElement(self, name):
        self.current_output += '</' + name + '>'
        if name == field:
            if re.match('^<' + field + '[ >]', self.current_output):
                newRow = copy.deepcopy(r)
                newRow['_raw'] = self.current_output
                self.newResults.append(newRow)
            self.current_output = ''

try:
    results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()

    keywords, argvals = splunk.Intersplunk.getKeywordsAndOptions()

    field = argvals.get("field", None)
    if field is None:
        raise Exception("Must supply name of field in field=fieldName")

    newResults = []

    handler = XmlHandler(field)

    for r in results:
        try:
            if 'xml' in r:
                xml_text = r['xml']
            else:
                raw = r["_raw"]
                xml_text = raw[ raw.index( '<' ) : raw.rindex( '>' )+1 ]

            handler.reset(newResults)
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            parser.setEntityResolver(NullEntityResolver())
            parser.parse(StringIO.StringIO(xml_text))
        except:
            import traceback
            stack = traceback.format_exc()
            r['_raw'] = "Failed to parse: " + str(stack) + r['_raw']
            newResults = [r]

except:
    import traceback
    stack =  traceback.format_exc()
    newResults = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

splunk.Intersplunk.outputResults( newResults )

