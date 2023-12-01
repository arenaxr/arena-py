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
target_distance = None


def msg_callback(_client, _userdata, msg):
    """
    Callback for incoming mesh data from pubsub. Will attempt to align incoming source
    mesh to the target pcd using ICP and publish the the resulting transformation
    to the scene topic. If no target pcd has been set, the first incoming mesh will
    be set as the target.
    """
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
    if target_pcd is None:  # No reference target, make this one the target
        print("No target pcd, setting as new target")
        target_mesh = load_mesh_data(payload, write=True, target=True)
        target_pcd = create_pcd(target_mesh, write=True)
        return
    else:  # Create PCD from incoming mesh JSON data. TODO: handle packed binary data
        print("New src mesh data, creating src PCD")
        src_mesh = load_mesh_data(payload, write=True)
        src_pcd = create_pcd(src_mesh)
        src_pcd.paint_uniform_color([1, 0, 0])
    if src_pcd is not None:
        vis.clear_geometries()
        res = icp(src_pcd, target_pcd)
        print(
            "ICP result for",
            usercam,
            ": fitness = ",
            res.fitness,
            ", transform = ",
            res.transformation,
        )

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
        # visualize results
        vis.add_geometry(src_pcd)
        vis.add_geometry(target_pcd)
        draw_registration_result(src_pcd, res.transformation)
    else:
        print("invalid mesh data")


def draw_registration_result(source, icp_transform, uniform_color=None):
    """
    Draws source pcd with ICP solution transform applied
    :param source: source pcd
    :param icp_transform: solution matrix
    :param uniform_color: rendered color of PCD
    """
    if uniform_color is None:
        uniform_color = [0, 0, 1]
    source_transformed = o3d.geometry.PointCloud(source)
    source_transformed.transform(icp_transform)
    source_transformed.paint_uniform_color(uniform_color)
    vis.add_geometry(source_transformed)


def load_mesh_data(mesh_data, write=False, target=False):
    """
    Taking in a mesh data, creates an Open3D TriangleMesh
    Optionally writes the mesh to a gltf file, and/or sets it as the target mesh
    :param mesh_data: mesh data payload dictionary
    :param write: whether to write the mesh to a gltf file
    :param target: whether to set the mesh as the target mesh
    :return: Open3D TriangleMesh
    """
    vertices = mesh_data.get("vertices")
    indices = mesh_data.get("indices")
    semanticLabel = mesh_data.get("semanticLabel")
    meshPose = mesh_data.get("meshPose")
    if vertices is None or semanticLabel != "global mesh":
        return None

    # Build mesh from vertices and indices
    mesh = o3d.geometry.TriangleMesh()
    np_vertices = np.array(vertices)
    np_vertices = np.reshape(np_vertices, (-1, 3))
    mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

    np_triangles = np.array(indices).astype(np.int32)
    np_triangles = np.reshape(np_triangles, (-1, 3))
    mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

    mesh.compute_triangle_normals()

    # Comes in as col-major, apply transform as specified from the meshPose
    np_transform = np.array(list(meshPose.values())).reshape((4, 4), order="F")
    if target:  # When we write target, we throw away translation of the meshPose
        np_transform[0, 3] = 0
        np_transform[2, 3] = 0

    mesh.transform(np_transform)

    if target:  # Also (temporarily) recenter the mesh on origi
        center = mesh.get_center()
        np_transform = np.identity(4)
        np_transform[0, 3] = -center[0]
        np_transform[2, 3] = -center[2]
        mesh.transform(np_transform)
        mesh.compute_triangle_normals()  # Recompute normals after transform

    if write:
        if target:
            print("Writing global_mesh gltf")
            o3d.io.write_triangle_mesh("meshes/global_mesh.glb", mesh)
        else:
            print("Writing mesh gltf")
            o3d.io.write_triangle_mesh(
                "meshes/meshes_" + str(int(time.time())) + ".glb", mesh
            )
    return mesh


def create_pcd(mesh, points=10000, write=False, crop_y=0.5):
    """
    Creates a point cloud from a mesh using poisson disk sampling
    :param mesh: mesh to convert
    :param points: how many points to produce for resuling point cloud
    :param write: whether to write the point cloud to a pcd file
    :param crop_y: how much to crop off the top and bottom of the mesh
    :return: Open3D PointCloud
    """
    pcd = mesh.sample_points_poisson_disk(
        number_of_points=points, use_triangle_normal=True
    )

    if crop_y > 0:  # Cropping floor and ceiling helps remove useless points for ICP
        aabb = pcd.get_axis_aligned_bounding_box()
        min_bound = np.array(aabb.min_bound)
        max_bound = np.array(aabb.max_bound)
        min_bound[1] += crop_y  # Increase the lower Y-bound
        max_bound[1] -= crop_y  # Decrease the upper Y-bound

        # Crop 0.5m off ceiling and floor
        cropped_aabb = o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
        pcd = pcd.crop(cropped_aabb)

    if write:
        print("Writing target.pcd")
        o3d.io.write_point_cloud("target.pcd", pcd)
    return pcd


def rotation_matrix_y(angle_degrees):
    """
    Creates a rotation matrix around the Y axis (only axis that shoudl matter for ICP)
    :param angle_degrees:
    :return: numpy 4x4 transformation matrix
    """
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


def set_target_distance():
    """
    Sets max correspondence distance for ICP based on target mesh size.
    """
    global target_distance
    if target_pcd is not None:
        obb = target_pcd.get_oriented_bounding_box()
        obb_dimensions = obb.extent
        w, h, d = obb_dimensions
        # Factor in surface area of the box with point cloud density
        target_distance = (w * h + w * d + h * d) / (2 * 10000**0.5)
        print("Target distance: ", target_distance)


def icp(src, target, distance=0, rotations=8):
    """
    Given a source and target point cloud, attempts to align the source to the target
    :param src: source point cloud
    :param target: target point cloud
    :param distance: max distance between points to consider a match
    :param rotations: how many sets of iterations to run by subdividing 360 degrees
                      into this many rotated initial transforms
    :return: Open3D registration result
    """
    if distance > 0:
        max_distance = distance
    else:
        if target_distance is None:
            set_target_distance()
        max_distance = target_distance

    # Start by aligning centroids for initial transform position
    src_center = src.get_center()
    target_center = target.get_center()
    init_transform = np.identity(4)
    init_transform[:3, 3] = target_center - src_center

    attempts = []
    rot_matrix = rotation_matrix_y(360 / rotations)

    # Try each rotation as initial transform and take the best result
    for i in range(rotations):
        # Incrementally rotate while preserving translation
        init_transform = rot_matrix @ init_transform

        res = o3d.pipelines.registration.registration_icp(
            src,
            target,
            max_correspondence_distance=max_distance,
            init=init_transform,
            estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            # criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=200),
        )
        attempts.append(res)
        # draw_registration_result(src, res.transformation, uniform_color=[0, 0, res.fitness])

    return min(attempts, key=lambda x: x.fitness)


scene = Scene(host="arena-dev1.conix.io")
scene.message_callback_add(LISTEN_TOPIC, msg_callback)

# o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
vis = o3d.visualization.Visualizer()
vis.create_window()

print("CUDA:", o3d.core.Device())

# Try to load target pcd, or target mesh, or target packed dict data as target pcd
if os.path.isfile("target.pcd"):
    print("Loading Target PCD")
    target_pcd = o3d.io.read_point_cloud("target.pcd")
else:
    if os.path.isfile("./meshes/global_mesh.glb"):
        print("Loading Target Mesh")
        target_mesh = o3d.io.read_triangle_mesh("./meshes/global_mesh.glb")
    else:
        if os.path.isfile("meshdata.pack"):
            with open("meshdata.pack", "rb") as f:
                print("Loading Target Packed Mesh Data")
                data = msgpack.load(f)
                target_mesh = load_mesh_data(data, write=True, target=True)
    if target_mesh is not None:
        target_pcd = create_pcd(target_mesh, write=True)
    else:  # No target mesh or pcd found, message handler sets first incoming as target
        print("No target mesh found")
        target_pcd = None

if target_pcd is not None:
    target_pcd.paint_uniform_color([0, 1, 0])
    vis.add_geometry(target_pcd)
    axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2)
    vis.add_geometry(axis)


# Test manually with input file
# with open("meshdata2.pack", 'rb') as f:
#     data = msgpack.load(f)
#     mesh_src = load_mesh_data(data)
#     src_pcd = create_pcd(mesh_src)
#     src_pcd.paint_uniform_color([1, 0, 0])
#     res = icp(src_pcd, target_pcd)
#     draw_registration_result(src_pcd, res.transformation)


# src_mesh = o3d.io.read_triangle_mesh("./meshes/meshes_1701379498.glb")
# src_pcd = create_pcd(src_mesh)
# src_pcd.paint_uniform_color([1, 0, 0])
# res = icp(src_pcd, target_pcd)
# print(res.transformation)
# draw_registration_result(src_pcd, res.transformation)


# Update loop for visualization
@scene.run_forever(interval_ms=50)
def update_viz():
    if vis is not None:
        vis.poll_events()
        vis.update_renderer()


scene.run_tasks()
