from arena import *
import open3d as o3d
import numpy as np
import signal

# from numba import jit

DEBUG = False
LISTEN_TOPIC = "realm/s/public/worldmap/#"

meshes = {}


def msg_callback(_client, _userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        if payload.get("uid"):
            if DEBUG:
                print(payload)
            process_geometry(payload)
    except ValueError:
        print("bad json")
        pass


def process_geometry(msg):
    global vis

    uid = msg.get("uid")
    action = msg.get("action")
    transform = msg.get("modelMatrix")
    vertex_positions = msg.get("vertexPositions")
    triangle_indices = msg.get("triangleIndices")

    if action == "create":
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
        mesh.paint_uniform_color(mesh.triangle_normals[0] / 2 + 0.5)

        meshes[uid] = mesh

        vis.add_geometry(mesh)
        vis.poll_events()
        vis.update_renderer()
        if DEBUG:
            print(len(meshes.items()))

    if action == "update":
        mesh = meshes.get(uid)
        if mesh is None:
            print("Invalid mesh:", uid)
            return

        if vertex_positions:
            np_vertices = np.array(list(vertex_positions.values()))
            np_vertices = np.reshape(np_vertices, (-1, 3))
            mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

        if triangle_indices:
            np_triangles = np.array(list(triangle_indices.values())).astype(np.int32)
            np_triangles = np.reshape(np_triangles, (-1, 3))
            mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

        np_transform = np.array(list(transform.values())).reshape(
            (4, 4), order="F"
        )  # col to row
        mesh.transform(np_transform)

        mesh.compute_triangle_normals()
        mesh.paint_uniform_color(mesh.triangle_normals[0] / 2 + 0.5)

        vis.update_geometry(mesh)
        vis.poll_events()
        vis.update_renderer()
        if DEBUG:
            print(len(meshes.items()))

    if action == "delete":
        if uid in meshes:
            vis.remove_geometry(meshes[uid])
            del meshes[uid]
            vis.poll_events()
            vis.update_renderer()


def write_meshes(scene):
    mesh_list = list(meshes.values())
    print("Writing", len(mesh_list), "meshes")
    combined_mesh = o3d.geometry.TriangleMesh()
    i = 0
    for m in mesh_list:
        o3d.io.write_triangle_mesh(
            "meshes/plane_meshes_" + str(i) + ".gltf", m, write_ascii=True
        )
        i += 1
        combined_mesh += m
    o3d.io.write_triangle_mesh("meshes/combined_plane_meshes.gltf", combined_mesh)
    vis.destroy_window()


scene = Scene(
    host="arena-dev1.conix.io", scene="blank", end_program_callback=write_meshes
)


scene.message_callback_add(LISTEN_TOPIC, msg_callback)
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
vis = o3d.visualization.Visualizer()
vis.create_window()

scene.run_tasks()
