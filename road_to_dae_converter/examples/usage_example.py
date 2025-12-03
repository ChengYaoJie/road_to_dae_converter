#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XODR到DAE转换工具使用示例

这个脚本展示了如何使用road_to_dae_converter库进行XODR文件到DAE文件的转换。
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simple_conversion():
    """
    简单转换示例
    """
    from road_to_dae_converter.src.main import convert_xodr_to_dae
    
    # 输入XODR文件路径
    xodr_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test.xodr")
    
    # 输出DAE文件路径
    output_dae = "output_road.dae"
    
    print(f"开始转换: {xodr_file} -> {output_dae}")
    
    # 执行转换
    success = convert_xodr_to_dae(
        xodr_file=xodr_file,
        output_dae=output_dae,
        step_size=1.0  # 控制网格精度
    )
    
    if success:
        print(f"✅ 转换成功！输出文件: {output_dae}")
    else:
        print("❌ 转换失败！")

def advanced_conversion():
    """
    高级转换示例 - 分步处理
    """
    from road_to_dae_converter.src.parsers.xodr_parser import XODRParser
    from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
    from road_to_dae_converter.src.generators.dae_exporter import DAEExporter
    from road_to_dae_converter.src.models.material import MaterialLibrary
    
    # 输入XODR文件路径
    xodr_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test.xodr")
    
    print("=== 高级转换示例 ===")
    
    # 1. 解析XODR文件
    print(f"1. 解析XODR文件: {xodr_file}")
    parser = XODRParser()
    road_network = parser.parse(xodr_file)
    print(f"   ✓ 成功解析 {len(road_network.roads)} 条道路")
    
    # 2. 创建材质库
    print("2. 创建材质库...")
    material_library = MaterialLibrary()
    material_library.create_default_materials()
    print(f"   ✓ 创建了 {len(material_library.materials)} 种材质")
    
    # 3. 生成网格
    print("3. 生成3D网格...")
    mesh_generator = MeshGenerator(material_library)
    meshes = mesh_generator.generate_meshes(road_network, step_size=0.5)  # 更精细的网格
    print(f"   ✓ 生成了 {len(meshes)} 个网格")
    
    # 统计网格信息
    total_vertices = sum(len(mesh.vertices) for mesh in meshes.values())
    total_indices = sum(len(mesh.indices) for mesh in meshes.values())
    print(f"   - 总顶点数: {total_vertices}")
    print(f"   - 总索引数: {total_indices}")
    
    # 4. 导出DAE文件
    print("4. 导出DAE文件...")
    exporter = DAEExporter()
    output_dae = "advanced_output_road.dae"
    exporter.export_to_dae(meshes, material_library, output_dae)
    print(f"   ✓ 成功导出: {output_dae}")
    
    print("=== 高级转换完成 ===")

def custom_material_conversion():
    """
    自定义材质转换示例
    """
    from road_to_dae_converter.src.parsers.xodr_parser import XODRParser
    from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
    from road_to_dae_converter.src.generators.dae_exporter import DAEExporter
    from road_to_dae_converter.src.models.material import MaterialLibrary, Material
    
    # 输入XODR文件路径
    xodr_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test.xodr")
    
    print("=== 自定义材质转换示例 ===")
    
    # 解析XODR文件
    parser = XODRParser()
    road_network = parser.parse(xodr_file)
    
    # 创建自定义材质库
    print("创建自定义材质库...")
    material_library = MaterialLibrary()
    
    # 添加自定义材质
    asphalt = Material("CustomAsphalt")
    asphalt.diffuse_color = (0.2, 0.2, 0.2)  # 更深的黑色
    asphalt.specular_color = (0.1, 0.1, 0.1)
    asphalt.shininess = 5.0
    
    lane_mark = Material("CustomLaneMark")
    lane_mark.diffuse_color = (1.0, 1.0, 0.8)  # 更亮的白色
    lane_mark.specular_color = (1.0, 1.0, 1.0)
    lane_mark.shininess = 100.0
    
    shoulder = Material("CustomShoulder")
    shoulder.diffuse_color = (0.4, 0.35, 0.25)  # 灰色路肩
    shoulder.specular_color = (0.1, 0.1, 0.1)
    shoulder.shininess = 1.0
    
    # 添加材质到库
    material_library.add_material(asphalt)
    material_library.add_material(lane_mark)
    material_library.add_material(shoulder)
    
    # 更新网格生成器使用的默认材质名称
    # 注意：这需要修改mesh_generator.py中的相应方法，这里仅作示例
    
    print(f"已创建 {len(material_library.materials)} 种自定义材质")
    print("=== 自定义材质转换配置完成 ===")

def main():
    """
    主函数，展示不同的转换示例
    """
    print("XODR到DAE转换工具使用示例\n")
    
    # 检查示例XODR文件是否存在
    xodr_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test.xodr")
    if not os.path.exists(xodr_file):
        print(f"警告: 示例XODR文件不存在: {xodr_file}")
        print("请确保test.xodr文件位于项目根目录下")
        return
    
    try:
        # 运行简单转换示例
        print("【示例1: 简单转换】")
        simple_conversion()
        print()
        
        # 运行高级转换示例
        print("【示例2: 高级分步转换】")
        advanced_conversion()
        print()
        
        # 展示自定义材质配置（不执行完整转换）
        print("【示例3: 自定义材质配置】")
        custom_material_conversion()
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
