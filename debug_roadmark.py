#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试脚本：检查 RoadMark 类型判断
"""

import sys
sys.path.insert(0, 'c:/Users/ChengYaoJie/Desktop/test/road_to_dae_converter')

from src.parsers.xodr_parser import XODRParser

def main():
    parser = XODRParser()
    road_network = parser.parse('c:/Users/ChengYaoJie/Desktop/test/test.xodr')
    
    print("=" * 80)
    print("OpenDRIVE 文件中的车道标线定义：")
    print("=" * 80)
    
    for road in road_network.roads:
        print(f"\n道路 {road.id}:")
        for lane_section in road.lane_sections:
            print(f"  车道段 (s={lane_section.s}):")
            
            # 左侧车道
            for lane in sorted(lane_section.left_lanes, key=lambda x: x.id):
                if lane.road_mark:
                    rm = lane.road_mark
                    print(f"    Lane {lane.id} (left, {lane.type}):")
                    print(f"      roadMark.type = '{rm.type}'")
                    print(f"      roadMark.color = '{rm.color}'")
                    print(f"      roadMark.width = {rm.width}")
                    print(f"      is_solid() = {rm.is_solid()}")
                    print(f"      is_broken() = {rm.is_broken()}")
                    print(f"      is_double() = {rm.is_double()}")
            
            # 中心车道
            for lane in lane_section.center_lanes:
                if lane.road_mark:
                    rm = lane.road_mark
                    print(f"    Lane {lane.id} (center):")
                    print(f"      roadMark.type = '{rm.type}'")
                    print(f"      roadMark.color = '{rm.color}'")
                    print(f"      roadMark.width = {rm.width}")
                    print(f"      is_solid() = {rm.is_solid()}")
                    print(f"      is_broken() = {rm.is_broken()}")
                    print(f"      is_double() = {rm.is_double()}")
            
            # 右侧车道
            for lane in sorted(lane_section.right_lanes, key=lambda x: x.id, reverse=True):
                if lane.road_mark:
                    rm = lane.road_mark
                    print(f"    Lane {lane.id} (right, {lane.type}):")
                    print(f"      roadMark.type = '{rm.type}'")
                    print(f"      roadMark.color = '{rm.color}'")
                    print(f"      roadMark.width = {rm.width}")
                    print(f"      is_solid() = {rm.is_solid()}")
                    print(f"      is_broken() = {rm.is_broken()}")
                    print(f"      is_double() = {rm.is_double()}")
    
    print("\n" + "=" * 80)
    print("预期结果：")
    print("  Lane 1 (left): type='broken', is_broken()=True")
    print("  Lane 2 (left): type='solid', is_solid()=True")
    print("  Lane 0 (center): type='solid solid', is_double()=True")
    print("  Lane -1 (right): type='broken', is_broken()=True")
    print("  Lane -2 (right): type='solid', is_solid()=True")
    print("=" * 80)

if __name__ == "__main__":
    main()
