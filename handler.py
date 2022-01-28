import asyncio
import os
from recorder import Recorder

more_str = u'工事中.......................working-on......................'

file_name_prefix = 'speech_'


def spin_text(state, window, time):
    if state['menu_idx'] == 'Record':
        pass
    elif state['menu_idx'] == 'More':
        offset = int(time / 10) % len(more_str)
        next_str = more_str[-offset:] + more_str[:-offset]
        window.Element('-More-').update(value=next_str)


def menu_handler(state, event, values, window, time):
    if event == '-Tab-':
        state['menu_idx'] = values[event]


def voice_file_name(index):
    return f'res/result/{file_name_prefix}{index}.wav'


def update_recorder_state(state, event, values, window, time):
    idx = state['selected']['index']
    content_loaded = len(state['source_content'])
    if not content_loaded:
        window.Element('-Record-').update(visible=False)
        return
    file_name = voice_file_name(idx)
    window.Element('-Record-').update(visible=True)
    if os.path.exists(file_name):
        window.Element('-Play-').update(visible=True)
    else:
        window.Element('-Play-').update(visible=False)
    pass


def text_list_handler(state, event, values, window, time):
    if event == '-FilePath-':
        state['loaded_file'] = values[event]
        file_path = state['loaded_file']
        with open(file_path, 'r', encoding='utf-8') as f:
            text_list = f.readlines()
            state['source_content'] = text_list.copy()
            state['shown_source_content'] = text_list
            print(f'get file contents{text_list}')
        window.Element('-TEXT LIST-').update(values=text_list)

    if event == '-TEXT LIST-' and len(state['source_content']) > 0:
        # init selected
        content = values[event][0]
        state['selected']['index'] = state['source_content'].index(content)
        state['selected']['content'] = content
        idx = state['selected']['index']
        name = voice_file_name(idx)
        exists = os.path.exists(name)
        state['selected']['path'] = name if exists else ''
        if exists:
            state['wav_list'][file_name_prefix + str(idx)] = state['selected']['content']

        # update recorder
        update_recorder_state(state, event, values, window, time)


def record_btn_handler(state, event, values, window, time, record: Recorder):
    if event == '-Record-':
        idx = state['selected']['index']
        file_path = voice_file_name(idx)
        if not record.is_recording:
            record.beginrec(file_path)
            state['shown_source_content'][idx] += '(recording...)'
        else:
            record.stoprec(file_path)
            state['selected']['path'] = file_path
            file_name = file_name_prefix + str(idx)
            state['wav_list'][file_name] = state['selected']['content']
            state['shown_source_content'][idx] += '(done)'
        text_list = state['shown_source_content']
        window.Element('-TEXT LIST-').update(values=text_list)



def play_btn_handler(state, event, values, window, time, record: Recorder):
    if event == '-Play-':
        idx = state['selected']['index']
        file_path = voice_file_name(idx)
        record.beginplay(file_path)


def dump_btn_handler(state, event, values, window, time, record: Recorder):
    if event == '-Dump-':
        wav_list = sorted(state['wav_list'].items(), key=lambda item: int(str(item[0]).split('_')[1]))
        with open('res/result/result.txt', 'w', encoding='utf-8') as f:
            wl = [k + '	' + v for k, v in wav_list]
            f.writelines(wl)
            print('finish dump')
