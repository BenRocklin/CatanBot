import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np

row_offsets = [0, -0.5, -1, -0.5, 0]
vertical_offset = (2 * np.sqrt(3) - 3) / (2 * np.sqrt(3))
hex_radius = 1/np.sqrt(3)

def convert_point_to_hex(point):
    """
    Converts from a point on a given row where buildings may be built/roads may end to hex coordinates for plotting.

    :param point: row and column of a CatanGame point
    :return: hex coordinate equivalent for plotting
    """
    [row, col] = point

    # if the row is larger than the third row, then we may "flip" our calculations for the y-coordinate
    factor = 1
    if row > 2:
        row -= 1
        factor = -1

    # compute x coordinate
    hex_col = -0.5 + 0.5 * col + row_offsets[row]

    # compute y coordinate
    hex_row = 4 - row + row * vertical_offset
    if col % 2 == 0:
        hex_row += factor * (hex_radius / 2)
    else:
        hex_row += factor * hex_radius

    return hex_col, hex_row

def convert_hexes_to_hex(game):
    """
    Helper function to convert board hexes to hex-coordinates for plotting, along with proper colors and number labels.
    :param game: CatanGame instance to plot
    :return: lists containing hex x coordinate, y coordinate, color, and associated number
    """
    colors = []
    labels = []
    hcoord = []
    vcoord = []
    for r in range(len(game.board.hex_nums)):
        row_resources = game.board.hexes[r]
        row_numbers = game.board.hex_nums[r]
        for i in range(len(row_numbers)):
            row = r
            col = i

            # convert hex row/col to proper plotting location
            y = 4-row+row*vertical_offset
            x = col + row_offsets[row]
            vcoord.append(y)
            hcoord.append(x)

            # append the dice roll needed for the hex to trigger as a label
            labels.append([row_numbers[i]])

            # display proper color for resourcce
            cell_number = row_resources[i]
            if cell_number == 0:
                # desert/robber
                colors.append(["Lightyellow"])
            elif cell_number == 1:
                # wheat
                colors.append(["Gold"])
            elif cell_number == 2:
                # sheep
                colors.append(["Chartreuse"])
            elif cell_number == 3:
                # ore
                colors.append(["DimGray"])
            elif cell_number == 4:
                # brick
                colors.append(["Firebrick"])
            elif cell_number == 5:
                # wood
                colors.append(["Green"])
            else:
                # small problem, this shouldn't ever trigger
                print("ERROR ENCODING HEX WITH NUMBER", cell_number, "AT POSITION", r, ",", i)
    return hcoord, vcoord, colors, labels

def convert_buildings_to_hex(game):
    """
    Helper function to convert all non-road buildings to hex-coordinates for plotting, along with proper player colors.
    :param game: CatanGame instance to plot
    :return: lists containing settlement and city x coordinate, y coordinate, and color
    """
    s_hcoord = []
    s_vcoord = []
    s_colors = []
    c_hcoord = []
    c_vcoord = []
    c_colors = []
    for r in range(len(game.board.points)):
        row_points = game.board.points[r]
        for i in range(len(row_points)):
            if row_points[i]:
                # only bother doing logic for spots that actually have a building
                structure = row_points[i]
                coord = convert_point_to_hex((r, i)) # fetch proper plot coordinates first

                # add building-specific function to proper arrays
                if structure.type == 0:
                    # settlement, add to all settlement plot arrays
                    s_hcoord.append(coord[0])
                    s_vcoord.append(coord[1])
                    if structure.owner == 0:
                        s_colors.append("RED")
                    else:
                        s_colors.append("BLUE")
                elif structure.type == 2:
                    # city, add to all city plot arrays
                    c_hcoord.append(coord[0])
                    c_vcoord.append(coord[1])
                    if structure.owner == 0:
                        c_colors.append("RED")
                    else:
                        c_colors.append("BLUE")
    return s_hcoord, s_vcoord, s_colors, c_hcoord, c_vcoord, c_colors

def plot_roads(game, ax):
    """
    Helper function to plot all roads in the CatanGame instance.

    :param game: CatanGame instance to plot
    :param ax: plot to plot roads on (need to plot each one at a time so do it here)
    """
    for road in game.board.roads:
        if road.type != 1:
            # if it's not a road, simulator has a bug in its roads list
            continue

        # convert road ending points to (x, y) pairs for plotting
        road_start = road.point_one
        road_end = road.point_two
        hex_road_start = convert_point_to_hex(road_start)
        hex_road_end = convert_point_to_hex(road_end)

        # get correct color of road based on owner
        r_color = None
        if road.owner == 0:
            r_color = "red"
        else:
            r_color = "blue"

        # plot the road as a line
        ax.plot([hex_road_start[0], hex_road_end[0]], [hex_road_start[1], hex_road_end[1]], color=r_color, zorder=1)

def draw_board(game, prior_plot=None, delay=0.01):
    """
    Controller function to handle plotting a CatanGame instance in a visual view. Also closes pre-existing windows if
    they exist.

    :param game: CatanGame instance to plot
    :param prior_plot: previous plot of game to close, if applicable
    :param delay: the amount of time to forcefully show the plot before closing and allowing logic to continue, useful for AI testing
    :return: a plot of the given CatanGame instance
    """
    if prior_plot:
        prior_plot.close()

    fig, ax = plt.subplots(1)
    ax.set_aspect('equal')

    # plot all hexes
    hcoord, vcoord, colors, labels = convert_hexes_to_hex(game)
    for x, y, c, l in zip(hcoord, vcoord, colors, labels):
        color = c[0].lower()
        hex = RegularPolygon((x, y), numVertices=6, radius=hex_radius,
                             facecolor=color, alpha=0.2, edgecolor='k')
        ax.add_patch(hex)
        ax.text(x, y+0.2, l[0], ha='center', va='center', size=20)
    ax.scatter(hcoord, vcoord, c=[c[0].lower() for c in colors], alpha=0.5)

    # plot all settlements/cities
    s_hcoord, s_vcoord, s_colors, c_hcoord, c_vcoord, c_colors = convert_buildings_to_hex(game)
    ax.scatter(s_hcoord, s_vcoord, c=[c[0].lower() for c in s_colors], marker="s", zorder=2)
    ax.scatter(c_hcoord, c_vcoord, c=[c[0].lower() for c in c_colors], marker="^", zorder=2)

    # plot all roads
    plot_roads(game, ax)

    plt.ion()
    plt.show()
    plt.pause(delay)
    return plt