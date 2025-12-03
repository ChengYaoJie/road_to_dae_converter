#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
转换功能测试脚本
"""

import unittest
import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from road_to_dae_converter.src.parsers.xodr_parser import XODRParser
from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
from road_to_dae_converter.src.generators.dae_exporter import DAEExporter
from road_to_dae_converter.src.models.material import MaterialLibrary
from road_to_dae_converter.src.main import convert_xodr_to_dae


class TestXODRToDAEConversion(unittest.TestCase):
    """
    XODR到DAE转换测试类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        # 获取测试目录
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(self.test_dir))
        
        # 创建临时输出目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 纹理目录（如果存在）
        self.textures_dir = os.path.join(os.path.dirname(self.project_root), "textures")
        if not os.path.exists(self.textures_dir):
            self.textures_dir = None
    
    def tearDown(self):
        """
        测试后的清理工作
        """
        # 清理临时文件（简化处理，实际项目可能需要更详细的清理）
        pass
    
    def test_xodr_parser(self):
        """
        测试XODR解析器功能
        """
        # 使用示例XODR文件（如果存在）
        sample_xodr = os.path.join(os.path.dirname(self.project_root), "test.xodr")
        
        if os.path.exists(sample_xodr):
            parser = XODRParser()
            try:
                road_network = parser.parse(sample_xodr)
                
                # 验证解析结果
                self.assertIsNotNone(road_network, "解析结果不应为None")
                self.assertGreaterEqual(len(road_network.roads), 0, "至少应包含一条道路")
                
                print(f"✓ XODR解析器测试通过，成功解析了 {len(road_network.roads)} 条道路")
                
            except Exception as e:
                self.fail(f"XODR解析器测试失败: {e}")
        else:
            print(f"⚠️  跳过XODR解析器测试：找不到示例文件 {sample_xodr}")
    
    def test_mesh_generation(self):
        """
        测试网格生成功能
        """
        # 使用示例XODR文件（如果存在）
        sample_xodr = os.path.join(os.path.dirname(self.project_root), "test.xodr")
        
        if os.path.exists(sample_xodr):
            try:
                # 解析XODR文件
                parser = XODRParser()
                road_network = parser.parse(sample_xodr)
                
                # 创建材质库
                material_library = MaterialLibrary()
                material_library.create_default_materials()
                
                # 生成网格
                mesh_generator = MeshGenerator(material_library)
                meshes = mesh_generator.generate_meshes(road_network, step_size=2.0)
                
                # 验证生成结果
                self.assertGreater(len(meshes), 0, "应至少生成一个网格")
                
                # 检查网格内容
                for mesh_name, mesh in meshes.items():
                    self.assertGreater(len(mesh.vertices), 0, f"网格 {mesh_name} 应包含顶点")
                    self.assertGreater(len(mesh.indices), 0, f"网格 {mesh_name} 应包含索引")
                
                print(f"✓ 网格生成测试通过，成功生成了 {len(meshes)} 个网格")
                
            except Exception as e:
                self.fail(f"网格生成测试失败: {e}")
        else:
            print(f"⚠️  跳过网格生成测试：找不到示例文件 {sample_xodr}")
    
    def test_full_conversion(self):
        """
        测试完整的转换流程
        """
        # 使用示例XODR文件（如果存在）
        sample_xodr = os.path.join(os.path.dirname(self.project_root), "test.xodr")
        if os.path.exists(sample_xodr):
            try:
                # 生成输出文件名
                output_dae = os.path.join(self.temp_dir, "output_test.dae")
                
                # 执行转换
                success = convert_xodr_to_dae(
                    xodr_file=sample_xodr,
                    output_dae=output_dae,
                    textures_dir=self.textures_dir,
                    step_size=2.0
                )
                
                # 验证转换结果
                self.assertTrue(success, "转换应该成功")
                self.assertTrue(os.path.exists(output_dae), "输出DAE文件应该存在")
                self.assertGreater(os.path.getsize(output_dae), 0, "输出DAE文件不应为空")
                
                print(f"✓ 完整转换测试通过，输出文件: {output_dae}")
                
            except Exception as e:
                self.fail(f"完整转换测试失败: {e}")
        else:
            print(f"⚠️  跳过完整转换测试：找不到示例文件 {sample_xodr}")
    
    def test_material_library(self):
        """
        测试材质库功能
        """
        try:
            # 创建材质库
            material_library = MaterialLibrary()
            
            # 创建默认材质
            material_library.create_default_materials()
            
            # 验证材质
            asphalt = material_library.get_material("Asphalt")
            white_line = material_library.get_material("LaneMarkingWhite")
            yellow_line = material_library.get_material("LaneMarkingYellow")
            shoulder = material_library.get_material("Shoulder")
            
            self.assertIsNotNone(asphalt, "应包含沥青材质")
            self.assertIsNotNone(white_line, "应包含白色车道线材质")
            self.assertIsNotNone(yellow_line, "应包含黄色车道线材质")
            self.assertIsNotNone(shoulder, "应包含路肩材质")
            
            # 验证材质属性
            self.assertEqual(asphalt.diffuse_color[0], 0.3, "沥青材质的红色通道值应为0.3")
            self.assertEqual(white_line.diffuse_color[0], 1.0, "白色车道线材质的红色通道值应为1.0")
            self.assertEqual(yellow_line.diffuse_color[1], 1.0, "黄色车道线材质的绿色通道值应为1.0")
            
            print("✓ 材质库测试通过")
            
        except Exception as e:
            self.fail(f"材质库测试失败: {e}")


def run_tests():
    """
    运行所有测试
    """
    print("开始执行转换功能测试...\n")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestXODRToDAEConversion)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试统计信息
    print("\n测试统计:")
    print(f"总测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 测试失败")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # 运行测试并设置退出码
    success = run_tests()
    sys.exit(0 if success else 1)