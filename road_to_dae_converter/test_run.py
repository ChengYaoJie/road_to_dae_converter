#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试脚本 - 用于直接运行XODR到DAE的转换
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import convert_xodr_to_dae


def main():
    """
    主函数，提供简单的测试接口
    """
    print("XODR到DAE转换工具 - 快速测试脚本")
    print("=" * 50)
    
    # 检查是否存在示例文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试找到test.xodr文件
    possible_xodr_paths = [
        os.path.join(current_dir, "test.xodr"),  # 当前目录
        os.path.join(os.path.dirname(current_dir), "test.xodr")  # 上级目录
    ]
    
    xodr_file = None
    for path in possible_xodr_paths:
        if os.path.exists(path):
            xodr_file = path
            break
    
    if not xodr_file:
        print("错误: 找不到test.xodr文件！")
        print("请将XODR文件放在项目根目录或上级目录中。")
        return 1
    
    print(f"找到XODR文件: {xodr_file}")
    
    # 输出DAE文件路径
    output_dae = os.path.join(current_dir, "output_road.dae")
    print(f"输出DAE文件: {output_dae}")
    
    # 纹理目录
    textures_dir = os.path.join(current_dir, "textures")
    if not os.path.exists(textures_dir):
        # 尝试上级目录
        textures_dir = os.path.join(os.path.dirname(current_dir), "textures")
    
    if not os.path.exists(textures_dir):
        textures_dir = None
        print("警告: 未找到纹理文件夹，将使用纯色材质")
    else:
        print(f"纹理文件夹: {textures_dir}")
    
    # 执行转换
    print("\n开始转换...")
    success = convert_xodr_to_dae(
        xodr_file=xodr_file,
        output_dae=output_dae,
        textures_dir=textures_dir,
        step_size=1.0
    )
    
    if success:
        print(f"\n✅ 转换成功！")
        print(f"输出文件: {os.path.abspath(output_dae)}")
        return 0
    else:
        print("\n❌ 转换失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())