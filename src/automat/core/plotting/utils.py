import pylab

DEFAULT_BASE_STYLE = {
              'linestyle' : '-',
              'marker'    : '.',
              'color'     : (0.0,0.0,0.0,1.0),
             }

def color_slice(cmap_name, num):
    cmap = pylab.get_cmap(cmap_name)
    return cmap(pylab.linspace(0.0,1.0,num))
    
def colormapped_styles(cmap_name, num, base_style_dict = DEFAULT_BASE_STYLE):
    colors = color_slice(cmap_name,num)
    styles = []
    for color in colors:
        style = base_style_dict.copy()
        style['color'] = color
        styles.append(style)
    return styles
