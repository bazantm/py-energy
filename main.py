from typing import Dict

START_LINE = 6

# Constants for important column indices (0-based)
NODE_INDEX = 1
NODE_KEY = 2
PARENT_INDEX = 3
CODE_INDEX = 7

class Node:
    """
    Represents a Parent object identified by an integer index.
    """
    def __init__(self, index: int):
        self.index = index
        # Additional initialization can be added here

    def __repr__(self):
        return f"Node(index={self.index})"


class PlantDiagram:
    _instance = None

    DIAGRAM_HEADER = "@startuml"
    DIAGRAM_FOOTER = "@enduml"

    LINE_SEPARATOR = '\n'

    COMPONENT_START = '['
    COMPONENT_END = ']'

    ARROW = ' -> '

    diag_objects: Dict[int, Node] = {}

    diag_text = DIAGRAM_HEADER + LINE_SEPARATOR

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PlantDiagram, cls).__new__(cls)
        return cls._instance

    def add_to_diag(self, data):
        node_key = data.get('node_key')
        parent = data.get('parent')
        code = data.get('code')

        PlantDiagram.diag_text += PlantDiagram.COMPONENT_START
        PlantDiagram.diag_text += str(node_key)
        PlantDiagram.diag_text += PlantDiagram.COMPONENT_END

        PlantDiagram.diag_text += PlantDiagram.ARROW

        PlantDiagram.diag_text += PlantDiagram.COMPONENT_START
        PlantDiagram.diag_text += str(parent)
        PlantDiagram.diag_text += PlantDiagram.COMPONENT_END

        PlantDiagram.diag_text += PlantDiagram.LINE_SEPARATOR


    def get_diagram_text(self):
        return PlantDiagram.diag_text

    def add_diagram_text_enduml(self):
        PlantDiagram.diag_text += PlantDiagram.DIAGRAM_FOOTER



class LineData:
    # Get the singleton instance
    diagram = PlantDiagram()

    """
    Represents the important data extracted from a single line of the file.
    """
    def __init__(self, data: Dict[str, str]):
        """
        Initialize with a dictionary containing important column data.
        """
        self.index = data.get('index')
        self.node_key = data.get('node_key')
        self.parent = data.get('parent')
        self.code = data.get('code')

    def process(self):
        try:
            node_key = int(self.node_key)
        except (TypeError, ValueError):
            print(f"Warning: Invalid node_key value '{self.node_key}', skipping processing")
            return

        if node_key not in PlantDiagram.diag_objects:
            PlantDiagram.diag_objects[node_key] = Node(node_key)

            if node_key != 1:
                LineData.diagram.add_to_diag({'node_key': node_key, 'parent': self.parent, 'code': self.code})

            print(f"Created new Parent object with index {node_key}")
        else:
            print(f"Parent object with index {node_key} already exists")

        # Example processing: print child and code values
        print(f"Processing node={self.node_key}, code={self.code}")


class FileProcessor:
    """
    Processes a large text file line by line, extracting important columns by fixed indices.
    """
    def __init__(self, filepath: str, delimiter: str = '|'):
        self.filepath = filepath
        self.delimiter = delimiter

    def process_file(self):
        """
        Read the file line by line, extract important columns by index, and process each line.
        """
        with open(self.filepath, 'r', encoding='utf-8') as file:
            # Skip header line if present
            header_line = next(file)

            for line_number, line in enumerate(file, start=2):
                if line_number < START_LINE:
                    continue


                parts = line.strip().split(self.delimiter)
                # Check if line has enough columns
                max_index = max(NODE_INDEX, NODE_KEY, PARENT_INDEX, CODE_INDEX)
                if len(parts) <= max_index:
                    print(f"Warning: Line {line_number} does not have enough columns, skipping")
                    continue

                # Extract important columns by index
                data = {
                    'index': parts[NODE_INDEX].strip(),
                    'node_key': parts[NODE_KEY].strip(),
                    'parent': parts[PARENT_INDEX].strip(),
                    'code': parts[CODE_INDEX].strip()
                }

                # Create LineData instance and process it
                line_data = LineData(data)
                line_data.process()

    @staticmethod
    def get_diag():
        return LineData.diagram


if __name__ == "__main__":
    processor = FileProcessor('build_document.txt')
    processor.process_file()
    processor.get_diag().add_diagram_text_enduml()
    print(processor.get_diag().get_diagram_text())
