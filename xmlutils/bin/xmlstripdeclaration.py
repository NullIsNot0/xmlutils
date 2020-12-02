# Copyright (C) 2010 Splunk Inc.  All Rights Reserved.  Version 4.0
import splunk.Intersplunk


try:
    results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()

    for r in results:
        try:
            if 'xml' in r:
                xml_text = r['xml']
                dest_field = 'xml'
            else:
                raw = r["_raw"]
                dest_field = '_raw'

                xml_text = raw[ raw.index( '<' ) : raw.rindex( '>' )+1 ]
            if xml_text.startswith('<?'):
                #remove the xml declaration. I know, I know, but I ran into a case where charset was wrong, and the parser explodes.
                xml_text = xml_text[ raw.index( '<' , 5 ) : raw.rindex( '>' )+1 ]

            r[dest_field] = xml_text

        except:
            import traceback
            stack = traceback.format_exc()
            r['_raw'] = "Failed to parse: " + str(stack) + r['_raw']

except:
    import traceback
    stack =  traceback.format_exc()
    results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

splunk.Intersplunk.outputResults( results )
