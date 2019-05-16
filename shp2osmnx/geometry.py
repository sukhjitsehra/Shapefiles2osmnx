def get_geojson(buffer):
    """
    Format GeoJSON from the array object.

    :param buffer: array of features
    :return: JSON object of GeoJSON data
    """
    return {"type": "FeatureCollection",
            "features": buffer}


def node_exist(point, nodes):
    """
    Used to check of a node exist in the array of nodes.

    :param point: longitude and latitude of the node to be queried.
    :param nodes: Array object of the nodes.
    :return: Boolean
        True: if node exist.
        False: of node doesn't exist
    """
    for n in nodes:
        if n['lon'] == point[0] and n['lat'] == point[1]:
            return True
    return False


def find_node(point, nodes):
    """
    Find the node ID of a particular node from the array of nodes.

    :param point: longitude and latitude of the node to be queried.
    :param nodes: Array object of the nodes.
    :return: NodeID of the node being queried.
    """
    for n in nodes:
        if n['lon'] == point[0] and n['lat'] == point[1]:
            return n['id']


def get_node(nodeID, coordinates, properties):
    """
    Create the dict object of the node.

    :param nodeID: NodeID of the node being created.
    :param coordinates: longitude and latitude of the node to be created.
    :param properties: properties/tags of the node to be created.
    :return: dict object of the node.
    """
    return {'lon': coordinates[0],
            'id': nodeID,
            'lat': coordinates[1],
            'tags': properties,
            'type': 'node'}


def get_way(wayID, nodesIndex, properties):
    """
    Create the dict object of the way.

    :param wayID: WayID of the way to be created
    :param nodesIndex: Array of nodes IDs that forms the way.
    :param properties: properties/tags of the way to be created.
    :return: dict object of the way.
    """
    return {'type': 'way',
            'nodes': nodesIndex,
            'id': wayID,
            'tags': properties}


def polygon():
    return {}
