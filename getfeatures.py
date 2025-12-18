#!/usr/bin/env python3
import numpy as np
import open3d as o3d
from scipy.signal import find_peaks


def find_nose_tip(points, prominence=5.0, width=10.0):
    z = points[:, 2]

    peaks, properties = find_peaks(z, prominence=prominence, width=width)

    if len(peaks) == 0:
        print("No distinct nose bump was found (Face might be very flat)")
        return None, None

    best_idx = np.argmax(properties['prominences'])
    peak_index = peaks[best_idx]

    idx_start = int(properties['left_ips'][best_idx])
    idx_end = int(properties['right_ips'][best_idx])

    nose_peak_point = points[peak_index]
    y_start = points[idx_start, 1]
    y_end = points[idx_end, 1]

    print(f"Nose found between Y={y_start:.1f} and Y={y_end:.1f}")

    return nose_peak_point, (y_start, y_end)


def main():
    pcd = o3d.io.read_point_cloud('./data/liams-face.ply')
    ori_points = np.asarray(pcd.points)
    points = ori_points

    nose_peak, nose_range = find_nose_tip(points, prominence=5.0, width=5.0)
    mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1)
    mesh_sphere.translate(nose_peak)
    mesh_sphere.paint_uniform_color([1, 0, 0])

    sphere_pcd = mesh_sphere.sample_points_uniformly(number_of_points=500)
    o3d.io.write_point_cloud("./data/debug_output.ply", sphere_pcd)

    return


if __name__ == "__main__":
    main()
