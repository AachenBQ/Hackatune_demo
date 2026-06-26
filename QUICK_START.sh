#!/bin/bash
# ============================================================
# Hackatune - 麦克风 + 手势识别 音乐可视化系统
# ============================================================
# 
# 这个脚本提供系统当前状态和使用说明
# 

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Hackatune - 麦克风 + 手势识别系统               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查环境
echo "📋 系统检查..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d ".venv" ]; then
    echo "✓ Python 虚拟环境: 已安装"
    PYTHON=".venv/bin/python"
else
    echo "✗ Python 虚拟环境: 未安装"
    exit 1
fi

if [ -f "virtual_camera_gen.py" ]; then
    echo "✓ 虚拟摄像头生成器: 已安装"
else
    echo "✗ 虚拟摄像头生成器: 缺失"
    exit 1
fi

if [ -f "mic_fft_demo_gui.py" ]; then
    echo "✓ 主程序: 已安装"
else
    echo "✗ 主程序: 缺失"
    exit 1
fi

echo ""
echo "🎯 可用命令："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 演示虚拟摄像头功能："
echo "   $PYTHON demo_virtual_camera.py"
echo ""
echo "2. 启动完整程序 (虚拟摄像头)："
echo "   $PYTHON mic_fft_demo_gui.py --virtual-camera --gesture swipe"
echo ""
echo "   支持的手势模式:"
echo "     • swipe   - 左右挥动（推荐）"
echo "     • circle  - 圆形运动"
echo "     • tap     - 上下点击"
echo "     • fist    - 握拳 (大小变化)"
echo ""
echo "3. 尝试使用真实摄像头（需要USB转发）："
echo "   $PYTHON mic_fft_demo_gui.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📚 详细文档："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "查看: README_VIRTUAL_CAMERA.md"
echo ""

echo "🎮 功能说明："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 左侧面板 - 摄像头画面"
echo "   • 显示实时视频（虚拟或真实）"
echo "   • 显示识别的手势"
echo "   • 显示对应的情绪"
echo "   • 显示触发的音乐动作"
echo ""
echo "📈 右侧面板 - 音频频谱"
echo "   • 实时 FFT 频谱分析"
echo "   • 显示当前主频率和对应音符"
echo "   • 频率范围: 80Hz - 2000Hz (人声/乐器范围)"
echo ""
echo "🎵 音频处理"
echo "   • 采样率: 44.1 kHz"
echo "   • 块大小: 4096 字节"
echo "   • 音符识别: MIDI 标准"
echo ""
echo "🖐️ 手势识别映射"
echo "   ├─ Fist (握拳)          → Calm      → Music stops"
echo "   ├─ Fast Swipe (快速挥动) → Excited   → Drums denser"
echo "   ├─ Double Open (双手开) → Relieved  → Enter chorus"
echo "   ├─ Tap (点击)           → Playful   → Add kick/snare"
echo "   ├─ Circle (圆形)        → Focused   → Loop pattern"
echo "   ├─ Double Close (双手闭) → Tense     → Chords tighten"
echo "   └─ Open Up (向上张开)   → Anticipation → Filter opens"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🚀 快速开始:"
echo "   $PYTHON mic_fft_demo_gui.py --virtual-camera"
echo ""
echo "⏹️  按 Q 或关闭窗口退出"
echo ""
