from ryven.NENV import *

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
        NodeInputBP('xlsx_loc', add_data={'widget name': 'choose file', 'widget pos': 'besides'})
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

)
