import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, gridplot, curdoc, save
from bokeh.sampledata.iris import flowers
from bokeh.embed import components, file_html
from bokeh.resources import CDN
from bokeh.layouts import layout, column
from bokeh.io import show, output_notebook, output_file
from bokeh.models import CustomJS, Dropdown, ColumnDataSource, Label, TextInput

output_file(filename="3_Point_Plot.html", title="Static HTML file")

out_corner_ratio = 22/23.75
def semicircle_bokeh(r, h=250, k=40):
    y0 = h - r  # determine x start
    y1 = h + r  # determine x finish
    corner_length = out_corner_ratio * r
    corner_top_y = h + corner_length
    corner_bot_y = h - corner_length
    y = np.linspace(y0, y1, 10000)  # many points to solve for y
    line_1_y = [corner_top_y] * 10000
    line_2_y = [corner_bot_y] * 10000
    # use numpy for array solving of the semicircle equation
    x = k + np.sqrt(r**2 - (y - h)**2) 
    corner_x = k + np.sqrt(r**2 - (corner_top_y - h)**2)
    line_1_x = np.linspace(0, corner_x, 10000)
    mask = (y < corner_top_y) & (y > corner_bot_y)
    new_x = x
    x_pts = [x[mask], line_1_x, line_1_x]
    y_pts = [y[mask], line_1_y, line_2_y]
    return x_pts, y_pts

def outside_3(x, y, r, h=250, k=40):
    corner_length = out_corner_ratio * r
    corner_top_y = h + corner_length
    corner_bot_y = h - corner_length
    #don't forget to flip x if it's on the right side of halfcourt
    if(x > 933/2):
        x = 933-x
    x_check = k + np.sqrt(r**2 - (y - h)**2)
    if(x > x_check):
        return True
    elif(y > corner_top_y):
        return True
    elif(y < corner_bot_y):
        return True
    else:
        return False

bokeh_doc = curdoc()

shot = pd.read_csv("Data/shot_data_by_game.csv")
#shot_for_game = shot[shot['GAME_ID'] == 21601222]
shot = shot[shot.HOME_X_MAKES != '[]']
game_ids = shot['GAME_ID'].astype(str).tolist()
dates = shot['GAME_DATE_EST'].astype(str).tolist()
home_team_names = shot['HOME_TEAM_ABBR'].astype(str).tolist()
away_team_names = shot['AWAY_TEAM_ABBR'].astype(str).tolist()
matchup_descriptor = ['']*len(game_ids)

for i in range(len(game_ids)):
    matchup_descriptor[i] = (dates[i] + ": " + away_team_names[i] + " @ " + home_team_names[i])
    
menu = list(zip(matchup_descriptor, game_ids))
dropdown = Dropdown(label="Game_IDS", menu=menu)
dropdown.js_on_event("menu_item_click", CustomJS(code="console.log('dropdown: ' + this.item, this.toString())"))

radius = 237.5
x,y = semicircle_bokeh(radius)
graph = figure(title = "3PointLine", plot_width = int(933/2))

source_3 = ColumnDataSource(data={'3_x' : x,
                                '3_y' : y})

graph.multi_line(xs = '3_x', ys = '3_y', source = source_3)

#shot['ThreePointerAdjusted'] = shot.apply(lambda x: outside_3(x.location_x, x.location_y, radius), axis=1)
shot_for_game = shot[shot['GAME_ID'] == 21601217]

x = shot_for_game['HOME_X_MAKES'].iloc[0]
x_h = x.strip('][').split(', ')

y = shot_for_game['HOME_Y_MAKES'].iloc[0]
y_h = y.strip('][').split(', ')

x_h = list(map(float, x_h))
y_h = list(map(float, y_h))

#shot['halfcourt_x'] =np.where(shot['location_x'] > 933/2, 933 - shot['location_x'],shot['location_x'])
#shot['halfcourt_y'] =np.where(shot['location_x'] > 933/2, 500 - shot['location_y'],shot['location_y'])

x_2 = shot_for_game['AWAY_X_MAKES'].iloc[0]
x_a = x_2.strip('][').split(', ')

y_2 = shot_for_game['AWAY_Y_MAKES'].iloc[0]
y_a = y_2.strip('][').split(', ')

x_a = list(map(float, x_a))
y_a = list(map(float, y_a))

#------------------------------------------
home_score_actual = 0
away_score_actual = 0
freethrows_home = 0
freethrows_away = 0

for i in range(len(x_h)):
    if(outside_3(x_h[i], y_h[i], radius)):
        home_score_actual += 3
    else:
        home_score_actual += 2
    
for i in range(len(x_a)):
    if(outside_3(x_a[i], y_a[i], radius)):
        away_score_actual += 3
    else:
        away_score_actual += 2

freethrows_home = shot_for_game['PTS_home'].iloc[0] - home_score_actual
freethrows_away = shot_for_game['PTS_away'].iloc[0] - away_score_actual
#---------------------------------------------

#transpose location data to all be on left half of court
shot_num = 0

#home shots
while(shot_num < len(x_h)):
    if (x_h[shot_num] > 933/2):
        x_h[shot_num] = 933 - x_h[shot_num]
        y_h[shot_num] = 500 - y_h[shot_num]
    shot_num += 1

shot_num = 0

#away shots
while(shot_num < len(x_a)):
    if (x_a[shot_num] > 933/2):
        x_a[shot_num] = 933 - x_a[shot_num]
        y_a[shot_num] = 500 - y_a[shot_num]
    shot_num += 1

shot_num = 0

x_h_col = pd.DataFrame(x_h, columns=['x_h_col'])
y_h_col = pd.DataFrame(y_h, columns=['y_h_col'])
x_a_col = pd.DataFrame(x_a, columns=['x_a_col'])
y_a_col = pd.DataFrame(y_a, columns=['y_a_col'])

source = ColumnDataSource(data={'x_h' : x_h_col['x_h_col'],
                                'y_h' : y_h_col['y_h_col']})

source_2 = ColumnDataSource(data={'x_a' : x_a_col['x_a_col'],
                                  'y_a' : y_a_col['y_a_col']})

graph.scatter(x = 'x_h',y = 'y_h',color = 'red', source = source, fill_alpha = 10, size = 10)
graph.scatter(x = 'x_a',y = 'y_a',color = 'blue', source = source_2, fill_alpha = 10, size = 10)

final_score = str(shot_for_game['HOME_TEAM_ABBR'].iloc[0]) + ':' + str(shot_for_game['PTS_home'].iloc[0]) + '   ' + str(shot_for_game['AWAY_TEAM_ABBR'].iloc[0]) + ':' + str(shot_for_game['PTS_away'].iloc[0])
mytext = Label(x=190, y=10, text=final_score)

graph.add_layout(mytext)

def update_plot(attr, old, new):
    radius = 237.5
    x_3pt_cb ,y_3pt_cb = semicircle_bokeh(radius)
    #graph = figure(title = "3PointLine", plot_width = 400)#int(933/2))
    #graph.multi_line(x, y)
    #shot['ThreePointerAdjusted'] = shot.apply(lambda x: outside_3(x.location_x, x.location_y, radius), axis=1)
    game_id = int(dropdown.value)
    shot_for_game_cb = shot[shot['GAME_ID'] == game_id]
    final_score_cb = str(shot_for_game_cb['HOME_TEAM_ABBR'].iloc[0]) + ":" + str(shot_for_game_cb['PTS_home'].iloc[0]) + '   ' + str(shot_for_game_cb['AWAY_TEAM_ABBR'].iloc[0]) + ":" + str(shot_for_game_cb['PTS_away'].iloc[0])
    mytext.text = final_score_cb
    x_cb = shot_for_game_cb['HOME_X_MAKES'].iloc[0]
    x_h_cb = x_cb.strip('][').split(', ')
    y_cb = shot_for_game_cb['HOME_Y_MAKES'].iloc[0]
    y_h_cb = y_cb.strip('][').split(', ')
    
    x_h_cb = list(map(float, x_h_cb))
    y_h_cb = list(map(float, y_h_cb))
    
    #shot['halfcourt_x'] =np.where(shot['location_x'] > 933/2, 933 - shot['location_x'],shot['location_x'])
    #shot['halfcourt_y'] =np.where(shot['location_x'] > 933/2, 500 - shot['location_y'],shot['location_y'])

    x_2_cb = shot_for_game_cb['AWAY_X_MAKES'].iloc[0]
    x_a_cb = x_2_cb.strip('][').split(', ')

    y_2_cb = shot_for_game_cb['AWAY_Y_MAKES'].iloc[0]
    y_a_cb = y_2_cb.strip('][').split(', ')

    x_a_cb = list(map(float, x_a_cb))
    y_a_cb = list(map(float, y_a_cb))

    #transpose location data to all be on left half of court
    shot_num = 0

    #home shots
    while(shot_num < len(x_h_cb)):
        if (x_h_cb[shot_num] > 933/2):
            x_h_cb[shot_num] = 933 - x_h_cb[shot_num]
            y_h_cb[shot_num] = 500 - y_h_cb[shot_num]
        shot_num += 1

    shot_num = 0

    #away shots
    while(shot_num < len(x_a_cb)):
        if (x_a_cb[shot_num] > 933/2):
            x_a_cb[shot_num] = 933 - x_a_cb[shot_num]
            y_a_cb[shot_num] = 500 - y_a_cb[shot_num]
        shot_num += 1

    shot_num = 0
    
    
    x_h_col = pd.DataFrame(x_h_cb, columns=['x_h_col'])
    y_h_col = pd.DataFrame(y_h_cb, columns=['y_h_col'])
    x_a_col = pd.DataFrame(x_a_cb, columns=['x_a_col'])
    y_a_col = pd.DataFrame(y_a_cb, columns=['y_a_col'])
    
    new_data = {'x_h' : x_h_col['x_h_col'],
                'y_h' : y_h_col['y_h_col']}

    new_data2 = {'x_a' : x_a_col['x_a_col'],
                 'y_a' : y_a_col['y_a_col']}
    
    new_data3 = {'3_x' : x_3pt_cb,
                 '3_y' : y_3pt_cb}
    
    source.data = new_data
    source_2.data = new_data2
    source_3.data = new_data3
    
def callback_linechange(attr, old, new):
    home_score = 0
    away_score = 0
    radius = float(text_input.value) * 10
    x_3pt_cb ,y_3pt_cb = semicircle_bokeh(radius)
    #graph = figure(title = "3PointLine", plot_width = 400)#int(933/2))
    #graph.multi_line(x, y)
    #shot['ThreePointerAdjusted'] = shot.apply(lambda x: outside_3(x.location_x, x.location_y, radius), axis=1)
    game_id = int(dropdown.value)
    shot_for_game_cb = shot[shot['GAME_ID'] == game_id]
    x_cb = shot_for_game_cb['HOME_X_MAKES'].iloc[0]
    x_h_cb = x_cb.strip('][').split(', ')
    y_cb = shot_for_game_cb['HOME_Y_MAKES'].iloc[0]
    y_h_cb = y_cb.strip('][').split(', ')
    
    x_h_cb = list(map(float, x_h_cb))
    y_h_cb = list(map(float, y_h_cb))
    
    #shot['halfcourt_x'] =np.where(shot['location_x'] > 933/2, 933 - shot['location_x'],shot['location_x'])
    #shot['halfcourt_y'] =np.where(shot['location_x'] > 933/2, 500 - shot['location_y'],shot['location_y'])

    x_2_cb = shot_for_game_cb['AWAY_X_MAKES'].iloc[0]
    x_a_cb = x_2_cb.strip('][').split(', ')

    y_2_cb = shot_for_game_cb['AWAY_Y_MAKES'].iloc[0]
    y_a_cb = y_2_cb.strip('][').split(', ')

    x_a_cb = list(map(float, x_a_cb))
    y_a_cb = list(map(float, y_a_cb))
    
    for i in range(len(x_h_cb)):
        if(outside_3(x_h_cb[i], y_h_cb[i], radius)):
            home_score += 3
        else:
            home_score += 2
    
    for i in range(len(x_a_cb)):
        if(outside_3(x_a_cb[i], y_a_cb[i], radius)):
            away_score += 3
        else:
            away_score += 2
    home_score += freethrows_home
    away_score += freethrows_away
    
    final_score_cb = str(shot_for_game_cb['HOME_TEAM_ABBR'].iloc[0]) + ":" + str(home_score) + '   ' + str(shot_for_game_cb['AWAY_TEAM_ABBR'].iloc[0]) + ":" + str(away_score)
    mytext.text = final_score_cb
    
    #transpose location data to all be on left half of court
    shot_num = 0

    #home shots
    while(shot_num < len(x_h_cb)):
        if (x_h_cb[shot_num] > 933/2):
            x_h_cb[shot_num] = 933 - x_h_cb[shot_num]
            y_h_cb[shot_num] = 500 - y_h_cb[shot_num]
        shot_num += 1

    shot_num = 0

    #away shots
    while(shot_num < len(x_a_cb)):
        if (x_a_cb[shot_num] > 933/2):
            x_a_cb[shot_num] = 933 - x_a_cb[shot_num]
            y_a_cb[shot_num] = 500 - y_a_cb[shot_num]
        shot_num += 1

    shot_num = 0
    
    
    x_h_col = pd.DataFrame(x_h_cb, columns=['x_h_col'])
    y_h_col = pd.DataFrame(y_h_cb, columns=['y_h_col'])
    x_a_col = pd.DataFrame(x_a_cb, columns=['x_a_col'])
    y_a_col = pd.DataFrame(y_a_cb, columns=['y_a_col'])
    
    new_data = {'x_h' : x_h_col['x_h_col'],
                'y_h' : y_h_col['y_h_col']}

    new_data2 = {'x_a' : x_a_col['x_a_col'],
                 'y_a' : y_a_col['y_a_col']}
    
    new_data3 = {'3_x' : x_3pt_cb,
                 '3_y' : y_3pt_cb}
    
    source.data = new_data
    source_2.data = new_data2
    source_3.data = new_data3

dropdown.value = '21601217'
dropdown.on_change('value', update_plot)
text_input = TextInput(title="Distance to 3")
text_input.on_change('value', callback_linechange)
bokeh_doc.add_root(column(dropdown, graph, text_input))
save(bokeh_doc)
html = file_html(bokeh_doc, CDN, "myplot")
save(html)
