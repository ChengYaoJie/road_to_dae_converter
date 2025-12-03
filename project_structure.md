# OpenDRIVE/OSM到DAE转换工具项目结构

## 项目概述

本项目旨在创建一个将OpenDRIVE和OSM格式的道路网络数据转换为COLLADA/DAE格式3D模型的工具。

## 目录结构

```
road_to_dae_converter/
├── src/
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── xodr_parser.py     # OpenDRIVE解析器
│   │   └── osm_parser.py      # OSM解析器（预留）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── road_network.py    # 道路网络数据模型
│   │   ├── geometry.py        # 几何实体模型
│   │   └── material.py        # 材质模型
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── road_to_mesh.py    # 道路到网格的转换
│   │   └── lane_marker.py     # 车道标记生成
│   ├── generators/
│   │   ├── __init__.py
│   │   └── dae_generator.py   # DAE文件生成器
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── math_utils.py      # 数学工具函数
│   │   └── coordinate.py      # 坐标转换工具
│   └── main.py                # 主程序入口
├── tests/
│   ├── __init__.py
│   ├── test_xodr_parser.py    # 解析器测试
│   └── test_conversion.py     # 转换测试
├── textures/                  # 纹理资源目录
│   ├── Asphalt1_Diff.png
│   └── LaneMarking1_Diff.png
├── requirements.txt           # 项目依赖
├── setup.py                   # 安装配置
└── README.md                  # 项目说明
```

## 核心类设计

### 1. 解析器模块 (parsers/)

#### XODRParser 类
- **功能**: 解析OpenDRIVE XML文件
- **主要方法**:
  - `parse(file_path)`: 解析XODR文件
  - `_parse_header()`: 解析文件头信息
  - `_parse_roads()`: 解析道路数据
  - `_parse_lanes()`: 解析车道数据
  - `_parse_road_marks()`: 解析道路标记

#### OSMParser 类 (预留)
- **功能**: 解析OSM XML文件
- **主要方法**:
  - `parse(file_path)`: 解析OSM文件
  - `_parse_ways()`: 解析道路数据
  - `_parse_nodes()`: 解析节点数据

### 2. 数据模型模块 (models/)

#### RoadNetwork 类
- **功能**: 表示完整的道路网络
- **主要属性**:
  - `roads`: 道路列表
  - `junctions`: 路口列表
- **主要方法**:
  - `add_road(road)`: 添加道路
  - `get_road_by_id(road_id)`: 根据ID获取道路

#### Road 类
- **功能**: 表示单条道路
- **主要属性**:
  - `id`: 道路ID
  - `name`: 道路名称
  - `length`: 道路长度
  - `geometry`: 道路几何形状
  - `lane_sections`: 车道段列表
- **主要方法**:
  - `get_lane_by_id(lane_id)`: 根据ID获取车道
  - `generate_mesh()`: 生成道路网格

#### Lane 类
- **功能**: 表示单个车道
- **主要属性**:
  - `id`: 车道ID
  - `type`: 车道类型
  - `width`: 车道宽度
  - `road_mark`: 道路标记
- **主要方法**:
  - `calculate_edge_points()`: 计算车道边缘点

#### Geometry 类
- **功能**: 表示几何形状
- **主要子类**:
  - `LineGeometry`: 直线几何
  - `ArcGeometry`: 圆弧几何（预留）
  - `SplineGeometry`: 样条曲线几何（预留）

### 3. 转换器模块 (converters/)

#### RoadToMeshConverter 类
- **功能**: 将道路数据转换为3D网格
- **主要方法**:
  - `convert(road)`: 转换道路为网格
  - `_generate_vertices()`: 生成顶点
  - `_generate_normals()`: 生成法线
  - `_generate_texcoords()`: 生成纹理坐标
  - `_generate_faces()`: 生成面

#### LaneMarkerConverter 类
- **功能**: 生成车道标记网格
- **主要方法**:
  - `convert(lane)`: 转换车道标记为网格
  - `_generate_solid_line()`: 生成实线
  - `_generate_broken_line()`: 生成虚线

### 4. 生成器模块 (generators/)

#### DAEGenerator 类
- **功能**: 生成DAE格式文件
- **主要方法**:
  - `generate(road_network, output_path)`: 生成DAE文件
  - `_create_dae_structure()`: 创建DAE XML结构
  - `_add_materials()`: 添加材质定义
  - `_add_geometries()`: 添加几何体定义
  - `_add_visual_scene()`: 添加视觉场景

### 5. 工具模块 (utils/)

#### MathUtils 类
- **功能**: 数学工具函数
- **主要方法**:
  - `calculate_heading_vector(heading)`: 计算航向向量
  - `rotate_point(point, angle)`: 旋转点

#### CoordinateConverter 类
- **功能**: 坐标系统转换
- **主要方法**:
  - `opendrive_to_dae(coordinates)`: OpenDRIVE坐标转DAE坐标

## 依赖项

- lxml: 用于解析XML文件
- numpy: 用于数学计算和数组操作
- matplotlib: 可选，用于可视化（调试用）

## 主程序流程

1. 加载并解析XODR/OSM文件
2. 创建道路网络模型
3. 转换道路数据为3D网格
4. 生成DAE文件
5. 保存输出文件