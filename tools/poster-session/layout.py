"""
*TL;DR
Returns tansforms (position and rotation) to layout a given collection (the collection is only used for its length)
"""
import math
import numpy as np

class Layout:
    """
    Generates layouts for the number of itens in the given collection

    Attributes
    ----------
    ROWCOL: Row/col layout type
    CIRCLE: Circle layout type
    SQUARE: Square layout type
    LINE: Line layout type

    """
    ROWCOL = 'rowcol'
    CIRCLE = 'circle'
    SQUARE = 'square'
    LINE = 'line'

    def __init__(self, type, collection):
        """
        Create an instance for the given layout type, for the given collection
        The collection if only used to get its length when creating the tranforms

        Parameters
        ----------
        type : str
            one of the types supported: Layout.ROWCOL, Layout.CIRCLE, ...
        collection : list
            a list of object to which we can do len(collection)
        """
        self.type = type
        self.collection = collection

    def get_transforms(self, **kwargs):
        """
        Return a list (of size len(collection); see constructor) of translation and rotation tuples
        The tuples returned are in the form { x, y, x, rx, ry, rx }

        Usage examples:
            t = Layout(Layout.ROWCOL, alist).get_transforms(row_dist=20, col_dist=20, row_off=20, col_off=-50)
            t = Layout(Layout.CIRCLE, alist).get_transforms(radius=50)
            t = Layout(Layout.SQUARE, alist).get_transforms(length=100)
            t = Layout(Layout.LINE, alist).get_transforms(length=200)

        Parameters
        ----------
        kwargs
            Variable list of parameters, depending on the layout type
        """
        if (self.type == Layout.ROWCOL):
            print(kwargs)
            return self.row_layout(**kwargs)
        if (self.type == Layout.CIRCLE): return self.circle_layout(**kwargs)
        if (self.type == Layout.LINE): return self.line_layout(**kwargs)
        if (self.type == Layout.SQUARE): return self.square_layout(**kwargs)

    def row_layout(self, row_dist=30, col_dist=30, row_off=0, col_off=0, col_dir=1, row_dir=-1, col_axis='x', row_axis='z', fixed_axis='y'):
        n = len(self.collection)
        cols = 1
        if n > 4:
            cols = math.ceil(math.sqrt(n));
        rows = math.ceil(n / cols);

        transform=[]
        for row in range(rows):
            for col in range(cols):
                t = {}
                t[col_axis] = col_off + col * col_dist * col_dir
                t[row_axis] = row_off + row * row_dist * row_dir
                t[fixed_axis] = 0
                t['r'+col_axis] = 0
                t['r'+row_axis] = 0
                t['r'+fixed_axis] = 0
                transform.append(t)
        return transform

    def circle_layout(self, radius=50, a1_off=0, a2_off=0, axis1='x', axis2='z', fixed_axis='y'):
        n = len(self.collection)
        transform = []
        for x in range(0,n):
            t={}
            t[axis1] = math.cos(2*math.pi/n*x)*radius + a1_off
            t[axis2] = math.sin(2*math.pi/n*x)*radius + a2_off
            t[fixed_axis] = 0
            t['r'+axis1] = 0
            t['r'+axis2] = 0
            t['r'+fixed_axis] = math.degrees(math.atan2(-t[axis1], -t[axis2]))
            transform.append(t)
        return transform

    def line_layout(self, length=200, rotation=90, alternating_rot=True, a1_off=0, a2_off=0, axis1='x', axis2='z', fixed_axis='y'):
        n = len(self.collection)
        a1_off = a1_off - length // 2
        (r, line) = self.line_points(n, 0, rotation, alternating_rot, length, a1_off, a2_off, axis1, axis2, fixed_axis);
        return line

    def square_layout(self, length=50, a1_off=0, a2_off=0, axis1='x', axis2='z', fixed_axis='y'):
        n = len(self.collection)
        nps = n // 4 # n per side
        r = n % 4 # reminder

        a1_off = a1_off - length // 2
        a2_off = a2_off - length // 2
        (r, top) = self.line_points(nps, r, 0, False, length, a1_off, a2_off, axis1, axis2, fixed_axis);
        (r, left) = self.side_points(nps, r, 90, False, length, a2_off, a1_off, axis2, axis1, fixed_axis);
        (r, right) = self.side_points(nps, r, 270, False, length, a2_off, a1_off+length, axis2, axis1, fixed_axis);
        (r, bottom) = self.side_points(nps, r, 180, False, length, a1_off, a2_off+length, axis1, axis2, fixed_axis);
        return np.concatenate([top, left, right, bottom])

    def line_points(self, nps, r, rot, arot, length, a_off, oa_off, axis, oaxis, fixed_axis):
        if r>0:
            nps = nps + 1
            r = r - 1
        transform=[]
        for p in range(int(length/nps/2), length, int(length/nps)):
            t = {}
            t[axis] = a_off + p
            t[oaxis] = oa_off
            t[fixed_axis] = 0
            t['r'+axis] = 0
            t['r'+oaxis] = 0
            t['r'+fixed_axis] = rot
            transform.append(t)
            if (arot): rot = -rot
        return (r, transform)
