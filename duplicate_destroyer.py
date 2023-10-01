import pandas as pd
import flet as ft
import uuid
from functools import partial
import hashlib
import os
from filecmp import cmp, clear_cache
from datetime import datetime


LOG_FILE = "log.txt"

class Item:
    def __init__(self, name, item_id, hash, is_main=False):
        self.name = name
        self.item_id = item_id
        self.is_main = is_main
        self.to_delete = False
        self.hash = hash
        self.is_deleted = False

items = {}
cb_counter = 0

def main(page: ft.Page):
    global items

    print(datetime.now(), file=open(LOG_FILE, "a"))

    def on_dialog_result(e: ft.FilePickerResultEvent):
        # print("Selected files:", e.files, file=open(LOG_FILE, "a"))
        # print("Selected file or directory:", e.path, file=open(LOG_FILE, "a"))
        if e.files != None:
            for i in e.files:
                file_list = textfield1.value.splitlines()
                if i.path not in file_list:
                    textfield1.value += i.path + "\n"
                button2.disabled = False
            page.update()

    def on_cb_change(item_id, e):
        global cb_counter

        if e.control.value == True:
            items[item_id].to_delete = True
            cb_counter += 1
        else:
            items[item_id].to_delete = False
            cb_counter -= 1
        
        if cb_counter > 0:
            button3.disabled = False
        elif cb_counter == 0:
            button3.disabled = True
        else:
            print("OMG HOW'S THAT EVEN POSSIBLE cb_counter < 0 !", file=open(LOG_FILE, "a"))

        # print(cb_counter)
        button3.update()
        show_widgets()

    def on_switch_change(item_id, e):
        if e.control.value == True:
            set_main(item_id, True)
        else:
            set_main(item_id, False)
        
        if cb_counter > 0:
            button3.disabled = False
        elif cb_counter == 0:
            button3.disabled = True
        else:
            print("OMG! WHAT THE HELL! cb_counter < 0 !", file=open(LOG_FILE, "a"))

        show_widgets()
        button3.update()
        # print(cb_counter)

    def show_widgets():
        col.controls = []
        hash_list = []

        for i in items:
            if items[i].hash not in hash_list:
                hash_list.append(items[i].hash)

        for hash in hash_list:
            col.controls.append(ft.Text(value="SHA-256:  " + hash))
            item_list = [items[i] for i in items if items[i].hash == hash]
            for i in item_list:
                sw = ft.Switch(value=i.is_main, on_change=partial(on_switch_change, i.item_id), disabled=i.is_deleted)
                if i.is_deleted == True:
                    cb = ft.Checkbox(label=i.name, value=i.to_delete,
                                     disabled=True, on_change=partial(on_cb_change, i.item_id),
                                     fill_color='Green')
                else:
                    cb = ft.Checkbox(label=i.name, value=i.to_delete, disabled=i.is_main, on_change=partial(on_cb_change, i.item_id),
                                     check_color="Red")
                col.controls.append(ft.Row([sw, cb]))
        col.update()

    def on_textfield_change(e):
        if e.control.value != '':
            button2.disabled = False
        else:
            button2.disabled = True
            status_text.value = "Let's hunt down some duplicates"
            status_text.color = "Green"
            col.controls = []
            col.update()
        page.update()

    def find_duplicates(e):
        global cb_counter

        cb_counter = 0

        lines = textfield1.value.splitlines()
        file_list = []
        hash_list = []

        global items
        items = {}

        status_text.value = "Finding those stinky duplicates..."
        status_text.color = "Red"
        status_text.update()

        for line in lines:
            if os.path.exists(line):
                if os.path.isfile(line):
                    if line not in file_list:
                        file_list.append(line)
                elif os.path.isdir(line):
                    for root, dirs, files in os.walk(line):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if file_path not in file_list:
                                file_list.append(file_path)
            else:
                pass
        
        for file in file_list:
            with open(file, "rb") as f:
                digest = hashlib.file_digest(f, "sha256")
                hash = digest.hexdigest()
                item_id = uuid.uuid1()
                if hash not in hash_list:
                    hash_list.append(hash)
                    item = Item(file, item_id, hash, is_main=True)
                else:
                    item = Item(file, item_id, hash)
                items[item_id] = item
        show_widgets()

        status_text.value = "Duplicate search completed"
        status_text.color = "Green"
        status_text.update()

    def delete_duplicates(e):
        global items
        global cb_counter

        hash_list = []
        
        for i in items:
            if items[i].hash not in hash_list:
                hash_list.append(items[i].hash)
        
        for hash in hash_list:
            files = [i for i in items if items[i].hash == hash and items[i].to_delete == True and items[i].is_main == False and items[i].is_deleted == False]
            main_file = [i for i in items if items[i].hash == hash and items[i].is_main == True]
            if len(main_file) == 1:
                main_file = main_file[0]
            else:
                print("OMG! ARE YOU SERIOUS?", file=open(LOG_FILE, "a"))

            for file in files:
                if file != main_file:
                    clear_cache()
                    paranoia_mode_check = cmp(items[file].name, items[main_file].name, shallow=False)
                    if paranoia_mode_check is True:
                        # print(items[file].name, "and", items[main_file].name, "are the same.", file=open(LOG_FILE, "a"))
                        items[file].is_deleted = True
                        cb_counter -= 1
                        # print(cb_counter, file=open(LOG_FILE, "a"))
                        
                        if os.path.exists(items[file].name):
                            os.remove(items[file].name)
                            print("File", items[file].name, "was destroyed successfully \m/.", file=open(LOG_FILE, "a"))
                            status_text.value = "Annihilated some duplicates in happiness and joy"
                            status_text.color = "Green"
                            status_text.update()

                            button3.disabled = True
                            button3.update()
                        else:
                            print("OMG NO THAT CAN'T BE TRUE!", file=open(LOG_FILE, "a")) 
                    else:
                        print("OMG NO!", file=open(LOG_FILE, "a"))
        show_widgets()

    def set_main(item_id, val):
        global cb_counter

        if val is True:
            items[item_id].is_main = True
            if items[item_id].to_delete == True:
                items[item_id].to_delete = False
                cb_counter -= 1
            hash = items[item_id].hash
            duplicates = [id for id in items if items[id].hash == hash and id != item_id]
            for i in duplicates:
                items[i].is_main = False
        else:
            hash = items[item_id].hash
            duplicates = [id for id in items if items[id].hash == hash]
            set_main(items[duplicates[0]].item_id, True)

    page.window_width = 640
    page.window_height = 480
    page.title = "Duplicate Destroyer \m/"
    page.scroll = ft.ScrollMode.ALWAYS
    page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thumb_visibility=True),
                          text_theme=ft.TextTheme(body_small=ft.TextStyle(size=10, color="Black"),
                                                  body_medium=ft.TextStyle(size=10, color="Black"),
                                                  body_large=ft.TextStyle(size=10, color="Black"),
                                                  label_small=ft.TextStyle(size=10, color="Black"),
                                                  label_large=ft.TextStyle(size=10, color="Black"),
                                                  label_medium=ft.TextStyle(size=10, color="Black"),
                                                  )
                        )
    page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

    button1 = ft.ElevatedButton(text="Choose files", on_click=lambda _: fp.pick_files(allow_multiple=True))
    button2 = ft.ElevatedButton(text="Find duplicates", disabled=True, on_click=find_duplicates)
    button3 = ft.ElevatedButton(text="Destroy 'Em All", disabled=True, on_click=delete_duplicates)
    textfield1 = ft.TextField(label="List of files/folders to check", multiline=True, max_lines=10, on_change=on_textfield_change)
    status_text = ft.Text(value="Let's hunt down some duplicates", color="Green")
    page.add(ft.Column(controls=[textfield1,
                                 status_text,
                                 ft.Row(controls=[button1, button2, button3])]))

    fp = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(fp)
    page.update()

    col = ft.Column()
    page.add(col)

ft.app(target=main)