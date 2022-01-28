import PySimpleGUI as sg
from handler import *
from recorder import *

state = {
    "menu_idx": 'Record',
    "loaded_file": '',
    "selected": {
        "index": 0,
        "path": '',
        "content": ''
    },
    "shown_source_content": [],
    "source_content": [],
    "wav_list": {}
}
tic = 0
recorder = Recorder()

def make_more_layout():
    return [[sg.T(u'工事中...', k='-More-')]]


def make_tts_rec_layout():
    return [
        [sg.T('Source:'),
         sg.In('', visible=False, k='-FilePath-', enable_events=True),
         sg.FileBrowse(button_text='LOAD'),
         sg.pin(sg.Btn(k='-Record-', button_text="record", visible=False)),
         sg.pin(sg.Btn(k='-Play-', button_text="play", visible=False)),
         sg.pin(sg.Btn(k='-Dump-', button_text="dump trans.txt")),
         ],
        [sg.Listbox(values=["empty"],
                    size=(100, 20),
                    horizontal_scroll=True,
                    k='-TEXT LIST-',
                    enable_events=True)]]


def make_window():
    sg.theme("Tan")
    layout = [[sg.Text('TTS TOOL', size=(38, 1), justification='center', font=("Helvetica", 16), relief=sg.RELIEF_RIDGE,
                       k='-TEXT HEADING-')]]
    layout += [[sg.TabGroup([[
        sg.Tab('Record', make_tts_rec_layout()),
        sg.Tab('More', make_more_layout())
    ]], enable_events=True, k='-Tab-')]]
    layout[-1].append(sg.Sizegrip())
    w = sg.Window('TTS Tool', layout,
                       resizable=True,
                       grab_anywhere=True,
                       right_click_menu_tearoff=True,
                       finalize=True)
    w.set_min_size(w.size)
    return w


window = make_window()


def main():
    global tic
    global window
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
        record_btn_handler(state, event, values, window, tic, recorder)
        play_btn_handler(state, event, values, window, tic, recorder)
        dump_btn_handler(state, event, values, window, tic, recorder)

    window.close()
    exit(0)


@recorder.regist(path='res/result', play=False, complete=True)
async def record_complete(path: str):
    print(f'record complete:{path}')
    window.Element('-Record-').update('Record')
    await asyncio.sleep(0.1)


@recorder.regist(path='res/result', play=False, complete=False)
async def record_begin(path: str):
    print(f'record begin:{path}')
    window.Element('-Record-').update('Recording')
    await asyncio.sleep(0.1)


@recorder.play()
async def play_begin(path: str):
    print(f'playing audio')
    await asyncio.sleep(0.1)


async def play_complete(path: str):
    print(f'play complete audio')
    await asyncio.sleep(0.1)


if __name__ == "__main__":
    recorder.run()
    main()
