import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six
import datetime

from selenium import webdriver


CLASS_ID = 4
BATCH_ID = "CS 1"

def get_time_table():

    try:
        driver = webdriver.Firefox()
    except:
        driver = webdriver.Chrome()

    url = "http://www.ncuindia.edu/timetable/cse2019.html"
    driver.get(url)

    headers = driver.find_elements_by_tag_name("h1")

    headers = list(map(lambda x: x.text, headers))

    table = driver.find_elements_by_tag_name("table")[CLASS_ID]

    tbody = table.find_element_by_tag_name("tbody")
    
    i, j, k = 0, 0, 0
    days = {}
    for row in tbody.find_elements_by_tag_name("tr"):
        lr = []
        j = 0
        for col in row.find_elements_by_tag_name("td"):
            if (j > 0) and (i > 0):
                if ((i % 2) is not 0):
                    lr.append(col.text)
            j += 1
        lr = list(map(lambda a: (a[:3]+a[4:]) if (len(a) == 5) else list(a), list(filter(lambda z: (len(z) > 2) or ((len(z) > 5) and (z[3] == BATCH_ID)), list(map(lambda x: list(filter(lambda y: (len(y) > 0) and (y is not " "), x.split("\n"))), lr))))))
        if len(lr) > 0:
            days[k] = {sub[3] : str(sub[0] + " in " + sub[2]) for sub in lr}
            k += 1
        i += 1

    driver.close()

    df = pd.DataFrame(days)

    df = df.T

    cols = df.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    df = df[cols]

    df.fillna("BREAK", inplace=True)

    index = ["MON", "TUE", "WED", "THU", "FRI"]

    df.index = index
    df = df.reset_index()
    df.rename(columns={"index" : "Days"}, inplace=True)

    df.to_csv("TimeTable.csv", index=False)

    render_mpl_table(df, header_columns=1, col_width=7).get_figure().savefig("TimeTable.png", dpi=200)

    return df


def render_mpl_table(data, col_width=3.0, row_height=3.5, font_size=32,
                     header_color='#40466e', row_colors=['#f5f5f5', 'w'], edge_color='black',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

# render_mpl_table(df, header_columns=1, col_width=7).get_figure().savefig("TimeTableG.png", dpi=200)

def fetch_next_room_number(df, next_rn=True):

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    currentDate = datetime.datetime.now()
    today = currentDate.strftime("%a")

    if today not in days:
        print("Its A Holiday Mate!")

    slots = df.columns.tolist()[1:]
    slots = list(map(lambda x: x.split(" - "), slots))
    slots = [j for sub in slots for j in sub]

    slots_obj = []
    pos = 0

    for slot in slots:
        if "pm" in slot.lower():
            slots_obj.append(currentDate.replace(hour=((int(slot.split(":")[0]) % 12) + 12), minute=int(slot.split(":")[1][:2])))
        else:
            slots_obj.append(currentDate.replace(hour=(int(slot.split(":")[0])), minute=int(slot.split(":")[1][:2])))

    if (currentDate > slots_obj[-1]):
        today = days[(days.index(today) + 1) % 5]

    if not next_rn:
        if ((currentDate < slots_obj[0]) or (currentDate > slots_obj[-1])):
            return "You've no class right now!"
    
    for i in range(len(slots_obj)-1):
        if ((currentDate >= slots_obj[i]) and (currentDate <= slots_obj[i+1])):
            if next_rn:
                pos = i+2
            else:
                pos = i
            break

    x = df.columns.tolist()[1:]

    try:
        x = list(filter(lambda x: slots[pos] in x, x))[-1]
    except:
        return "You've no class right now!"
    
    y = " ".join(str(df[df["Days"] == today.upper()][x]).split("\n")[0].split()[1:])

    if next_rn:
        if "BREAK" in y:
            return "Your next slot is *free*! Enjoy!"
        return "You're next class is *" + y + "*"
    
    else:
        if "BREAK" in y:
            return "You've a *break* right now! Enjoy!"
        return "You're class right now is *" + y + "*"


