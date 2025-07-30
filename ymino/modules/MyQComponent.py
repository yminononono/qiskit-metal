from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import gdspy
import yaml
import numpy as np

class MyQComponent(QComponent):
    """Demonstration1 - Straight segment with variable width/length"""

    default_options = Dict(filename='TcSampleDesign')

    ### def __init__() <- comes from QComponent
    ###   Initiaizes base variables such as self.id, self.name and self.options
    ###   Also launches the first execution of make()

    ### def rebuild() <- comes from QComponent
    ###   Clear output from previous runs of make() (geom/pin/net) and re-runs it

    def make(self):

        p = self.p

        lib = gdspy.GdsLibrary()
        filename = f'./mygds/{p.filename}.gds'
        scale = 1e-3
        #print( gdspy.get_gds_units(filename) )
        #print( design.get_units())
        lib.read_gds(filename, 'import')
        cell = lib.top_level()[0]
          
        ## Add Geometry
        pocket_list = []
        metal_list = []
        for polygon in cell.polygons:
            for poly_points, layer in zip(polygon.polygons, polygon.layers):
                poly = draw.Polygon(poly_points * scale)
                if layer == 1:
                    pocket_list.append(poly)
                else:
                    metal_list.append(poly)

        pocket_list = draw.unary_union(pocket_list)
        metal_list = draw.unary_union(metal_list)
       
        self.add_qgeometry('poly', dict(launch_pad=metal_list), subtract = False, layer=1) 
        self.add_qgeometry('poly', dict(pocket=pocket_list), subtract = True, layer=1)

        ## Add Port
        with open(f"./mygds/{p.filename}.yaml", 'r') as f:
            port_data = yaml.safe_load(f)
        for name, info in port_data.items():  
            if "LaunchPad" in name:
                self.add_pin(name, [np.array(info["start"])*scale,np.array(info["end"])*scale], info["width"]*scale, gap=info["gap"]*scale)
            elif "Junction" in name:
                print(name, info)
                rect_jj = draw.LineString([np.array(info["start"])*scale, np.array(info["end"])*scale])
                self.add_qgeometry('junction', {name : rect_jj}, width=info["width"]*scale, layer=1)