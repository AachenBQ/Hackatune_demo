#!/bin/bash
# 启动虚拟摄像头手势识别演示

cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "错误: 虚拟环境不存在"
    exit 1
fi

# 获取手势模式参数（默认为 swipe）
GESTURE=${1:-swipe}

echo "启动虚拟摄像头演示 - 手势模式: $GESTURE"
echo "按 Q 退出程序"
echo ""

# 启动程序
.venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture "$GESTURE"
