# Tk-Nonogram

## 介绍

使用 `tkinter` 库制作的数织游戏。

## 使用方法

### 一般用户

前往 [GitHub Releases](https://github.com/Dragon1573/Tk-Nonogram/releases/tag/v0.4.0) ，下载最新版本的可执行二进制文件。

> [!TIP]
>
> 目前已支持以下操作系统和架构：
>
> |         |       amd64        |        i386        |       arm64        |
> | :-----: | :----------------: | :----------------: | :----------------: |
> | Windows | :heavy_check_mark: | :heavy_check_mark: |                    |
> |  macOS  | :heavy_check_mark: |                    | :heavy_check_mark: |
> |  Linux  | :heavy_check_mark: |                    |                    |

### 进阶用户（全平台开发者）

> [!TIP]
>
> 此项目使用 [PDM](https://pdm-project.org/en/stable/) 进行管理，请您提前准备 Python v3.11 和 PDM 环境。

```powershell
# 使用 SSH Clone (推荐)
git clone --progress git@github.com:Dragon1573/tk-nonogram.git
# 使用 HTTPS Clone
git clone --progress https://github.com/Dragon1573/tk-nonogram.git
# 中国大陆用户使用 SSH Clone (推荐)
git clone --progress git@gitee.com:Dragon1573/tk-nonogram.git
# 中国大陆用户使用 HTTPS Clone
git clone --progress https://gitee.com/Dragon1573/tk-nonogram.git

# 切换到项目目录
cd ./tk-nonogram

# 安装依赖项（仅运行）
pdm install --prod

# 启动运行（源文件模式）
pdm run play

# 安装依赖项（编译构建）
pdm install

# 安装提交钩子，用于自动格式化代码
pdm run git

# 编译构建
pdm run ci
pdm run build Numzle

# 启动运行（Windows 编译产物模式）
./dist/Numzle.exe
# 启动运行（macOS/Linux 编译产物模式）
./dist/Numzle
```

## 应用截图

![开发模式截图](assets/dev_launch.png)
