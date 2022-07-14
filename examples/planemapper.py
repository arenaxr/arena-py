from arena import *
import open3d as o3d
import numpy as np

# from numba import jit

DEBUG = False
LISTEN_TOPIC = "realm/s/public/worldmap/#"

meshes = {}


def msg_callback(client, userdata, msg):
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
    vertex_positions = msg.get("vertexPositions")
    triangle_indices = msg.get("triangleIndices")
    vertex_normals = msg.get("vertexNormals")

    # mesh = o3d.geometry.TriangleMesh()
    # np_vertices = np.array([[0.05494517460465431, 2.2637174129486084, 0],
    #                         [0.21290962398052216, 2.2568495273590088, 0],
    #                         [0.9409201145172119, 4.8928432464599609, 0]])
    # np_vertices = np_vertices * 10
    # print(np_vertices)
    # np_triangles = np.array([[0, 1, 2]]).astype(np.int32)
    # np_normals = np.array([[0, 0, -1], [0, 0, -1], [0, 0, -1]])
    #
    # mesh.vertices = o3d.utility.Vector3dVector(np_vertices)
    # mesh.triangles = o3d.utility.Vector3iVector(np_triangles)
    # mesh.vertex_normals = o3d.utility.Vector3dVector(np_normals)
    #
    # mesh.paint_uniform_color(np.random.rand(3))
    # vis.add_geometry(mesh)
    # vis.poll_events()
    # vis.update_renderer()
    # foo = False
    # return

    if action == "create":
        mesh = o3d.geometry.TriangleMesh()

        np_vertices = np.array(list(vertex_positions.values()))
        np_vertices = np.reshape(np_vertices, (-1, 3))
        # np_vertices[:, [2, 1]] = np_vertices[:, [1, 2]]
        mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

        np_triangles = np.array(list(triangle_indices.values())).astype(np.int32)
        np_triangles = np.reshape(np_triangles, (-1, 3))
        mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

        np_normals = np.array(list(vertex_normals.values()))
        np_normals = np.reshape(np_normals, (-1, 3))
        # np_normals[:, [2, 1]] = np_normals[:, [1, 2]]
        mesh.vertex_normals = o3d.utility.Vector3dVector(np_normals)

        mesh.paint_uniform_color(np.random.rand(3))

        meshes[uid] = mesh

        vis.add_geometry(mesh)
        vis.poll_events()
        vis.update_renderer()
        print(len(meshes.items()))

    if action == "update":
        mesh = meshes.get(uid)
        if mesh is None:
            print("Invalid mesh:", uid)
            return

        if vertex_positions:
            np_vertices = np.array(list(vertex_positions.values()))
            np_vertices = np.reshape(np_vertices, (-1, 3))
            # np_vertices[:, [2, 1]] = np_vertices[:, [1, 2]]
            mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

        if triangle_indices:
            np_triangles = np.array(list(triangle_indices.values())).astype(np.int32)
            np_triangles = np.reshape(np_triangles, (-1, 3))
            mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

        if vertex_normals:
            np_normals = np.array(list(vertex_normals.values()))
            np_normals = np.reshape(np_normals, (-1, 3))
            # np_normals[:, [2, 1]] = np_normals[:, [1, 2]]
            mesh.vertex_normals = o3d.utility.Vector3dVector(np_normals)

        mesh.paint_uniform_color(np.random.rand(3))

        vis.update_geometry(mesh)
        vis.poll_events()
        vis.update_renderer()
        print(len(meshes.items()))

    if action == "delete":
        if uid in meshes:
            vis.remove_geometry(meshes[uid])
            del meshes[uid]
            vis.poll_events()
            vis.update_renderer()


scene = Scene(
    host="arena-dev1.conix.io",
    scene="blank",
)

scene.message_callback_add(LISTEN_TOPIC, msg_callback)
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()

scene.run_tasks()

# vis.destroy_window()
# o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Info)
