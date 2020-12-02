# Copyright (C) 2010 Splunk Inc.  All Rights Reserved.  Version 4.0
import sys,splunk.Intersplunk
import xml.sax
import xml.sax.saxutils as saxutils
from xml.sax.handler import ContentHandler
from xml.sax.handler import EntityResolver
from xml.sax.xmlreader import InputSource
import StringIO

class NullInputSource(InputSource):
    def getByteStream(self):
        return StringIO.StringIO("entity files not supported.")

class NullEntityResolver(EntityResolver):
    def resolveEntity(self,publicId,systemId):
        return NullInputSource()

class XmlHandler(ContentHandler):
    def __init__(self):
        self.indent = 0

    def reset(self , r):
        self.current_output = ''
        self.indent = 0
        self.open_tag = ''

    def getOutput(self):
        return self.current_output

    def startElement(self, name, attrs):
        self.open_tag = name
        self.current_output += '\n' + '  ' * self.indent
        self.indent += 1
        self.current_output += '<' + name

        if attrs.getLength() > 0:
            for k in attrs.getNames():
                self.current_output += ' ' + k + '=' + saxutils.quoteattr(attrs.getValue(k))
        self.current_output += '>'

    def characters(self, content):
        if len(content.strip()) > 0:
#            self.current_output += '  ' * self.indent
            self.current_output += saxutils.escape( content ) #+ '\n'

    def endElement(self, name):
        self.indent -= 1
        if self.open_tag != name:
            self.current_output += '\n' + '  ' * self.indent
        self.current_output += '</' + name + '>'


try:
    results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()

    handler = XmlHandler()

    for r in results:
        try:
            if 'xml' in r:
                xml_text = r['xml']
                dest_field = 'xml'
            else:
                raw = r["_raw"]
                dest_field = '_raw'

                xml_text = raw[ raw.index( '<' ) : raw.rindex( '>' )+1 ]

            handler.reset(xml_text)
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            parser.setEntityResolver(NullEntityResolver())
            parser.parse(StringIO.StringIO(xml_text))

            r[dest_field] = handler.getOutput()

            if 'xml' in r:
                xml_text = r['xml']
            else:
                raw = r["_raw"]

        except:
            import traceback
            stack =  traceback.format_exc()
            r['_raw'] = "Failed to parse: " + str(stack) + "\n" + r['_raw']

except:
    import traceback
    stack =  traceback.format_exc()
    results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

splunk.Intersplunk.outputResults( results )
