#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
转换功能验证脚本

这个脚本提供更详细的XODR到DAE转换验证，包括：
- 命令行参数支持
- 详细的转换过程日志
- 输出文件有效性检查
- 生成网格的统计信息
"""

import os
import sys
import argparse
import logging
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from road_to_dae_converter.src.main import convert_xodr_to_dae
from road_to_dae_converter.src.parsers.xodr_parser import XODRParser
from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
from road_to_dae_converter.src.models.material import MaterialLibrary

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('verify_conversion')

def verify_xodr_to_dae_conversion(xodr_file, output_dae, textures_dir=None, step_size=1.0):
    """
    验证XODR到DAE的转换过程
    
    Args:
        xodr_file: 输入的XODR文件路径
        output_dae: 输出的DAE文件路径
        textures_dir: 纹理目录路径（可选）
        step_size: 网格生成的步长
    
    Returns:
        bool: 转换是否成功
    """
    start_time = time.time()
    
    try:
        # 1. 验证输入文件
        if not os.path.exists(xodr_file):
            logger.error(f"输入文件不存在: {xodr_file}")
            return False
        
        logger.info(f"开始验证转换: {xodr_file} -> {output_dae}")
        
        # 2. 单独验证XODR解析
        logger.info("验证XODR解析...")
        parser = XODRParser()
        road_network = parser.parse(xodr_file)
        
        # 统计道路信息
        num_roads = len(road_network.roads)
        logger.info(f"成功解析 {num_roads} 条道路")
        
        for i, road in enumerate(road_network.roads):
            num_lane_sections = len(road.lane_sections)
            total_lanes = 0
            
            for lane_section in road.lane_sections:
                total_lanes += len(lane_section.left_lanes) + len(lane_section.right_lanes) + len(lane_section.center_lanes)
            
            logger.info(f"  道路 {road.id}: {num_lane_sections} 个车道段, {total_lanes} 个车道")
        
        # 3. 单独验证网格生成
        logger.info("验证网格生成...")
        material_library = MaterialLibrary()
        material_library.create_default_materials()
        
        mesh_generator = MeshGenerator(material_library)
        meshes = mesh_generator.generate_meshes(road_network, step_size=step_size)
        
        # 统计网格信息
        logger.info(f"成功生成 {len(meshes)} 个网格")
        
        total_vertices = 0
        total_indices = 0
        mesh_types = {}
        
        for mesh_name, mesh in meshes.items():
            total_vertices += len(mesh.vertices)
            total_indices += len(mesh.indices)
            
            # 统计网格类型
            if "mark" in mesh_name:
                mesh_type = "车道线"
            elif "lane" in mesh_name:
                mesh_type = "车道"
            else:
                mesh_type = "其他"
            
            mesh_types[mesh_type] = mesh_types.get(mesh_type, 0) + 1
            logger.info(f"  网格 {mesh_name}: {len(mesh.vertices)} 顶点, {len(mesh.indices)} 索引, 材质: {mesh.material_name}")
        
        # 输出网格类型统计
        logger.info("网格类型统计:")
        for mesh_type, count in mesh_types.items():
            logger.info(f"  {mesh_type}: {count} 个")
        
        logger.info(f"总顶点数: {total_vertices}")
        logger.info(f"总索引数: {total_indices}")
        
        # 4. 执行完整转换
        logger.info("执行完整转换...")
        success = convert_xodr_to_dae(
            xodr_file=xodr_file,
            output_dae=output_dae,
            textures_dir=textures_dir,
            step_size=step_size
        )
        
        if not success:
            logger.error("转换失败")
            return False
        
        # 5. 验证输出文件
        if not os.path.exists(output_dae):
            logger.error(f"输出文件未生成: {output_dae}")
            return False
        
        output_size = os.path.getsize(output_dae)
        logger.info(f"输出文件已生成: {output_dae} (大小: {output_size/1024:.2f} KB)")
        
        # 检查文件内容（简单检查）
        with open(output_dae, 'r', encoding='utf-8') as f:
            content = f.read(100)  # 只读取前100个字符
            if "COLLADA" not in content:
                logger.warning("输出文件可能不是有效的COLLADA文件，未找到COLLADA标记")
            else:
                logger.info("输出文件包含COLLADA标记")
        
        end_time = time.time()
        logger.info(f"验证完成！总耗时: {end_time - start_time:.2f} 秒")
        
        return True
        
    except Exception as e:
        logger.error(f"验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    主函数，处理命令行参数并执行验证
    """
    parser = argparse.ArgumentParser(description='验证XODR到DAE的转换功能')
    parser.add_argument('--xodr', type=str, required=True, help='输入的XODR文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出的DAE文件路径')
    parser.add_argument('--textures', type=str, default=None, help='纹理目录路径')
    parser.add_argument('--step-size', type=float, default=1.0, help='网格生成的步长（默认: 1.0）')
    parser.add_argument('--verbose', action='store_true', help='显示详细日志')
    
    args = parser.parse_args()
    
    # 如果启用详细日志
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"创建输出目录: {output_dir}")
    
    # 执行验证
    success = verify_xodr_to_dae_conversion(
        xodr_file=args.xodr,
        output_dae=args.output,
        textures_dir=args.textures,
        step_size=args.step_size
    )
    
    # 设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
