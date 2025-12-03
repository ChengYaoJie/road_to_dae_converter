#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
道路网络数据模型
"""

from typing import List, Dict, Optional
from .geometry import Geometry
from .lane import Lane

# Initialize lane_section to None when Lane instances are created in LaneSection methods
def initialize_lane_reference(lane_section, lane):
    """Set the lane_section reference on a lane"""
    lane.lane_section = lane_section


class Road:
    """
    道路类，表示单条道路
    """
    
    def __init__(self, road_id: str, name: str, length: float, junction: str):
        self.id = road_id
        self.name = name
        self.length = length
        self.junction = junction
        self.geometry = None  # Geometry对象
        self.geometries = []  # 几何列表
        self.lane_sections = []  # 车道段列表
        self.elevation_profile = []  # 高程记录列表
        self.lateral_profile = []  # 车道偏移列表
        
    def add_geometry(self, geometry):
        """
        添加几何对象到道路
        
        Args:
            geometry: 几何对象
        """
        self.geometries.append(geometry)
        
    def add_lane_section(self, lane_section):
        """添加车道段"""
        self.lane_sections.append(lane_section)
    
    def add_elevation_record(self, elevation_record):
        """
        添加高程记录
        
        Args:
            elevation_record: 高程记录对象
        """
        if not self.elevation_profile:
            self.elevation_profile = []
        self.elevation_profile.append(elevation_record)
    
    def add_lane_offset(self, s: float, a: float, b: float, c: float, d: float):
        """
        添加车道偏移信息
        
        Args:
            s: 起点桩号
            a: 常数项
            b: 一次项系数
            c: 二次项系数
            d: 三次项系数
        """
        if not hasattr(self, 'lateral_profile'):
            self.lateral_profile = []
        
        self.lateral_profile.append({
            's': s,
            'a': a,
            'b': b,
            'c': c,
            'd': d
        })
    
    def get_geometry_at(self, s: float):
        """
        根据给定的桩号s获取对应的几何信息
        
        Args:
            s: 桩号
            
        Returns:
            几何信息对象，如果没有找到则返回None
        """
        # 简化实现：返回最后添加的几何信息
        # 实际应用中应该根据s值在geometry列表中查找合适的几何段
        if hasattr(self, 'geometries') and self.geometries:
            # 这里简单返回第一个几何信息
            # 实际应该根据s值找到对应的几何段
            return self.geometries[0]
        return None
    
    def get_elevation_at(self, s: float) -> float:
        """
        根据给定的桩号s获取对应的高程
        
        Args:
            s: 桩号
            
        Returns:
            高程值，如果没有找到则返回0.0
        """
        # 简化实现：返回0.0高程
        # 实际应用中应该根据elevation_profile计算实际高程
        return 0.0
    
    def get_lane_by_id(self, lane_id: int) -> Optional[Lane]:
        """根据ID获取车道"""
        for section in self.lane_sections:
            for lane in section.left_lanes + section.right_lanes + ([section.center_lane] if section.center_lane else []):
                if lane.id == lane_id:
                    return lane
        return None
    
    def generate_mesh(self):
        """生成道路网格"""
        # 这个方法将由转换器模块实现
        pass


class LaneSection:
    """
    车道段类，表示道路的一个车道截面
    """
    def __init__(self, s_offset: float, single_side: bool = False):
        """
        初始化车道段
        
        Args:
            s_offset: 起点桩号
            single_side: 是否为单侧车道
        """
        self.s_offset = s_offset
        self.s = s_offset  # 别名，保持向后兼容
        self.single_side = single_side
        self.left_lanes = []  # 左侧车道列表
        self.center_lane = None  # 中央车道
        self.center_lanes = []  # 兼容用的中央车道列表
        self.right_lanes = []  # 右侧车道列表
        
    def add_left_lane(self, lane: Lane):
        """添加左侧车道"""
        self.left_lanes.append(lane)
    
    def add_right_lane(self, lane: Lane):
        """添加右侧车道"""
        self.right_lanes.append(lane)
    
    def add_center_lane(self, lane: Lane):
        """
        添加中央车道
        
        Args:
            lane: 车道对象
        """
        self.center_lane = lane
        # 添加到兼容用的中央车道列表
        self.center_lanes = [lane]  # 只保留一个中央车道
        # 设置车道段引用
        lane.lane_section = self
    
    # 兼容方法别名
    def set_center_lane(self, lane: Lane):
        """
        设置中央车道(兼容方法)
        """
        self.add_center_lane(lane)
    
    def add_left_lane(self, lane):
        """
        添加左侧车道
        
        Args:
            lane: 车道对象
        """
        self.left_lanes.append(lane)
        # 设置车道段引用
        lane.lane_section = self
    
    def add_right_lane(self, lane):
        """
        添加右侧车道
        
        Args:
            lane: 车道对象
        """
        self.right_lanes.append(lane)
        # 设置车道段引用
        lane.lane_section = self


class RoadNetwork:
    """
    道路网络类，表示完整的道路网络
    """
    
    def __init__(self):
        self.roads = []  # Road对象列表
        self.junctions = []  # Junction对象列表
        self.header = None  # 文件头信息
        
    def add_road(self, road: Road):
        """添加道路"""
        self.roads.append(road)
    
    def add_junction(self, junction):
        """添加交叉口"""
        self.junctions.append(junction)
    
    def get_road_by_id(self, road_id: str) -> Optional[Road]:
        """根据ID获取道路"""
        for road in self.roads:
            if road.id == road_id:
                return road
        return None
    
    def get_junction_by_id(self, junction_id: str):
        """根据ID获取交叉口"""
        for junction in self.junctions:
            if junction.id == junction_id:
                return junction
        return None
    
    def set_header(self, header):
        """设置文件头信息"""
        self.header = header


class ElevationRecord:
    """
    高程记录类
    """
    
    def __init__(self, s: float, a: float, b: float, c: float, d: float):
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d
    
    def get_elevation(self, s_pos: float) -> float:
        """计算指定s位置的高程值"""
        delta_s = s_pos - self.s
        return self.a + self.b * delta_s + self.c * delta_s**2 + self.d * delta_s**3


class Header:
    """
    OpenDRIVE文件头信息
    """
    
    def __init__(self, rev_major: int = 1, rev_minor: int = 4, name: str = "", version: str = "", 
                 north: float = 0.0, south: float = 0.0, east: float = 0.0, west: float = 0.0, vendor: str = ""):
        self.rev_major = rev_major
        self.rev_minor = rev_minor
        self.name = name
        self.version = version
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.vendor = vendor
        self.user_data = None


class Junction:
    """
    交叉口类
    """
    
    def __init__(self, junction_id: str, name: str = "", main_road: str = "", side_road: str = ""):
        self.id = junction_id
        self.name = name
        self.main_road = main_road
        self.side_road = side_road
        self.connections = []  # Connection列表
        
    def add_connection(self, connection):
        """添加连接道路"""
        self.connections.append(connection)


class Connection:
    """
    交叉口连接类
    """
    
    def __init__(self, connection_id: str, incoming_road: str, connecting_road: str, 
                 contact_point: str = "start"):
        self.id = connection_id
        self.incoming_road = incoming_road
        self.connecting_road = connecting_road
        self.contact_point = contact_point  # start, end
        self.lane_links = []  # LaneLink列表
        
    def add_lane_link(self, lane_link):
        """添加车道连接"""
        self.lane_links.append(lane_link)


class LaneLink:
    """
    车道连接类
    """
    
    def __init__(self, from_lane: str, to_lane: str):
        self.from_lane = from_lane
        self.to_lane = to_lane