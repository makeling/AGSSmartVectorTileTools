# 矢量切片自动优化工具集使用说明

## 1 优化思想

​	可以想象我们乘坐飞机，鸟瞰大陆和海洋，随着飞机飞行高度的下降，地物从无到有，从小黑点儿逐渐显现轮廓，就像我们在浏览地图时从小比例尺逐步放大到大比例尺地图一样。在大数据时代，数据爆炸式增长，数据就像能源一样驱动着智能，如何在地图上展现地理大数据？将千万甚至上亿的数据同时显示在地图上，是否有意义？如果不是特别必要，那哪些数据应该显示，哪些数据应该隐藏？带着这些问题，借鉴飞机鸟瞰逐级显化的思想，这个工具包实现了对千万级数据量矢量切片的自动优化，按照比例尺级别逐级显示数据，在小比例尺保留数据的趋势，兼顾性能和信息量，在大比例尺显示细节，从而实现通过矢量切片在一个屏幕上展现千万级地理要素的能力。

## 2 工具使用说明

### 2.1 CalculateLodsTool

功能说明：按照当前地图范围，通过算法计算每个要素起始显示的比例尺级别。

工具窗口： 

![vtpk_calculatelods](https://raw.githubusercontent.com/makeling/makeling.github.io/master/img/blog_imgs/vtpk_calculatelods.png)

输入参数：

Input Map： 输入需要优化的地图

Input Layers： 输入需要优化的图层，支持多图层同时优化。

输出结果：

在优化图层上新增LOD字段，存储每个要素显示的最小比例尺级别。

注意事项：

工具会直接修改输入图层数据源，为了确保原有数据的安全，建议在执行工具前，自行做好数据备份。

### 2.2 GenerateBGLayerTool

功能说明：为大数据面图层计算生成背景底图。

工具窗口：

![vtpk_generatebglayer](https://raw.githubusercontent.com/makeling/makeling.github.io/master/img/blog_imgs/vtpk_generatebglayer.png) 

输入参数：

Input Map： 输入需要优化的地图

Input Layers： 输入需要优化的图层，支持多图层同时优化。

输出结果：

会生成新的面图层，结果以”图层名_background”输出，这个图层会被自动添加到地图，并排在优化图层之后。

### 2.3 RepairSymbologyTool

功能说明：修正原有地图的配图模版：

​         - 简单渲染更新为唯一值渲染，渲染字段为“lod”，遍历修复每个符号的值为原有简单渲染的符号值，以保证渲染效果和原图一致。

​	- 如果图层渲染是唯一值渲染，新增渲染字段“lod”, 遍历修复符号组的符号和原有渲染效果匹配。

工具窗口： 

![vtpk_repairsymbologytool](https://raw.githubusercontent.com/makeling/makeling.github.io/master/img/blog_imgs/vtpk_repairsymbologytool.png)

输入参数：

Input Map： 输入需要优化的地图

Input Layers： 输入需要优化的图层，支持多图层同时优化。

Save A Copy： 确认是否保存一个副本。

输出结果：

优化后的地图符号渲染，显示效果和原有地图一致，但是这个地图具备分级显示矢量要素的能力。

### 2.4 RepairVTPKStyleTool

功能说明：这个工具是针对生成好的VTPK自动修复root.style 文件中的最小显示比例尺参数minzoom，以确保每个图层可以按照lod级别分级显示。

工具窗口： 

![vtpk_repairvtpkstyletool](https://raw.githubusercontent.com/makeling/makeling.github.io/master/img/blog_imgs/vtpk_repairvtpkstyletool.png)

输入参数：

in vtpk: 输入待优化的矢量切片包。

输出结果：

原输入的矢量切片包。

注意事项：

工具并不会自动备份输入的矢量切片包，为了安全，建议在执行工具前自行做好切片包备份。

### 2.5 SmartOptimizeVTPKTool

功能说明：这是一个一键式的自动化优化工具，完整的执行优化矢量切片包的各个环节，顺次执行：

   - CalculateLodsTool

   - GenerateBGLayerTool

   - RepairSymbobogyTool

   - Generate VTPK

   - RepairVTPKStyleTool

工具窗口： 

![vtpk_smartoptimizevtpktool](https://raw.githubusercontent.com/makeling/makeling.github.io/master/img/blog_imgs/vtpk_smartoptimizevtpktool.png)

输入参数：

Input Map： 输入需要优化的地图。

Input Layers： 输入需要优化的图层，支持多图层同时优化。

Save A Copy： 确认是否保存一个副本。

out vtpk: 输出矢量切片包路径。

输出结果：

优化后的矢量切片包

经过这个工具集处理生成的矢量切片包可以承载千万级以上点线面数据的流畅展示。每个工具可独立使用，为了方便也可以运行整合后的一键式优化工具，自动完成所有环节。