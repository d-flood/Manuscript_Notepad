import ctypes
import json
import pathlib
from natsort import natsorted
import PySimpleGUI as sg


class Manage_Notes():

    """
    A class for managing changes to the JSON notes file and loaded dictionary.
    """

    def __init__(self, main_dir, notes_dir):

        self.main_dir = main_dir
        self.notes_dir = notes_dir

        self.open_notes(self.notes_dir)

    def open_notes(self, notes_dir):

        starter_dict = {
        'Readme': {
            'A note!': {
                'note': 'If you are reading this, then either this is your first time opening up the Manuscript Notepad, or the app failed to load your saved notes.',
                'page': '',
                'pos': '', 
                'tag': ''
                        }
                    }
                }
        try:
            with open(notes_dir, 'r', encoding='utf-8') as file:
                self.notes = json.load(file)
        except:
            with open(f'{self.main_dir}/ms_notes.json', 'w', encoding='utf-8') as file:
                json.dump(starter_dict, file, indent=4)
            self.notes = starter_dict
            self.notes_dir = f'{self.main_dir}/ms_notes.json'
            update_settings('notes_dir', f'{self.main_dir}/ms_notes.json', self.main_dir)
        return self.notes

    def add_item(self, values: tuple):
        if values[0] in self.notes.keys():
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
        return self.notes

    def save_notes(self):
        with open(self.notes_dir, 'w', encoding='utf-8') as file:
            json.dump(self.notes, file, indent=4, ensure_ascii=False)
    
    def rename_notes_dir(self, notes_dir):
        self.notes_dir = notes_dir


def build_tree(notes):
    treedata = sg.TreeData()
    for key in natsorted(notes.keys()):
        treedata.Insert(parent='', key=f'-{key}-', text=key, values=[])
        try:
            for k in notes[key]:
                treedata.Insert(f'-{key}-', f'{key}_{k}', text=k, 
                    values=[
                        notes[key][k]['page'],
                        notes[key][k]['pos'],
                        notes[key][k]['tag']
                    ])
        except:
            print('list index error')
    return treedata


def build_layout(file_notes, dpi):

    ref_tip = 'Individual note title;\n\
Duplicates are not allowed under the same witness'
    note_column = [[sg.Multiline('', key='-note_output-', size=(50, 31))]]
    delete_tip = 'Notes are not permanently deleted until "Saved"'
    fftn = (15, 1)
    if dpi == 0:
        row_ht = 24
        b_space = (3, 20)
        s_space = (3, 10)
    elif dpi > 0:
        row_ht = 35
        b_space = (3, 30)
        s_space = (3, 15)

    menu_bar = [
        ['File', ['Save As']],
        ['Settings', ['Select Notes File', 'Change DPI Setting']]
    ]

    edit_tags_column = [
        [sg.B('New Note', size=fftn, pad=s_space)],
        [sg.B('Add', size=fftn, pad=s_space)],
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
        [sg.B('Delete', size=fftn, pad=b_space, tooltip=delete_tip)],
        [sg.B('Save', size=fftn, pad=b_space)],
        [sg.B('Exit', size=fftn)]
        ]

    return [[sg.Menu(menu_bar)],
        [sg.Tree(data=build_tree(file_notes.notes),
                    headings=['page', 'pos', 'tag'],
                    auto_size_columns=False,
                    num_rows=20,
                    col0_width=15,
                    key='-TREE-',
                    show_expanded=False,
                    enable_events=True,
                    col_widths=[5, 10, 10],
                    row_height=row_ht),
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

def clear_inputs(window):
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

def get_settings(main_dir):
    try:
        with open(f'{main_dir}/settings.json', 'r', encoding='utf-8') as settings:
            settings = json.load(settings)
    except:
        settings = dict(dpi = 1, notes_dir = '')
        with open(f'{main_dir}/settings.json', 'w', encoding='utf-8') as file:
            json.dump(settings, file)
    return settings['dpi'], settings['notes_dir']

def update_settings(new_key, new_value, main_dir):
    with open(f'{main_dir}/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
    settings[new_key] = new_value
    with open(f'{main_dir}/settings.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file)
        
def set_notes_file(main_dir):
    notes_fn = sg.PopupGetFile('Select your notes file', title='Set Saved Notes Path', 
                  default_extension='.json', file_types=[("JSON Files", '*.json')],
                  initial_folder=main_dir, no_window=True, icon=f'{main_dir}/icon.ico')
    if notes_fn != None and notes_fn != '':
        update_settings('notes_dir', notes_fn, main_dir)
    return notes_fn

def save_as(file_notes, main_dir):
    new_fn = sg.popup_get_file('', save_as=True, no_window=True, 
                                default_extension='.json', 
                                file_types=[("JSON Files", '*.json')],
                                icon=f"{main_dir}/icon.ico")
    if new_fn:
        with open(new_fn, 'w', encoding='utf-8') as file:
            json.dump(file_notes.notes, file, ensure_ascii=False, indent=4)
        file_notes.rename_notes_dir(new_fn)

def change_dpi(main_dir):
    layout = [
        [sg.T('Select a DPI awareness setting:')],
        [sg.Radio('0', 'dpi')],
        [sg.Radio('1', 'dpi')],
        [sg.Radio('2', 'dpi')],
        [sg.B('Submit', size=(8, 1))]
        ]

    _, values = sg.Window('Change DPI', layout).read(close=True)

    if values[0] is True:
        update_settings('dpi', 0, main_dir)
        sg.popup('You selected 0. Restart the app for the changes to take affect.', no_titlebar=True, background_color='#302401')
    elif values[1] is True:
        update_settings('dpi', 1, main_dir)
        sg.popup('You selected 1. Restart the app for the changes to take affect.', no_titlebar=True, background_color='#302401')
    elif values[2] is True:
        update_settings('dpi', 2, main_dir)
        sg.popup('You selected 2. Restart the app for the changes to take affect.', no_titlebar=True, background_color='#302401')

def main():

    main_dir = str(pathlib.Path(__file__)).replace('\\', '/')
    main_dir = main_dir.replace("manuscript_notes.py", "")
    main_dir = main_dir.replace("manuscript_notes.exe", "")

    dpi, notes_dir = get_settings(main_dir)    

    ctypes.windll.shcore.SetProcessDpiAwareness(dpi)

    sg.theme('Topanga')
    sg.set_options(icon=f'{main_dir}/icon.ico')
    file_notes = Manage_Notes(main_dir, notes_dir)
    window = sg.Window('Manuscript Notepad', build_layout(file_notes, dpi))#, no_titlebar=True, grab_anywhere=True)

    while True:     # Event Loop
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel', 'Quit', 'Exit'):
            # file_notes.save_notes() 
            break

        elif event == "-TREE-":
            input_filler(event, values, file_notes, window)

        elif event == 'Add':
            if check_for_blank_inputs(values) is True:
                treedata = build_tree(add_item(values, file_notes))
                window['-TREE-'].update(values=treedata)
        
        elif event == 'Delete':
            if check_for_blank_inputs(values) is True:
                treedata = build_tree(delete_entry(values, file_notes))
                window['-TREE-'].update(values=treedata)

        elif event == 'New Note':
            clear_inputs(window)

        elif event == 'Select Notes File':
            notes_dir = set_notes_file(main_dir)
            treedata = build_tree(file_notes.open_notes(notes_dir))
            window['-TREE-'].update(values=treedata)

        elif event == 'Save':
            file_notes.save_notes()
            sg.Popup('Your notes have been saved', title="Saved!")

        elif event == 'Save As':
            save_as(file_notes, main_dir)

        elif event == 'Change DPI Setting':
            change_dpi(main_dir)

    window.close()

if __name__ == "__main__":
    main()