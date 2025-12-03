# XODR到DAE转换器 API文档

本文档详细介绍了XODR到DAE转换器的API接口，帮助开发者正确使用各个组件。

## 目录

- [核心模块](#核心模块)
- [解析器模块](#解析器模块)
- [生成器模块](#生成器模块)
- [模型模块](#模型模块)
- [使用示例](#使用示例)

## 核心模块

### main.py

#### `convert_xodr_to_dae(xodr_file, output_dae, textures_dir=None, step_size=1.0)`

**功能**: 执行完整的XODR到DAE转换流程

**参数**:
- `xodr_file` (str): 输入的XODR文件路径
- `output_dae` (str): 输出的DAE文件路径
- `textures_dir` (str, 可选): 纹理目录路径，默认为None
- `step_size` (float, 可选): 网格生成步长，默认为1.0

**返回值**:
- `bool`: 转换是否成功

**示例**:
```python
from road_to_dae_converter.src.main import convert_xodr_to_dae

success = convert_xodr_to_dae(
    xodr_file="test.xodr",
    output_dae="output.dae",
    step_size=0.5
)
```

## 解析器模块

### xodr_parser.py

#### `XODRParser` 类

**功能**: 解析XODR文件并创建道路网络模型

#### `XODRParser.parse(xodr_file)`

**功能**: 解析XODR文件

**参数**:
- `xodr_file` (str): XODR文件路径

**返回值**:
- `RoadNetwork`: 解析后的道路网络对象

**示例**:
```python
from road_to_dae_converter.src.parsers.xodr_parser import XODRParser

parser = XODRParser()
road_network = parser.parse("test.xodr")
```

## 生成器模块

### mesh_generator.py

#### `MeshGenerator` 类

**功能**: 从道路网络生成3D网格

#### `MeshGenerator.__init__(material_library=None)`

**功能**: 初始化网格生成器

**参数**:
- `material_library` (MaterialLibrary, 可选): 材质库对象，默认为None

#### `MeshGenerator.generate_meshes(road_network, step_size=1.0)`

**功能**: 从道路网络生成3D网格

**参数**:
- `road_network` (RoadNetwork): 道路网络对象
- `step_size` (float, 可选): 网格生成步长，默认为1.0

**返回值**:
- `Dict[str, MeshData]`: 网格名称到网格数据的映射

**示例**:
```python
from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
from road_to_dae_converter.src.models.material import MaterialLibrary

material_library = MaterialLibrary()
material_library.create_default_materials()

mesh_generator = MeshGenerator(material_library)
meshes = mesh_generator.generate_meshes(road_network, step_size=0.5)
```

#### `MeshData` 类

**功能**: 存储网格的顶点、法线、纹理坐标和索引数据

#### 属性:
- `name` (str): 网格名称
- `vertices` (List[Tuple[float, float, float]]): 顶点列表
- `normals` (List[Tuple[float, float, float]]): 法线列表
- `tex_coords` (List[Tuple[float, float]]): 纹理坐标列表
- `indices` (List[int]): 三角形索引列表
- `material_name` (Optional[str]): 材质名称

#### 方法:
- `add_vertex(x, y, z)`: 添加顶点
- `add_normal(nx, ny, nz)`: 添加法线
- `add_tex_coord(u, v)`: 添加纹理坐标
- `add_triangle(i1, i2, i3)`: 添加三角形索引
- `set_material(material_name)`: 设置材质名称

### dae_exporter.py

#### `DAEExporter` 类

**功能**: 将网格数据导出为DAE文件

#### `DAEExporter.export_to_dae(meshes, material_library, output_file)`

**功能**: 导出网格数据到DAE文件

**参数**:
- `meshes` (Dict[str, MeshData]): 网格数据字典
- `material_library` (MaterialLibrary): 材质库
- `output_file` (str): 输出文件路径

**返回值**:
- `bool`: 导出是否成功

**示例**:
```python
from road_to_dae_converter.src.generators.dae_exporter import DAEExporter

exporter = DAEExporter()
success = exporter.export_to_dae(meshes, material_library, "output.dae")
```

## 模型模块

### material.py

#### `Material` 类

**功能**: 表示3D模型的材质

#### 属性:
- `name` (str): 材质名称
- `diffuse_color` (Tuple[float, float, float]): 漫反射颜色 (r, g, b)
- `specular_color` (Tuple[float, float, float]): 镜面反射颜色 (r, g, b)
- `shininess` (float): 光泽度
- `texture` (Optional[Texture]): 纹理对象

#### `MaterialLibrary` 类

**功能**: 管理材质集合

#### `MaterialLibrary.__init__()`

**功能**: 初始化材质库

#### `MaterialLibrary.add_material(material)`

**功能**: 添加材质到库中

**参数**:
- `material` (Material): 材质对象

#### `MaterialLibrary.get_material(name)`

**功能**: 根据名称获取材质

**参数**:
- `name` (str): 材质名称

**返回值**:
- `Optional[Material]`: 材质对象，如果不存在则返回None

#### `MaterialLibrary.create_default_materials()`

**功能**: 创建默认材质集合

**示例**:
```python
from road_to_dae_converter.src.models.material import MaterialLibrary

material_library = MaterialLibrary()
material_library.create_default_materials()
asphalt = material_library.get_material("Asphalt")
```

### road_network.py

#### `RoadNetwork` 类

**功能**: 表示整个道路网络

#### 属性:
- `roads` (List[Road]): 道路列表

#### `Road` 类

**功能**: 表示单条道路

#### 属性:
- `id` (str): 道路ID
- `length` (float): 道路长度
- `lane_sections` (List[LaneSection]): 车道段列表
- `geometries` (List[Geometry]): 几何元素列表
- `elevation_profile` (List[ElevationRecord]): 高程记录列表
- `lateral_profile` (List[SuperelevationRecord]): 横坡记录列表

#### 方法:
- `get_geometry_at(s)`: 获取指定桩号位置的几何对象
- `get_elevation_at(s)`: 获取指定桩号位置的高程

#### `LaneSection` 类

**功能**: 表示道路的车道段

#### 属性:
- `s` (float): 起始桩号
- `left_lanes` (List[Lane]): 左侧车道列表
- `right_lanes` (List[Lane]): 右侧车道列表
- `center_lane` (Optional[Lane]): 中央车道
- `center_lanes` (List[Lane]): 中央车道列表（兼容用）

#### 方法:
- `add_left_lane(lane)`: 添加左侧车道
- `add_right_lane(lane)`: 添加右侧车道
- `add_center_lane(lane)`: 添加中央车道
- `set_center_lane(lane)`: 设置中央车道

#### `Lane` 类

**功能**: 表示单个车道

#### 属性:
- `id` (int): 车道ID
- `is_left` (bool): 是否为左侧车道
- `is_right` (bool): 是否为右侧车道
- `road_mark` (Optional[RoadMark]): 车道线标记
- `lane_section` (Optional[LaneSection]): 所属的车道段

#### 方法:
- `get_width_at(s)`: 获取指定桩号位置的车道宽度
- `is_driving_lane()`: 判断是否为行驶车道
- `is_shoulder()`: 判断是否为路肩

#### `RoadMark` 类

**功能**: 表示车道线标记

#### 属性:
- `s_offset` (float): 起始偏移
- `width` (float): 宽度
- `color` (str): 颜色
- `type` (str): 类型

#### 方法:
- `is_solid()`: 判断是否为实线
- `is_broken()`: 判断是否为虚线

### geometry.py

#### `Geometry` 类

**功能**: 基类，表示道路的几何形状

#### 方法:
- `get_position(s)`: 获取指定桩号在几何线上的位置和航向角
- `get_normal_vector(s)`: 获取指定桩号位置的法线向量

#### `LineGeometry` 类

**功能**: 表示直线几何形状

#### `ArcGeometry` 类

**功能**: 表示圆弧几何形状

## 使用示例

### 完整转换流程

```python
from road_to_dae_converter.src.parsers.xodr_parser import XODRParser
from road_to_dae_converter.src.models.material import MaterialLibrary
from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
from road_to_dae_converter.src.generators.dae_exporter import DAEExporter

# 1. 解析XODR文件
parser = XODRParser()
road_network = parser.parse("test.xodr")
print(f"解析了 {len(road_network.roads)} 条道路")

# 2. 创建材质库
material_library = MaterialLibrary()
material_library.create_default_materials()

# 3. 生成网格
mesh_generator = MeshGenerator(material_library)
meshes = mesh_generator.generate_meshes(road_network, step_size=1.0)
print(f"生成了 {len(meshes)} 个网格")

# 4. 导出DAE文件
exporter = DAEExporter()
success = exporter.export_to_dae(meshes, material_library, "output.dae")

if success:
    print("转换成功！")
else:
    print("转换失败！")
```

### 自定义材质

```python
from road_to_dae_converter.src.models.material import MaterialLibrary, Material

# 创建材质库
material_library = MaterialLibrary()

# 创建自定义材质
custom_asphalt = Material("CustomAsphalt")
custom_asphalt.diffuse_color = (0.1, 0.1, 0.15)
custom_asphalt.specular_color = (0.2, 0.2, 0.2)
custom_asphalt.shininess = 10.0

custom_lane_mark = Material("CustomLaneMark")
custom_lane_mark.diffuse_color = (1.0, 1.0, 0.9)
custom_lane_mark.specular_color = (1.0, 1.0, 1.0)
custom_lane_mark.shininess = 200.0

# 添加材质到库
material_library.add_material(custom_asphalt)
material_library.add_material(custom_lane_mark)

# 使用自定义材质库
mesh_generator = MeshGenerator(material_library)
```

### 网格生成控制

```python
# 精细网格（小步长）- 更高质量但处理较慢
fine_meshes = mesh_generator.generate_meshes(road_network, step_size=0.25)

# 粗略网格（大步长）- 较低质量但处理较快
rough_meshes = mesh_generator.generate_meshes(road_network, step_size=5.0)
```

## 注意事项

1. 当处理复杂道路网络时，建议适当调整`step_size`参数以平衡质量和性能
2. 确保XODR文件格式符合OpenDRIVE标准
3. 对于大型道路网络，可能需要增加系统内存
4. 导出的DAE文件可在大多数3D建模软件和游戏引擎中使用

---

*更多详细信息，请参考源代码和示例文件。*