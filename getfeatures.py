#!/usr/bin/env python3
import numpy as np
import open3d as o3d
from scipy import stats
'''
Plans:
    * find the saddle of the nose
    * find the optimal search space for the nose peak
    * find the the top of the head and the bottom of the head determinisitcally
Assumptions:
    * the user made a scan where there is no data being picked up
      in the background
Truths:
    * the forehead is always above the nose
    * the nose is always above the mouth
    * the mouth is always above the chin
    * the chin is the bottom of the face
    * the forehead is the top of the face
    * the saddle of the nose is between the peak of the forehead and the
      peak of the nose
    * the point cloud is referential to the camera
    * the search space for all points is above the tip of the nose
'''


class Dimensions:
    def __init__(self, x, y, z):
        self.x_min = x[0]
        self.x_max = x[1]
        self.y_min = y[0]
        self.y_max = y[1]
        self.z_min = z[0]
        self.z_max = z[1]
        self.x = x
        self.y = y
        self.z = z

    def set_x(self, new_x: tuple):
        self.x = new_x
        self.x_min = new_x[0]
        self.x_max = new_x[1]
        return

    def set_y(self, new_y: tuple):
        self.y = new_y
        self.y_min = new_y[0]
        self.y_max = new_y[1]
        return

    def set_z(self, new_z: tuple):
        self.z = new_z
        self.z_min = new_z[0]
        self.z_max = new_z[1]
        return

    def get_dimensions(self):
        return self.x, self.y, self.z


class Face_Scan:
    def __init__(self, scan_file: str):
        self.pcd = o3d.io.read_point_cloud(scan_file)
        self.ORIGINAL_POINTS = np.asarray(self.pcd.points)
        self.points = self.ORIGINAL_POINTS
        x, y, z = self.get_dimensions()
        self.dim = Dimensions(x, y, z)

    def get_dimensions(self) -> tuple:
        x = self.points[:, 0]
        y = self.points[:, 1]
        z = self.points[:, 2]
        x_dim = (np.min(x), np.max(x))
        y_dim = (np.min(y), np.max(y))
        z_dim = (np.min(z), np.max(z))
        return x_dim, y_dim, z_dim


def get_subspace(points, dim: Dimensions):
    x_mask = (points[:, 0] >= dim.x_min) & (points[:, 0] <= dim.x_max)
    y_mask = (points[:, 1] >= dim.y_min) & (points[:, 1] <= dim.y_max)
    z_mask = (points[:, 2] >= dim.z_min) & (points[:, 2] <= dim.z_max)
    mask = x_mask & y_mask & z_mask
    out = points[mask]
    return out


def find_hill(points):
    z = points[:, 2]
    best_idx = np.argmax(z)
    hill = points[best_idx]
    return hill


def find_valley(points):
    z = points[:, 2]
    best_idx = np.argmin(z)
    valley = points[best_idx]
    return valley


def crop_to_head_simple(pcd):
    points = np.asarray(pcd.points)
    # 1. Find the height limits
    y_min = np.min(points[:, 1])
    y_max = np.max(points[:, 1])
    # 2. Define a cut-off (e.g., keep the top 60% of the scan)
    # This usually safely removes the chest and lower neck
    cut_off = y_min + 0.4 * (y_max - y_min)
    # 3. Apply mask
    mask = points[:, 1] > cut_off
    # 4. Create new cloud
    head_pcd = pcd.select_by_index(np.where(mask)[0])
    return head_pcd


def align_face_to_front(pcd):
    """
    Detects the main plane of the face (cheeks/forehead) and rotates
    the point cloud so that the face points straight at the camera (Z-axis).
    """
    pcd = crop_to_head_simple(pcd)
    plane_model, inliers = pcd.segment_plane(distance_threshold=5.0,
                                             ransac_n=3,
                                             num_iterations=1000)

    [a, b, c, d] = plane_model
    current_normal = np.array([a, b, c])
    target_normal = np.array([0, 0, 1])
    v = np.cross(current_normal, target_normal)
    c_val = np.dot(current_normal, target_normal)
    if np.linalg.norm(v) == 0:
        return pcd

    vx = np.array([[0, -v[2], v[1]],
                   [v[2], 0, -v[0]],
                   [-v[1], v[0], 0]])

    rotation_matrix = np.eye(3) + vx + (vx @ vx) * ((1 - c_val) /
                                                    (np.linalg.norm(v)**2))

    pcd.rotate(rotation_matrix, center=np.array([0, 0, 0]))
    print("Face rotated. New normal aligned to Z.")
    return pcd


def find_hills(face_scan: Face_Scan, prominence: float) -> list:
    '''
    * traverse the point cloud's z values in y order
    '''
    points = get_subspace(face_scan.points, face_scan.dim)

    # find the facial average
    z = points[:, 2]
    face_surface = (stats.mode(z, keepdims=False)).mode
    print(face_surface)

    # sort by y val (descending)
    sorted_indicies = np.argsort(points[:, 1])
    descending_indicies = sorted_indicies[::-1]
    sorted_points = points[descending_indicies]

    hills = []
    hill_size = face_surface
    peaked = (False, [0, 0, 0])

    target = face_surface + prominence

    for point in sorted_points:
        hill_size -= point[2]
        if hill_size <= face_surface and peaked[0]:
            hills.append(peaked[1])
            hill_size = face_surface
            peaked = (False, [0, 0, 0])
        elif hill_size >= target:
            if point[2] > peaked[1][2]:
                peaked = (True, point)
            else:
                peaked = (True, peaked[1])

    return hills


def debug_blob(point, size):
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=size)
    sphere.translate(point)
    sphere.paint_uniform_color([1, 0, 0])

    sphere_pcd = sphere.sample_points_uniformly(number_of_points=500)
    return sphere_pcd


def main():
    # all you need to know is coordinates are ordered (x, y, z):(0, 1, 2)
    # For finding the nose
    y_range = (-2.0, 2.0)

    # For finding all other facial "hills"
    slice_size = 10.0  # percent

    # prominence of z-facing features
    prominence = 1.0  # millimeters

    # Initialization
    face_scan = Face_Scan('./data/liams-face.ply')
    x_axis_size = np.abs(face_scan.dim.x_max) + np.abs(face_scan.dim.x_min)
    slice = float(x_axis_size) * (slice_size / 100.0)

    new_pcd = align_face_to_front(face_scan.pcd)
    o3d.io.write_point_cloud("./data/corrected_face.ply", new_pcd)
    '''
    # find nose tip
    nose_dimensions = Dimensions(face_scan.dim.x, y_range, face_scan.dim.z)
    nose_subspace = get_subspace(face_scan.points, nose_dimensions)
    nose_tip_point = find_hill(nose_subspace)

    # get a subspace of the points that are above the nose tip
    # and the size of the slice_size
    face_scan.dim.set_y((nose_tip_point[1], face_scan.dim.y_max))
    face_scan.dim.set_x((nose_tip_point[0] - (slice / 2.0),
                         nose_tip_point[0] + (slice / 2.0)))

    # find the hills in the x-slice of the z-y plane
    print(f'Search Space: {face_scan.dim.get_dimensions()}')
    print(f'Prominent Features: {find_hills(face_scan, prominence)}')
    # debugging crap
    nose_blob = debug_blob(nose_tip_point, 1)
    debug_pcd = nose_blob
    o3d.io.write_point_cloud("./data/debug_output.ply", debug_pcd)
    '''
    return


if __name__ == "__main__":
    main()
