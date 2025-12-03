#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试复杂路网转换功能
包含曲线路段和交叉口支持
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.parsers.xodr_parser import XODRParser
from src.generators.mesh_generator import MeshGenerator
from src.generators.dae_exporter import DAEExporter
from src.models.material import MaterialLibrary

def test_simple_road():
    """测试简单直路（test.xodr）"""
    print("=" * 60)
    print("测试简单直路 (test.xodr)")
    print("=" * 60)
    
    try:
        parser = XODRParser()
        road_network = parser.parse('../../test.xodr')
        
        print(f"解析成功！")
        print(f"道路数量: {len(road_network.roads)}")
        print(f"交叉口数量: {len(road_network.junctions)}")
        
        # 检查几何类型
        for road in road_network.roads:
            print(f"道路 {road.id}: 包含 {len(road.geometries)} 个几何段")
            for i, geom in enumerate(road.geometries):
                print(f"  几何 {i}: {type(geom).__name__}")
        
        # 生成网格
        material_lib = MaterialLibrary()
        generator = MeshGenerator(material_lib)
        meshes = generator.generate_meshes(road_network, step_size=2.0)
        
        print(f"生成的网格数量: {len(meshes)}")
        for name, mesh in meshes.items():
            print(f"  {name}: {len(mesh.vertices)} 个顶点")
            
        # 导出DAE
        exporter = DAEExporter()
        output_file = "output_test_simple.dae"
        exporter.export(meshes, output_file)
        print(f"DAE文件已导出到: {output_file}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_complex_road():
    """测试复杂路网（map.xodr）"""
    print("\n" + "=" * 60)
    print("测试复杂路网 (map.xodr)")
    print("=" * 60)
    
    try:
        parser = XODRParser()
        road_network = parser.parse('../map.xodr')
        
        print(f"解析成功！")
        print(f"道路数量: {len(road_network.roads)}")
        print(f"交叉口数量: {len(road_network.junctions)}")
        
        # 统计几何类型
        geometry_stats = {}
        total_roads = 0
        curved_roads = 0
        
        for road in road_network.roads[:10]:  # 只显示前10条道路的详细信息
            total_roads += 1
            has_curve = False
            
            print(f"道路 {road.id} ({road.name}): {len(road.geometries)} 个几何段")
            for i, geom in enumerate(road.geometries):
                geom_type = type(geom).__name__
                if geom_type not in geometry_stats:
                    geometry_stats[geom_type] = 0
                geometry_stats[geom_type] += 1
                
                if geom_type != 'LineGeometry':
                    has_curve = True
                
                print(f"  几何 {i}: {geom_type} (长度: {geom.length:.2f}m)")
            
            if has_curve:
                curved_roads += 1
        
        print(f"\n几何类型统计:")
        for geom_type, count in geometry_stats.items():
            print(f"  {geom_type}: {count}")
        
        print(f"\n包含曲线的道路: {curved_roads}/{total_roads}")
        
        # 检查交叉口信息
        for junction in road_network.junctions[:5]:  # 显示前5个交叉口
            print(f"交叉口 {junction.id}: {len(junction.connections)} 个连接")
            for conn in junction.connections:
                print(f"  连接 {conn.id}: {conn.incoming_road} -> {conn.connecting_road}")
        
        # 生成网格（使用更小的步长以处理曲线）
        print(f"\n开始生成网格...")
        material_lib = MaterialLibrary()
        generator = MeshGenerator(material_lib)
        
        # 由于路网较大，只处理前几条道路进行测试
        test_network = type(road_network.road_network if hasattr(road_network, 'road_network') else road_network)()
        test_network.roads = road_network.roads[:5]  # 只取前5条道路
        test_network.junctions = road_network.junctions[:2]  # 只取前2个交叉口
        test_network.header = road_network.header
        
        meshes = generator.generate_meshes(test_network, step_size=1.0)
        
        print(f"生成的网格数量: {len(meshes)}")
        for name, mesh in meshes.items():
            print(f"  {name}: {len(mesh.vertices)} 个顶点")
        
        # 导出DAE
        exporter = DAEExporter()
        output_file = "output_complex_test.dae"
        exporter.export(meshes, output_file)
        print(f"DAE文件已导出到: {output_file}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("OpenDRIVE复杂路网转换测试")
    print("测试曲线路段和交叉口支持功能")
    
    # 测试简单道路
    test_simple_road()
    
    # 测试复杂路网
    test_complex_road()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()