import PySimpleGUI as sg
from handler import *

state = {
    "menu_idx": 'Record',
    "loaded_file": '',
    "selected": {
        "index": 0,
        "path": '',
        "content": ''
    },
    "source_content": []
}
tic = 0


def make_more_layout():
    return [[sg.T(u'工事中...', k='-More-')]]


def make_tts_rec_layout():
    return [
        [sg.T('Source:'),
         sg.In('', visible=False, k='-FilePath-', enable_events=True),
         sg.FileBrowse(button_text='LOAD')],
        [sg.Listbox(values=["empty"],
                    size=(100, 20),
                    horizontal_scroll=True,
                    k='-TEXT LIST-',
                    enable_events=True)]]


def make_window():
    sg.theme("Tan")
    layout = [[sg.Text('TTS TOOL', size=(38, 1), justification='center', font=("Helvetica", 16), relief=sg.RELIEF_RIDGE,
                       k='-TEXT HEADING-', enable_events=True)]]
    layout += [[sg.TabGroup([[
        sg.Tab('Record', make_tts_rec_layout()),
        sg.Tab('More', make_more_layout())
    ]], enable_events=True, k='-Tab-')]]
    layout[-1].append(sg.Sizegrip())
    window = sg.Window('TTS Tool', layout,
                       resizable=True,
                       grab_anywhere=True,
                       right_click_menu_tearoff=True,
                       finalize=True)
    window.set_min_size(window.size)
    return window


def main():
    window = make_window()
    global tic
    while True:
        event, values = window.read(timeout=100)
        tic += 1
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            for key in values:
                print(f"Event({key} = {values[key]})")
        if event in (None, 'Exit'):
            break
        menu_handler(state, event, values, window, tic)
        spin_text(state, window, tic)
        text_list_handler(state, event, values, window, tic)

    window.close()
    exit(0)


if __name__ == "__main__":
    main()
