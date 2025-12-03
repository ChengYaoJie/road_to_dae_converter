#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的XODR到DAE转换测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import convert_xodr_to_dae

if __name__ == "__main__":
    # 定义文件路径
    xodr_file = r"C:\Users\ChengYaoJie\Desktop\map.xodr"
    output_dae = r"C:\Users\ChengYaoJie\Desktop\map.dae"
    textures_dir = r"C:\Users\ChengYaoJie\Desktop\test"
    
    # 执行转换
    print("=" * 60)
    print("测试 XODR 到 DAE 转换")
    print("=" * 60)
    
    success = convert_xodr_to_dae(
        xodr_file=xodr_file,
        output_dae=output_dae,
        textures_dir=textures_dir,
        step_size=1.0
    )
    
    if success:
        print("\n" + "=" * 60)
        print("转换成功！")
        print(f"输出文件: {output_dae}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("转换失败！")
        print("=" * 60)
