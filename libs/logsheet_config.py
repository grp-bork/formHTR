import csv


ROI_TYPES = {'h': 'Handwritten',
             'c': 'Checkbox',
             'b': 'Barcode'}


class Region:
    """
    Class to represent single ROI
    """
    def __init__(self, start_x, start_y, end_x, end_y, content_type=None, varname=None):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.content_type = content_type
        self.varname = varname

    def __lt__(self, other):
        pass

    def __hash__(self):
        pass

    def __str__(self):
        return f'Region {self.varname}: ({self.start_x}, {self.start_y}) ({self.end_x}, {self.end_y}) - {self.content_type}'

    def get_start(self):
        return (self.start_x, self.start_y)
    
    def get_end(self):
        return (self.end_x, self.end_y)

    def to_list(self):
        return [self.start_x, self.start_y, self.end_x, self.end_y, self.varname, self.content_type]

    def update_content_type(self, content_type):
        self.content_type = content_type

    def update_varname(self, varname):
        self.varname = varname


class LogsheetConfig:
    """
    Class to store and represent the whole config.
    """
    def __init__(self):
        self.regions = []
        self.filename = None
        self.height = None
        self.width = None

    def set_attributes(self, regions, filename, height, width):
        self.regions = [Region(*region) for region in regions]
        self.filename = filename
        self.height = height
        self.width = width

    def add_region(self, start_x, start_y, end_x, end_y, content_type=None, varname=None):
        """
        Create new region
        """
        self.regions.append(Region(start_x, start_y, end_x, end_y, content_type, varname))

    def delete_last_region(self):
        """
        The undo command
        """
        if self.regions:
            self.regions.pop()

    def update_content_type(self, index, content_type):
        """
        Update content type of particular region

        Args:
            index (int): region identifier
            content_type (str): new content type
        """
        if content_type is not None:
            self.regions[index].update_content_type(ROI_TYPES[content_type])
        else:
            self.regions[index].update_content_type(None)

    def update_varname(self, index, name):
        """
        Update variable name of particular region

        Args:
            index (int): region identifier
            name (str): new variable name
        """
        self.regions[index].update_varname(name)

    def announce_status(self, index, clean_len=20):
        """
        Print current region status to command line

        Args:
            index (int): region identifier
            clean_len (int, optional): length of text to clear. Defaults to 20.
        """
        print(str(self.regions[index]) + ' ' * clean_len, end='\r')

    def export_to_csv(self, output_file=None, remove_unannotated=False):
        """
        Output logsheet config to CSV file

        Args:
            output_file (str, optional): location of output file. Defaults to None.
            remove_unannotated (bool, optional): Remove ROIs without any content type specified. Defaults to False.
        """
        filename = output_file if output_file else self.filename

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([self.filename, self.width, self.height, None, None])

            if remove_unannotated:
                for region in self.regions:
                    if region.content_type is not None:
                        writer.writerow(region.to_list())
            else:
                for region in self.regions:
                    writer.writerow(region.to_list())

    def import_from_csv(self, input_file):
        """
        Import losheet config from a CSV file

        Args:
            input_file (str): path to CSV file
        """
        with open(input_file, newline='') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=','))
            self.filename, self.width, self.height = reader[0][0], int(reader[0][1]), int(reader[0][2])
            for row in reader[1:]:
                content_type = row[5] if row[5] else None
                varname = row[4] if row[4] else None
                self.add_region(*list(map(int, row[:4])), content_type, varname)
