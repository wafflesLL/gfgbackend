#!/usr/bin/env python3
import numpy as np
import open3d as o3d


def define_search_space(points,
                        x_range,
                        y_range,
                        z_range):
    x_mask = (points[:, 0] >= x_range[0]) & (points[:, 0] <= x_range[1])
    y_mask = (points[:, 1] >= y_range[0]) & (points[:, 1] <= y_range[1])
    z_mask = (points[:, 2] >= z_range[0]) & (points[:, 2] <= z_range[1])
    mask = x_mask & y_mask & z_mask
    out = points[mask]

    return out


def find_closest_point(points):
    z = points[:, 2]

    best_idx = np.argmax(z)

    nose_peak_point = points[best_idx]
    return nose_peak_point


def main():
    x_range = (-5.0, 5.0)
    y_range = (-2.0, 2.0)
    z_range = (-10.0, 0.0)
    pcd = o3d.io.read_point_cloud('./data/liams-face.ply')
    ori_points = np.asarray(pcd.points)
    points = ori_points

    def debug_blob(point, size):
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=size)
        sphere.translate(point)
        sphere.paint_uniform_color([1, 0, 0])

        sphere_pcd = sphere.sample_points_uniformly(number_of_points=500)
        return sphere_pcd

    subspace = define_search_space(points, x_range, y_range, z_range)

    max_range = debug_blob(np.asarray([x_range[1], y_range[1], z_range[1]]),
                           0.5)
    min_range = debug_blob(np.asarray([x_range[0], y_range[0], z_range[0]]),
                           0.5)
    nose_blob = debug_blob(find_closest_point(subspace), 1)

    debug_pcd = max_range + min_range + nose_blob

    o3d.io.write_point_cloud("./data/debug_output.ply", debug_pcd)
    return


if __name__ == "__main__":
    main()
