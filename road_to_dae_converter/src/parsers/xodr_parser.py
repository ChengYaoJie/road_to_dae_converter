#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XODR文件解析器
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple
import math

from src.models.road_network import RoadNetwork, Road, Header, ElevationRecord, LaneSection, Junction, Connection, LaneLink
from src.models.geometry import LineGeometry, ArcGeometry, SplineGeometry
from src.models.lane import Lane, WidthRecord, RoadMark, SpeedRecord


class XODRParser:
    """
    OpenDRIVE文件解析器
    """
    
    def __init__(self):
        self.road_network = None
    
    def parse(self, file_path: str) -> RoadNetwork:
        """
        解析XODR文件并返回道路网络对象
        """
        try:
            # 解析XML文件
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 创建道路网络对象
            self.road_network = RoadNetwork()
            
            # 解析header
            self._parse_header(root.find('header'))
            
            # 解析roads
            for road_elem in root.findall('road'):
                road = self._parse_road(road_elem)
                self.road_network.add_road(road)
            
            # 解析junction
            for junction_elem in root.findall('junction'):
                self._parse_junction(junction_elem)
            
            return self.road_network
            
        except ET.ParseError as e:
            raise ValueError(f"XODR文件解析错误: {e}")
        except Exception as e:
            raise ValueError(f"解析XODR文件时发生错误: {e}")
    
    def _parse_header(self, header_elem):
        """
        解析header元素
        """
        if header_elem is None:
            return
        
        rev_major = int(header_elem.get('revMajor', 1))
        rev_minor = int(header_elem.get('revMinor', 4))
        name = header_elem.get('name', '')
        version = header_elem.get('version', '')
        north = float(header_elem.get('north', 0.0))
        south = float(header_elem.get('south', 0.0))
        east = float(header_elem.get('east', 0.0))
        west = float(header_elem.get('west', 0.0))
        
        header = Header(rev_major, rev_minor, name, version, north, south, east, west)
        self.road_network.header = header
    
    def _parse_road(self, road_elem) -> Road:
        """
        解析road元素
        """
        road_id = int(road_elem.get('id'))
        name = road_elem.get('name', '')
        length = float(road_elem.get('length'))
        junction = int(road_elem.get('junction', -1))
        
        road = Road(road_id, name, length, junction)
        
        # 解析planView
        self._parse_plan_view(road_elem.find('planView'), road)
        
        # 解析elevationProfile
        self._parse_elevation_profile(road_elem.find('elevationProfile'), road)
        
        # 解析lateralProfile
        self._parse_lateral_profile(road_elem.find('lateralProfile'), road)
        
        # 解析lanes
        self._parse_lanes(road_elem.find('lanes'), road)
        
        # 解析objects
        self._parse_objects(road_elem.find('objects'), road)
        
        # 解析signals
        self._parse_signals(road_elem.find('signals'), road)
        
        return road
    
    def _parse_plan_view(self, plan_view_elem, road: Road):
        """
        解析planView元素，包含道路几何信息
        """
        if plan_view_elem is None:
            return
        
        # 解析geometry元素
        for geo_elem in plan_view_elem.findall('geometry'):
            s = float(geo_elem.get('s'))
            x = float(geo_elem.get('x'))
            y = float(geo_elem.get('y'))
            hdg = float(geo_elem.get('hdg'))  # 方向角
            length = float(geo_elem.get('length'))
            
            # 确定几何类型
            line_elem = geo_elem.find('line')
            arc_elem = geo_elem.find('arc')
            spiral_elem = geo_elem.find('spiral')
            parametric_poly3_elem = geo_elem.find('paramPoly3')
            cubic_poly_elem = geo_elem.find('cubicPoly')
            
            if line_elem is not None:
                geometry = LineGeometry(s, x, y, hdg, length)
            elif arc_elem is not None:
                curvature = float(arc_elem.get('curvature'))
                geometry = ArcGeometry(s, x, y, hdg, length, curvature)
            elif spiral_elem is not None:
                # 处理螺旋线（clothoid）
                curvature_start = float(spiral_elem.get('curvStart'))
                curvature_end = float(spiral_elem.get('curvEnd'))
                geometry = SplineGeometry(s, x, y, hdg, length, curvature_start, curvature_end)
            elif parametric_poly3_elem is not None:
                # 简化处理，暂不支持
                geometry = LineGeometry(s, x, y, hdg, length)
            elif cubic_poly_elem is not None:
                # 简化处理，暂不支持
                geometry = LineGeometry(s, x, y, hdg, length)
            else:
                # 默认为直线
                geometry = LineGeometry(s, x, y, hdg, length)
            
            road.add_geometry(geometry)
    
    def _parse_elevation_profile(self, elevation_profile_elem, road: Road):
        """
        解析elevationProfile元素，包含道路高程信息
        """
        if elevation_profile_elem is None:
            return
        
        for elevation_elem in elevation_profile_elem.findall('elevation'):
            s = float(elevation_elem.get('s'))
            a = float(elevation_elem.get('a'))
            b = float(elevation_elem.get('b', 0.0))
            c = float(elevation_elem.get('c', 0.0))
            d = float(elevation_elem.get('d', 0.0))
            
            elevation_record = ElevationRecord(s, a, b, c, d)
            road.add_elevation_record(elevation_record)
    
    def _parse_lateral_profile(self, lateral_profile_elem, road: Road):
        """
        解析lateralProfile元素，包含超高和横坡信息
        """
        if lateral_profile_elem is None:
            return
        
        # 简化处理，暂不实现横坡计算
        pass
    
    def _parse_lanes(self, lanes_elem, road: Road):
        """
        解析lanes元素，包含车道信息
        """
        if lanes_elem is None:
            return
        
        # 解析laneOffset
        for lane_offset_elem in lanes_elem.findall('laneOffset'):
            s = float(lane_offset_elem.get('s'))
            a = float(lane_offset_elem.get('a'))
            b = float(lane_offset_elem.get('b', 0.0))
            c = float(lane_offset_elem.get('c', 0.0))
            d = float(lane_offset_elem.get('d', 0.0))
            road.add_lane_offset(s, a, b, c, d)
        
        # 解析laneSection
        for lane_section_elem in lanes_elem.findall('laneSection'):
            s = float(lane_section_elem.get('s'))
            lane_section = LaneSection(s)
            road.add_lane_section(lane_section)
            
            # 解析left, center, right
            self._parse_lane_group(lane_section_elem.find('left'), lane_section, 'left')
            self._parse_lane_group(lane_section_elem.find('center'), lane_section, 'center')
            self._parse_lane_group(lane_section_elem.find('right'), lane_section, 'right')
    
    def _parse_lane_group(self, lane_group_elem, lane_section: LaneSection, group_type: str):
        """
        解析车道组（left, center, right）
        """
        if lane_group_elem is None:
            return
        
        for lane_elem in lane_group_elem.findall('lane'):
            lane_id = int(lane_elem.get('id'))
            lane_type = lane_elem.get('type', 'driving')
            level = lane_elem.get('level', 'false').lower() == 'true'
            
            lane = Lane(lane_id, lane_type, level)
            
            # 解析width
            for width_elem in lane_elem.findall('width'):
                s_offset = float(width_elem.get('sOffset', 0.0))
                a = float(width_elem.get('a'))
                b = float(width_elem.get('b', 0.0))
                c = float(width_elem.get('c', 0.0))
                d = float(width_elem.get('d', 0.0))
                
                width_record = WidthRecord(s_offset, a, b, c, d)
                lane.add_width_record(width_record)
            
            # 解析roadMark
            road_mark_elem = lane_elem.find('roadMark')
            if road_mark_elem is not None:
                s_offset = float(road_mark_elem.get('sOffset', 0.0))
                mark_type = road_mark_elem.get('type', 'solid')
                width = float(road_mark_elem.get('width', 0.15))
                material = road_mark_elem.get('material', 'standard')
                weight = road_mark_elem.get('weight', 'standard')
                color = road_mark_elem.get('color', 'white')
                lane_change = road_mark_elem.get('laneChange', 'both')
                
                road_mark = RoadMark(s_offset, mark_type, width, material, weight, color, lane_change)
                lane.set_road_mark(road_mark)
            
            # 解析speed
            speed_elem = lane_elem.find('speed')
            if speed_elem is not None:
                s_offset = float(speed_elem.get('sOffset', 0.0))
                max_speed = float(speed_elem.get('max', 50.0))
                unit = speed_elem.get('unit', 'km/h')
                
                speed_record = SpeedRecord(s_offset, max_speed, unit)
                lane.speed = speed_record
            
            # 添加到对应的车道组
            if group_type == 'left':
                lane_section.add_left_lane(lane)
            elif group_type == 'center':
                lane_section.add_center_lane(lane)
            elif group_type == 'right':
                lane_section.add_right_lane(lane)
    
    def _parse_junction(self, junction_elem):
        """
        解析junction元素
        """
        if junction_elem is None:
            return
            
        junction_id = junction_elem.get('id')
        name = junction_elem.get('name', '')
        main_road = junction_elem.get('mainRoad', '')
        side_road = junction_elem.get('sideRoad', '')
        
        junction = Junction(junction_id, name, main_road, side_road)
        
        # 解析connection元素
        for conn_elem in junction_elem.findall('connection'):
            connection_id = conn_elem.get('id')
            incoming_road = conn_elem.get('incomingRoad')
            connecting_road = conn_elem.get('connectingRoad')
            contact_point = conn_elem.get('contactPoint', 'start')
            
            connection = Connection(connection_id, incoming_road, connecting_road, contact_point)
            
            # 解析laneLink元素
            for link_elem in conn_elem.findall('laneLink'):
                from_lane = link_elem.get('from')
                to_lane = link_elem.get('to')
                
                lane_link = LaneLink(from_lane, to_lane)
                connection.add_lane_link(lane_link)
            
            junction.add_connection(connection)
        
        self.road_network.add_junction(junction)
    
    def _parse_objects(self, objects_elem, road: Road):
        """
        解析objects元素
        """
        # 简化处理，暂不实现对象解析
        pass
    
    def _parse_signals(self, signals_elem, road: Road):
        """
        解析signals元素
        """
        # 简化处理，暂不实现信号解析
        pass


# 测试函数
def test_parser():
    """
    测试解析器功能
    """
    parser = XODRParser()
    try:
        # 这里可以填入实际的XODR文件路径进行测试
        # road_network = parser.parse('test.xodr')
        print("XODR解析器测试准备就绪")
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_parser()