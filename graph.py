#!/usr/bin/env python
# ECTS Striden 
import re
from sets import Set
from random import randint

YEAR_START = 2000
YEAR_END = 2011

COLORS = []

def clean_name(name):
    return re.sub(r'[^A-Za-z0-9]', '_', name)

def get_color(i):
    return 'rgb' + str(COLORS[i])

def populate_colors(n):
    for i in range(n):
        COLORS.append((randint(0, 255), randint(0, 255), randint(0, 255)))

def make_svg(data):
    users = map(clean_name, sorted(data.keys()))

    print """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:cc="http://creativecommons.org/ns#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
	xmlns:svg="http://www.w3.org/2000/svg"
	xmlns="http://www.w3.org/2000/svg"
	width="1500"
	height="700.0">
<script type="text/javascript">
<![CDATA[
var user_toggle = {};
var user_list = """ + str(users) + """;
var toggled = true;
var futureon = false;

function toggle_user(user) {
	if(user_toggle[user]==undefined) {
		user_toggle[user] = true;
	}
	var line = document.getElementById('user-score-'+user+'-line');
	var rect = document.getElementById('user-label-'+user+'-rect');
	var future = document.getElementById('user-score-'+user+'-prediction');
	if(user_toggle[user]) { //so it is lit!
		line.setAttribute("opacity", "0");
		rect.setAttribute("opacity", "0.5");
		future.setAttribute("opacity", "0");
	} else {
		line.setAttribute("opacity", "1");
		rect.setAttribute("opacity", "1");
		if ( futureon )
			future.setAttribute("opacity", "0.4");
	}
	user_toggle[user] = !user_toggle[user];
}

function toggle_all() {
	for( var i = 0; i < user_list.length; i++ ) {
		user_toggle[user_list[i]] = toggled;
		toggle_user(user_list[i]);
	}
	toggled = !toggled;
}

function toggle_future() {
	for( var i = 0; i < user_list.length; i++ ) {
		var user = user_list[i];
		var future = document.getElementById('user-score-'+user+'-prediction');
		if ( !user_toggle[user] && user_toggle[user]!=undefined )
			continue;
		if ( futureon ) {
			future.setAttribute("opacity", "0");
		} else {
			future.setAttribute("opacity", "0.4");
		}
	}
	futureon = !futureon;
}
]]>
</script>
<style type="text/css">
text {
  font-family: tahoma, sans;
  font-size: 12px;
}
#block-backs rect {
  opacity: 0.4;
}
#user-labels text {
  fill: #ffffff;
}
.user-line-prediction {
  stroke-width: 3;
}
#titles text {
  font-family: tahoma, sans;
  font-size: 22px;
}
</style>
    """

    num_years = YEAR_END - YEAR_START + 1

    print '<g id="years-backs">'
    for y in range(num_years):
        print '<rect x="' + str(50 + 100 * y) + '" y="50" width="100" ' + \
              'height="500" style="fill: ' + \
              (y % 2 == 0 and '#c3c3c3' or '#f3f3f3') + '"/>'
    print '</g>'

    latestY, latestB = max(max(user.keys()) for user in data.itervalues())

    print '<g id="block-backs">'
    maxB = (latestY - YEAR_START)*4 + (latestB - 1)
    for b in range(4*num_years):
        print '<rect x="' + str(50 + 25 * b) + '" y="50" width="25" ' + \
              'height="500" style="fill: ' + \
              (b % 2 == 0 and (b > maxB and '#8383f3' or '#e3e3f3') \
                           or (b > maxB and '#aaaaff' or '#ffffff')) + '"/>'
    print '</g>'

    print '<g id="user-lines">'
    for user in data.keys():
        points = []
        score = 0
        studiestartX = None
        for y in range(num_years):
            year = y + YEAR_START
            for b in range(4):
                if (year, b+1) in data[user]:
                    studiestartX = studiestartX or (50+100*y+25*b)
                    points.append((50 + 100*y + 25*b, 550 - score/60*100))
                    score += data[user][(year, b+1)]
                    points.append((50 + 100*y + 25*(b+1), 550 - score/60*100))

        points.append((50 + 100*(latestY-YEAR_START) + 25*latestB, 550 - score/60*100))
        points = sorted(list(Set(points)))

        pointstr = ' '.join(map(lambda (x, y): str(x)+','+str(y), points))

        index = users.index(clean_name(user))
        print '<polyline points="' + pointstr + '" style="' + \
              'stroke-width: 3px; stroke: '+get_color(index)+'; fill:none;" ' + \
              'id="user-score-'+clean_name(user)+'-line" />'

        x1 = 50 + 100*(latestY-YEAR_START) + 25*latestB
        y1 = 550 - score/60*100
        x2 = 50 + 100* num_years
        y2 = max((550 - y1) / (studiestartX - x1) * (x2 - x1) + y1, 50)
        print '<line x1="' + str(x1)+ '" y1="' + str(y1) + \
              '" x2="' + str(x2) + '" y2="' + str(y2) + '" ' + \
              'class="user-line-prediction" style="stroke: ' + \
              get_color(index) + ';" opacity="0" id="user-score-' + \
              clean_name(user) + '-prediction" />'
    print '</g>'

    print '<g id="user-labels">'
    i = 0
    for user in sorted(data):
        index = users.index(clean_name(user))
        print '<rect x="' + str(56.25 + 100*(i%num_years)) + '" y="' + \
              str(600.0 + 20 * (i//num_years)) + '" width="87.5" height="15" ' + \
              'style="fill:' + get_color(index) + ';" rx="5" ry="5" ' + \
              'id="user-label-' + clean_name(user) + '-rect" ' + \
              'onclick="toggle_user(\'' + clean_name(user) + '\');" />'
        print '<text x="' + str(60.0 + 100*(i%num_years)) + '" y="' + \
              str(611.0 + 20 * (i//num_years)) + '" id="user-label-' + \
              clean_name(user) + '-text" onclick="toggle_user(\'' + \
              clean_name(user) + '\');">' + user + '</text>'
        i += 1

    print '<rect x="56.25" y="' + str(600.0 + 20 * (i//num_years + 1)) + \
          '" width="87.5" height="15" style="fill:#000000;" rx="5" ry="5" ' + \
          'onclick="toggle_all();" />'
    print '<text x="68.25" y="' + str(611.0 + 20 * (i//num_years + 1)) + \
          '" onclick="toggle_all();" style="fill:#ffffff;">Toggle all</text>'
    print '<rect x="156.25" y="' + str(600.0 + 20 * (i//num_years + 1)) + \
          '" width="87.5" height="15" style="fill:#000000;" rx="5" ry="5" ' + \
          'onclick="toggle_future();" />'
    print '<text x="160.25" y="' + str(611.0 + 20 * (i//num_years + 1)) + \
          '" onclick="toggle_future();" style="fill:#ffffff;">Toggle future</text>'

    print '</g>'

    print """
<g id="ects-labels">
<line x1="50" y1="550.0" x2="1250" y2="550.0" style="stroke-width: 1.5; stroke: #000000;" />
<text x="20" y="555.0">0</text>
<line x1="50" y1="450.0" x2="1250" y2="450.0" style="stroke-width: 1.5; stroke: #000000;" />
<text x="20" y="455.0">60</text>
<line x1="50" y1="350.0" x2="1250" y2="350.0" style="stroke-width: 1.5; stroke: #000000;" />
<text x="20" y="355.0">120</text>
<line x1="50" y1="250.0" x2="1250" y2="250.0" style="stroke-width: 3; stroke: #000000;" />
<text x="20" y="255.0">180</text>
<line x1="50" y1="150.0" x2="1250" y2="150.0" style="stroke-width: 1.5; stroke: #000000;" />
<text x="20" y="155.0">240</text>
<line x1="50" y1="50.0" x2="1250" y2="50.0" style="stroke-width: 3; stroke: #000000;" />
<text x="20" y="55.0">300</text>
</g>"""

    print '<g id="timeline-labels">'
    for y in range(num_years):
        print '<rect x="' + str(50 + 100 * y) + '" y="570.0" width="100" ' + \
              'height="20" style="fill: ' + \
              (y % 2 == 0 and '#c3c3c3' or '#f3f3f3') + '"/>'
        print '<text x="'+str(84 + 100*y)+'" y="585.0">' + \
              str(YEAR_START + y) + '</text>'
    for b in range(4*num_years):
        print '<rect x="' + str(50 + 25 * b) + '" y="550.0" width="25" ' + \
              'height="20" style="fill: ' + \
              (b % 2 == 0 and '#e3e3f3' or '#ffffff') + '"/>'
        print '<text x="'+str(58 + 25 * b)+'" y="565.0">' + \
              str(b % 4 + 1) + '</text>'
    print '</g>'

    print '<g id="titles">'
    print '<text x="565" y="30">ECTS Striden</text>'
    print '</g>'

    print '</svg>'


def parse_data(filename):
    f = open(filename, 'r')
    data = {}
    while True:
        line = f.readline()

        # End of File
        if line == '':
            break

        line = line.strip()

        # Blanke linjer + kommentarer skippes
        if line == '' or line[0] == '#':
            continue

        if line[:2] == '::':
            name = line[2:]
            data[name] = {}
            continue

        tempYear, line = line.split(',', 1)
        tempYear = tempYear.strip()
        if tempYear.isdigit():
            year = int(tempYear)

        line = line.split(':')
        blok = line[0].strip()
        ects = float(line[1].strip())

        if len(blok) == 1:
            key = (year, int(blok))
            if key not in data[name]:
                data[name][key] = ects
            else:
                data[name][key] += ects
        elif blok == 's1':
            for key in [(year, 1), (year, 2)]:
                if key not in data[name]:
                    data[name][key] = ects/2
                else:
                    data[name][key] += ects/2
        elif blok == 's2':
            for key in [(year, 3), (year, 4)]:
                if key not in data[name]:
                    data[name][key] = ects/2
                else:
                    data[name][key] += ects/2

    return data

if __name__ == '__main__':
    print "Content-Type: image/svg+xml\n"

    data = parse_data('ectsdata')

    populate_colors(len(data))

    make_svg(data)


