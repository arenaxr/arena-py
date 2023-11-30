from arena import *
import open3d as o3d
import numpy as np
import msgpack
import json
from scipy.spatial.transform import Rotation as R
from math import radians
import time


DEBUG = False
LISTEN_TOPIC = "realm/proc/debug/+/+/+/meshes"
vis = None
target_mesh = None
target_pcd = None


def msg_callback(_client, _userdata, msg):
    global target_mesh, target_pcd
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
    except ValueError:
        print("bad json data")
        return
    if DEBUG:
        print(payload)
    topic_split = msg.topic.split("/")
    name_scene = "/".join(topic_split[3:5])
    usercam = topic_split[5]
    if target_mesh is None:  # No reference target, make this one the target
        target_mesh = load_mesh_data(payload, write=True, target=True)
        target_pcd = create_pcd(target_mesh, write=True)
        return
    else:
        src_mesh = load_mesh_data(payload, write=True)
        src_pcd = create_pcd(src_mesh)
    src_pcd.paint_uniform_color([1, 0, 0])
    if src_pcd is not None:
        res = icp(src_pcd, target_pcd)
        print("ICP result for", usercam, ":", res.transformation)

        mat = np.copy(res.transformation)
        pos = mat[0:3, 3]
        quat = R.from_matrix(mat[0:3, 0:3]).as_quat()

        pub_topic = f"realm/s/{name_scene}/{usercam}"
        pub_msg = json.dumps(
            {
                "object_id": usercam,
                "action": "update",
                "type": "rig",
                "data": {
                    "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
                    "rotation": {
                        "x": quat[0],
                        "y": quat[1],
                        "z": quat[2],
                        "w": quat[3],
                    },
                },
            }
        )
        scene.mqttc.publish(pub_topic, pub_msg)
        # visualize
        vis.clear_geometries()
        vis.add_geometry(src_pcd)
        vis.add_geometry(target_pcd)
        draw_registration_result(src_pcd, res.transformation)
    else:
        print("invalid mesh data")


def draw_registration_result(source, icp_transform, color=[0, 0, 1]):
    source_transformed = o3d.geometry.PointCloud(source)
    source.transform(icp_transform)
    source.paint_uniform_color(color)
    vis.add_geometry(source_transformed)


def load_mesh_data(mesh_data, write=False, target=False):
    vertices = mesh_data.get("vertices")
    indices = mesh_data.get("indices")
    semanticLabel = mesh_data.get("semanticLabel")
    meshPose = mesh_data.get("meshPose")
    if vertices is None or semanticLabel != "global mesh":
        return None

    mesh = o3d.geometry.TriangleMesh()
    np_vertices = np.array(vertices)
    np_vertices = np.reshape(np_vertices, (-1, 3))
    mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

    np_triangles = np.array(indices).astype(np.int32)
    np_triangles = np.reshape(np_triangles, (-1, 3))
    mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

    mesh.compute_triangle_normals()

    # Comes in as col-major
    np_transform = np.array(list(meshPose.values())).reshape((4, 4), order="F")
    if write:
        np_transform[0, 3] = 0
        np_transform[2, 3] = 0

    mesh.transform(np_transform)

    if write:
        center = mesh.get_center()
        np_transform = np.identity(4)
        np_transform[0, 3] = -center[0]
        np_transform[2, 3] = -center[2]
        mesh.transform(np_transform)

    if write:
        print("Writing global_mesh gltf")
        if target:
            o3d.io.write_triangle_mesh("meshes/global_mesh.gltf", mesh)
        else:
            o3d.io.write_triangle_mesh(
                "meshes/meshes_" + str(int(time.time())) + ".gltf", mesh
            )
    return mesh


def create_pcd(mesh, points=10000, write=False, crop_y=0.5):
    pcd = mesh.sample_points_poisson_disk(
        number_of_points=points, use_triangle_normal=True
    )

    if crop_y > 0:
        aabb = pcd.get_axis_aligned_bounding_box()
        min_bound = np.array(aabb.min_bound)
        max_bound = np.array(aabb.max_bound)
        min_bound[1] += crop_y  # Increase the lower Y-bound
        max_bound[1] -= crop_y  # Decrease the upper Y-bound

        # Crop 0.5m off ceiling and floor
        cropped_aabb = o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
        pcd = pcd.crop(cropped_aabb)

    if write:
        o3d.io.write_point_cloud("target.pcd", pcd)
    return pcd


def rotation_matrix_y(angle_degrees):
    angle_radians = radians(angle_degrees)
    cos_theta = np.cos(angle_radians)
    sin_theta = np.sin(angle_radians)

    return np.array(
        [
            [cos_theta, 0, sin_theta, 0],
            [0, 1, 0, 0],
            [-sin_theta, 0, cos_theta, 0],
            [0, 0, 0, 1],
        ]
    )


def icp(src, target, distance=5, rotations=8):
    src_center = src.get_center()
    target_center = target.get_center()
    init_transform = np.identity(4)
    init_transform[:3, 3] = target_center - src_center

    attempts = []
    # Assuming a square room, try all 4 wall-aligned rotations
    rot_matrix = rotation_matrix_y(360 / rotations)

    for i in range(rotations):
        init_transform = rot_matrix @ init_transform

        res = o3d.pipelines.registration.registration_icp(
            src,
            target,
            max_correspondence_distance=distance,
            init=init_transform,
            estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            # criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=200),
        )
        attempts.append(res)

    return min(attempts, key=lambda x: x.fitness)


scene = Scene(host="arena-dev1.conix.io")
scene.message_callback_add(LISTEN_TOPIC, msg_callback)

# o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
vis = o3d.visualization.Visualizer()
vis.create_window()

print("CUDA:", o3d.core.Device())

if os.path.isfile("target.pcd"):
    print("Loading Target PCD")
    target_pcd = o3d.io.read_point_cloud("target.pcd")
else:
    if os.path.isfile("./meshes/global_mesh.gltf"):
        print("Loading Target Mesh")
        target_mesh = o3d.io.read_triangle_mesh("./meshes/global_mesh.gltf")
    else:
        if os.path.isfile("meshdata.pack"):
            with open("meshdata.pack", "rb") as f:
                print("Loading Target Packed Mesh Data")
                data = msgpack.load(f)
                target_mesh = load_mesh_data(data, write=True, target=True)
    if target_mesh is not None:
        target_pcd = create_pcd(target_mesh, write=True)
    else:
        print("No target mesh found")
        target_pcd = None

if target_pcd is not None:
    target_pcd.paint_uniform_color([0, 1, 0])


# with open("meshdata2.pack", 'rb') as f:
#     data = msgpack.load(f)
#     mesh_src = load_mesh_data(data)
#     src_pcd = create_pcd(mesh_src)
#     src_pcd.paint_uniform_color([1, 0, 0])
#     res = icp(src_pcd, target_pcd)
#     draw_registration_result(src_pcd, target_pcd, res.transformation)
#     origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2)
#     vis.add_geometry(origin)


@scene.run_forever(interval_ms=100)
def update_viz():
    if vis is not None:
        vis.poll_events()
        vis.update_renderer()


scene.run_tasks()
