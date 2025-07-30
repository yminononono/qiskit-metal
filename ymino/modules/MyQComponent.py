from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import gdspy
import yaml
import numpy as np

def MyQComponents(design, filelist):

    component_list = []
    scale = 1e-3

    for filename in filelist:
        # Get Component Info
        with open(f"./mygds/{filename}.yaml", 'r') as f:
            data = yaml.safe_load(f)

        # Get GDS design
        lib_metal = gdspy.GdsLibrary()
        fin = f'./mygds/{filename}.gds'
        lib_metal.read_gds(fin, 'import')
        cell_metal = lib_metal.top_level()[0]

        lib_pocket = gdspy.GdsLibrary()
        fin = f'./mygds/{filename}_pocket.gds'
        lib_pocket.read_gds(fin, 'import')
        cell_pocket = lib_pocket.top_level()[0]

        layer_list = [data[component]["layer"] for component in data]

        # collect polygons by layer information
        pocket_list = {k: [] for k in layer_list}
        metal_list = {k: [] for k in layer_list}
        for polygon in cell_metal.polygons:
            for poly_points, layer in zip(polygon.polygons, polygon.layers):
                poly = draw.Polygon(poly_points * scale)
                metal_list[layer].append(poly)
        for polygon in cell_pocket.polygons:
            for poly_points, layer in zip(polygon.polygons, polygon.layers):
                poly = draw.Polygon(poly_points * scale)
                pocket_list[layer].append(poly)     

        for component in data:
            layer = data[component]["layer"]
            if "ports" in data[component]:
                port_data = data[component]["ports"]
            else:
                port_data = {}
            options = Dict(
                polygons_metal = metal_list[layer],
                polygons_pocket = pocket_list[layer],
                port_data = port_data,
                scale = 1e-3,
            )
            MyQComponent(design, component, options = options)
            component_list.append( component )    
    
    return component_list

class MyQComponent(QComponent):
    """Demonstration1 - Straight segment with variable width/length"""

    default_options = Dict(
        polygons_metal = [],
        polygons_pocket = [],
        port_data = {},
        scale = 1e-3,
    )

    ### def __init__() <- comes from QComponent
    ###   Initiaizes base variables such as self.id, self.name and self.options
    ###   Also launches the first execution of make()

    ### def rebuild() <- comes from QComponent
    ###   Clear output from previous runs of make() (geom/pin/net) and re-runs it

    def make(self):

        p = self.p

        ## Add Geometry
        metal_list = draw.unary_union(p.polygons_metal)
        pocket_list = draw.unary_union(p.polygons_pocket)
       
        self.add_qgeometry('poly', dict(metal=metal_list), subtract = False, layer=1) 
        self.add_qgeometry('poly', dict(pocket=pocket_list), subtract = True, layer=1)

        ## Add Port
        for name, info in p.port_data.items():  
            if "LaunchPad" in name:
                self.add_pin(name, [np.array(info["start"])*p.scale,np.array(info["end"])*p.scale], info["width"]*p.scale, gap=info["gap"]*p.scale)
            elif "Junction" in name:
                print(name, info)
                rect_jj = draw.LineString([np.array(info["start"])*p.scale, np.array(info["end"])*p.scale])
                self.add_qgeometry('junction', dict(rect_jj=rect_jj), width=info["width"]*p.scale, layer=1)