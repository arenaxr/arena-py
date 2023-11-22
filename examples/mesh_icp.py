from arena import *
import open3d as o3d
import numpy as np


DEBUG = False
LISTEN_TOPIC = "realm/proc/debug/+/+/+/meshes"


def msg_callback(_client, _userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        if payload.get("uid"):
            if DEBUG:
                print(payload)
            src = create_pcd(payload)
            res = icp(src, pcd_target)
            draw_registration_result(src, pcd_target, res.transformation)
            # visualize
    except ValueError:
        print("bad json")
        pass


def draw_registration_result(source, target, icp_transform):
    vis.clear_geometries()
    source_transformed = o3d.geometry.PointCloud(source)
    source.transform(icp_transform)
    source.paint_uniform_color([0, 0, 1])
    vis.add_geometry(source)
    vis.add_geometry(source_transformed)
    vis.add_geometry(target)


def create_pcd(json_data, points=10000, write=False, crop_y=0.5):
    vertices = json_data.get("vertices")
    indices = json_data.get("indices")
    semanticLabel = json_data.get("semanticLabel")
    meshPose = json_data.get("meshPose")
    if vertices is None or semanticLabel != "global mesh":
        return

    mesh = o3d.geometry.TriangleMesh()
    np_vertices = np.array(list(vertices.values()))
    np_vertices = np.reshape(np_vertices, (-1, 3))
    mesh.vertices = o3d.utility.Vector3dVector(np_vertices)

    np_triangles = np.array(list(indices.values())).astype(np.int32)
    np_triangles = np.reshape(np_triangles, (-1, 3))
    mesh.triangles = o3d.utility.Vector3iVector(np_triangles)

    mesh.compute_triangle_normals()

    # Comes in as col-major
    np_transform = np.array(list(meshPose.values())).reshape((4, 4), order="F")
    if write:
        # Reference clouds don't need position offset, just shift XZ to centroid
        # TODO: Assign reference offset/rotation to scene origin?
        center = mesh.get_center()
        np_transform[0, 3] = -center[0]
        np_transform[2, 3] = -center[2]

    mesh.transform(np_transform)

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


def icp(src, target, distance=5):
    rotate_90 = np.identity(4)
    rotate_90[:3, :3] = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])

    src_center = src.get_center()
    target_center = target.get_center()
    init_transform = np.identity(4)
    init_transform[:3, 3] = target_center - src_center

    attempts = []
    # Assuming a square room, try all 4 wall-aligned rotations
    for i in range(4):
        init_transform = init_transform @ rotate_90

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


# scene = Scene()
# scene.message_callback_add(LISTEN_TOPIC, msg_callback)

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
vis = o3d.visualization.Visualizer()
vis.create_window()

print("CUDA:", o3d.core.Device())

if os.path.isfile("target.pcd"):
    pcd_target = o3d.io.read_point_cloud("target.pcd")
else:
    with open("meshdata.json") as f:
        data = json.load(f)
        pcd_target = create_pcd(data, write=True)
pcd_target.paint_uniform_color([0, 1, 0])

with open("meshdata2.json") as f:
    data = json.load(f)
    pcd_src = create_pcd(data)
    pcd_src.paint_uniform_color([1, 0, 0])
    res = icp(pcd_src, pcd_target)
    draw_registration_result(pcd_src, pcd_target, res.transformation)

while True:
    if not vis.poll_events():
        break
    vis.update_renderer()

# scene.run_tasks()
