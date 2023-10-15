import open3d as o3d
import numpy as np
import json
import sys
from random import randint
from random import random


meshes = {}
planes = {}
DEBUG = False

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
vis = o3d.visualization.Visualizer()
vis.create_window()


def process_geometry(msg):
    global vis

    label = msg.get("semanticLabel") + "-" + str(randint(1000, 9999))
    transform = msg.get("meshPose")
    vertex_positions = msg.get("vertices")
    triangle_indices = msg.get("indices")

    mesh = o3d.geometry.TriangleMesh()

    np_vertices = np.array(list(vertex_positions.values()))
    np_vertices = np.reshape(np_vertices, (-1, 3))
    mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

    np_triangles = np.array(list(triangle_indices.values())).astype(np.int32)
    np_triangles = np.reshape(np_triangles, (-1, 3))
    mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

    np_transform = np.array(list(transform.values())).reshape(
        (4, 4), order="F"
    )  # col to row
    mesh.transform(np_transform)

    mesh.compute_triangle_normals()
    # mesh.paint_uniform_color(mesh.triangle_normals[0]/2 + 0.5)
    mesh.paint_uniform_color([random(), random(), random()])

    meshes[label] = mesh

    vis.add_geometry(mesh)
    vis.poll_events()
    vis.update_renderer()
    if DEBUG:
        print(len(meshes.items()))


def process_plane(msg):
    global vis

    label = msg.get("semanticLabel") + "-" + str(randint(1000, 9999))
    transform = msg.get("planePose")
    polygons = msg.get("polygon")

    vertex_positions = [[p["x"], p["y"], p["z"]] for p in polygons]

    triangle_indices = []
    for i in range(2, len(vertex_positions)):
        triangle_indices.append([0, i - 1, i])

    mesh = o3d.geometry.TriangleMesh()

    np_vertices = np.array(vertex_positions)
    mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

    np_triangles = np.array(triangle_indices).astype(np.int32)
    mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

    np_transform = np.array(list(transform.values())).reshape(
        (4, 4), order="F"
    )  # col to row
    mesh.transform(np_transform)

    mesh.compute_triangle_normals()
    mesh.paint_uniform_color([random(), random(), random()])

    planes[label] = mesh

    vis.add_geometry(mesh)
    vis.poll_events()
    vis.update_renderer()
    if DEBUG:
        print(len(planes.items()))


def write_meshes():
    mesh_list = list(meshes.values())
    print("Writing", len(mesh_list), "meshes")
    combined_mesh = o3d.geometry.TriangleMesh()
    i = 0
    for m in mesh_list:
        o3d.io.write_triangle_mesh(
            "meshes/meshes_" + str(i) + ".gltf", m, write_ascii=True
        )
        i += 1
        combined_mesh += m
    o3d.io.write_triangle_mesh("meshes/combined_meshes.gltf", combined_mesh)
    vis.destroy_window()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plane_mesh_mapper.py <json_filename>")
        sys.exit(1)

    json_filename = sys.argv[1]

    with open(json_filename, "r") as f:
        json_content = json.load(f)

    for entry in json_content:
        if entry.get("vertices"):
            if entry.get("semanticLabel") == "global mesh":  # skip or only global mesh
                continue
            process_geometry(entry)
        elif entry.get("polygon"):
            process_plane(entry)

    while True:
        vis.poll_events()
        vis.update_renderer()
