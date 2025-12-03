# XODR到DAE转换器

[![测试状态](https://img.shields.io/badge/test-passing-brightgreen.svg)](https://github.com/yourusername/road_to_dae_converter)
[![Python版本](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)

一个用于将OpenDRIVE(XODR)道路格式转换为COLLADA(DAE)3D模型格式的Python工具。

## 📋 功能特性

- ✅ 完整解析XODR道路网络文件
- ✅ 生成高质量的3D网格模型
- ✅ 支持车道、车道线、路肩等道路元素
- ✅ 可自定义材质和纹理
- ✅ 灵活的网格精度控制
- ✅ 详细的验证和测试工具
- ✅ 支持命令行和编程接口使用

## 📦 安装指南

### 系统要求

- Python 3.6 或更高版本
- 无需额外依赖库（使用Python标准库实现）

### 安装步骤

1. 克隆或下载本项目

```bash
git clone https://github.com/yourusername/road_to_dae_converter.git
cd road_to_dae_converter
```

2. 确保Python环境正确

```bash
python --version  # 应显示 Python 3.6 或更高版本
```

## 🚀 使用方法

### 命令行使用

项目提供了验证脚本，可以直接在命令行中使用：

```bash
# 基本使用
python -m tests.verify_conversion --xodr path/to/test.xodr --output output.road.dae

# 指定步长（控制网格精度）
python -m tests.verify_conversion --xodr path/to/test.xodr --output output.road.dae --step-size 0.5

# 指定纹理目录
python -m tests.verify_conversion --xodr path/to/test.xodr --output output.road.dae --textures path/to/textures

# 显示详细日志
python -m tests.verify_conversion --xodr path/to/test.xodr --output output.road.dae --verbose
```

### 编程接口使用

在Python代码中使用转换器：

```python
from road_to_dae_converter.src.main import convert_xodr_to_dae

# 简单转换
success = convert_xodr_to_dae(
    xodr_file="path/to/test.xodr",
    output_dae="output.road.dae",
    step_size=1.0
)

if success:
    print("转换成功！")
else:
    print("转换失败！")
```

### 高级使用（分步处理）

对于需要更多控制的场景，可以分步使用各个组件：

```python
from road_to_dae_converter.src.parsers.xodr_parser import XODRParser
from road_to_dae_converter.src.generators.mesh_generator import MeshGenerator
from road_to_dae_converter.src.generators.dae_exporter import DAEExporter
from road_to_dae_converter.src.models.material import MaterialLibrary

# 1. 解析XODR文件
parser = XODRParser()
road_network = parser.parse("path/to/test.xodr")

# 2. 创建材质库
material_library = MaterialLibrary()
material_library.create_default_materials()

# 3. 生成3D网格
mesh_generator = MeshGenerator(material_library)
meshes = mesh_generator.generate_meshes(road_network, step_size=0.5)

# 4. 导出DAE文件
exporter = DAEExporter()
exporter.export_to_dae(meshes, material_library, "output.road.dae")
```

## 📁 项目结构

```
road_to_dae_converter/
├── src/
│   ├── parsers/         # XODR解析器
│   ├── generators/      # 网格生成器和DAE导出器
│   ├── models/          # 数据模型定义
│   └── main.py          # 主入口和转换函数
├── tests/               # 测试文件
│   ├── test_conversion.py    # 基本测试
│   └── verify_conversion.py  # 详细验证工具
├── examples/            # 使用示例
│   └── usage_example.py      # 代码示例
└── README.md            # 项目文档
```

## 🧪 运行测试

项目包含完整的测试套件，可以确保转换功能正常工作：

```bash
# 运行基本测试
python -m tests.test_conversion

# 运行详细验证
python -m tests.verify_conversion --xodr test.xodr --output test_output.dae
```

## 🎨 材质系统

默认材质包括：

- **Asphalt**：道路沥青材质，深灰色
- **Shoulder**：路肩材质，浅灰色
- **LaneMarkingWhite**：白色车道线
- **LaneMarkingYellow**：黄色车道线

您可以自定义材质属性，如颜色、反光度等。

## ⚙️ 参数说明

### 转换参数

- **xodr_file**：输入的XODR文件路径
- **output_dae**：输出的DAE文件路径
- **textures_dir**：纹理目录路径（可选）
- **step_size**：网格生成步长，默认1.0
  - 较小的值（如0.5）生成更精细的网格
  - 较大的值（如2.0）生成更粗糙的网格，处理更快

## 🚧 限制和注意事项

- 目前支持基本的道路元素，复杂的道路特征可能需要进一步扩展
- 高程和横坡处理采用简化模型
- 车道线生成在某些复杂路口可能需要手动调整

## 🔧 故障排除

### 常见问题

1. **文件不存在错误**
   - 确保输入XODR文件路径正确
   - 确保输出目录存在且有写入权限

2. **网格为空错误**
   - 检查XODR文件格式是否正确
   - 尝试减小step_size参数

3. **DAE导入其他软件失败**
   - 确保DAE文件已成功生成（不为空）
   - 检查目标软件是否支持COLLADA 1.4/1.5格式

## 📝 版本历史

### v1.0.0
- 初始版本
- 支持基本XODR文件解析
- 生成3D道路网格
- 导出COLLADA DAE格式

## 🤝 贡献指南

欢迎贡献代码或报告问题！请遵循以下步骤：

1. Fork本仓库
2. 创建功能分支
3. 提交更改
4. 运行测试确保一切正常
5. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 🌟 致谢

感谢所有为项目做出贡献的开发者和用户！

---

*如有问题或建议，请联系项目维护者。*
