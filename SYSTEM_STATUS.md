# Hackatune - 系统配置完成总结

## ✅ 系统状态

### 已解决的问题
1. **摄像头不可用**: WSL2 环境中无法直接访问 Windows 主机摄像头
   - ✓ 解决方案: 已创建虚拟摄像头生成器，可立即测试所有功能
   - ✓ 替代方案: 提供 USB 摄像头转发配置指南

2. **音频处理**: 已完全实现且可工作
   - ✓ 麦克风输入: 44.1kHz, 单声道
   - ✓ FFT 频谱分析: 80Hz-2000Hz 范围
   - ✓ 音符识别: MIDI 标准映射

3. **手势识别**: 已完全实现
   - ✓ 基于 OpenCV 的皮肤检测
   - ✓ 轮廓分析和手指计数
   - ✓ 轨迹分析 (挥动、点击、圆形)
   - ✓ 情绪→音乐动作映射

## 📂 项目文件结构

```
/home/bowen/Hackatune/
├── .venv/                          # Python 3.12 虚拟环境
├── mic_fft_demo_gui.py            # 主程序 - Tkinter GUI 应用
├── mic_fft_demo.py                # 备选 - 终端版本 FFT 显示
├── virtual_camera_gen.py          # 虚拟摄像头生成器
├── demo_virtual_camera.py         # 虚拟摄像头演示脚本
├── run_virtual_camera.sh          # 快速启动脚本
├── QUICK_START.sh                 # 快速启动指南
├── README_VIRTUAL_CAMERA.md       # 详细文档
├── requirements.txt               # 依赖列表
└── .gitignore                     # Git 忽略配置
```

## 🚀 使用方法

### 方案 1: 使用虚拟摄像头（推荐）

虚拟摄像头会生成模拟的手部移动图像，用于演示手势识别功能。

**启动程序:**
```bash
cd /home/bowen/Hackatune
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture swipe
```

**选择手势模式:**
```bash
# swipe - 左右挥动（默认）
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture swipe

# circle - 圆形运动
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture circle

# tap - 上下点击
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture tap

# fist - 握拳
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture fist
```

### 方案 2: 演示虚拟摄像头功能

快速查看虚拟摄像头的所有手势演示:
```bash
.venv/bin/python demo_virtual_camera.py
```

### 方案 3: 尝试使用真实摄像头

如果已设置 USB 摄像头转发，直接启动:
```bash
.venv/bin/python mic_fft_demo_gui.py
```

## 📊 GUI 界面说明

### 左侧面板 (520×360px)
- **视频显示**: 实时摄像头画面 (虚拟或真实)
- **手势识别**: 当前识别的手势
- **情绪输出**: 对应的情感状态
- **音乐动作**: 触发的音乐操作指令

### 右侧面板 (760×520px)
- **FFT 频谱**: 实时频率分析
- **峰值频率**: 当前主频率 (Hz)
- **音符显示**: 对应的乐器音符 (C, C#, D, ... 等)
- **频谱柱状图**: 彩色表示幅度

### 顶部信息栏
```
Mic + Gesture Music Visualizer
Peak: 440.5 Hz   Note: A4
Gesture: tap   Emotion: playful
Music result: add kick / snare
```

## 🎮 手势→情绪→音乐映射表

| 手势 | 英文 | 情绪 | 音乐动作 |
|------|------|------|---------|
| 握拳 | Fist | Calm | Music stops |
| 快速挥动 | Fast Swipe | Excited | Drums get denser |
| 双手张开 | Double Open | Relieved | Enter chorus / Drop |
| 点击 | Tap | Playful | Add kick / Snare |
| 圆形 | Circle | Focused | Loop current pattern |
| 双手握拳 | Double Close | Tense | Chords tighten |
| 向上张开 | Open Up | Anticipation | Filter opens / Volume rises |
| 空闲 | Idle | Neutral | Standby |

## ⚙️ 技术参数

### 音频处理
- **采样率**: 44100 Hz
- **块大小**: 4096 字节
- **通道数**: 1 (单声道)
- **频率范围**: 80 Hz - 2000 Hz
- **FFT 窗口**: Hanning
- **音符参考**: A4 = 440 Hz (国际标准音)

### 视频处理
- **分辨率**: 640×480 (输入) → 520×360 (显示)
- **帧率**: 30 FPS
- **颜色空间**: BGR (OpenCV) → HSV (皮肤检测)
- **皮肤颜色范围**: 
  - H: 0-20, 156-180
  - S: 10-40
  - V: 60-255

### 手势检测算法
1. **皮肤提取**: HSV 颜色空间阈值分割
2. **轮廓检测**: OpenCV 轮廓查找和近似
3. **手指计数**: 凸包点和凸性缺陷分析
4. **轨迹追踪**: 中心点坐标时间序列
5. **手势分类**: 手指数量 + 移动速度 + 轨迹形状

## 🔧 依赖库

```
numpy           # 数值计算
scipy           # FFT 频谱分析
librosa         # 音频处理
soundfile       # WAV 文件 I/O
pydub           # 音频格式转换
audioread       # 音频文件读取
sounddevice     # 实时麦克风输入
opencv-python   # 图像处理和手势检测
matplotlib      # 数据可视化
PIL/Pillow      # 图像处理
tkinter         # GUI 框架
```

## 📝 命令行参数

```bash
.venv/bin/python mic_fft_demo_gui.py [OPTIONS]

OPTIONS:
  --samplerate INT              音频采样率 (默认: 44100)
  --blocksize INT               音频块大小 (默认: 4096)
  --channels INT                音频通道数 (默认: 1)
  --virtual-camera             使用虚拟摄像头 (推荐)
  --gesture {swipe,circle,tap,fist} 虚拟摄像头手势模式 (默认: swipe)
  --help                        显示帮助信息
```

## 🎯 功能演示实例

### 演示场景 1: 探索音频频谱
```bash
# 启动程序并对着麦克风演唱 "啦、啦、啦"
.venv/bin/python mic_fft_demo_gui.py --virtual-camera
# 观察右侧频谱图中的频率变化和音符识别结果
```

### 演示场景 2: 测试手势识别
```bash
# 使用虚拟摄像头的"圆形"手势模式
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture circle
# 观察手势识别和对应的情绪、音乐动作
```

### 演示场景 3: 连续演示所有手势
```bash
# 运行演示脚本
.venv/bin/python demo_virtual_camera.py
# 自动演示所有 4 种手势模式
```

## 🐛 故障排除

### 问题: GUI 窗口不出现

**检查显示环境:**
```bash
echo $DISPLAY
```

**解决方案:**
- 如果无输出或显示为空，设置 X11 转发
- WSL2 用户: 确保安装了 WSLg 或配置了 X11 服务器

### 问题: "Camera unavailable" 消息

**解决方案:**
- 虚拟摄像头模式: 使用 `--virtual-camera` 参数
- 真实摄像头: 检查 `/dev/video*` 是否存在
- USB 转发: 参考 `README_VIRTUAL_CAMERA.md` 中的 USB 转发配置

### 问题: 麦克风无输入

**检查麦克风:**
```bash
.venv/bin/python -c "import sounddevice; print(sounddevice.default_microphone)"
```

**列出可用设备:**
```bash
.venv/bin/python -c "import sounddevice; print(sounddevice.query_devices())"
```

### 问题: 手势识别不工作

**检查摄像头输入:**
1. 确保虚拟摄像头已启动或真实摄像头可用
2. 调整光线条件（皮肤检测对光线敏感）
3. 尝试在相机 1-1.5 米范围内做出手势

## 📚 延伸阅读

- [README_VIRTUAL_CAMERA.md](README_VIRTUAL_CAMERA.md) - 详细的虚拟摄像头和 USB 转发配置指南
- [OpenCV 皮肤检测文档](https://docs.opencv.org/master/d3/db4/tutorial_py_morphological_ops.html)
- [Tkinter Canvas 参考](https://docs.python.org/3/tkinter/#canvas)
- [SciPy FFT 文档](https://docs.scipy.org/doc/scipy/reference/fft.html)

## ✨ 下一步建议

1. **实时音乐生成**
   - 集成 PYO 或 python-rtmidi 库
   - 根据手势触发预定义的 MIDI 序列

2. **更多手势模式**
   - 添加拇指检测
   - 实现多手相互作用

3. **音效处理**
   - 集成音效库 (混响、延迟、失真等)
   - 手势→音效参数映射

4. **机器学习改进**
   - 使用 OpenPose 或 MediaPipe 更精确的骨骼检测
   - 用神经网络进行手势分类

5. **数据可视化增强**
   - 添加实时波形显示
   - 显示手部骨骼点

---

**系统配置日期**: 2024-12-19
**Python 版本**: 3.12.3
**环境**: WSL2 (Ubuntu 24.04)
**显示**: X11 (:0) - 支持 GUI

