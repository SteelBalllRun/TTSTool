import os

more_str = u'工事中.......................working-on......................'


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
    return f'res/result/speech{index%2}.wav'


def update_recorder_state(state, event, values, window, time):
    pass


def text_list_handler(state, event, values, window, time):
    if event == '-FilePath-':
        state['loaded_file'] = values[event]
        file_path = state['loaded_file']
        with open(file_path, 'r', encoding='utf-8') as f:
            text_list = f.readlines()
            state['source_content'] = text_list
            print(f'get file contents{text_list}')
        window.Element('-TEXT LIST-').update(values=text_list)

    if event == '-TEXT LIST-':
        # init selected
        content = values[event][0]
        state['selected']['index'] = state['source_content'].index(content)
        state['selected']['content'] = content
        idx = state['selected']['index']
        name = voice_file_name(idx)
        exists = os.path.exists(name)
        state['selected']['path'] = name if exists else ''

        # update recorder
        update_recorder_state(state, event, values, window, time)



