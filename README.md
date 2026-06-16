# BCacheTranslation

B站客户端缓存视频提取转换工具。自动识别 Bilibili 客户端缓存目录中的 `.m4s` 文件，去除前导零字节填充，通过内置 ffmpeg 重新编码并合并为标准 MP4 文件，支持批量处理和 MP3 音频单独提取。

## 功能

- **自动扫描缓存**：自动检测 Windows 下 B 站客户端默认缓存目录，支持手动拖放文件夹
- **解析视频信息**：读取 `videoInfo.json` 获取标题、时长等元数据，展示封面缩略图
- **宫格预览**：以卡片流式布局展示所有缓存视频，双击查看详情，单击选中
- **文件清理**：去除 B 站 `.m4s` 缓存文件的前导零字节填充
- **格式转换**：内置 ffmpeg，将视频重编码为 H.264，音频重编码为 MP3，最终合并为 MP4
- **MP3 提取**：可单独提取音频为 MP3 文件
- **批量处理**：支持多选视频批量转换，后台线程执行，可随时停止
- **实时监控**：监听缓存目录变化，自动检测新下载的视频
- **暗色主题**：内置 Catppuccin Mocha 风格暗色主题
- **设置持久化**：自动保存用户偏好（输出目录、MP3 提取选项等）

## 系统要求

- **操作系统**：Windows 10/11（64位）
- **无需安装 Python 或 ffmpeg**，开箱即用

## 安装

### 方式一：使用安装包（推荐）

运行 `BCacheTranslation_Setup_x.x.x.exe`，按向导完成安装。可选项包括创建桌面快捷方式和开始菜单快捷方式。

### 方式二：便携版

下载 `BCacheTranslation_Portable_x.x.x.zip`，解压后双击 `BCacheTranslation.exe` 即可运行，所有配置保存在程序目录下。

### 方式三：源码运行

```bash
git clone <your-repo-url>
cd BCacheTranslation
pip install -r requirements.txt
python main.py