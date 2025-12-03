#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
几何实体模型
"""

import math
from typing import Tuple, List


class Geometry:
    """
    几何基类
    """
    
    def __init__(self, s: float, x: float, y: float, hdg: float, length: float):
        self.s = s  # 起点桩号
        self.x = x  # 起点X坐标
        self.y = y  # 起点Y坐标
        self.hdg = hdg  # 起点航向角（弧度）
        self.length = length  # 几何长度
    
    def get_position(self, s_pos: float) -> Tuple[float, float, float]:
        """
        计算指定桩号位置的坐标
        返回 (x, y, heading)
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def get_tangent_vector(self, s_pos: float) -> Tuple[float, float]:
        """
        计算指定桩号位置的切线向量
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def get_normal_vector(self, s_pos: float) -> Tuple[float, float]:
        """
        计算指定桩号位置的法线向量（左侧）
        """
        tx, ty = self.get_tangent_vector(s_pos)
        return -ty, tx


class LineGeometry(Geometry):
    """
    直线几何类
    """
    
    def get_position(self, s_pos: float) -> Tuple[float, float, float]:
        """
        计算直线上指定桩号位置的坐标
        """
        # 确保s_pos在有效范围内
        s_offset = min(max(0, s_pos - self.s), self.length)
        
        # 计算终点坐标
        x = self.x + s_offset * math.cos(self.hdg)
        y = self.y + s_offset * math.sin(self.hdg)
        
        # 直线的航向角保持不变
        return x, y, self.hdg
    
    def get_tangent_vector(self, s_pos: float) -> Tuple[float, float]:
        """
        直线的切线向量是常数
        """
        return math.cos(self.hdg), math.sin(self.hdg)
    
    def generate_points(self, step_size: float = 1.0) -> List[Tuple[float, float]]:
        """
        生成直线上的点列表
        step_size: 点之间的步长
        """
        points = []
        num_points = max(2, int(self.length / step_size) + 1)
        
        for i in range(num_points):
            s_offset = min(i * step_size, self.length)
            x, y, _ = self.get_position(self.s + s_offset)
            points.append((x, y))
        
        # 确保包含终点
        if num_points > 1:
            x_end, y_end, _ = self.get_position(self.s + self.length)
            if (x_end, y_end) != points[-1]:
                points.append((x_end, y_end))
        
        return points


class ArcGeometry(Geometry):
    """
    圆弧几何类（预留）
    """
    
    def __init__(self, s: float, x: float, y: float, hdg: float, length: float, curvature: float):
        super().__init__(s, x, y, hdg, length)
        self.curvature = curvature  # 曲率，半径的倒数
        self.radius = 1.0 / abs(curvature) if curvature != 0 else float('inf')
    
    def get_position(self, s_pos: float) -> Tuple[float, float, float]:
        # 计算圆弧上的位置
        s_offset = min(max(0, s_pos - self.s), self.length)
        
        if self.curvature == 0:
            # 退化为直线
            x = self.x + s_offset * math.cos(self.hdg)
            y = self.y + s_offset * math.sin(self.hdg)
            return x, y, self.hdg
        
        # 计算角度变化
        delta_angle = s_offset * self.curvature
        
        # 圆心计算：在起点的左法线方向上（左转为正曲率）
        center_offset_x = -math.sin(self.hdg) * self.radius * (1 if self.curvature > 0 else -1)
        center_offset_y = math.cos(self.hdg) * self.radius * (1 if self.curvature > 0 else -1)
        center_x = self.x + center_offset_x
        center_y = self.y + center_offset_y
        
        # 计算从圆心到起点的向量角度
        to_start_angle = math.atan2(self.y - center_y, self.x - center_x)
        
        # 计算新点角度
        new_point_angle = to_start_angle + delta_angle
        
        # 计算点坐标
        x = center_x + math.cos(new_point_angle) * self.radius
        y = center_y + math.sin(new_point_angle) * self.radius
        
        # 计算新的航向角
        new_hdg = self.hdg + delta_angle
        
        return x, y, new_hdg
    
    def get_tangent_vector(self, s_pos: float) -> Tuple[float, float]:
        _, _, hdg = self.get_position(s_pos)
        return math.cos(hdg), math.sin(hdg)
    
    def generate_points(self, step_size: float = 1.0) -> List[Tuple[float, float]]:
        """
        生成圆弧上的点列表
        step_size: 点之间的步长
        """
        points = []
        # 对于曲线，使用更小的步长以保证精度
        effective_step = min(step_size, self.length / 20.0)  # 至少20个点
        num_points = max(2, int(self.length / effective_step) + 1)
        
        for i in range(num_points):
            s_offset = min(i * effective_step, self.length)
            x, y, _ = self.get_position(self.s + s_offset)
            points.append((x, y))
        
        # 确保包含终点
        if num_points > 1:
            x_end, y_end, _ = self.get_position(self.s + self.length)
            if (x_end, y_end) != points[-1]:
                points.append((x_end, y_end))
        
        return points


class SplineGeometry(Geometry):
    """
    样条曲线几何类
    """
    
    def __init__(self, s: float, x: float, y: float, hdg: float, length: float, 
                 curv_start: float = 0.0, curv_end: float = 0.0):
        super().__init__(s, x, y, hdg, length)
        self.curv_start = curv_start  # 起点曲率
        self.curv_end = curv_end      # 终点曲率
    
    def get_position(self, s_pos: float) -> Tuple[float, float, float]:
        """
        计算样条曲线上的位置
        使用三次多项式近似：曲率从curv_start线性变化到curv_end
        """
        s_offset = min(max(0, s_pos - self.s), self.length)
        
        if self.length == 0:
            return self.x, self.y, self.hdg
        
        # 归一化参数 t ∈ [0, 1]
        t = s_offset / self.length
        
        # 线性插值曲率
        curvature_t = self.curv_start + (self.curv_end - self.curv_start) * t
        
        # 使用数值积分计算位置和航向角
        # 将路径分成小段进行积分
        num_steps = max(10, int(self.length))
        dt = t / num_steps if t > 0 else 0
        
        x, y, hdg = self.x, self.y, self.hdg
        
        for i in range(int(t * num_steps)):
            t_i = (i + 0.5) * dt  # 中点法则
            curv_i = self.curv_start + (self.curv_end - self.curv_start) * t_i
            
            # 小步长
            ds = self.length * dt
            
            # 更新位置和航向角
            x += ds * math.cos(hdg)
            y += ds * math.sin(hdg)
            hdg += ds * curv_i
        
        return x, y, hdg
    
    def get_tangent_vector(self, s_pos: float) -> Tuple[float, float]:
        _, _, hdg = self.get_position(s_pos)
        return math.cos(hdg), math.sin(hdg)
    
    def generate_points(self, step_size: float = 1.0) -> List[Tuple[float, float]]:
        """
        生成样条曲线上的点列表
        """
        points = []
        # 对于样条曲线，使用更密集的采样
        effective_step = min(step_size, self.length / 30.0)  # 至少30个点
        num_points = max(2, int(self.length / effective_step) + 1)
        
        for i in range(num_points):
            s_offset = min(i * effective_step, self.length)
            x, y, _ = self.get_position(self.s + s_offset)
            points.append((x, y))
        
        # 确保包含终点
        if num_points > 1:
            x_end, y_end, _ = self.get_position(self.s + self.length)
            if (x_end, y_end) != points[-1]:
                points.append((x_end, y_end))
        
        return points