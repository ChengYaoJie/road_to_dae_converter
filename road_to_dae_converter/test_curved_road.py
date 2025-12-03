#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试曲线道路生成功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.parsers.xodr_parser import XODRParser
from src.generators.mesh_generator import MeshGenerator  
from src.generators.dae_exporter import DAEExporter
from src.models.material import MaterialLibrary
from src.models.geometry import LineGeometry, ArcGeometry, SplineGeometry
from src.models.road_network import RoadNetwork, Road, LaneSection
from src.models.lane import Lane, RoadMark, WidthRecord

def create_test_curved_road():
    """创建一个包含曲线的测试道路"""
    
    # 创建道路网络
    road_network = RoadNetwork()
    
    # 创建一条包含直线和圆弧的道路
    road = Road("test_curve", "Test Curved Road", 150.0, "-1")
    
    # 添加几何：直线 + 圆弧 + 直线
    # 1. 直线段：0-50m
    line1 = LineGeometry(0.0, 0.0, 0.0, 0.0, 50.0)
    road.add_geometry(line1)
    
    # 2. 圆弧段：50-100m，90度左转
    # 起点 (50, 0)，航向角 0，长度 50m，曲率 1/radius
    radius = 50.0 / (3.14159/2)  # 90度圆弧，半径约32m
    curvature = 1.0 / radius
    arc = ArcGeometry(50.0, 50.0, 0.0, 0.0, 50.0, curvature)
    road.add_geometry(arc)
    
    # 3. 直线段：100-150m
    # 起点需要计算圆弧终点位置
    arc_end_x, arc_end_y, arc_end_hdg = arc.get_position(100.0)
    line2 = LineGeometry(100.0, arc_end_x, arc_end_y, arc_end_hdg, 50.0)
    road.add_geometry(line2)
    
    # 创建车道段
    lane_section = LaneSection(0.0, False)
    
    # 创建车道
    # 左侧车道
    left_lane = Lane(1, "driving", False)
    left_lane.add_width_record(WidthRecord(0.0, 3.5, 0.0, 0.0, 0.0))  # 3.5m宽
    left_lane.road_mark = RoadMark(0.0, "solid", 0.125, "standard", "standard", "white", "none")
    lane_section.add_left_lane(left_lane)
    
    # 中心车道
    center_lane = Lane(0, "none", False)
    center_lane.add_width_record(WidthRecord(0.0, 0.0, 0.0, 0.0, 0.0))
    center_lane.road_mark = RoadMark(0.0, "solid solid", 0.125, "standard", "standard", "yellow", "none")
    lane_section.center_lanes = [center_lane]
    
    # 右侧车道
    right_lane = Lane(-1, "driving", False)
    right_lane.add_width_record(WidthRecord(0.0, 3.5, 0.0, 0.0, 0.0))  # 3.5m宽
    right_lane.road_mark = RoadMark(0.0, "solid", 0.125, "standard", "standard", "white", "none")
    lane_section.add_right_lane(right_lane)
    
    road.add_lane_section(lane_section)
    road_network.add_road(road)
    
    return road_network

def test_curved_road_generation():
    """测试曲线道路生成"""
    print("=" * 60)
    print("测试曲线道路生成")
    print("=" * 60)
    
    try:
        # 创建测试道路
        road_network = create_test_curved_road()
        
        print(f"创建道路网络成功")
        print(f"道路数量: {len(road_network.roads)}")
        
        road = road_network.roads[0]
        print(f"道路 {road.id}: 包含 {len(road.geometries)} 个几何段")
        
        for i, geom in enumerate(road.geometries):
            print(f"  几何 {i}: {type(geom).__name__} (长度: {geom.length:.2f}m)")
            if isinstance(geom, ArcGeometry):
                print(f"    曲率: {geom.curvature:.6f}, 半径: {geom.radius:.2f}m")
        
        # 测试几何计算
        print(f"\n几何位置测试:")
        for s in [0, 25, 50, 75, 100, 125, 150]:
            geometry = road.get_geometry_at(s)
            if geometry:
                x, y, hdg = geometry.get_position(s)
                print(f"  s={s:3.0f}m: ({x:6.2f}, {y:6.2f}), hdg={hdg:6.3f}rad ({hdg*180/3.14159:6.1f}°)")
        
        # 生成网格
        print(f"\n开始生成网格...")
        material_lib = MaterialLibrary()
        generator = MeshGenerator(material_lib)
        meshes = generator.generate_meshes(road_network, step_size=1.0)
        
        print(f"生成的网格数量: {len(meshes)}")
        for name, mesh in meshes.items():
            print(f"  {name}: {len(mesh.vertices)} 个顶点")
        
        # 导出DAE
        exporter = DAEExporter()
        output_file = "output_curved_test.dae"
        exporter.export(meshes, output_file)
        print(f"DAE文件已导出到: {output_file}")
        
        print(f"\n测试成功！生成了包含曲线几何的道路网格")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_curved_road_generation()