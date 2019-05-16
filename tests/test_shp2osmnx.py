from unittest import TestCase

import shp2osmnx
import osmnx as ox


class test_shp2osmnx(TestCase):
    def test_graph_from_shapefile(self):
        g = shp2osmnx.graph_from_shapefile(
            'test.shp',
            custom_standards=shp2osmnx.default_standard, retain_all=True,
            in_crs='EPSG:32643')
        ec = ['r' if data['oneway'] else 'k' for u, v, key, data in g.edges(keys=True, data=True)]
        print(g.edges(keys=True, data=True))
        ox.plot_graph(g, edge_color=ec)
