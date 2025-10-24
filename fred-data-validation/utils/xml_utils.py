import xml.etree.ElementTree as ET

def check_abstract_in_xml(xml_file_path):
    """Check if XML contains abstract or summary content"""
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        abstract_found = False
        abstract_content = ""

        namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

        for _, ns_uri in namespaces.items():
            xpath_patterns = [
                f".//{{{ns_uri}}}abstract",
                f".//{{{ns_uri}}}div[@type='abstract']",
                f".//{{{ns_uri}}}div[@subtype='abstract']",
                f".//{{{ns_uri}}}summary",
                f".//{{{ns_uri}}}div[@type='summary']"
            ]
            for pattern in xpath_patterns:
                elements = root.findall(pattern)
                for element in elements:
                    text_content = get_element_text(element)
                    if text_content and text_content.strip():
                        abstract_found = True
                        abstract_content = text_content.strip()
                        break
                if abstract_found:
                    break
            if abstract_found:
                break

        if not abstract_found:
            xpath_patterns = [
                ".//abstract",
                ".//div[@type='abstract']",
                ".//div[@subtype='abstract']",
                ".//summary",
                ".//div[@type='summary']"
            ]
            for pattern in xpath_patterns:
                elements = root.findall(pattern)
                for element in elements:
                    text_content = get_element_text(element)
                    if text_content and text_content.strip():
                        abstract_found = True
                        abstract_content = text_content.strip()
                        break
                if abstract_found:
                    break

        return abstract_found, abstract_content

    except Exception as e:
        print(f"Error parsing XML {xml_file_path}: {e}")
        return False, ""


def get_element_text(element):
    """Recursively extract all text content from an element and its children"""
    text_parts = []

    if element.text:
        text_parts.append(element.text.strip())

    for child in element:
        child_text = get_element_text(child)
        if child_text:
            text_parts.append(child_text)
        if child.tail:
            text_parts.append(child.tail.strip())

    return ' '.join(filter(None, text_parts))
