import geopandas as gpd
import osmnx as ox
import progressbar
import shapefile

from .transform import coordinate_transform, to_standard
from .geometry import get_geojson, find_node, node_exist, get_node, get_way

osm_id_field_name = None

# Default standard for some known variations of field names in shapeFile
default_standard = {"LINK_ID": "osm_id",
                    "DIRONSIGN": "oneway",
                    "HIGHWAY_NM": "name",
                    "SUB_TYPE": "highway",
                    "FUNC_CLASS": "highway"}


def shp2geojson(shape_file_path, standards=None):
    """
    Convert ShapeFile to GeoJSON.

    :param shape_file_path: Path of the shapeFile to be converted.
    :param standards: Dict object used to convert non standard properties attributes to standard
    example = {
        "LINK_ID": "osm_id",
        "DIRONSIGN":"oneway"
    }
    json format Key:Value
    where:
        Key is the Field Name from the shapeFile.
        Value is the standard to convert it to.
    See documentation for more.
    :return: JSON object of GeoJSON Data
    """
    reader = shapefile.Reader(shape_file_path)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    if standards is not None:
        field_names = to_standard(field_names, standards=standards)
    buffer = []
    global osm_id_field_name
    if "osm_id" in field_names:
        osm_id_field_name = "osm_id"
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr))
    return get_geojson(buffer)


def geojson2osm_json(geojson):
    """
    Convert GeoJSON to OSM JSON format.

    :param geojson: JSON object of the GeoJSON Data
    :return: JSON object of OSM JSON Data
    """
    features = geojson['features']
    n_index = 0
    nodes = []
    ways = []
    print('Progress of conversion of shapeFile to OSM JSON')
    relations = []
    size = len(features)
    bar = progressbar.ProgressBar(max_value=size,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.SimpleProgress(),
                                           ' Geometries', ' ', progressbar.Percentage(), ' ',
                                           progressbar.AdaptiveETA()])
    bar.start()
    for feature in features:
        # bar.update(features.index(feature))
        properties = feature['properties']
        if 'oneway' in properties:
            if isinstance(properties['oneway'], int):
                properties['oneway'] = str(properties['oneway'])
            elif isinstance(properties['oneway'], str):
                properties['oneway'] = str(properties['oneway']).lower()
        geometry = feature['geometry']
        if geometry['type'] == 'Point':
            bar.update(features.index(feature))
            point = geometry['coordinates']
            if osm_id_field_name is not None:
                osm_id = properties[osm_id_field_name]
            else:
                osm_id = n_index
                n_index += 1
            if not node_exist(point, nodes):
                new_node = get_node(osm_id, point, properties)
                nodes.append(new_node)
            else:
                find_node(point, nodes)  # if nodes exist at that point
        elif geometry['type'] == 'LineString':
            bar.update(features.index(feature))
            nodes_index = []
            for point in geometry['coordinates']:
                if not node_exist(point, nodes):
                    empty_node = get_node(n_index, point, {})  # TODO find properties of new node is not exist
                    nodes_index.append(n_index)
                    n_index += 1
                    nodes.append(empty_node)
                else:
                    nodes_index.append(find_node(point, nodes))
            if osm_id_field_name is not None:
                osm_id = properties[osm_id_field_name]
            else:
                osm_id = n_index
                n_index += 1
            ways.append(get_way(osm_id, nodes_index, properties))
        elif geometry['type'] == 'MultiLineString':
            bar.update(features.index(feature))
            for point_group in geometry['coordinates']:
                nodes_index = []
                for point in point_group:
                    if not node_exist(point, nodes):
                        empty_node = get_node(n_index, point, {})  # TODO find properties of new node is not exist
                        nodes_index.append(n_index)
                        n_index += 1
                        nodes.append(empty_node)
                    else:
                        nodes_index.append(find_node(point, nodes))
                if osm_id_field_name is not None:
                    osm_id = str(properties[osm_id_field_name]) + str(geometry['coordinates'].index(point_group))
                else:
                    osm_id = n_index
                    n_index += 1
                ways.append(get_way(osm_id, nodes_index, properties))
        elif geometry['type'] == 'Polygon':
            bar.update(features.index(feature))
            nodes_index = []
        elif geometry['type'] == 'MultiPolygon':
            bar.update(features.index(feature))
            nodes_index = []
    final = []
    for n in nodes:
        final.append(n)
    for w in ways:
        final.append(w)
    bar.finish()
    return [{'elements': final}]


def gdf_from_shapefile(path, in_crs=None, gdf_name='unnamed', buffer_dist=None):
    """
    Create a GeoDataFrame from a shapeFile.

    :param path: Path of the shapeFile.
    :param in_crs: CRS of the shapeFile. Should be a string in 'EPSG:{number}' format. (Default = 'EPSG:4326')
    :param gdf_name: Name of the GDF to be created.(default = unnamed)
    :param buffer_dist: distance to buffer around the place geometry, in meters. (default = None)
    :return: GeoDataFrame object of the shapeFile.
    """
    geojson = shp2geojson(path)
    if in_crs is not None:
        geojson = coordinate_transform(geojson, in_crs=in_crs)
    features = geojson['features']
    if len(features) > 0:
        gdf = gpd.GeoDataFrame.from_features(features)
        gdf.gdf_name = gdf_name
        gdf.crs = {'init': 'epsg:4326'}
        if buffer_dist is not None:
            gdf_utm = ox.project_gdf(gdf)
            gdf_utm['geometry'] = gdf_utm['geometry'].buffer(buffer_dist)
            gdf = ox.project_gdf(gdf_utm, to_latlong=True)
        return gdf
    else:
        gdf = gpd.GeoDataFrame()
        gdf.gdf_name = gdf_name
        return gdf


def graph_from_shapefile(path, in_crs=None, custom_standards=None, name='unnamed', retain_all=False, simplify=True):
    """
    Create Networkx Graph from the shapeFile provided.

    :param path: Path of the shapeFile.
    :param in_crs: CRS of the shapeFile. Should be a string in 'EPSG:{number}' format. (Default = 'EPSG:4326')
    :param custom_standards: Dict object used to convert non standard properties attributes to standard
    example = {
        "LINK_ID": "osm_id",
        "DIRONSIGN":"oneway"
    }
    json format Key:Value
    where:
        Key is the Field Name from the shapeFile.
        Value is the standard to convert it to.
    See documentation for more.
    :param name: Name of the Graph to be created.(default = unnamed)
    :param retain_all: if True, return the entire graph even if it is not connected
    :param simplify: Simplify the graph. (default = True)
    :return: Networkx MultiDiGraph
    """
    geojson = shp2geojson(path, custom_standards)
    if in_crs is not None:
        geojson = coordinate_transform(geojson, in_crs=in_crs)
    json_data = geojson2osm_json(geojson)
    g = ox.create_graph(json_data, name, retain_all=retain_all)
    if simplify is True:
        g = ox.simplify_graph(g)
    return g
