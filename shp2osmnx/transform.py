import progressbar
import pyproj
import json


def coordinate_transform(geojson, in_crs, out_crs='EPSG:4326'):
    """
    Convert Coordinates to the provided CRS in a GeoJSON object.

    :param geojson: JSON object of the GeoJSON Data
    :param in_crs: CRS of the shapeFile. Should be a string in 'EPSG:{number}' format.
    :param out_crs: CRS to which the coordinates of the geometry in the shapeFile is converted.
    Should be a string in 'EPSG:{number}' format. (Default = 'EPSG:4326')
    :return: JSON object of GeoJSON data
    """
    features = geojson['features']
    result = []
    print('Progress of conversion of CRS')
    size = len(features)
    bar = progressbar.ProgressBar(max_value=size,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.SimpleProgress(),
                                           ' Geometries', ' ', progressbar.Percentage(), ' ',
                                           progressbar.AdaptiveETA()])
    bar.start()
    for feature in features:
        bar.update(features.index(feature))
        properties = feature['properties']
        geometry = feature['geometry']
        converted_points = []
        if geometry['type'] == 'Point':
            point = geometry['coordinates']
            projfrom = pyproj.Proj(init=in_crs)
            projto = pyproj.Proj(init=out_crs)
            point = pyproj.transform(projfrom, projto, point[0], point[1])
            converted_points.append(point)
            converted_geometry = {"type": "Point", "coordinates": converted_points}
        elif geometry['type'] == 'LineString':
            for point in geometry['coordinates']:
                p1 = pyproj.Proj(init=in_crs)
                p2 = pyproj.Proj(init=out_crs)
                point = pyproj.transform(p1, p2, point[0], point[1])
                converted_points.append(point)
            converted_geometry = {"type": "LineString", "coordinates": converted_points}
        elif geometry['type'] == 'MultiLineString':
            for point_group in geometry['coordinates']:
                converted_point_group = []
                for point in point_group:
                    p1 = pyproj.Proj(init=in_crs)
                    p2 = pyproj.Proj(init=out_crs)
                    point = pyproj.transform(p1, p2, point[0], point[1])
                    converted_point_group.append(point)
                converted_points.append(converted_point_group)
            converted_geometry = {"type": "MultiLineString", "coordinates": converted_points}
        elif geometry['type'] == 'Polygon':
            for poly in geometry['coordinates']:
                converted_poly = []
                for point in poly:
                    p1 = pyproj.Proj(init=in_crs)
                    p2 = pyproj.Proj(init=out_crs)
                    point = pyproj.transform(p1, p2, point[0], point[1])
                    converted_poly.append(point)
                converted_points.append(converted_poly)
            converted_geometry = {"type": "Polygon", "coordinates": converted_points}
        else:
            converted_geometry = {"type": "Unknown", "coordinates": {}}
        converted_feature = {"type": "Feature", 'geometry': converted_geometry, 'properties': properties}
        result.append(converted_feature)
    bar.finish()
    return {"type": "FeatureCollection",
            "features": result}


def verify_standard(geojson):
    return


def to_standard(field_names, standards=None):
    """
    Convert Non-Standard Field Names to Standard.

    :param field_names: array of field names.
    :param standards: dict object contain the mapping of non standard field names to standard.
    example = {
        "LINK_ID": "osm_id",
        "DIRONSIGN":"oneway"
    }
    json format Key:Value
    where
        Key is the Field Name from the shapeFile.
        Value is the standard to convert it to.

    :return: array of field names.
    """
    if isinstance(standards, str):
        standards = json.loads(standards)
    standard = standards
    fields = []
    for field in field_names:
        if field in standard:
            field = standard[field]
        fields.append(field)
    return fields
