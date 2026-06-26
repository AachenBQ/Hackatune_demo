# 虚拟摄像头使用指南

## 问题

系统是 **WSL2 (Windows Subsystem for Linux 2)** 环境，Windows 主机上的摄像头无法直接被 WSL2 Linux 子系统访问。这是 WSL2 的一个已知限制。

## 解决方案

已提供两个解决方案：

### 方案 1：使用虚拟摄像头（推荐用于测试）

虚拟摄像头生成器可以生成模拟手部移动的视频帧，用于测试手势识别和情绪映射功能。

**启动虚拟摄像头模式：**

```bash
cd /home/bowen/Hackatune
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture swipe
```

**可用的手势模式：**
- `swipe` - 左右挥动（默认）
- `circle` - 圆形运动
- `tap` - 上下点击
- `fist` - 握拳 (大小变化)

**在运行过程中切换手势：**
- 按空格键切换不同的手势模式
- 按 Q 退出

### 方案 2：启用 WSL2 USB 摄像头转发（使用真实摄像头）

如果你有 USB 摄像头并想在 WSL2 中使用，需要执行以下步骤：

#### 步骤 1：在 Windows 上安装 usbipd

```powershell
# 以管理员身份在 PowerShell 中运行
winget install usbipd
```

#### 步骤 2：在 WSL2 中安装 usb 工具

```bash
sudo apt update
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools-*/usbip 20
```

#### 步骤 3：识别并转发摄像头

```powershell
# 在 Windows PowerShell（管理员）中，列出所有 USB 设备
usbipd list

# 找到你的摄像头设备（通常是 Integrated Camera），记下 BUSID
# 然后执行转发：
usbipd attach --wsl --busid <BUSID>
# 例如：usbipd attach --wsl --busid 3-9
```

#### 步骤 4：在 WSL2 中验证摄像头

```bash
ls -la /dev/video*
```

如果成功，你应该看到 `/dev/video0` 等设备。

#### 步骤 5：启动带实际摄像头的程序

```bash
cd /home/bowen/Hackatune
.venv/bin/python mic_fft_demo_gui.py
```

## 功能说明

### 音频处理
- 实时麦克风捕获 (44.1 kHz)
- FFT 频谱分析 (80 Hz - 2000 Hz)
- MIDI 音符识别

### 手势识别（虚拟摄像头中的手势演示）
| 手势 | 情绪 | 音乐动作 |
|------|------|---------|
| Fist (握拳) | Calm | Music stops |
| Fast Swipe (快速挥动) | Excited/Focused | Drums get denser / Increase energy |
| Double Open (双手张开) | Relieved | Enter chorus / Drop |
| Tap (点击) | Playful | Add kick / Snare |
| Circle (圆形) | Focused | Loop current pattern |
| Double Close (双手握拳) | Tense | Chords tighten |
| Open Up (向上张开) | Anticipation | Filter opens / Volume rises |

### 虚拟摄像头手势演示

虚拟摄像头可以自动演示各种手势运动模式，帮助你理解手势识别系统的工作原理。

## 命令行选项

```bash
.venv/bin/python mic_fft_demo_gui.py --help

选项:
  --samplerate INT          音频采样率 (默认: 44100)
  --blocksize INT           音频块大小 (默认: 4096)
  --channels INT            音频通道数 (默认: 1 - 单声道)
  --virtual-camera         使用虚拟摄像头 (用于没有硬件摄像头的系统)
  --gesture {swipe,circle,tap,fist}  虚拟摄像头演示的手势 (默认: swipe)
```

## 故障排除

### 虚拟摄像头显示"Camera unavailable"

这通常意味着虚拟摄像头生成器没有正确导入。请确保：
1. `virtual_camera_gen.py` 文件在同一目录中
2. 文件未被修改
3. 没有导入错误

### 实际摄像头仍然显示"Camera unavailable"

1. 检查摄像头设备：`ls -la /dev/video*`
2. 检查权限：`sudo usermod -aG video $USER`（然后重新打开终端）
3. 测试 OpenCV 摄像头访问：
   ```bash
   .venv/bin/python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera ready' if cap.isOpened() else 'Camera failed')"
   ```

### USB 摄像头与 WSL2 集成问题

- 确保在 PowerShell 中执行 `usbipd` 命令时使用管理员权限
- 如果附加失败，尝试从 Windows 设备管理器检查摄像头是否被其他应用占用
- 如果需要分离设备：`usbipd detach --busid <BUSID>`

## 开发和测试

### 测试虚拟摄像头生成器

可以单独运行虚拟摄像头生成器来查看它的输出：

```bash
.venv/bin/python virtual_camera_gen.py
```

然后在窗口中按空格键切换手势，按 Q 退出。

### 同时显示摄像头和音频可视化

主程序 `mic_fft_demo_gui.py` 同时显示：
- 左侧：摄像头画面 + 手势识别结果
- 右侧：实时 FFT 频谱图
- 顶部：当前主频率和音符
- 文本：识别的手势、情绪和音乐动作结果

## 性能提示

- 虚拟摄像头的帧率为 30 FPS
- 音频采样率为 44.1 kHz，块大小为 4096 字节 (约 93ms 延迟)
- 如果 Tkinter GUI 卡顿，可以尝试增加 FFT 的 --blocksize 参数

##后续优化

如果完全集成后需要：
1. 添加更多手势识别模式
2. 集成真实的音乐生成引擎 (例如使用 PYO 或其他合成库)
3. 添加手势到 MIDI 映射
4. 实现实时音效处理 (混响、延迟、过滤等)
