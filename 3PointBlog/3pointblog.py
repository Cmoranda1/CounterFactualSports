import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.sampledata.iris import flowers
from bokeh.embed import components, file_html
from bokeh.resources import CDN

#the 3 pt line is not uniform throughout and is shorter at the corners
out_corner_ratio = 22/23.75
#nba 3 point line is 22 feet from the center of the basket at the corners 
#nba 3 point line is 23.75 feet from the center of the basket elsewhere but the circle is centered 4 feet out
#because the basket is 4 feet from the baseline
#to generate the standard 3 point line give these parameters: etc. x_3p,y_3p = generate_3pt_line(0,250,237.5, 0.1)
def generate_3pt_line(center_x, center_y, radius, stepsize=0.1):
    """
    generates coordinates for a semicircle, centered at center_x, center_y
    """        
    x = np.arange(center_x, center_x+radius+stepsize, stepsize)
    y = np.sqrt(radius**2 - x**2)

    # since each x value has two corresponding y-values, duplicate x-axis.
    # [::-1] is required to have the correct order of elements for plt.plot. 
    x = np.concatenate([x,x[::-1]])

    # concatenate y and flipped y. 
    y = np.concatenate([y,-y[::-1]])
    y3p = y + center_y
    corner_length = out_corner_ratio * (radius-4)
    line3 = plt.plot([0,171], [470,470], color = 'g')
    line4 = plt.plot([0,171], [30,30], color = 'g')
    mask = (y3p < 470) & (y3p > 30)
    
    line1 = plt.plot(x[mask], y3p[mask], color = 'g')
    return line1, line3, line4

def semicircle(r, h=250, k=40):
    y0 = h - r  # determine x start
    y1 = h + r  # determine x finish
    corner_length = out_corner_ratio * r
    corner_top_y = h + corner_length
    corner_bot_y = h - corner_length
    y = np.linspace(y0, y1, 10000)  # many points to solve for y

    # use numpy for array solving of the semicircle equation
    x = k + np.sqrt(r**2 - (y - h)**2) 
    corner_x = k + np.sqrt(r**2 - (corner_top_y - h)**2)
    line3 = plt.plot([0,corner_x], [corner_top_y,corner_top_y], color = 'g')
    line4 = plt.plot([0,corner_x], [corner_bot_y,corner_bot_y], color = 'g')
    mask = (y < corner_top_y) & (y > corner_bot_y)
    
    line1 = plt.plot(x[mask],y[mask],color='g')
    return line1

 def semicircle_bokeh(r, h=250, k=40):
    y0 = h - r  # determine x start
    y1 = h + r  # determine x finish
    corner_length = out_corner_ratio * r
    corner_top_y = h + corner_length
    corner_bot_y = h - corner_length
    y = np.linspace(y0, y1, 10000)  # many points to solve for y

    # use numpy for array solving of the semicircle equation
    x = k + np.sqrt(r**2 - (y - h)**2) 
    corner_x = k + np.sqrt(r**2 - (corner_top_y - h)**2)
    line3 = plt.plot([0,corner_x], [corner_top_y,corner_top_y], color = 'g')
    line4 = plt.plot([0,corner_x], [corner_bot_y,corner_bot_y], color = 'g')
    mask = (y < corner_top_y) & (y > corner_bot_y)
    new_x = x

    line1 = plt.plot(x[mask],y[mask],color='g')
    return line1

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

# The data consists of the shot log for the NBA season 2016/17
#standard radius = 237.5
radius = 237.5
shot = pd.read_csv("../Desktop/shot_logs_16_17.csv")
games = pd.read_csv("../Desktop/games.csv")
game_details = pd.read_csv("../Desktop/games_details.csv")
games = games[(games['GAME_DATE_EST'] >= "2016-10-25") & (games['GAME_DATE_EST'] <= "2017-4-12")]
game_details = game_details[(game_details['GAME_ID'] >= games['GAME_ID'].min()) & (game_details['GAME_ID'] <= games['GAME_ID'].max())]
pd.set_option('display.max_columns', 100)
print(shot.columns.tolist())
shot['date'] = pd.to_datetime(shot['date'])
shot.describe()
shot = shot[(shot['date'] == "2016-10-27")  & (shot['home_team'] == "ATL") & (shot['current_shot_outcome'] == "SCORED")]
shot['ThreePointerAdjusted'] = shot.apply(lambda x: outside_3(x.location_x, x.location_y, radius), axis=1)

line1 = semicircle(radius,250,40)
x = shot['location_x']
y = shot['location_y']

#col = np.where(shot['home_game'] == "Yes",'b',np.where(shot['home_game'] == "No",'r','g'))
col = np.where(shot['ThreePointerAdjusted'] == True,'blue',np.where(shot['ThreePointerAdjusted'] == False,'red','green'))

x = shot['location_x']
y = shot['location_y']
left_half_line = plt.scatter(x,y, s=10,c=col, marker= '.')
plt.xlim(0,933/2)

#-----------------bokeh
p = figure(title="Shot Scatter")
p.xaxis.axis_label = 'LocX'
p.yaxis.axis_label = 'LocY'

p.scatter(x,y,color = col, fill_alpha = 10, size = 10)
show(p)
html = file_html(p, CDN, "myplot")
print(html)
#-----------------

shot['halfcourt_x'] =np.where(shot['location_x'] > 933/2, 933 - shot['location_x'],shot['location_x'])
shot['halfcourt_y'] =np.where(shot['location_x'] > 933/2, 500 - shot['location_y'],shot['location_y'])
#shot.describe()
# all shots shown on a half court

hx = shot['halfcourt_x']
hy = shot['halfcourt_y']
right_half_line = plt.scatter(hx,hy, s=10,c=col, marker= '.')
plt.title("Shots", fontsize = 15)
plt.minorticks_on()
plt.grid(which='major', linewidth='.5', color='black')
plt.grid(which='minor', linewidth='.5', color='red')
#plt.show()
score_1 = len(shot[(shot['ThreePointerAdjusted']==True) & (shot['home_game'] == "Yes")])*3
score_1 = score_1 + len(shot[(shot['ThreePointerAdjusted']==False) & (shot['home_game'] == "Yes")])*2
              
score_2 = len(shot[(shot['ThreePointerAdjusted']==True) & (shot['home_game'] == "No")])*3
score_2 = score_2 + len(shot[(shot['ThreePointerAdjusted']==False) & (shot['home_game'] == "No")])*2

print("ATL: " + str(score_1))
print("WAS: " + str(score_2))