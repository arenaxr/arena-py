from arena import *
import open3d as o3d
import numpy as np
import msgpack
import json
from scipy.spatial.transform import Rotation as R
import time


DEBUG = False  # Enable open3d debug messages, including ICP iteration details
VISUALIZE = False  # Enable visualization of incoming meshes and ICP results
SAVE_MESHES = True  # Enable saving of incoming meshes to gltf files
MIN_FITNESS_THRESHOLD = 0.9  # TODO: figure out cutoff for "wrong room mesh"
USE_CUDA = False  # Enable CUDA acceleration. Requires CUDA GPU, build o3d from source

vis = None
target_mesh = None
target_pcd = None
target_pcd_cuda = None
target_distance = None
cuda_device = o3d.core.Device("CUDA:0")


# This removes artificial boundary box created in Quest3 room meshes
QUEST_CROP = 0.06
QUEST_Y_CROP = 0.25


def filter_registration_results(results, threshold=1):
    filtered_results = []
    for result in results:
        if USE_CUDA:
            transformation_matrix = result.transformation.cpu().numpy()
        else:
            transformation_matrix = result.transformation
        rotation_matrix = np.array(transformation_matrix[:3, :3])
        rot = R.from_matrix(rotation_matrix)
        euler_angles = rot.as_euler("xyz", degrees=True)
        x_rotation, _, z_rotation = abs(euler_angles)
        if (180 - threshold) > abs(x_rotation) > threshold:
            continue
        if (180 - threshold) > abs(z_rotation) > threshold:
            continue
        filtered_results.append(result)
    print(f"Filtered out {len(results) - len(filtered_results)} results")
    return filtered_results


def msg_callback(_client, _userdata, msg):
    """
    Callback for incoming mesh data from pubsub. Will attempt to align incoming source
    mesh to the target pcd using ICP and publish the resulting transformation
    to the scene topic. If no target pcd has been set, the first incoming mesh will
    be set as the target.
    """
    global target_mesh, target_pcd, target_pcd_cuda
    src_pcd_cuda = None

    try:
        payload = msgpack.unpackb(msg.payload)
    except Exception:
        print("ignoring non-msgpack data")
        return
    topic_split = msg.topic.split("/")
    name_scene = "/".join(topic_split[2:4])
    usercam = topic_split[4]
    if target_pcd is None:  # No reference target, make this one the target
        print("No target pcd, setting as new target")
        target_mesh = load_mesh_data(payload, write=True, target=True)
        target_pcd = create_pcd(target_mesh, write=True)
        if USE_CUDA:
            target_pcd_cuda = o3d.t.geometry.PointCloud().from_legacy(target_pcd)
        return
    else:  # Create PCD from incoming mesh JSON data.
        print("New src mesh data, creating src PCD")
        src_mesh = load_mesh_data(payload, write=SAVE_MESHES)
        src_pcd = create_pcd(src_mesh)
        src_pcd.paint_uniform_color([1, 0, 0])
        if USE_CUDA:
            src_pcd_cuda = o3d.t.geometry.PointCloud().from_legacy(src_pcd)
    if src_pcd is not None:
        if vis is not None:
            vis.clear_geometries()
        start_time = time.time()
        if USE_CUDA:
            res = icp(src_pcd_cuda, target_pcd_cuda)
        else:
            res = icp(src_pcd, target_pcd)
        print(
            "Execution time: ",
            time.time() - start_time,
            ". ICP result for",
            usercam,
            ": fitness:",
            res.fitness,
            ", inlier_rmse:",
            res.inlier_rmse,
            ", transform:\n",
            res.transformation,
        )

        if res.fitness < MIN_FITNESS_THRESHOLD:
            print("ICP fitness too low, ignoring")
            return

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
        if vis is not None:
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
    if vis is None:
        return
    if uniform_color is None:
        uniform_color = [0, 0, 1]
    if USE_CUDA:
        source_transformed = source.to_legacy()
        if icp_transform.cpu is not None:
            icp_transform = icp_transform.cpu().numpy()
    else:
        source_transformed = o3d.geometry.PointCloud(source)
    source_transformed.transform(icp_transform)
    source_transformed.paint_uniform_color(uniform_color)
    vis.add_geometry(source_transformed)


def load_mesh_data(mesh_data, write=False, target=False):
    """
    Taking in a mesh data, creates an Open3D TriangleMesh
    Optionally writes the mesh to a gltf file, and/or sets it as the target mesh
    :param dict mesh_data: mesh data payload dictionary
    :param bool write: whether to write the mesh to a gltf file
    :param bool target: whether to set the mesh as the target mesh
    :return open: Open3D TriangleMesh
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

    # Comes in as col-major, apply transform as specified from the meshPose
    np_transform = np.array(meshPose).reshape((4, 4), order="F")
    mesh.transform(np_transform)

    if target:  # Also recenter the mesh on origin
        center = mesh.get_center()
        mesh.translate([-center[0], 0, -center[2]])

    mesh.compute_triangle_normals()
    mesh.compute_vertex_normals()

    if write:
        if target:
            print("Writing global_mesh gltf")
            o3d.io.write_triangle_mesh("meshes/global_mesh.glb", mesh)
        else:
            # Hash filename based on vertices, indices, and y-rotation/yaw of meshPose
            v = len(vertices)
            i = len(indices)
            filename = f"meshes/mesh_{v}_{i}.glb"
            print("Writing mesh gltf")
            o3d.io.write_triangle_mesh(filename, mesh)
    return mesh


def create_pcd(mesh, point_density=100, write=False, crop_bounds=QUEST_Y_CROP):
    """
    Creates a point cloud from a mesh using poisson disk sampling
    :param mesh: mesh to convert
    :param int point_density: How many points per square meter of surface area
    :param bool write: whether to write the point cloud to a pcd file
    :param float crop_bounds: how much to crop off the bounding box on all sides
    :return: Open3D PointCloud
    """
    area = mesh.get_surface_area()
    points = int(area * point_density)
    start = time.time()
    pcd = mesh.sample_points_poisson_disk(
        number_of_points=points, use_triangle_normal=True, init_factor=5
    )
    print("Poisson disk sampling time: ", time.time() - start)
    distances = pcd.compute_nearest_neighbor_distance()
    # Calculate standard deviation of distances
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    print("Mean distance: ", mean_dist, "std deviation: ", std_dist)

    if crop_bounds > 0:
        # obb = pcd.get_minimal_oriented_bounding_box(robust=True)
        # pcd.rotate(np.linalg.inv(obb.R))
        aabb = pcd.get_axis_aligned_bounding_box()
        min_bound = np.array(aabb.min_bound)
        max_bound = np.array(aabb.max_bound)
        min_bound[1] += crop_bounds
        max_bound[1] -= crop_bounds
        aabb.min_bound = min_bound
        aabb.max_bound = max_bound
        pcd = pcd.crop(aabb)
        # pcd.rotate(obb.R)

    if write:
        print("Writing target.pcd")
        o3d.io.write_point_cloud("target.pcd", pcd)
    print("PCD creation time: ", time.time() - start, "total points: ", len(pcd.points))
    return pcd


def rotation_matrix_y(angle_degrees):
    """
    Creates a rotation matrix around the Y axis (only axis that should matter for ICP)
    :param float angle_degrees:
    :return: numpy 4x4 transformation matrix
    """
    angle_radians = np.deg2rad(angle_degrees)
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
        target_dims = target_pcd.get_axis_aligned_bounding_box().get_extent()
        target_distance = np.linalg.norm(target_dims) / 2
        if USE_CUDA:
            target_distance = target_distance.item()
        print("Target distance: ", target_distance)


def icp(src, target, distance=0, rotations=12):
    """
    Given a source and target point cloud, attempts to align the source to the target
    :param src: source point cloud
    :param target: target point cloud
    :param float distance: max distance between points to consider a match
    :param int rotations: how many sets of iterations to run by subdividing 360 degrees
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
    if USE_CUDA:
        src_center = src.get_center().numpy()
        target_center = target.get_center().numpy()
    else:
        src_center = src.get_center()
        target_center = target.get_center()
    init_transform = np.identity(4)
    init_transform[:3, 3] = target_center - src_center

    if USE_CUDA:
        # Move to CUDA device
        src = src.cuda(0)
        target = target.cuda(0)

    attempts = []
    rot_matrix = rotation_matrix_y(360 / rotations)

    # Tukey loss function for robustness
    sigma = 200 / 1000
    if not USE_CUDA:
        loss = o3d.pipelines.registration.TukeyLoss(k=sigma)
        p2pl = o3d.pipelines.registration.TransformationEstimationPointToPlane(loss)

    # Try each rotation as initial transform and take the best result
    for i in range(rotations):
        # Incrementally rotate while preserving translation
        init_transform = rot_matrix @ init_transform
        if USE_CUDA:
            init_transform_cuda = o3d.core.Tensor(
                init_transform, dtype=o3d.core.Dtype.Float64
            )
            res = o3d.t.pipelines.registration.icp(
                src,
                target,
                max_correspondence_distance=max_distance,
                init_source_to_target=init_transform_cuda,
                estimation_method=o3d.t.pipelines.registration.TransformationEstimationPointToPlane(),
                criteria=o3d.t.pipelines.registration.ICPConvergenceCriteria(
                    max_iteration=100
                ),
            )
        else:
            res = o3d.pipelines.registration.registration_icp(
                src,
                target,
                max_correspondence_distance=max_distance,
                init=init_transform,
                estimation_method=p2pl,
                criteria=o3d.pipelines.registration.ICPConvergenceCriteria(
                    max_iteration=100
                ),
            )
        attempts.append(res)
        # draw_registration_result(src, res.transformation, uniform_color=[0, 0, res.fitness])

    attempts = filter_registration_results(attempts)
    if len(attempts) == 0:
        res = o3d.pipelines.registration.RegistrationResult()
        res.fitness = 0
        res.inlier_rmse = 0
        res.transformation = np.identity(4)
        return res
    # Handle ties for maxed fitness by lowest inlier_rmse
    max_fitness = max(attempts, key=lambda x: x.fitness).fitness
    matches = [x for x in attempts if x.fitness == max_fitness]
    return min(matches, key=lambda x: x.inlier_rmse)


scene = Scene(namespace="public", scene="arena", environment=True)
LISTEN_TOPIC = topics.SUBSCRIBE_TOPICS.SCENE_ENV_PRIVATE.substitute(
    realm="realm",
    nameSpace=scene.namespace,
    sceneName=scene.scene,
    idTag="-",
    userClient="+",
)
scene.message_callback_add(LISTEN_TOPIC, msg_callback)

if DEBUG:
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
if VISUALIZE:
    vis = o3d.visualization.Visualizer()
    vis.create_window()

# Try to load target pcd, or target mesh, or target packed dict data as target pcd
if os.path.isfile("target.pcd"):
    print("Loading Target PCD")
    target_pcd = o3d.io.read_point_cloud("target.pcd")
else:
    if os.path.isfile("./meshes/global_mesh.glb"):
        print("Loading Target Mesh")
        target_mesh = o3d.io.read_triangle_mesh("./meshes/global_mesh.glb")
        target_mesh.compute_triangle_normals()
        target_mesh.compute_vertex_normals()
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
    if vis is not None:
        vis.add_geometry(target_pcd)
        axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2)
        vis.add_geometry(axis)
    if USE_CUDA:
        target_pcd_cuda = o3d.t.geometry.PointCloud().from_legacy(target_pcd)


# Test manually with input file
# with open("meshdata2.pack", 'rb') as f:
#     data = msgpack.load(f)
#     mesh_src = load_mesh_data(data, write=True)
#     src_pcd = create_pcd(mesh_src)
#     src_pcd.paint_uniform_color([1, 0, 0])
#     res = icp(src_pcd, target_pcd)
#     print("ICP fitness: ", res.fitness, ", transform:", res.transformation)
#     draw_registration_result(src_pcd, res.transformation)

# start = time.time()
# src_mesh = o3d.io.read_triangle_mesh("./meshes/mesh_77043_155502.glb")
# if not src_mesh.has_triangle_normals():
#     src_mesh.compute_triangle_normals()
# if not src_mesh.has_vertex_normals():
#     src_mesh.compute_vertex_normals()
# src_pcd = create_pcd(src_mesh, point_density=200)
# # o3d.io.write_point_cloud("src.pcd", src_pcd)
#
# # src_pcd = o3d.io.read_point_cloud("src.pcd")
# RANDOM_ROTATE = -50
# if RANDOM_ROTATE:
#     src_pcd.rotate(rotation_matrix_y(RANDOM_ROTATE)[:3, :3])
# src_pcd.paint_uniform_color([1, 0, 0])
# vis.add_geometry(src_pcd)
# if USE_CUDA:
#     src_pcd = o3d.t.geometry.PointCloud().from_legacy(src_pcd)
#     target_pcd = target_pcd_cuda
# start_time = time.time()
# res = icp(src_pcd, target_pcd)
# print(
#     "Execution time:",
#     time.time() - start_time,
#     ", fitness:",
#     res.fitness,
#     ", inlier_rmse:",
#     res.inlier_rmse,
#     ", transform:\n",
#     res.transformation,
# )
# draw_registration_result(src_pcd, res.transformation)


# Update loop for visualization
@scene.run_forever(interval_ms=50)
def update_viz():
    if vis is not None:
        vis.poll_events()
        vis.update_renderer()


scene.run_tasks()
