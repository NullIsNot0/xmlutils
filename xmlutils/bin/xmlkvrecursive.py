# Copyright (C) 2010 Splunk Inc.  All Rights Reserved.  Version 4.0
import sys,splunk.Intersplunk
import re
import urllib
import xml.sax
import xml.sax.saxutils as saxutils
from xml.sax.handler import ContentHandler
from xml.sax.handler import EntityResolver
from xml.sax.xmlreader import InputSource
from io import StringIO
import types

class NullInputSource(InputSource):
    def getByteStream(self):
        return StringIO("entity files not supported.")

class NullEntityResolver(EntityResolver):
    def resolveEntity(self,publicId,systemId):
        return NullInputSource()

class XmlHandler(ContentHandler):
    def __init__(self, flatten):
        self.flatten = flatten

    def reset(self):
        self.key_prefix = []
        self.keys_seen = []
        self.new_fields = {}

    def getNewFields(self):
        return self.new_fields

    def setValue( self, value, suffix='' ):
        dest_key = '_'.join(self.key_prefix) + suffix

        if( len( str(value).strip() ) > 0 ):
            #handle multiple values
            if dest_key in self.new_fields:
                self.new_fields['multi values'] = 'yep'
                #this is only the second value, so convert value to a list
                if type(self.new_fields[dest_key]) is not types.ListType:
                    self.new_fields[dest_key] = [self.new_fields[dest_key]]
                #append the value to the list
                self.new_fields[dest_key].append(str(value))
            else:
                #insert the simple value
                self.new_fields[dest_key] = str(value)

    def startElement(self, name, attrs):
        self.key_prefix.append(name)

        #if flatten is set, then create a new prefix if this prefix has already been used
        if flatten and '_'.join(self.key_prefix) in self.keys_seen:
            self.key_prefix.pop()
            count = 2
            newName = name + '[' + str(count) + ']'
            while '_'.join(self.key_prefix) + '_' + newName in self.keys_seen:
                count += 1
                newName = name + '[' + str(count) + ']'
            self.key_prefix.append(newName)

        self.keys_seen.append( '_'.join(self.key_prefix) )

        if attrs.getLength() > 0:
            for k in attrs.getNames():
                self.setValue( attrs.getValue(k), "-" + k )

    def characters(self, content):
        if content is not None and content.strip() is not '':
            self.setValue( content.strip() )

    def endElement(self, name):
        self.key_prefix.pop()


try:
    results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()

    keywords, argvals = splunk.Intersplunk.getKeywordsAndOptions()

    flatten = argvals.get("flatten", "False")
    if flatten.strip().lower() in ['true','1','yes']:
        flatten = True
    else:
        flatten = False

    handler = XmlHandler(flatten)

    for r in results:
        try:
            if 'xml' in r:
                xml_text = r['xml']
            else:
                raw = r["_raw"]

                xml_text = raw[ raw.index( '<' ) : raw.rindex( '>' )+1 ]

            handler.reset()

            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            parser.setEntityResolver(NullEntityResolver())
            parser.parse(StringIO(xml_text))

            for k,v in handler.getNewFields().iteritems():
                r[k] = v
        except:
            import traceback
            stack =  traceback.format_exc()
            r['_raw'] = "Failed to parse: " + str(stack) + "\n" + r['_raw']

except:
    import traceback
    stack =  traceback.format_exc()
    results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

splunk.Intersplunk.outputResults( results )
