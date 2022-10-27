from ryven.NENV import *
from julia import ProRF as p
from datetime import datetime as d

widgets = import_widgets(__file__)


class NodeBase(Node):
    color = '#00a6ff'


class DualNodeBase(NodeBase):
    """For nodes that can be active and passive"""

    def __init__(self, params, active=True):
        super().__init__(params)

        self.active = active
        if active:
            self.actions['make passive'] = {'method': self.make_passive}
        else:
            self.actions['make active'] = {'method': self.make_active}

    def make_passive(self):
        del self.actions['make passive']

        self.delete_input(0)
        self.delete_output(0)
        self.active = False

        self.actions['make active'] = {'method': self.make_active}

    def make_active(self):
        del self.actions['make active']

        self.create_input(type_='exec', insert=0)
        self.create_output(type_='exec', insert=0)
        self.active = True

        self.actions['make passive'] = {'method': self.make_passive}

    def get_state(self) -> dict:
        return {
            'active': self.active
        }

    def set_state(self, data: dict, version):
        self.active = data['active']


class ReadData(NodeBase):
    """Reads fasta, excel data file and return X, Y value"""

    title = 'Read Data file'
    input_widget_classes = {
        'choose fasta': widgets.FASTAInputWidget,
        'choose xlsx': widgets.XLSXInputWidget
    }
    init_inputs = [
        NodeInputBP(label='fasta_loc', add_data={'widget name': 'choose fasta', 'widget pos': 'besides'}),
        NodeInputBP(label='xlsx_loc', add_data={'widget name': 'choose xlsx', 'widget pos': 'besides'}),
        NodeInputBP(label='xlsx_col', dtype=dtypes.String()),
        NodeInputBP(label='xlsx_sheet', dtype=dtypes.String(default='Sheet1')),
        NodeInputBP(label='xlsx_title', dtype=dtypes.Boolean(default=True)),
        NodeInputBP(label='seq_loc', dtype=dtypes.String(default='0')),
    ]
    init_outputs = [
        NodeOutputBP('X'),
        NodeOutputBP('Y'),
        NodeOutputBP('L'),
    ]

    def __init__(self, params):
        super().__init__(params)

        self.xlsx_filepath = ''
        self.fasta_filepath = ''

    def view_place_event(self):
        self.input_widget(0).path_chosen.connect(self.path_chosen_fasta)
        self.input_widget(1).path_chosen.connect(self.path_chosen_xlsx)

    def get_state(self):
        data = {'fasta path': self.fasta_filepath, 'xlsx path': self.xlsx_filepath}
        return data

    def set_state(self, data):
        self.path_chosen_fasta(data['fasta path'])
        self.path_chosen_xlsx(data['xlsx path'])

    def path_chosen_fasta(self, file_path):
        self.fasta_filepath = file_path
        self.update()

    def path_chosen_xlsx(self, file_path):
        self.xlsx_filepath = file_path
        self.update()

    def update_event(self, inp=-1):
        if (self.input(0) is not None or self.fasta_filepath != '') and \
                (self.input(1) is not None or self.xlsx_filepath != '') and \
                self.input(2) != '' and self.input(3) != '' and self.input(4) != '':
            fasta_loc = self.fasta_filepath if self.input(0) is None else self.input(0)
            xlsx_loc = self.xlsx_filepath if self.input(1) is None else self.input(1)
            xlsx_col = self.input(2)
            xlsx_sheet = self.input(3)
            xlsx_title = self.input(4)
            seq_loc = self.input(5).strip()
            loc = 0

            try:
                if ',' in seq_loc:
                    loc = map(int, seq_loc.split(','))
                else:
                    loc = int(seq_loc)
            except ValueError:
                pass

            x, y, lo = p.get_data(p.RF(fasta_loc, xlsx_loc, loc), p.only(xlsx_col), title=xlsx_title, sheet=xlsx_sheet)
            self.set_output_val(0, x)
            self.set_output_val(1, y)
            self.set_output_val(2, lo)


class ReadDataset(NodeBase):
    """Reads dataset folder and return X, Y value"""

    title = 'Read Dataset'
    input_widget_classes = {
        'choose folder': widgets.FolderInputWidget,
    }
    init_inputs = [
        NodeInputBP(label='dataset_loc', add_data={'widget name': 'choose folder', 'widget pos': 'besides'}),
        NodeInputBP(label='xlsx_col', dtype=dtypes.String()),
        NodeInputBP(label='xlsx_sheet', dtype=dtypes.String(default='Sheet1')),
        NodeInputBP(label='xlsx_title', dtype=dtypes.Boolean(default=True)),
    ]
    init_outputs = [
        NodeOutputBP('X'),
        NodeOutputBP('Y'),
        NodeOutputBP('L'),
    ]

    def __init__(self, params):
        super().__init__(params)

        self.image_filepath = ''

    def view_place_event(self):
        self.input_widget(0).path_chosen.connect(self.path_chosen)

    def get_state(self):
        data = {'file path': self.image_filepath}
        return data

    def set_state(self, data, version):
        self.path_chosen(data['file path'])

    def path_chosen(self, file_path):
        self.image_filepath = file_path
        self.update()

    def update_event(self, inp=-1):
        if (self.input(0) is not None or self.image_filepath != '') and \
                self.input(1) != '' and self.input(2) != '' and self.input(3) != '':
            folder_loc = self.image_filepath if self.input(0) is None else self.input(0)
            xlsx_col = self.input(1)
            xlsx_sheet = self.input(2)
            xlsx_title = self.input(3)

            x, y, lo = p.get_data(p.RF(folder_loc), p.only(xlsx_col), title=xlsx_title, sheet=xlsx_sheet)
            self.set_output_val(0, x)
            self.set_output_val(1, y)
            self.set_output_val(2, lo)


class PrintNode(DualNodeBase):
    title = 'Print'
    version = 'v0.1'
    init_inputs = [
        NodeInputBP(type_='exec'),
        NodeInputBP(dtype=dtypes.Data(size='m')),
    ]
    init_outputs = [
        NodeOutputBP(type_='exec'),
    ]
    color = '#5d95de'

    def __init__(self, params):
        super().__init__(params, active=True)

    def update_event(self, inp=-1):
        if self.active and inp == 0:
            print(self.input(1))
        elif not self.active:
            print(self.input(0))


export_nodes(
    ReadData,
    ReadDataset,
    PrintNode,
)
