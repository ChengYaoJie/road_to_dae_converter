#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAE/COLLADA格式导出器
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional
import os

from src.generators.mesh_generator import MeshData
from src.models.material import MaterialLibrary, Material, Texture


class DAEExporter:
    """
    DAE/COLLADA格式导出器
    """
    
    def __init__(self, material_library: Optional[MaterialLibrary] = None):
        self.material_library = material_library or MaterialLibrary()
        self.xml_namespace = {
            'collada': 'http://www.collada.org/2005/11/COLLADASchema'
        }
        # 注册命名空间，确保生成的XML使用正确的前缀
        ET.register_namespace('', 'http://www.collada.org/2005/11/COLLADASchema')
    
    def export(self, meshes: Dict[str, MeshData], output_file: str, textures_dir: Optional[str] = None):
        """
        导出网格数据为DAE文件
        """
        try:
            # 创建COLLADA根元素
            root = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}COLLADA')
            root.set('version', '1.4.1')
            
            # 添加asset元素
            self._add_asset(root)
            
            # 添加library_effects (必须在library_materials之前)
            library_effects = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}library_effects')
            
            # 添加library_images (在library_effects和library_materials之间)
            library_images = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}library_images')
            
            # 添加纹理图像
            for texture_name, texture in self.material_library.textures.items():
                image = ET.SubElement(library_images, '{http://www.collada.org/2005/11/COLLADASchema}image')
                clean_name = texture.file_path.replace('.', '_').replace(' ', '_')
                image.set('id', clean_name)
                image.set('name', clean_name)
                
                init_from = ET.SubElement(image, '{http://www.collada.org/2005/11/COLLADASchema}init_from')
                init_from.text = texture.file_path
            
            # 添加library_materials
            library_materials = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}library_materials')
            
            # 添加材质和效果
            self._add_materials_and_effects(library_materials, library_effects, textures_dir)
            
            # 添加library_geometries
            library_geometries = self._add_library_geometries(root, meshes)
            
            # 添加library_visual_scenes
            library_visual_scenes = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}library_visual_scenes')
            visual_scene_id = self._add_visual_scene(library_visual_scenes, meshes, library_geometries)
            
            # 添加scene
            self._add_scene(root, visual_scene_id)
            
            # 生成格式化的XML字符串
            xml_string = self._prettify_xml(root)
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_string)
            
            print(f"DAE文件已成功导出: {output_file}")
            
        except Exception as e:
            raise ValueError(f"导出DAE文件时发生错误: {e}")
    
    def _add_asset(self, root):
        """
        添加asset元素，包含单位、坐标系等信息
        """
        asset = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}asset')
        
        # 添加contributor
        contributor = ET.SubElement(asset, '{http://www.collada.org/2005/11/COLLADASchema}contributor')
        author = ET.SubElement(contributor, '{http://www.collada.org/2005/11/COLLADASchema}author')
        author.text = 'Road to DAE Converter'
        
        # 添加created
        created = ET.SubElement(asset, '{http://www.collada.org/2005/11/COLLADASchema}created')
        created.text = '2024-01-01T00:00:00Z'  # 简化处理
        
        # 添加modified
        modified = ET.SubElement(asset, '{http://www.collada.org/2005/11/COLLADASchema}modified')
        modified.text = '2024-01-01T00:00:00Z'  # 简化处理
        
        # 添加unit
        unit = ET.SubElement(asset, '{http://www.collada.org/2005/11/COLLADASchema}unit')
        unit.set('name', 'meter')
        unit.set('meter', '1.0')
        
        # 添加up_axis
        up_axis = ET.SubElement(asset, '{http://www.collada.org/2005/11/COLLADASchema}up_axis')
        up_axis.text = 'Z_UP'  # 使用Z轴作为上方向
    
    def _add_library_geometries(self, root, meshes: Dict[str, MeshData]):
        """
        添加library_geometries元素，包含网格数据
        """
        library_geometries = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}library_geometries')
        
        for mesh_name, mesh in meshes.items():
            # 创建geometry元素
            geometry = ET.SubElement(library_geometries, '{http://www.collada.org/2005/11/COLLADASchema}geometry')
            geometry.set('id', f'geometry_{mesh_name}')
            geometry.set('name', mesh_name)
            
            # 创建mesh元素
            mesh_elem = ET.SubElement(geometry, '{http://www.collada.org/2005/11/COLLADASchema}mesh')
            
            # 添加vertices元素
            vertices = ET.SubElement(mesh_elem, '{http://www.collada.org/2005/11/COLLADASchema}vertices')
            vertices.set('id', f'vertices_{mesh_name}')
            
            # 添加input元素到vertices
            input_elem = ET.SubElement(vertices, '{http://www.collada.org/2005/11/COLLADASchema}input')
            input_elem.set('semantic', 'POSITION')
            input_elem.set('source', f'#{mesh_name}-positions')
            
            # 添加position源数据
            self._add_source(mesh_elem, mesh_name, 'positions', 'float_array', 
                           [coord for vertex in mesh.vertices for coord in vertex], 
                           len(mesh.vertices), 3)
            
            # 添加normal源数据
            self._add_source(mesh_elem, mesh_name, 'normals', 'float_array',
                           [coord for normal in mesh.normals for coord in normal],
                           len(mesh.normals), 3)
            
            # 添加texcoord源数据
            self._add_source(mesh_elem, mesh_name, 'texcoords', 'float_array',
                           [coord for texcoord in mesh.tex_coords for coord in texcoord],
                           len(mesh.tex_coords), 2)
            
            # 添加triangles元素
            triangles = ET.SubElement(mesh_elem, '{http://www.collada.org/2005/11/COLLADASchema}triangles')
            triangles.set('material', f'{mesh.material_name}' if mesh.material_name else 'Asphalt')
            triangles.set('count', str(len(mesh.indices) // 3))
            
            # 添加input元素到triangles
            input_position = ET.SubElement(triangles, '{http://www.collada.org/2005/11/COLLADASchema}input')
            input_position.set('semantic', 'VERTEX')
            input_position.set('source', f'#{vertices.get("id")}')
            input_position.set('offset', '0')
            
            input_normal = ET.SubElement(triangles, '{http://www.collada.org/2005/11/COLLADASchema}input')
            input_normal.set('semantic', 'NORMAL')
            input_normal.set('source', f'#{mesh_name}-normals')
            input_normal.set('offset', '0')
            
            input_texcoord = ET.SubElement(triangles, '{http://www.collada.org/2005/11/COLLADASchema}input')
            input_texcoord.set('semantic', 'TEXCOORD')
            input_texcoord.set('source', f'#{mesh_name}-texcoords')
            input_texcoord.set('offset', '0')
            input_texcoord.set('set', '0')
            
            # 添加p元素（三角形索引）
            p = ET.SubElement(triangles, '{http://www.collada.org/2005/11/COLLADASchema}p')
            # 简化：所有输入使用相同的索引
            p.text = ' '.join(map(str, mesh.indices))
        
        return library_geometries
    
    def _add_source(self, parent, mesh_name, source_id, array_type, data, count, stride):
        """
        添加source元素，包含顶点数据、法线数据或纹理坐标数据
        """
        # 创建source元素
        source = ET.SubElement(parent, '{http://www.collada.org/2005/11/COLLADASchema}source')
        source.set('id', f'{mesh_name}-{source_id}')
        
        # 创建float_array元素
        float_array = ET.SubElement(source, '{http://www.collada.org/2005/11/COLLADASchema}float_array')
        float_array.set('id', f'{mesh_name}-{source_id}-array')
        float_array.set('count', str(len(data)))
        float_array.text = ' '.join(map(str, data))
        
        # 创建technique_common元素
        technique_common = ET.SubElement(source, '{http://www.collada.org/2005/11/COLLADASchema}technique_common')
        
        # 创建accessor元素
        accessor = ET.SubElement(technique_common, '{http://www.collada.org/2005/11/COLLADASchema}accessor')
        accessor.set('source', f'#{float_array.get("id")}')
        accessor.set('count', str(count))
        accessor.set('stride', str(stride))
        
        # 根据数据类型添加param元素
        if source_id == 'positions':
            param_names = ['X', 'Y', 'Z']
        elif source_id == 'normals':
            param_names = ['X', 'Y', 'Z']
        elif source_id == 'texcoords':
            param_names = ['S', 'T']
        else:
            param_names = [f'P{i}' for i in range(stride)]
        
        for name in param_names:
            param = ET.SubElement(accessor, '{http://www.collada.org/2005/11/COLLADASchema}param')
            param.set('name', name)
            param.set('type', 'float')
    
    def _add_materials_and_effects(self, library_materials, library_effects, textures_dir: Optional[str]):
        """
        添加材质和效果，参考Blender导出的DAE格式
        """
        for material_name, material in self.material_library.materials.items():
            # 创建effect
            effect = ET.SubElement(library_effects, '{http://www.collada.org/2005/11/COLLADASchema}effect')
            effect_id = f'{material_name}_effect'
            effect.set('id', effect_id)
            
            # 创建profile_COMMON
            profile_common = ET.SubElement(effect, '{http://www.collada.org/2005/11/COLLADASchema}profile_COMMON')
            
            # 如果有纹理，添加newparam
            if material.diffuse_texture and textures_dir:
                clean_name = material.diffuse_texture.file_path.replace('.', '_').replace(' ', '_')
                
                # surface参数
                newparam_surface = ET.SubElement(profile_common, '{http://www.collada.org/2005/11/COLLADASchema}newparam')
                newparam_surface.set('sid', f'{clean_name}-surface')
                surface = ET.SubElement(newparam_surface, '{http://www.collada.org/2005/11/COLLADASchema}surface')
                surface.set('type', '2D')
                init_from = ET.SubElement(surface, '{http://www.collada.org/2005/11/COLLADASchema}init_from')
                init_from.text = clean_name
                
                # sampler参数
                newparam_sampler = ET.SubElement(profile_common, '{http://www.collada.org/2005/11/COLLADASchema}newparam')
                newparam_sampler.set('sid', f'{clean_name}-sampler')
                sampler2d = ET.SubElement(newparam_sampler, '{http://www.collada.org/2005/11/COLLADASchema}sampler2D')
                source = ET.SubElement(sampler2d, '{http://www.collada.org/2005/11/COLLADASchema}source')
                source.text = f'{clean_name}-surface'
            
            # 创建technique (使用lambert着色器)
            technique = ET.SubElement(profile_common, '{http://www.collada.org/2005/11/COLLADASchema}technique')
            technique.set('sid', 'common')
            
            lambert = ET.SubElement(technique, '{http://www.collada.org/2005/11/COLLADASchema}lambert')
            
            # 添加emission
            emission = ET.SubElement(lambert, '{http://www.collada.org/2005/11/COLLADASchema}emission')
            color = ET.SubElement(emission, '{http://www.collada.org/2005/11/COLLADASchema}color')
            color.set('sid', 'emission')
            color.text = ' '.join(map(str, material.emission_color))
            
            # 添加diffuse
            diffuse = ET.SubElement(lambert, '{http://www.collada.org/2005/11/COLLADASchema}diffuse')
            if material.diffuse_texture and textures_dir:
                clean_name = material.diffuse_texture.file_path.replace('.', '_').replace(' ', '_')
                texture = ET.SubElement(diffuse, '{http://www.collada.org/2005/11/COLLADASchema}texture')
                texture.set('texture', f'{clean_name}-sampler')
                texture.set('texcoord', 'diffuse')
            else:
                # 使用纯色
                color = ET.SubElement(diffuse, '{http://www.collada.org/2005/11/COLLADASchema}color')
                color.text = ' '.join(map(str, material.diffuse_color))
            
            # 添加index_of_refraction
            ior = ET.SubElement(lambert, '{http://www.collada.org/2005/11/COLLADASchema}index_of_refraction')
            float_val = ET.SubElement(ior, '{http://www.collada.org/2005/11/COLLADASchema}float')
            float_val.set('sid', 'ior')
            float_val.text = '1.5'
            
            # 创建material
            material_elem = ET.SubElement(library_materials, '{http://www.collada.org/2005/11/COLLADASchema}material')
            material_id = f'{material_name}_material'
            material_elem.set('id', material_id)
            material_elem.set('name', material_name)
            
            # 添加instance_effect
            instance_effect = ET.SubElement(material_elem, '{http://www.collada.org/2005/11/COLLADASchema}instance_effect')
            instance_effect.set('url', f'#{effect_id}')
    
    def _add_visual_scene(self, library_visual_scenes, meshes: Dict[str, MeshData], library_geometries):
        """
        添加visual_scene元素，包含场景结构
        """
        visual_scene = ET.SubElement(library_visual_scenes, '{http://www.collada.org/2005/11/COLLADASchema}visual_scene')
        visual_scene.set('id', 'scene')
        visual_scene.set('name', 'RoadScene')
        
        # 为每个网格创建节点
        for mesh_name, mesh in meshes.items():
            node = ET.SubElement(visual_scene, '{http://www.collada.org/2005/11/COLLADASchema}node')
            node.set('id', f'node_{mesh_name}')
            node.set('name', mesh_name)
            node.set('type', 'NODE')
            
            # 添加instance_geometry
            instance_geometry = ET.SubElement(node, '{http://www.collada.org/2005/11/COLLADASchema}instance_geometry')
            instance_geometry.set('url', f'#geometry_{mesh_name}')
            
            # 添加bind_material
            bind_material = ET.SubElement(instance_geometry, '{http://www.collada.org/2005/11/COLLADASchema}bind_material')
            
            # 添加technique_common
            technique_common = ET.SubElement(bind_material, '{http://www.collada.org/2005/11/COLLADASchema}technique_common')
            
            # 添加instance_material
            instance_material = ET.SubElement(technique_common, '{http://www.collada.org/2005/11/COLLADASchema}instance_material')
            if mesh.material_name and mesh.material_name in self.material_library.materials:
                instance_material.set('symbol', mesh.material_name)
                instance_material.set('target', f'#{mesh.material_name}_material')
                
                # 添加bind_vertex_input
                bind_vertex_input = ET.SubElement(instance_material, '{http://www.collada.org/2005/11/COLLADASchema}bind_vertex_input')
                bind_vertex_input.set('semantic', 'diffuse')
                bind_vertex_input.set('input_semantic', 'TEXCOORD')
                bind_vertex_input.set('input_set', '0')
            else:
                # 使用默认材质
                instance_material.set('symbol', 'default')
                instance_material.set('target', '#Asphalt_material')
        
        return visual_scene.get('id')
    
    def _add_scene(self, root, visual_scene_id):
        """
        添加scene元素，引用visual_scene
        """
        scene = ET.SubElement(root, '{http://www.collada.org/2005/11/COLLADASchema}scene')
        
        # 添加instance_visual_scene
        instance_visual_scene = ET.SubElement(scene, '{http://www.collada.org/2005/11/COLLADASchema}instance_visual_scene')
        instance_visual_scene.set('url', f'#{visual_scene_id}')
    
    def _prettify_xml(self, root):
        """
        格式化XML字符串，使其具有良好的缩进
        """
        # 将ElementTree转换为字符串
        rough_string = ET.tostring(root, 'utf-8')
        
        # 使用minidom进行美化
        reparsed = minidom.parseString(rough_string)
        
        # 返回格式化后的XML字符串
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')