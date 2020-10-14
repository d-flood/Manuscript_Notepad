import ctypes
import json
import pathlib
import PySimpleGUI as sg

main_dir = str(pathlib.Path(__file__)).replace('\\', '/')
main_dir = main_dir.replace("manuscript_notes.py", "")
print(main_dir)

ctypes.windll.shcore.SetProcessDpiAwareness(1)

starter_dict = {
    'blank': {
        'blank': {
            'note': 'There was a problem finding the notes file or this is the first use. Add an entry before deleting this one.',
            'page': '1',
            'pos': 'na', 
            'tag': 'na',
        }
    }
}

class Manage_Notes():

    """
    A class for managing changes to the JSON notes file and loaded dictionary.
    """

    def __init__(self):

        try:
            with open(f'{main_dir}/ms_notes.json', 'r', encoding='utf-8') as file:
                self.notes = json.load(file)
        except:
            with open(f'{main_dir}/ms_notes.json', 'w', encoding='utf-8') as file:
                json.dump(starter_dict, file, indent=4)
            self.notes = starter_dict

    def add_item(self, values: tuple):
        if values[0] in self.notes.keys():
            print('it exists!')
            self.notes[values[0]].update({values[1]: {'page': values[2], 'pos': values[3], 'tag': values[4], 'note': values[5]}})
        else:
            self.notes[values[0]] = {values[1]: {'page': values[2], 'pos': values[3], 'tag': values[4], 'note': values[5]}}
        self.save_notes()
        return self.notes

    def delete_item(self, values: tuple):
        try:
            self.notes[values[0]].pop(values[1])
        except KeyError:
            pass
        try:
            if not self.notes[values[0]]:
                try:
                    self.notes.pop(values[0])
                except KeyError:
                    print('Looks like you tried to delete something that does not exist')
        except KeyError:
            pass
        self.save_notes()
        return self.notes

    def save_notes(self):
        with open(f'{main_dir}/ms_notes.json', 'w', encoding='utf-8') as file:
            json.dump(self.notes, file, indent=4, ensure_ascii=False)


def build_tree(notes):
    treedata = sg.TreeData()
    for key in notes:
        treedata.Insert(parent='', key=f'-{key}-', text=key, values=[])
        for k in notes[key]:
            treedata.Insert(f'-{key}-', f'{key}_{k}', text=k, 
                values=[
                    notes[key][k]['page'],
                    notes[key][k]['pos'],
                    notes[key][k]['tag']
                ])
    return treedata


def build_layout(file_notes):

    ref_tip = 'Individual note title;\n\
Duplicates are not allowed under the same witness'
    note_column = [[sg.Multiline('', key='-note_output-', size=(50, 30))]]

    fftn = (15, 1)

    edit_tags_column = [
        [sg.B('New Note', size=fftn, pad=(3, 20))],
        [sg.B('Save', size=fftn, pad=(5, 40))],
        [sg.Text('Siglum', size=fftn, justification='r')],
        [sg.I('', size=fftn, key='-siglum-')],
        [sg.Text('Reference', size=fftn, justification='r', tooltip=ref_tip)],
        [sg.I('', size=fftn, key='-ref-', tooltip=ref_tip)],
        [sg.Text('_______________')],
        [sg.Text('Page', size=fftn, justification='r')],
        [sg.I('', size=fftn, key='-page-')],
        [sg.Text('Position', size=fftn, justification='r')],
        [sg.I('', size=fftn, key='-pos-')],
        [sg.Text('Tag', size=fftn, justification='r')],
        [sg.I('', size=fftn, key='-tag-')],
        [sg.B('Delete', size=fftn, pad=(3, 60))],
        [sg.B('Exit', size=fftn)]
        ]

    return [[sg.Tree(data=build_tree(file_notes.notes),
                    headings=['page', 'pos', 'tag'],
                    auto_size_columns=False,
                    num_rows=20,
                    col0_width=15,
                    key='-TREE-',
                    show_expanded=False,
                    enable_events=True,
                    col_widths=[5, 10, 10],
                    row_height=35),
            sg.Column(note_column), 
            sg.Column(edit_tags_column, vertical_alignment='top')]]


def get_note_data_for_display(which, file_notes):
    siglum = which.split('_')[0]
    ref = which.split('_')[1]
    return (siglum, ref, 
           file_notes.notes[siglum][ref]['page'], 
           file_notes.notes[siglum][ref]['pos'], 
           file_notes.notes[siglum][ref]['tag'], 
           file_notes.notes[siglum][ref]['note'])

def clear_inputs():
    window['-siglum-'].update('')
    window['-ref-'].update('')
    window['-page-'].update('')
    window['-pos-'].update('')
    window['-tag-'].update('')
    window['-note_output-'].update('')

def fill_inputs(values, window):
    window['-siglum-'].update(values[0])
    window['-ref-'].update(values[1])
    window['-page-'].update(values[2])
    window['-pos-'].update(values[3])
    window['-tag-'].update(values[4])
    window['-note_output-'].update(values[5])

def get_from_inputs(values):
    return (values['-siglum-'],
            values['-ref-'],
            values['-page-'],
            values['-pos-'],
            values['-tag-'],
            values['-note_output-'])

def add_item(values, file_notes):
    return file_notes.add_item(get_from_inputs(values))

def input_filler(event, values, file_notes, window):
    if len(values[event]) == 1 and '_' in values[event][0]:
        display_values = get_note_data_for_display(values[event][0], file_notes)
        fill_inputs(display_values, window)
    else:
        window['-siglum-'].update(values[event][0].strip('-'))

def delete_entry(values, file_notes):
    return file_notes.delete_item(get_from_inputs(values))

def check_for_blank_inputs(values):
    if values['-siglum-'] == '' or values['-ref-'] == '':
        sg.popup('Neither "Siglum" nor "Reference" input fields\n\
can be left blank.')
        return False
    else:
        return True

sg.theme('Topanga')
file_notes = Manage_Notes()
window = sg.Window('Manuscript Notes', build_layout(file_notes), icon=f'{main_dir}/icon.ico')#, no_titlebar=True, grab_anywhere=True)

while True:     # Event Loop
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Cancel', 'Quit', 'Exit'):
        file_notes.save_notes()
        break

    elif event == "-TREE-":
        input_filler(event, values, file_notes, window)

    elif event == 'Save':
        if check_for_blank_inputs(values) is True:
            treedata = build_tree(add_item(values, file_notes))
            window['-TREE-'].update(values=treedata)
    
    elif event == 'Delete':
        if check_for_blank_inputs(values) is True:
            treedata = build_tree(delete_entry(values, file_notes))
            window['-TREE-'].update(values=treedata)

    elif event == 'New Note':
        clear_inputs()
    # print(event)
window.close()
