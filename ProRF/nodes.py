from ryven.NENV import *
from datetime import datetime as d

widgets = import_widgets(__file__)


class NodeBase(Node):
    color = '#00a6ff'


class ReadXlsx(NodeBase):
    """Reads an excel file and return Y value"""

    title = 'Read Excel file'
    input_widget_classes = {
        'choose file': widgets.XLSXInputWidget
    }
    init_inputs = [
        NodeInputBP(label='location', add_data={'widget name': 'choose file', 'widget pos': 'besides'}),
        NodeInputBP(dtype=dtypes.String(), label='column'),
        NodeInputBP(dtype=dtypes.Boolean(default=True), label='title'),
    ]
    init_outputs = [
        NodeOutputBP('Y')
    ]

    def __init__(self, params):
        super().__init__(params)

        self.image_filepath = ''

    def view_place_event(self):
        self.input_widget(0).path_chosen.connect(self.path_chosen)
        # self.main_widget_message.connect(self.main_widget().show_path)

    def update_event(self, inp=-1):
        if (self.input(0) is not None or self.image_filepath != '') and self.input(1) != '':
            xlsx_loc = self.image_filepath if self.input(0) is None else self.input(0)
            xlsx_col = self.input(1)
            xlsx_title = self.input(2)
            # print(d.now())
            # self.set_output_val(0, )

    def get_state(self):
        data = {'file path': self.image_filepath}
        return data

    def set_state(self, data, version):
        self.path_chosen(data['file path'])
        # self.image_filepath = data['image file path']

    def path_chosen(self, file_path):
        self.image_filepath = file_path
        self.update()


class ReadFasta(NodeBase):
    """Reads a fasta file and return X value"""

    title = 'Read Fasta file'
    input_widget_classes = {
        'choose file': widgets.FASTAInputWidget
    }
    init_inputs = [
        NodeInputBP('location', add_data={'widget name': 'choose file', 'widget pos': 'besides'})
    ]
    init_outputs = [
        NodeOutputBP('X')
    ]

    def __init__(self, params):
        super().__init__(params)

        self.image_filepath = ''

    def view_place_event(self):
        self.input_widget(0).path_chosen.connect(self.path_chosen)
        # self.main_widget_message.connect(self.main_widget().show_path)

    def update_event(self, inp=-1):
        if self.input(0) is None:
            if self.image_filepath == '':
                return

            try:
                self.set_output_val(0, self.image_filepath)
            except Exception as e:
                print(e)
        else:
            self.set_output_val(0, self.input(0))

    def get_state(self):
        data = {'file path': self.image_filepath}
        return data

    def set_state(self, data, version):
        self.path_chosen(data['file path'])
        # self.image_filepath = data['image file path']

    def path_chosen(self, file_path):
        self.image_filepath = file_path
        self.update()


export_nodes(
    ReadXlsx,
    ReadFasta,

)
