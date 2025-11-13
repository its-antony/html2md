#!/bin/bash
# 安装GUI依赖脚本

echo "🎨 安装GUI依赖"
echo "=================="
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "✓ 使用现有虚拟环境"
    source venv/bin/activate
else
    echo "✓ 创建虚拟环境"
    python3 -m venv venv
    source venv/bin/activate
fi

echo ""
echo "📦 选择要安装的GUI库："
echo "  1) Gradio（推荐：最简单，界面美观）"
echo "  2) PyQt6（推荐：专业桌面应用）"
echo "  3) 全部安装"
echo "  4) 仅Tkinter（无需安装，Python自带）"
echo ""
read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "📥 安装Gradio..."
        pip install gradio
        echo ""
        echo "✅ Gradio安装完成！"
        echo "运行: python gui_gradio.py"
        ;;
    2)
        echo ""
        echo "📥 安装PyQt6..."
        pip install PyQt6
        echo ""
        echo "✅ PyQt6安装完成！"
        echo "运行: python gui_pyqt.py"
        ;;
    3)
        echo ""
        echo "📥 安装所有GUI库..."
        pip install gradio PyQt6
        echo ""
        echo "✅ 全部安装完成！"
        echo "运行Gradio: python gui_gradio.py"
        echo "运行PyQt6: python gui_pyqt.py"
        echo "运行Tkinter: python gui_tkinter.py"
        ;;
    4)
        echo ""
        echo "✅ Tkinter是Python标准库，无需安装"
        echo "运行: python gui_tkinter.py"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 完成！"
