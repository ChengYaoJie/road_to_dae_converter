#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
车道和道路标记数据模型
"""

from typing import List, Optional


class RoadMark:
    """
    道路标记类
    """
    
    def __init__(self, s_offset: float, mark_type: str, width: float,
                 material: str, weight: str, color: str, lane_change: str):
        self.s_offset = s_offset  # 标记起始桩号
        self.type = mark_type     # 标记类型：solid, broken, solid solid等
        self.width = width        # 标记宽度
        self.material = material  # 标记材质
        self.weight = weight      # 标记粗细
        self.color = color        # 标记颜色：white, yellow等
        self.lane_change = lane_change  # 车道变换限制
    
    def is_solid(self) -> bool:
        """判断是否为实线"""
        return "solid" in self.type and not "broken" in self.type
    
    def is_broken(self) -> bool:
        """判断是否为虚线"""
        return "broken" in self.type
    
    def is_double(self) -> bool:
        """判断是否为双黄线等双线标记"""
        return self.type.count("solid") >= 2


class WidthRecord:
    """
    车道宽度记录类
    """
    
    def __init__(self, s_offset: float, a: float, b: float = 0.0, c: float = 0.0, d: float = 0.0):
        self.s_offset = s_offset  # 宽度记录起始桩号
        self.a = a  # 常数项
        self.b = b  # s的一次项系数
        self.c = c  # s的二次项系数
        self.d = d  # s的三次项系数
    
    def get_width(self, s_pos: float) -> float:
        """计算指定桩号位置的车道宽度"""
        delta_s = s_pos - self.s_offset
        return self.a + self.b * delta_s + self.c * delta_s**2 + self.d * delta_s**3


class Lane:
    """
    车道类
    """
    
    def __init__(self, lane_id: int, lane_type: str, level: bool):
        self.id = lane_id              # 车道ID，左侧为正，右侧为负
        self.type = lane_type          # 车道类型：driving, shoulder等
        self.level = level             # 是否与其他车道在同一高度
        self.widths = []               # 宽度记录列表
        self.road_mark = None          # 车道边界标记
        self.speed = None              # 速度限制
        self.user_data = None          # 用户数据
        self.is_left = lane_id > 0     # 是否为左侧车道
        self.is_right = lane_id < 0    # 是否为右侧车道
        self.is_center = lane_id == 0  # 是否为中央车道
    
    def add_width_record(self, width_record: WidthRecord):
        """添加宽度记录"""
        self.widths.append(width_record)
    
    def set_road_mark(self, road_mark: RoadMark):
        """设置道路标记"""
        self.road_mark = road_mark
    
    def get_width_at(self, s_pos: float) -> float:
        """
        获取指定桩号位置的车道宽度
        如果没有匹配的宽度记录，返回最后一个记录的值
        """
        if not self.widths:
            return 0.0
        
        # 找到适用的宽度记录
        applicable_width = self.widths[0]
        for width_record in self.widths:
            if width_record.s_offset <= s_pos:
                applicable_width = width_record
            else:
                break
        
        return applicable_width.get_width(s_pos)
    
    def calculate_edge_points(self, road_geometry, s_start: float, s_end: float, step_size: float = 1.0):
        """
        计算车道边缘点
        返回左侧边缘和右侧边缘的点列表
        """
        left_edge_points = []
        right_edge_points = []
        
        # 从s_start到s_end，按step_size采样
        current_s = s_start
        while current_s <= s_end:
            # 获取当前桩号在道路中心线上的位置和航向角
            x, y, hdg = road_geometry.get_position(current_s)
            
            # 获取法线向量（指向左侧）
            nx, ny = road_geometry.get_normal_vector(current_s)
            
            # 获取当前位置的车道宽度
            width = self.get_width_at(current_s)
            
            # 计算左右边缘点
            if self.is_left:
                # 左侧车道：从中心线向左偏移
                left_offset = sum(w.get_width(current_s) for w in self.widths) if self.widths else 0
                left_x = x + nx * left_offset
                left_y = y + ny * left_offset
                right_x = x
                right_y = y
            elif self.is_right:
                # 右侧车道：从中心线向右偏移（负的法线方向）
                right_offset = sum(w.get_width(current_s) for w in self.widths) if self.widths else 0
                left_x = x
                left_y = y
                right_x = x - nx * right_offset
                right_y = y - ny * right_offset
            else:
                # 中央车道
                half_width = width / 2.0
                left_x = x + nx * half_width
                left_y = y + ny * half_width
                right_x = x - nx * half_width
                right_y = y - ny * half_width
            
            left_edge_points.append((left_x, left_y))
            right_edge_points.append((right_x, right_y))
            
            current_s += step_size
        
        return left_edge_points, right_edge_points
    
    def is_driving_lane(self) -> bool:
        """判断是否为行车道"""
        return self.type == "driving"
    
    def is_shoulder(self) -> bool:
        """判断是否为路肩"""
        return self.type == "shoulder"
    
    def is_border(self) -> bool:
        """判断是否为边界"""
        return self.type == "border"


class SpeedRecord:
    """
    速度限制记录类
    """
    
    def __init__(self, s_offset: float, max_speed: float, unit: str = "m/s"):
        self.s_offset = s_offset  # 速度记录起始桩号
        self.max_speed = max_speed  # 最大速度
        self.unit = unit  # 速度单位
    
    def get_max_speed(self, unit: str = None) -> float:
        """
        获取最大速度，可选择单位转换
        支持的单位: m/s, km/h, mph
        """
        speed = self.max_speed
        
        # 首先转换为m/s
        if self.unit == "km/h":
            speed = speed / 3.6
        elif self.unit == "mph":
            speed = speed * 0.44704
        
        # 然后转换为目标单位
        if unit == "km/h":
            return speed * 3.6
        elif unit == "mph":
            return speed / 0.44704
        elif unit == "m/s" or unit is None:
            return speed
        else:
            raise ValueError(f"不支持的速度单位: {unit}")