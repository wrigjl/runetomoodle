
"""Helper functions for the grade manangement utilities"""

def load_skip_users(su):
    """When students drop, we want to skip them (less noise on import)"""
    with open('skip_users.csv', encoding='UTF-8') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                su.add(line)


def create_simple_text_node(docroot, parent, name, text):
    """create <name>text</name> and append it as a child to 'parent'"""

    n = docroot.createElement(name)
    parent.appendChild(n)
    t = docroot.createTextNode(text)
    n.appendChild(t)


def create_moodle_entry(docroot, result, assignment, student, score):
    """Create the appropriate nodes in the XML tree for Moodle"""
    create_simple_text_node(docroot, result,
                            'assignment', assignment)
    create_simple_text_node(docroot, result,
                            'student', student)
    create_simple_text_node(docroot, result,
                            'score', score)
