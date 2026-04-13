# PDF-Master

全能型 PDF 处理 Claude Code 插件。

## 功能

- **解析提取**：文本、表格、图片、元数据
- **编辑修改**：合并、拆分、旋转、水印
- **格式转换**：PDF -> Word/Excel/图片/Markdown
- **AI 增强**：智能摘要、文档问答、翻译
- **OCR**：扫描件识别
- **LaTeX**：LaTeX -> PDF
- **安全权限**：加密、解密、签名、涂抹

## 安装

```bash
# 克隆仓库
git clone https://github.com/zshyc/pdf-master.git
cd pdf-master

# 安装依赖
pip install -r requirements.txt
```

## 使用

在 Claude Code 中使用 `/pdf` 命令：

```
/pdf extract document.pdf
/pdf merge file1.pdf file2.pdf -o merged.pdf
/pdf summarize document.pdf
```

## 许可证

MIT License
