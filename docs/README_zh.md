<p align="center">
  <img width="15%" align="center" src="app/resource/images/logo.png" alt="logo">
</p>
  <h1 align="center">
  Fluent M3U8
</h1>
<p align="center">
  基于 PySide6 的跨平台 m3u8 下载软件
</p>

<p align="center">

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.11.11-blue.svg?color=00B16A" alt="Python 3.11.11"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/PySide-6.4.2-blue?color=00B16A" alt="PySide 6.4.2"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Win32%20|%20Linux%20|%20macOS-blue?color=00B16A" alt="Platform Win32 | Linux | macOS"/>
  </a>
</p>

<p align="center">
<a href="../README.md">English</a> | 简体中文
</p>

![界面](./screenshot/主界面.png)

## 特性

* **多线程并发下载**：充分利用带宽资源，实现极速下载体验
* **智能下载管理**：实时监控下载进度，提供便捷的任务管理功能
* **高度可定制**：提供基础与高级配置选项，满足从入门到专业用户的不同需求
* **现代化界面设计**：基于 Fluent Design 设计语言，界面简洁优雅、直观易用


## 快速开始
1. 创建虚拟环境:

    ```shell
    conda create -n fluent-m3u8 python=3.11
    conda activate fluent-m3u8
    pip install -r requirements.txt
    ```

2. 下载 [FFmpeg](https://www.ffmpeg.org/download.html) 和 [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE)

3. 将 ffmpeg 和 N_m3u8DL-RE 的可执行文件放在 `tools` 目录下.

3. 启动 Fluent M3U8:

    ```shell
    conda activate fluent-m3u8
    python Fluent-M3U8.py
    ```


## 致谢

- [zhiyiYo/PyQt-Fluent-Widgets](https://qfluentwidgets.com/zh/)：强大、可扩展、美观优雅的 Fluent Design 风格组件库
- [nilaoda/N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE)：跨平台且功能强大的 MPD/M3U8/ISM 下载器

## 许可证
Fluent-M3U8 使用 GPLv3 许可证进行授权。

版权所有 © 2025 by zhiyiYo.
