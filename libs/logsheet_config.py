import json

from libs.region import ROI, Residual


ROI_TYPES = {'h': 'Handwritten',
             'c': 'Checkbox',
             'b': 'Barcode'}


class LogsheetConfig:
    """
    Class to store and represent the whole config.
    """
    def __init__(self, regions, residuals, height=None, width=None):
        self.regions = regions
        self.residuals = residuals
        self.height = height
        self.width = width

    def add_roi(self, start_x, start_y, end_x, end_y, varname=None, content_type=None):
        """
        Create new ROI
        """
        self.regions.append(ROI(start_x, start_y, end_x, end_y, varname, content_type))

    def delete_last_region(self):
        """
        The undo command
        """
        if self.regions:
            self.regions.pop()

    def update(self, index, attribute, value):
        """
        Update content type of particular region

        Args:
            index (int): region identifier
            attribute (str): attribute to be set
            value (str): desired value
        """
        if attribute == 'content_type':
            value = ROI_TYPES[value]
        setattr(self.regions[index], attribute, value)

    def announce_status(self, index, clean_len=20):
        """
        Print current region status to command line

        Args:
            index (int): region identifier
            clean_len (int, optional): length of text to clear. Defaults to 20.
        """
        print(str(self.regions[index]) + ' ' * clean_len, end='\r')

    def export_to_json(self, output_file, remove_unannotated=False):
        """
        Output logsheet config to JSON file

        Args:
            output_file (str): location of output file.
            remove_unannotated (bool, optional): Remove ROIs without any content type specified. Defaults to False.
        """
        output = {'to_ignore': [], 'content': [], 'height': self.height, 'width': self.width}

        if remove_unannotated:
            for region in self.regions:
                if region.content_type is not None:
                    output['content'].append({'coords': region.get_coords(), 'varname': region.varname, 'type': region.content_type})
        else:
            for region in self.regions:
                output['content'].append({'coords': region.get_coords(), 'varname': region.varname, 'type': region.content_type})

        for residual in self.residuals:
            output['to_ignore'].append({'coords': residual.get_coords(), 'content': residual.expected_content})
        
        with open(output_file, 'w') as f:
            json.dump(output, f, sort_keys=True, indent=4)

    def import_from_json(self, input_file):
        """
        Import losheet config from a JSON file

        Args:
            input_file (str): path to JSON file
        """
        with open(input_file, 'r') as f:
            data = json.load(f)

        for residual in data['to_ignore']:
            self.residuals.append(Residual(*residual['coords'],
                                    expected_content=residual['content']))
        for region in data['content']:
            self.regions.append(ROI(*region['coords'],
                                    varname=region['varname'],
                                    content_type=region['type']))
            
        self.height = int(data['height'])
        self.width = int(data['width'])
