# 快速开始指南

## 5分钟上手XODR到DAE转换

### 第一步：准备环境

确保你有Python 3.6+：

```bash
python --version
```

### 第二步：准备输入文件

你需要：
1. 一个XODR文件（例如：test.xodr）
2. （可选）纹理图片文件（如Asphalt1_Diff.png, LaneMarking1_Diff.png）

### 第三步：运行转换

最简单的方法：

```bash
cd road_to_dae_converter
python test_conversion_simple.py
```

或者使用命令行：

```bash
python src/main.py <你的xodr文件> <输出dae文件>
```

**完整示例**：

```bash
# 假设test.xodr在上级目录
cd road_to_dae_converter
python src/main.py ../test.xodr ../output.dae --textures ../
```

### 第四步：查看结果

转换完成后，你会得到一个DAE文件，可以用以下软件打开：
- Blender（推荐）
- Maya
- 3ds Max
- 任何支持COLLADA格式的3D软件

### 完整示例代码

创建一个Python脚本（例如`my_conversion.py`）：

```python
from src.main import convert_xodr_to_dae

# 设置文件路径
xodr_file = "path/to/your/file.xodr"
output_dae = "path/to/output.dae"
textures_dir = "path/to/textures"  # 可选

# 执行转换
success = convert_xodr_to_dae(
    xodr_file=xodr_file,
    output_dae=output_dae,
    textures_dir=textures_dir,
    step_size=1.0  # 1米采样一次，可调整精度
)

if success:
    print(f"转换成功！输出文件：{output_dae}")
else:
    print("转换失败，请检查错误信息")
```

### 常见参数调整

#### 调整网格精度

```python
# 更精细的网格（更多三角形，文件更大）
step_size=0.5

# 更粗糙的网格（更少三角形，文件更小，处理更快）
step_size=2.0
```

#### 添加纹理

将纹理图片放在指定目录，并确保文件名正确：
- `Asphalt1_Diff.png` - 沥青路面纹理
- `LaneMarking1_Diff.png` - 车道线纹理

```python
convert_xodr_to_dae(
    xodr_file="test.xodr",
    output_dae="output.dae",
    textures_dir="./textures",  # 纹理目录
    step_size=1.0
)
```

### 验证转换结果

查看生成的DAE文件应包含：
- 道路表面网格
- 车道标线网格
- 材质定义
- 纹理引用（如果提供了纹理）

在Blender中导入DAE文件：
1. 打开Blender
2. File → Import → Collada (DAE)
3. 选择生成的DAE文件
4. 点击Import

### 故障排除

**问题1：ModuleNotFoundError**

解决方法：确保在正确的目录运行脚本

```bash
cd road_to_dae_converter
python test_conversion_simple.py
```

**问题2：文件未找到**

解决方法：使用绝对路径

```python
import os
xodr_file = os.path.abspath("../test.xodr")
output_dae = os.path.abspath("../output.dae")
```

**问题3：转换成功但DAE文件为空或很小**

解决方法：检查XODR文件是否包含道路数据，可以先用XML编辑器查看

### 下一步

- 查看完整的[README.md](README.md)了解更多功能
- 阅读[API文档](docs/API文档.md)了解详细接口
- 查看[examples/usage_example.py](examples/usage_example.py)了解更多用法

---

**需要帮助？** 请在GitHub提交Issue或查阅项目文档。
