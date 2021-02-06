class SVG(list):
    def __init__(self, units, width, height, view_width, view_height, dpi):
        super(SVG, self).__init__()

        self.append('<?xml version="1.0" standalone="no"?>')
        self.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"  ')
        self.append('  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">  ')
        self.append('<svg width="%f%s" height="%f%s" viewBox="0 0 %f %f"  '
                    % (width, units, height, units, view_width, view_height))
        self.append('     xmlns="http://www.w3.org/2000/svg" version="1.1">')
        self.append('  <title> F-engrave Output </title>')
        self.append('  <desc>SVG File Created By F-Engrave</desc>')
        self.dpi = dpi

    def line(self, x1, y1, x2, y2, thickness):
        self.append('  <path d="M %f %f L %f %f"'
                    % (x1 * self.dpi,
                       y1 * self.dpi,
                       x2 * self.dpi,
                       y2 * self.dpi))
        self.append('        fill="none" stroke="blue" stroke-width="%f" stroke-linecap="round" stroke-linejoin="round"/>'
                    % (thickness * self.dpi))

    def circle(self, center_x, center_y, radius, thickness):
        self.append('  <circle cx="%f" cy="%f" r="%f"'
                    % (center_x * self.dpi,
                       center_y * self.dpi,
                       radius * self.dpi))
        self.append('        fill="none" stroke="blue" stroke-width="%f"/>'
                    % (thickness * self.dpi))

    def close(self):
        self.append('</svg>')
