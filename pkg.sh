#!/usr/bin/env bash

set -e
DIR=$(realpath $0) && DIR=${DIR%/*}
cd $DIR
set -x

if [ ! -d ".venv" ]; then
  if ! command -v uv 2>/dev/null; then
    pip install uv
    uv venv
    uv pip install -r requirements.txt pyinstaller
  fi
fi

source .venv/bin/activate

# 定义打包和压缩函数
build_and_compress() {
  local plt=$1
  echo "正在为 ${plt} 平台打包..."

  local plt_dist="dist/${plt}"
  mkdir -p "${plt_dist}"

  # 1. 打包可执行文件
  if [ "$plt" == "win" ]; then
    if command -v wine >/dev/null 2>&1; then
      echo "检测到 Wine，正在执行跨平台打包 (Windows)..."
      wine python -m PyInstaller --onefile --distpath "${plt_dist}" main.py
    else
      echo "警告: 未检测到 Wine 环境，请确保已安装 Wine 以打包 Windows 版本。"
      pyinstaller --onefile --distpath "${plt_dist}" main.py
    fi
  else
    pyinstaller --onefile --distpath "${plt_dist}" main.py
  fi

  # 2. 分发资源文件
  echo "正在为 ${plt} 分发资源..."
  cp AliHYAiHei.ttf "${plt_dist}/"
  cp user.csv "${plt_dist}/"
  cp config.py "${plt_dist}/"
  cp -R ./done/ "${plt_dist}/input"
  mkdir -p "${plt_dist}/out" "${plt_dist}/done"

  # 3. 压缩为 7z
  if command -v 7z >/dev/null 2>&1; then
    echo "正在生成 ${plt}.7z ..."
    (cd dist && 7z a -t7z "${plt}.7z" "${plt}/")
  else
    echo "警告: 未找到 7z 命令，跳过压缩步骤。"
  fi
}

rm -rf dist build

# 执行多平台打包
platforms=("mac" "win")
# platforms=("win")
for plt in "${platforms[@]}"; do
  build_and_compress "${plt}"
done

echo "打包流程已全部完成"
