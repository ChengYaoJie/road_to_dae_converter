#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XODR到DAE转换工具主程序
"""

import argparse
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.parsers.xodr_parser import XODRParser
from src.generators.mesh_generator import MeshGenerator
from src.generators.dae_exporter import DAEExporter
from src.models.material import MaterialLibrary, Texture


def convert_xodr_to_dae(xodr_file: str, output_dae: str, textures_dir: str = None, step_size: float = 1.0):
    """
    将XODR文件转换为DAE文件
    
    Args:
        xodr_file: 输入的XODR文件路径
        output_dae: 输出的DAE文件路径
        textures_dir: 纹理文件夹路径
        step_size: 采样步长，控制生成网格的精度
    
    Returns:
        bool: 转换是否成功
    """
    try:
        print(f"开始转换: {xodr_file} -> {output_dae}")
        
        # 1. 创建材质库并添加默认材质
        material_library = MaterialLibrary()
        material_library.create_default_materials()
        
        # 2. 如果提供了纹理文件夹，尝试加载纹理
        if textures_dir and os.path.exists(textures_dir):
            # 尝试加载沥青路面纹理
            asphalt_texture_file = "Asphalt1_Diff.png"
            if os.path.exists(os.path.join(textures_dir, asphalt_texture_file)):
                asphalt_texture = Texture("AsphaltTexture", asphalt_texture_file)
                material_library.add_texture(asphalt_texture)
                
                # 设置沥青材质使用纹理
                asphalt_material = material_library.get_material("Asphalt")
                if asphalt_material:
                    asphalt_material.set_diffuse_texture(asphalt_texture)
            
            # 尝试加载车道线纹理
            lane_marking_texture_file = "LaneMarking1_Diff.png"
            if os.path.exists(os.path.join(textures_dir, lane_marking_texture_file)):
                lane_marking_texture = Texture("LaneMarkingTexture", lane_marking_texture_file)
                material_library.add_texture(lane_marking_texture)
                
                # 设置车道线材质使用纹理
                white_material = material_library.get_material("LaneMarkingWhite")
                yellow_material = material_library.get_material("LaneMarkingYellow")
                if white_material:
                    white_material.set_diffuse_texture(lane_marking_texture)
                if yellow_material:
                    yellow_material.set_diffuse_texture(lane_marking_texture)
        
        # 3. 解析XODR文件
        print("正在解析XODR文件...")
        parser = XODRParser()
        road_network = parser.parse(xodr_file)
        
        # 4. 生成3D网格
        print("正在生成3D网格...")
        mesh_generator = MeshGenerator(material_library)
        meshes = mesh_generator.generate_meshes(road_network, step_size)
        
        # 5. 导出DAE文件
        print(f"正在导出DAE文件到: {output_dae}")
        exporter = DAEExporter(material_library)
        exporter.export(meshes, output_dae, textures_dir)
        
        print("转换完成！")
        return True
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def main():
    """
    主函数，处理命令行参数
    """
    parser = argparse.ArgumentParser(description='XODR到DAE文件转换工具')
    
    # 必选参数
    parser.add_argument('input', help='输入的XODR文件路径')
    parser.add_argument('output', help='输出的DAE文件路径')
    
    # 可选参数
    parser.add_argument('--textures', '-t', help='纹理文件夹路径', default=None)
    parser.add_argument('--step', '-s', help='采样步长（默认1.0米）', type=float, default=1.0)
    
    # 解析参数
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"错误: 无法创建输出目录: {e}")
            sys.exit(1)
    
    # 执行转换
    success = convert_xodr_to_dae(
        xodr_file=args.input,
        output_dae=args.output,
        textures_dir=args.textures,
        step_size=args.step
    )
    
    # 根据转换结果设置退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()