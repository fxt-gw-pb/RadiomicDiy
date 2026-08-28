# 医学影像 AI 自学室

一个面向医学、公共卫生与临床科研背景学习者的**医学影像 AI / 影像组学自学知识库**的网页版。

🔗 **在线阅读：** https://fxt-gw-pb.github.io/RadiomicDiy/

## 现在有什么

| 模块 | 内容 | 篇数 |
|---|---|---|
| 00 学习导航 | 全景图、使用方法、学习顺序、按需补数学 | 4 |
| 01 医学影像基础 | X 线/DR、CT、HU 与窗、MRI、超声、PET、病理、voxel、解剖平面、spacing、domain shift | 13 |
| 02 影像文件与工具 | DICOM、NIfTI、NRRD/MHA 与标注格式、dcm2niix、PACS、去标识化、Slicer、ITK-SNAP、ROI、数据目录 | 13 |
| 03 Python 医学图像处理 | NumPy、pydicom、SimpleITK、nibabel、CT / mask / 叠加显示 | 8 |
| 04 医学图像预处理 | 重采样、插值、归一化、窗宽窗位、裁剪、滤波、阈值、形态学、数据增强 | 11 |
| 05 Radiomics | 总体思想与工作流、一阶 / 形状特征、五类纹理矩阵、Wavelet 与 LoG、灰度离散化、PyRadiomics、IBSI、Delta Radiomics | 16 |
| 06 Radiomics 统计与机器学习 | 过拟合、ICC、标准化与筛选、七类模型、交叉验证与超参数搜索 | 17 |
| 07 医学 AI 模型评价 | 划分与泄漏、AUC、阈值指标、校准、外部验证、SHAP、决策曲线 | 16 |
| 08 PyTorch 与 CNN | 张量、Dataset、训练循环、卷积、感受野、BatchNorm、激活 | 15 |
| 09 ResNet 与迁移学习 | 残差连接、ResNet-18/34/50、预训练、特征提取与 fine-tuning | 8 |
| 10 医学图像分割与 U-Net | 任务定义、encoder/decoder/skip、Dice/IoU、loss 与类别不平衡 | 15 |
| 附 | 术语表、学习清单 | 2 |

模块 11 起规划中，见站内「后续模块」。

## 网页特点

- **首页是一台可交互的阅片器**：拖动窗宽窗位滑块，或点软组织窗 / 肺窗 / 骨窗 / 脑窗，
  鼠标移到图上可读出该点 HU。同一份数据换个窗就完全变样——这正是第 01 模块的第一课。
- **单文件、零外部依赖**：图片全部以 WebP data URI 内嵌，下载下来断网也能看。
- 学习进度、明暗主题存在浏览器本地，不上传任何数据。
- 章节搜索、页内目录、← → 翻页、代码一键复制。

## 重新构建

网页由知识库的 Markdown 编译而成：

```bash
export MIA_ROOT=/path/to/medical_imaging_ai_selfstudy
python build/build.py
```

需要 `Pillow`（用于压缩内嵌图片）。产出 `radiomics_site.html`，
部署时改名为 `index.html` 覆盖仓库根目录即可。

| 文件 | 职责 |
|---|---|
| `build/build.py` | 页面骨架、导航、首页、路由与前端逻辑 |
| `build/structure.py` | 模块与章节顺序、后续模块路线图 |
| `build/mdconv.py` | Markdown → HTML（表格、代码高亮、数学、图片内嵌） |
| `build/build_css.py` | 设计 token 与全部样式 |

新增模块只需在 `structure.py` 的 `MODULES` 里加一段并从 `ROADMAP` 删掉对应行，
导航、进度、搜索、翻页、页内目录都会自动跟上。

## 说明

- 站内插图由 AI 生成后经人工核对，用于教学示意，**不是临床影像**，不可用于诊断。
- 示例代码与合成数据仅供学习，不用于临床决策。
- 正文中的事实性内容标注了来源（官方文档、DICOM 标准、同行评议文献）。
