# CAJ Converter Web

一个基于 FastAPI + JavaScript 的 CAJ 批量转 PDF Web 工具，解决知网 CAJ 文件难以转换的痛点。

## 🌐 在线演示

🚀 **[点击这里体验在线版本](https://caj-converter.onrender.com/)**

---

## 📷 项目展示

![CAJ Converter 界面截图](assets/screenshot.png)

> *提示：运行本地项目后截图保存到 assets/screenshot.png*

## ✨ 功能特性

- 📁 **批量上传**：支持拖拽多个 CAJ 文件
- ⚡ **自动转换**：后台自动处理，无需人工干预
- 📊 **实时进度**：显示转换进度和状态
- 📦 **批量下载**：一键下载所有转换后的 PDF
- 🔒 **本地处理**：文件仅在本地处理，不上传到云端
- 🎨 **美观界面**：现代化的 Web 界面

## 🔧 技术栈

- **后端**：Python + FastAPI
- **前端**：HTML + Tailwind CSS + JavaScript
- **转换核心**：caj2pdf 库
- **部署**：Render（免费云平台）

## 📁 项目结构

```
caj_converter/
├── backend/          # 后端代码
│   ├── main.py       # FastAPI 服务主程序
│   ├── cajparser.py  # CAJ 文件解析器
│   ├── utils.py      # 工具函数
│   ├── pdfwutils.py  # PDF 处理工具
│   ├── HNParsePage.py # HN 格式解析
│   ├── jbigdec.py    # JBIG 解码
│   └── jbig2dec.py   # JBIG2 解码
├── frontend/         # 前端代码
│   └── static/       # 静态文件
│       └── index.html # Web 界面
├── lib/              # caj2pdf 库
│   └── bin/          # Windows DLL 文件
├── requirements.txt  # Python 依赖
├── start.bat         # 启动脚本
├── .gitignore        # Git 忽略配置
└── README.md         # 本文件
```

## 🚀 快速开始

### 方法一：在线体验（推荐）
🌐 直接访问：https://caj-converter.onrender.com/

### 方法二：一键启动（本地）
1. 双击 `start.bat` 文件
2. 自动打开浏览器访问 http://127.0.0.1:8000

### 方法三：手动启动（开发者）
```bash
# 1. 打开终端，进入项目目录
cd caj_converter

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python backend/main.py

# 4. 访问 http://127.0.0.1:8000
```

##  使用说明

1. **上传文件**：拖拽 CAJ 文件到上传区域，或点击选择文件
2. **等待转换**：系统会自动处理，显示实时进度
3. **下载文件**：转换完成后点击下载按钮获取 PDF
4. **批量操作**：可以同时处理多个文件，支持批量下载

## 🎯 适用场景

- 📚 学术研究：批量转换知网文献
- 🎓 学生学习：将 CAJ 转为 PDF 方便阅读
- 💼 办公文档：统一文档格式

## 🔍 常见问题

**Q: 转换失败怎么办？**
A: 确保 CAJ 文件完整，尝试重新上传

**Q: 支持哪些格式？**
A: 支持 .caj、.kdh、.nh 格式

**Q: 文件大小限制？**
A: 单个文件最大 50MB

**Q: 是否需要 CAJViewer？**
A: 不需要，使用 caj2pdf 库实现转换

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**🎉 祝您使用愉快！**