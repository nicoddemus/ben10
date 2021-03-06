from ._pretty_xml import WritePrettyXMLElement
from xml.etree import ElementTree



#===================================================================================================
# XmlFactory
#===================================================================================================
class XmlFactory(object):
    '''
    Fast and easy XML creation class.

    This class provides a simple and fast way of creating XML files in Python. It tries to deduce as
    much information as possible, creating intermediate elements as necessary.

    Example:
        xml = XmlFactory('root')

        xml['alpha/bravo/charlie'] # Create intermediate nodes
        xml['alpha/bravo.one'] # Create attribute on "alpha/bravo" tag
        xml['alpha/delta'] = 'XXX' # Create delta tag with text

        xmlWrite('filename.xml') # Always write with a pretty XML format
    '''

    def __init__(self, root_element):
        '''
        :type root_element: str | Element
        :param root_element:
            The name of the root element.
            Well formated XML files have only one root element.
        '''
        if isinstance(root_element, (str, unicode)):
            self.root = ElementTree.Element(root_element)
        elif isinstance(root_element, ElementTree._ElementInterface):
            self.root = root_element
        else:
            raise TypeError("Unknown root_element parameter type: %s" % type(root_element))


    def __setitem__(self, name, value):
        '''
        Create a new element or attribute:

        :param str name:
            A XML path including or not an attribute definition

        :param str value:
            The value to associate with the element or attribute

        :rtype: Element
        :returns:
            Returns the element created.
            If setting an attribute value, returns the owner element.

        @examples:
            xml['alpha/bravo'] = 'XXX' # Create bravo tag with 'XXX' as text contents
            xml['alpha.class'] = 'CLS' # Create alpha with the attribute class='CLS'
        '''
        if '@' in name:
            element_name, attr_name = name.rsplit('@')
            result = self._ObtainElement(element_name)
            result.attrib[attr_name] = str(value)
        else:
            result = self._ObtainElement(name)
            result.text = None if value is None else str(value)
        return XmlFactory(result)


    def __getitem__(self, name):
        '''
        Create and returns xml element.

        :param str name:
            A XML path including or not an attribute definition.

        :rtype: Element
        :returns:
            Returns the element created.
        '''
        assert '@' not in name, 'The "at" (@) is used for attribute definitions'
        result = self._ObtainElement(name)
        return XmlFactory(result)


    def _ObtainElement(self, name):
        '''
        Create and returns a xml element with the given name.

        :param str name:
            A XML path including. Each sub-client tag separated by a slash.
            If any of the parts ends with a "+" it creates a new sub-element in that part even if
            it already exists.
        '''
        parent = self.root
        if name == '':
            # On Python 2.7 parent.find('') returns None instead of the parent itself
            result = parent
        else:
            parts = name.split('/')
            for i_part in parts:
                if i_part.endswith('+'):
                    i_part = i_part[:-1]
                    result = ElementTree.SubElement(parent, i_part)
                else:
                    result = parent.find(i_part)
                    if result is None:
                        result = ElementTree.SubElement(parent, i_part)
                parent = result
        return result


    def GetContent(self, xml_header=False):
        '''
        Returns the full XML contents.

        :param bool xml_header:
            Prepends the XML with xml version header: '<?xml version="1.0" ?>'

        :return str:
        '''
        from StringIO import StringIO

        oss = StringIO()
        if xml_header:
            oss.write('<?xml version="1.0" ?>\n')
        WritePrettyXMLElement(oss, self.root)
        return oss.getvalue()

