#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
材质模型
"""

from typing import Optional, Dict, List


class Texture:
    """
    纹理类
    """
    
    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path
        self.wrap_s = "repeat"  # S轴纹理环绕方式
        self.wrap_t = "repeat"  # T轴纹理环绕方式
        self.min_filter = "linear_mipmap_linear"  # 缩小过滤方式
        self.mag_filter = "linear"  # 放大过滤方式


class Material:
    """
    材质类
    """
    
    def __init__(self, name: str):
        self.name = name
        self.diffuse_color = (1.0, 1.0, 1.0, 1.0)  # RGBA漫反射颜色
        self.specular_color = (0.0, 0.0, 0.0, 1.0)  # RGBA镜面反射颜色
        self.emission_color = (0.0, 0.0, 0.0, 1.0)  # RGBA自发光颜色
        self.shininess = 0.0  # 光泽度
        self.opacity = 1.0  # 不透明度
        self.diffuse_texture = None  # 漫反射纹理
    
    def set_diffuse_color(self, r: float, g: float, b: float, a: float = 1.0):
        """设置漫反射颜色"""
        self.diffuse_color = (r, g, b, a)
    
    def set_specular_color(self, r: float, g: float, b: float, a: float = 1.0):
        """设置镜面反射颜色"""
        self.specular_color = (r, g, b, a)
    
    def set_emission_color(self, r: float, g: float, b: float, a: float = 1.0):
        """设置自发光颜色"""
        self.emission_color = (r, g, b, a)
    
    def set_shininess(self, shininess: float):
        """设置光泽度"""
        self.shininess = shininess
    
    def set_opacity(self, opacity: float):
        """设置不透明度"""
        self.opacity = opacity
    
    def set_diffuse_texture(self, texture: Texture):
        """设置漫反射纹理"""
        self.diffuse_texture = texture


class MaterialLibrary:
    """
    材质库类，管理多个材质
    """
    
    def __init__(self):
        self.materials: Dict[str, Material] = {}
        self.textures: Dict[str, Texture] = {}
    
    def add_material(self, material: Material):
        """添加材质"""
        self.materials[material.name] = material
    
    def get_material(self, name: str) -> Optional[Material]:
        """获取材质"""
        return self.materials.get(name)
    
    def add_texture(self, texture: Texture):
        """添加纹理"""
        self.textures[texture.name] = texture
    
    def get_texture(self, name: str) -> Optional[Texture]:
        """获取纹理"""
        return self.textures.get(name)
    
    def create_default_materials(self):
        """
        创建默认材质
        """
        # 沥青路面材质
        asphalt = Material("Asphalt")
        asphalt.set_diffuse_color(0.3, 0.3, 0.3, 1.0)
        self.add_material(asphalt)
        
        # 车道线材质 - 白色
        lane_marking_white = Material("LaneMarkingWhite")
        lane_marking_white.set_diffuse_color(1.0, 1.0, 1.0, 1.0)
        self.add_material(lane_marking_white)
        
        # 车道线材质 - 黄色
        lane_marking_yellow = Material("LaneMarkingYellow")
        lane_marking_yellow.set_diffuse_color(1.0, 1.0, 0.0, 1.0)
        self.add_material(lane_marking_yellow)
        
        # 路肩材质
        shoulder = Material("Shoulder")
        shoulder.set_diffuse_color(0.4, 0.4, 0.4, 1.0)
        self.add_material(shoulder)