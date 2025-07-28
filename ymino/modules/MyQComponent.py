from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import gdspy
import yaml
import numpy as np

class MyQComponent(QComponent):
    """Demonstration1 - Straight segment with variable width/length"""

    ### def __init__() <- comes from QComponent
    ###   Initiaizes base variables such as self.id, self.name and self.options
    ###   Also launches the first execution of make()

    ### def rebuild() <- comes from QComponent
    ###   Clear output from previous runs of make() (geom/pin/net) and re-runs it

    def make(self):
        lib = gdspy.GdsLibrary()
        filename = './mygds/TcSampleDesign.gds'
        scale = 1e-3
        #print( gdspy.get_gds_units(filename) )
        #print( design.get_units())
        lib.read_gds(filename, 'import')
        print(lib)
        cell = lib.top_level()[0]

        polygon_list = []        
        polygon_pocket_list = []                
        for polygon in cell.polygons:
            for poly_points, layer in zip(polygon.polygons, polygon.layers):
                poly = draw.Polygon(poly_points * scale)
                if layer == 1:
                    self.add_qgeometry('poly', dict(poly=poly), subtract = True, layer=1)
                    polygon_pocket_list.extend(poly_points * scale)
                else:
                    self.add_qgeometry('poly', dict(poly=poly), subtract = False, layer=1)    
                    polygon_list.extend(poly_points * scale)                

        
        with open("./mygds/TcSampleDesign.yaml", 'r') as f:
            port_data = yaml.safe_load(f)
        for name, info in port_data.items():  
            print(name, info)   
            self.add_pin(name, [np.array(info["start"])*scale,np.array(info["end"])*scale], info["width"]*scale, gap=info["gap"]*scale)
