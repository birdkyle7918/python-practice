import datetime
import json
import os
import sys
from typing import Dict

import numpy as np
from scipy.ndimage import label, find_objects
import pyarrow.parquet as pq


# 读取parquet文件
def read_map(mapdata):
    table = pq.read_table(mapdata)
    lons, lats, height = (
        table.column("longitude").to_numpy(),
        table.column("latitude").to_numpy(),
        table.column("elevation").to_numpy(),
    )
    return lons, lats, height


# ======================= 【新增】椭圆包含关系检测和去重 =======================
def is_ellipse_contained(
    ellipse1: Dict[str, float], ellipse2: Dict[str, float]
) -> bool:
    """
    检查椭圆1是否完全被椭圆2包含
    ellipse1: 被检查的椭圆（可能是小椭圆）
    ellipse2: 检查椭圆（可能是大椭圆）
    """
    # 如果椭圆1的面积大于等于椭圆2，则椭圆1不可能被椭圆2包含
    if ellipse1["area"] >= ellipse2["area"]:
        return False

    # 检查椭圆1的边界点是否都在椭圆2内部
    # 采样椭圆1边界上的多个点进行检测
    center1_lon, center1_lat = ellipse1["center_lon"], ellipse1["center_lat"]
    a1, b1 = ellipse1["a_lon"], ellipse1["b_lat"]

    center2_lon, center2_lat = ellipse2["center_lon"], ellipse2["center_lat"]
    a2, b2 = ellipse2["a_lon"], ellipse2["b_lat"]

    # 生成椭圆1边界上的采样点
    angles = np.linspace(0, 2 * np.pi, 36)  # 36个采样点
    boundary_lons = center1_lon + a1 * np.cos(angles)
    boundary_lats = center1_lat + b1 * np.sin(angles)

    # 检查这些边界点是否都在椭圆2内部
    relative_lons = boundary_lons - center2_lon
    relative_lats = boundary_lats - center2_lat
    ellipse2_equation = (relative_lons**2 / a2**2) + (relative_lats**2 / b2**2)

    # 如果所有边界点都在椭圆2内部（<=1），则椭圆1被椭圆2包含
    return np.all(ellipse2_equation <= 1.0)


def get_ellipse_original_points(lons, lats, heights, height_threshold):
    """
    根据高度阈值筛选点，识别这些点形成的离散矩形区域，
    然后为每个矩形计算其外接椭圆，并返回所有被这些椭圆圈选中的原始经度点和纬度点。
    假定lons和lats是网格化的，相同的经度或纬度表示点是连通的。

    参数:
    lons : 经度numpy数组。
    lats : 纬度numpy数组。
    heights : 高度numpy数组。
    height_threshold : 高度阈值。

    返回:
    tuple: 包含两个numpy数组的元组 (lons_in_ellipse_result, lats_in_ellipse_result)。
           lons_in_ellipse_result: 所有被识别出的离散矩形外接椭圆圈选中的原始经度点。
           lats_in_ellipse_result: 所有被识别出的离散矩形外接椭圆圈选中的原始纬度点。
           heights_in_ellipse_result: 所有被识别出的离散矩形外接椭圆圈选中的原始高度。
           如果未找到任何区域，则返回空的numpy数组。
    """

    # 第一步：根据高度阈值筛选经纬度
    above_threshold_indices = np.where(heights > height_threshold)[0]
    lons_above_threshold = lons[above_threshold_indices]
    lats_above_threshold = lats[above_threshold_indices]

    if lons_above_threshold.size == 0:
        print("没有找到高于高度阈值的点。")
        return np.array([]), np.array([])

    # 第二步：识别离散的矩形区域，用二进制表格做的
    unique_lons = np.unique(lons)
    unique_lats = np.unique(lats)

    # 网格大小，行数、列数
    grid_shape = (len(unique_lats), len(unique_lons))

    # 二进制表格，初始默认全是 0
    binary_grid = np.zeros(grid_shape, dtype=int)

    # 定义原始经度、纬度，到二进制表格的映射关系
    lon_to_idx = dict()
    lat_to_idx = dict()
    for i, lon in enumerate(unique_lons):
        lon_to_idx[lon] = i
    for i, lat in enumerate(unique_lats):
        lat_to_idx[lat] = i

    # 将高度高于阈值的二进制格子，值赋为 1
    for i in range(lons_above_threshold.size):
        lon_idx = lon_to_idx[lons_above_threshold[i]]
        lat_idx = lat_to_idx[lats_above_threshold[i]]
        binary_grid[lat_idx, lon_idx] = 1

    # 使用四连通规则，找出二进制表格上所有互相连接的 1 的区域
    four_connectivity_structure = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    labeled_grid, labeled_grid_slice_count = label(
        binary_grid, structure=four_connectivity_structure
    )

    slices = find_objects(labeled_grid)

    # ======================= 【新增】存储椭圆信息的列表 =======================
    ellipse_info_list = []

    # 遍历每个找到的连通组件的切片（即每个离散矩形）
    for temp_slice in slices:
        if temp_slice is None:
            continue

        lat_slice, lon_slice = temp_slice

        # 将网格索引转换回真实的经纬度值，得到矩形的四个边界
        min_lat = unique_lats[lat_slice.start]
        max_lat = unique_lats[lat_slice.stop - 1]

        min_lon = unique_lons[lon_slice.start]
        max_lon = unique_lons[lon_slice.stop - 1]

        # 计算矩形的中心点的值，lon、lat
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2

        # 矩形的宽度和高度
        rectangle_width = max_lat - min_lat
        rectangle_height = max_lon - min_lon

        # 如果范围太大，直接弃用
        if (rectangle_width > 3) or (rectangle_height > 3):
            continue

        if rectangle_width == 0 or rectangle_height == 0:
            continue

        # 椭圆的半长轴，等于矩形的长边除以√2
        a_lon = rectangle_width / np.sqrt(2)

        # 椭圆的半短轴，等于矩形的短边除以√2
        b_lat = rectangle_height / np.sqrt(2)

        # ======================= 【新增】将椭圆信息存储到列表中 =======================
        ellipse_info_dict = {
            "center_lon": center_lon,
            "center_lat": center_lat,
            "a_lon": a_lon,
            "b_lat": b_lat,
            "area": np.pi * a_lon * b_lat,  # 椭圆面积，用于排序
        }
        ellipse_info_list.append(ellipse_info_dict)

    # 按面积从小到大排序，优先检查小椭圆
    ellipse_info_list.sort(key=lambda x: x["area"])

    # 双层循环标记需要保留的有效椭圆
    valid_ellipses = []
    for i, ellipse in enumerate(ellipse_info_list):
        is_contained = False
        # 检查当前椭圆是否被其他椭圆包含
        for j, other_ellipse in enumerate(ellipse_info_list):
            if i != j and is_ellipse_contained(ellipse, other_ellipse):
                is_contained = True
                break
        if not is_contained:
            valid_ellipses.append(ellipse)

    print(f"去重前椭圆数量: {len(ellipse_info_list)}")
    print(f"去重后椭圆数量: {len(valid_ellipses)}")

    # ======================= 【修改】使用去重后的椭圆列表处理原始点 =======================
    # 用于聚合所有被外接圆圈选的原始经度和纬度点和高度
    all_lons_in_ellipse = []
    all_lats_in_ellipse = []
    all_heights_in_ellipse = []

    # 遍历每个有效的椭圆
    for ellipse_info_dict in valid_ellipses:
        center_lon = ellipse_info_dict["center_lon"]
        center_lat = ellipse_info_dict["center_lat"]
        a_lon = ellipse_info_dict["a_lon"]
        b_lat = ellipse_info_dict["b_lat"]

        # 计算所有原始点到椭圆中心的相对坐标
        relative_lons = lons - center_lon
        relative_lats = lats - center_lat

        # 计算椭圆方程的左侧值
        ellipse_equation_lhs = (relative_lons**2 / a_lon**2) + (
            relative_lats**2 / b_lat**2
        )

        # 筛选出距离小于等于椭圆方程左侧值小于等于1的点，也就是在椭圆内的点
        # 同样筛选靠近边界的环带
        condition_1 = ellipse_equation_lhs <= 1.03
        condition_2 = ellipse_equation_lhs >= 0.97
        in_ellipse_indices = np.where(condition_1 & condition_2)[0]

        # 提取被当前圆圈选中的原始经度点和纬度点
        temp_lons_in_ellipse = lons[in_ellipse_indices]
        temp_lats_in_ellipse = lats[in_ellipse_indices]
        temp_heights_in_ellipse = heights[in_ellipse_indices]

        # 添加到总列表中
        all_lons_in_ellipse.extend(temp_lons_in_ellipse)
        all_lats_in_ellipse.extend(temp_lats_in_ellipse)
        all_heights_in_ellipse.extend(temp_heights_in_ellipse)

    # 转变为 numpy array，返回。
    lons_in_ellipse_result = np.array(all_lons_in_ellipse)
    lats_in_ellipse_result = np.array(all_lats_in_ellipse)
    heights_in_ellipse_result = np.array(all_heights_in_ellipse)

    return lons_in_ellipse_result, lats_in_ellipse_result, heights_in_ellipse_result


if __name__ == "__main__":

    # 文件路径
    folder_path = sys.path[0] + "/" + "Input"
    mapdata = folder_path + "/" + "geotiff_coordinates.parquet"

    map_lons, map_lats, map_heights = read_map(mapdata)

    date_str = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")

    for height_threshold in (6000, 5000):
        print(f"现在处理的高度是 {height_threshold}--------------")

        # 获取圈选的坐标数据
        lons_in_shape, lats_in_shape, heights_in_shape = get_ellipse_original_points(
            map_lons, map_lats, map_heights, height_threshold
        )

        display_terrain_list = []
        for lon, lat, height in zip(lons_in_shape, lats_in_shape, heights_in_shape):
            temp_terrain_list = [float(lon), float(lat), float(height)]
            display_terrain_list.append(temp_terrain_list)

        # 创建目录
        path_to_create = file = sys.path[0] + "/" + "Output" + "/" + date_str
        if not os.path.exists(path_to_create):
            os.mkdir(path_to_create)

        # 写入文件
        display_terrain_file = (
            path_to_create
            + "/"
            + "terrain_"
            + str(height_threshold)
            + "m"
            + "_"
            + date_str
            + ".json"
        )
        try:
            with open(display_terrain_file, "w", encoding="utf-8") as f:
                json.dump(display_terrain_list, f, indent=None, separators=(",", ":"))
            print(f"地形数据成功保存为文件 '{display_terrain_file}'")
        except IOError as e:
            print(f"写入文件时发生错误: {e}")
