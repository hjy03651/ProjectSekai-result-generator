# -*- coding: utf-8 -*-
"""
Project Sekai Result Generator (Ver 1.0.0)
Date: 2025-02-20
Creator: twt @nezuki_ini__

Version History:
Ver 1.0.0 // 2025-02-20
"""

# Import modules ===================================================
import cv2
import pandas as pd
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk
from tkinter import Canvas
from PIL import Image, ImageTk, ImageDraw
import csv


# Preprocessing ====================================================
df = pd.read_excel('./data/prsk.xlsx').drop(0).drop('Unnamed: 0', axis=1)
df.columns = ['name', 'lvl', 'coord_y', 'coord_x', 'difficulty', 'tag']

proposal_data = {}
with open("./data/songs.csv", "r", encoding="utf-8-sig") as file:
    reader = csv.reader(file)
    for row in reader:
        name = row[0].strip() if '\ufeff' not in row[0] else row[0].replace('\ufeff', '').strip()
        proposal_data[(str(name), int(row[1]))] = row[2]

image = [cv2.imread('./images/mas_1.png'), cv2.imread('./images/mas_2.png')]

coord_x = [[925, 2645, 4365], [973, 2133, 3293]]  # phy, all, cog
coord_y = [4495, 4035, 3295, 2135, 975, 3460, 2440, 1420, 960, 820, 680, 540, 400]  # 25~37

font = 'AppleSDGothicNeoM00'
font_jp = 'Yu Gothic Medium'


# Functions ========================================================
def get_data(song_name, lvl):
    find_df = df[(df['name'] == song_name) & (df['lvl'] == lvl)]
    return find_df.iloc[0, [2, 3, 5]].tolist()  # y, x, tag


def draw_dots(song_name, lvl, color):
    dy, dx, tag = get_data(song_name, lvl)
    index = 1 if lvl > 29 else 0
    tag = 0 if tag == 'phy' else (1 if tag == 'all' else 2)
    lvl -= 25
    color = (255, 32, 32) if color == 'blue' else (32, 31, 255)
    table = image[index]

    x = coord_x[index][tag] + dx * 140 + 60
    y = coord_y[lvl] - dy * 140 + 60

    cv2.circle(table, (x, y), 35, color, thickness=-1)
    cv2.circle(table, (x, y), 35, (251, 252, 255), thickness=5)


# UI ===============================================================
# > main table ===============================
root = tk.Tk()
root.title('프로세카 성과표 생성기')
root.geometry('960x720+150+150')
root.resizable(False, False)
root['bg'] = '#CCCCCC'
icon = ImageTk.PhotoImage(file='./images/miku.png')
root.iconphoto(True, icon, icon)

bg = Image.open("./images/bg.png")
bg_image = ImageTk.PhotoImage(bg)
rectangle = Image.open("./images/rectangle.png").convert("RGBA")
rectangle_image = ImageTk.PhotoImage(rectangle)

canvas = tk.Canvas(root, width=960, height=720)
canvas.pack()
canvas.create_image(0, 0, anchor="nw", image=bg_image)
canvas.create_image(0, 0, anchor="nw", image=rectangle_image)

# > combobox =================================
combo_level = ttk.Combobox(root, values=['all']+[str(i) for i in range(25, 38)], font=(font, 10))
combo_level.current(0)
combo_level.place(x=200, y=134, width=148)

# combo_diff = ttk.Combobox(root, values=['all', 'EXPERT', 'MASTER'], font=(font, 10))
combo_diff = ttk.Combobox(root, values=['all', '아직 개발 중입니다!'], font=(font, 10))
combo_diff.current(0)
combo_diff.place(x=430, y=134, width=148)

combo_sort = ttk.Combobox(root, values=['난이도 상승', '난이도 하강', '곡명'], font=(font, 10))
combo_sort.current(0)
combo_sort.place(x=644, y=134, width=148)

# > treeview =================================
style = ttk.Style()
style.configure("Treeview", font=(font_jp, 12))
style.configure("Treeview.Heading", font=(font, 12, "bold"))

columns = ("name", "level", "checkbox")
tree = ttk.Treeview(root, columns=columns, show="headings", height=22)

tree.heading("name", text="곡명")
tree.heading("level", text="레벨")
tree.heading("checkbox", text="fc/ap 여부")

tree.column("name", width=600)
tree.column("level", width=70, anchor='center')
tree.column("checkbox", width=89, anchor="center")

state_labels = ["", "FC", "AP"]
current_states = [0] * len(proposal_data)

tree.yview_moveto(0)
scroll = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
scroll.place(x=852, y=169, height=462)
tree.configure(yscrollcommand=scroll.set)


# > functions for table ======================
def insert_data(data_list):
    for item in tree.get_children():
        tree.delete(item)
    for item in data_list:
        song_name, level, checked = item
        tag = '' if checked == 'X' else checked
        tree.insert("", "end", values=(song_name, level, tag))


def apply_filters(_=None):
    level_selected = combo_level.get()
    # diff_selected = combo_diff.get()
    sort_selected = combo_sort.get()

    filtered_data = sorted([[k[0], k[1], v] for k, v in list(proposal_data.items())], key=lambda x: x[1])

    if level_selected != "all":
        filtered_data = [item for item in filtered_data if str(item[1]) == level_selected]
    if sort_selected == "난이도 상승":
        filtered_data.sort(key=lambda x: x[1])
    elif sort_selected == "난이도 하강":
        filtered_data.sort(key=lambda x: x[1], reverse=True)
    else:
        filtered_data.sort(key=lambda x: x[0])

    insert_data(filtered_data)


def update_check(event):
    item = tree.identify_row(event.y)
    col = tree.identify_column(event.x)
    if col == "#3":  # checkbox 열 클릭 시
        index = tree.index(item)
        current_states[index] = (current_states[index] + 1) % 3  # 0→1→2→0 순환
        song_name, level, checked = list(tree.item(item, "values"))
        checked = state_labels[current_states[index]]  # 상태 변경
        tree.item(item, values=[song_name, level, checked])

        proposal_data[(song_name, int(level))] = checked

        # print(proposal_data) ; debugging
        with open("./data/songs.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            for k, v in list(proposal_data.items()):
                tag = 'X' if not v else v
                writer.writerow([k[0], k[1], tag])


def print_proposal(_=None):
    fc_list, ap_list = [], []
    with open("./data/songs.csv", "r", encoding="utf-8-sig") as f:
        files = csv.reader(f)
        for line in files:
            if line[2] == 'FC':
                fc_list.append((line[0], int(line[1])))
            elif line[2] == 'AP':
                ap_list.append((line[0], int(line[1])))

    for song_name, lvl in fc_list:
        draw_dots(song_name, lvl, 'blue')
    for song_name, lvl in ap_list:
        draw_dots(song_name, lvl, 'red')

    for n, i in enumerate(image):
        cv2.imwrite(f'./outputs/output_{n + 1}.png', i)

    msg.showinfo('생성 완료!', '성과표가 폴더에 저장되었습니다.')


# > buttons ==================================
btn_print = tk.Button(text='성과표 출력', font=("a옛날사진관3", 12), command=print_proposal, bg='#ffffff')

# > texts ====================================
canvas.create_text(420, 110, text="2025년 2월 19일 기준, 익스~마스터 성과표입니다. 개인차 있을 수 있음!",
                   font=("a옛날사진관3", 10), fill="white", anchor='center')
canvas.create_text(950, 700, text="v1.0.0. Tool - by @nezuki_ini__ / Table - by Wjddn",
                   font=("a어린이날L", 13), fill="#070707", anchor='e')

# > key bindings =============================
combo_level.bind("<<ComboboxSelected>>", apply_filters)
combo_diff.bind("<<ComboboxSelected>>", apply_filters)
combo_sort.bind("<<ComboboxSelected>>", apply_filters)
tree.bind("<Button-1>", update_check)

tree.place(x=90, y=167)
btn_print.place(x=750, y=80, width=120)


# Main =============================================================
apply_filters()
root.mainloop()
