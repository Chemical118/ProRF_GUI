import numpy
from ryven.NENV import *
from julia import ProRF as p
import numpy as np
from datetime import datetime as d

widgets = import_widgets(__file__)
protein_dict = ['vol', 'pI', 'hyd', 'vol, pI', 'vol, hyd', 'pI, hyd', 'all']


class ViewData:
    def __init__(self, val, size, seed):
        self.val = val
        self.size = size
        self.seed = seed

    def get_data(self):
        return self.val, self.size, self.seed


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

    def set_state(self, data: dict):
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
        NodeInputBP(label='seq_dict', dtype=dtypes.Choice(default='all', items=protein_dict)),
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
                self.input(2) != '' and self.input(3) != '' and self.input(5) != '' and self.input(6) in protein_dict:
            fasta_loc = self.fasta_filepath if self.input(0) is None else self.input(0)
            xlsx_loc = self.xlsx_filepath if self.input(1) is None else self.input(1)
            xlsx_col = self.input(2)
            xlsx_sheet = self.input(3)
            xlsx_title = self.input(4)
            seq_loc = self.input(5).replace(' ', '')
            seq_dict = self.input(6).replace(' ', '').split(',') if ',' in self.input(6) else self.input(6)
            loc = 0

            try:
                if ',' in seq_loc:
                    loc = map(int, seq_loc.split(','))
                else:
                    loc = int(seq_loc)
            except ValueError:
                pass

            x, y, lo = p.get_data(p.RF(fasta_loc, xlsx_loc, loc), p.only(xlsx_col), title=xlsx_title, sheet=xlsx_sheet,
                                  convert=seq_dict)
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
        NodeInputBP(label='seq_dict', dtype=dtypes.Choice(default='all', items=protein_dict)),
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
            seq_dict = self.input(4).replace(' ', '').split(',') if ',' in self.input(4) else self.input(4)

            x, y, lo = p.get_data(p.RF(folder_loc), p.only(xlsx_col), title=xlsx_title, sheet=xlsx_sheet,
                                  convert=seq_dict)

            self.set_output_val(0, x)
            self.set_output_val(1, y)
            self.set_output_val(2, lo)


class MinMaxNormNode(NodeBase):
    """Perform Min-Max normalization"""

    title = 'Norm'
    style = 'small'
    init_inputs = [
        NodeInputBP(label='Y'),
    ]
    init_outputs = [
        NodeOutputBP(label='Y'),
    ]

    def update_event(self, inp=-1):
        if type(self.input(0)) == np.ndarray:
            y = self.input(0)
            self.set_output_val(0, (y - y.min()) / (y.max() - y.min()))


def isminmaxable(obj):
    try:
        np.min(obj)
    except:
        return False
    return True


class RevMinMaxNormNode(NodeBase):
    """Perform reverse of Min-Max normalization"""

    title = 'Rev norm'
    style = 'small'
    init_inputs = [
        NodeInputBP(label='ref'),
        NodeInputBP(label='Y'),
    ]
    init_outputs = [
        NodeOutputBP(label='Y'),
    ]

    def update_event(self, inp=-1):
        if isminmaxable(self.input(0)) and type(self.input(1)) == np.ndarray:
            mi, ma = np.min(self.input(0)), np.max(self.input(0))
            self.set_output_val(0, self.input(1) * (ma - mi) + mi)


class FitModelNode(NodeBase):
    """Fit random forest model"""

    title = 'Fit model'
    init_inputs = [
        NodeInputBP(label='X'),
        NodeInputBP(label='Y'),
        NodeInputBP(label='feat', dtype=dtypes.Integer(default=6, bounds=(1, 100))),
        NodeInputBP(label='tree', dtype=dtypes.Integer(default=100, bounds=(1, 2000))),
        NodeInputBP(label='test_size', dtype=dtypes.Float(default=0.3)),
        NodeInputBP(label='depth', dtype=dtypes.Integer(default=-1, bounds=(-1, 1000))),
        NodeInputBP(label='arg', dtype=dtypes.Data(default='', size='m')),
    ]
    init_outputs = [
        NodeOutputBP(label='M'),
    ]

    def update_event(self, inp=-1):
        if type(self.input(0)) == np.ndarray and type(self.input(1)) == np.ndarray and \
                self.input(2) > 0 and self.input(3) > 0 and (self.input(5) == -1 or self.input(5) > 0) and \
                0 < self.input(4) < 1 and (self.input(6) == '' or type(self.input(6)) == dict):

            arg_dict = self.input(6)
            if arg_dict == '':
                arg_dict = dict()
                seed = p.rand(p.UInt64)
            else:
                seed = arg_dict.get('data_state', p.rand(p.UInt64))
            arg_dict['data_state'] = seed
            arg_dict['test_size'] = self.input(4)
            
            model = p.rf_model(self.input(0), self.input(1), self.input(2), self.input(3), val_mode=True, **arg_dict)
            self.set_output_val(0, ViewData(model, self.input(4), seed))


class PredictNode(NodeBase):
    """Predict from model and X value"""

    title = 'Predict'
    style = 'small'
    init_inputs = [
        NodeInputBP(label='M'),
        NodeInputBP(label='X'),
    ]
    init_outputs = [
        NodeOutputBP(label='PY'),
    ]

    def update_event(self, inp=-1):
        if type(self.input(0)) == ViewData and type(self.input(1)) == np.ndarray:
            model, size, seed = self.input(0).get_data()
            self.set_output_val(0, ViewData(p.parallel_predict(model, self.input(1)), size, seed))


class PredictViewNode(NodeBase):
    """View predict result"""

    title = 'View predict result'
    init_inputs = [
        NodeInputBP(label='PY'),
        NodeInputBP(label='Y'),
        NodeInputBP(label='nbin', dtype=dtypes.Integer(default=150, bounds=(1, 1000))),
        NodeInputBP(label='test_set', dtype=dtypes.Boolean(default=True)),
    ]
    init_outputs = [
        NodeOutputBP(label='NRMSE'),
    ]
    main_widget_class = widgets.PredictViewWidget
    main_widget_pos = 'below ports'

    def update_event(self, inp=-1):
        if self.session.gui and type(self.input(0)) == ViewData and type(self.input(1)) == numpy.ndarray:
            py, size, seed = self.input(0).get_data()
            y = self.input(1)
            n = np.size(y)
            ed_idx = p.gui_split_index(n, seed, size, self.input(3))
            py, y = py[ed_idx], y[ed_idx]

            if n > 150:
                c = p.gui_color_index(py, y, self.input(2))
                so_idx = np.argsort(c)
                nrmse_val = self.main_widget().show_result(py[so_idx], y[so_idx], z=c[so_idx])
            else:
                nrmse_val = self.main_widget().show_result(py, y)
            self.set_output_val(0, nrmse_val)


class ViewImportanceNode(NodeBase):
    """View feature importance from model by shapley value"""
    title = 'View importance'
    init_inputs = [
        NodeInputBP(label='M'),
        NodeInputBP(label='X'),
        NodeInputBP(label='L'),
        NodeInputBP(label='imp_iter', dtype=dtypes.Integer(default=60, bounds=(1, 100))),
        NodeInputBP(label='imp_arg', dtype=dtypes.Data(default='', size='m')),
        NodeInputBP(label='show_number', dtype=dtypes.Integer(default=15, bounds=(1, 40))),
    ]
    init_outputs = [
        NodeOutputBP(label='F'),
    ]
    main_widget_class = widgets.ImportanceViewWidget
    main_widget_pos = 'below ports'

    def update_event(self, inp=-1):
        if self.session.gui and type(self.input(0)) == ViewData and type(self.input(1)) == numpy.ndarray and \
                type(self.input(2)) == list and (self.input(4) == '' or type(self.input(4)) == dict):

            imp_arg_dict = dict() if self.input(4) == '' else self.input(4)
            imp_arg_dict['imp_iter'] = self.input(3)
            imp_arg_dict['val_mode'] = True

            model = self.input(0).get_data()[0]
            f = p.rf_importance(p.RF(''), model, self.input(1), self.input(2), **imp_arg_dict)
            self.main_widget().show_result(f, self.input(2), self.input(5))
            self.set_output_val(0, f)


class PrintNode(DualNodeBase):
    title = 'Print'
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
    RevMinMaxNormNode,
    PredictViewNode,
    ViewImportanceNode,
    MinMaxNormNode,
    FitModelNode,
    PredictNode,
    PrintNode,
)
