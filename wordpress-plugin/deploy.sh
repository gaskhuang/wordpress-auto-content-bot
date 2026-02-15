#!/bin/bash

# Gasker Content Refresher - 部署打包腳本
# 用途: 創建可發布的 WordPress 插件 ZIP 檔案
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 插件資訊
PLUGIN_NAME="gasker-content-refresher"
VERSION="1.0.2"
BUILD_DIR="build"
RELEASE_DIR="release"
ZIP_FILE="${PLUGIN_NAME}-${VERSION}.zip"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gasker Content Refresher - 部署打包${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 清理舊的建置檔案
echo -e "${YELLOW}[1/6]${NC} 清理舊的建置檔案..."
if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
    echo "  ✓ 已刪除舊的 build 目錄"
fi

if [ -d "$RELEASE_DIR" ]; then
    echo "  ✓ release 目錄已存在"
else
    mkdir -p "$RELEASE_DIR"
    echo "  ✓ 已創建 release 目錄"
fi

# 2. 創建建置目錄
echo -e "${YELLOW}[2/6]${NC} 創建建置目錄..."
mkdir -p "$BUILD_DIR/$PLUGIN_NAME"
echo "  ✓ 已創建 $BUILD_DIR/$PLUGIN_NAME"

# 3. 複製必要檔案
echo -e "${YELLOW}[3/6]${NC} 複製必要檔案..."

# 複製主要檔案
cp gasker-content-refresher.php "$BUILD_DIR/$PLUGIN_NAME/"
echo "  ✓ 複製主插件文件"

# 複製 includes 目錄
cp -r includes "$BUILD_DIR/$PLUGIN_NAME/"
echo "  ✓ 複製 includes 目錄"

# 複製 assets 目錄
cp -r assets "$BUILD_DIR/$PLUGIN_NAME/"
echo "  ✓ 複製 assets 目錄"

# 複製文件檔案
cp README.md "$BUILD_DIR/$PLUGIN_NAME/"
cp readme.txt "$BUILD_DIR/$PLUGIN_NAME/"
cp CHANGELOG.md "$BUILD_DIR/$PLUGIN_NAME/"
cp LICENSE "$BUILD_DIR/$PLUGIN_NAME/"
cp INSTALL.md "$BUILD_DIR/$PLUGIN_NAME/"
cp QUICKSTART.md "$BUILD_DIR/$PLUGIN_NAME/"
echo "  ✓ 複製文件檔案"

# 4. 清理不需要的檔案
echo -e "${YELLOW}[4/6]${NC} 清理不需要的檔案..."
cd "$BUILD_DIR/$PLUGIN_NAME"

# 刪除 macOS 檔案
find . -name ".DS_Store" -delete
find . -name "._*" -delete
echo "  ✓ 已刪除 macOS 系統檔案"

# 刪除開發檔案
rm -f .gitignore
echo "  ✓ 已刪除開發檔案"

cd ../..

# 5. 創建 ZIP 檔案
echo -e "${YELLOW}[5/6]${NC} 創建 ZIP 檔案..."
cd "$BUILD_DIR"
zip -r "../$RELEASE_DIR/$ZIP_FILE" "$PLUGIN_NAME" -q
cd ..

if [ -f "$RELEASE_DIR/$ZIP_FILE" ]; then
    FILE_SIZE=$(du -h "$RELEASE_DIR/$ZIP_FILE" | cut -f1)
    echo -e "  ✓ 已創建 ${GREEN}$ZIP_FILE${NC} (${FILE_SIZE})"
else
    echo -e "${RED}  ✗ 創建 ZIP 檔案失敗${NC}"
    exit 1
fi

# 6. 清理建置目錄
echo -e "${YELLOW}[6/6]${NC} 清理建置目錄..."
rm -rf "$BUILD_DIR"
echo "  ✓ 已清理建置目錄"

# 完成
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}打包完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "檔案位置: ${GREEN}$RELEASE_DIR/$ZIP_FILE${NC}"
echo -e "檔案大小: ${GREEN}$(du -h "$RELEASE_DIR/$ZIP_FILE" | cut -f1)${NC}"
echo ""
echo -e "${YELLOW}部署步驟:${NC}"
echo "1. 上傳 $ZIP_FILE 到 WordPress"
echo "2. 前往 插件 → 安裝插件 → 上傳插件"
echo "3. 選擇 ZIP 檔案並安裝"
echo "4. 啟用插件"
echo ""
echo -e "${YELLOW}注意事項:${NC}"
echo "- 請確保已安裝 AI Engine 插件"
echo "- 請在 AI Engine 中設定 API Key"
echo "- 建議先在測試環境測試"
echo ""

exit 0
