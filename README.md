# 胖乖生活积分助手

一个基于 Python 的工具，用于批量完成“胖乖生活”日常积分任务。支持多账号、实时彩色日志、一键启停，并已打包为独立 EXE 运行，无需安装 Python 环境。

> ⚠️ **免责声明**：本项目仅供学习交流 Python 网络编程与 GUI 开发使用，请勿用于任何违规用途。使用者需自行承担因使用本工具产生的一切后果。

---

## 使用方法

### 获取 Token 和 UA

1. **获取 Token**：
   * 在电脑浏览器中打开：`https://h5user.qiekj.com/integral/activity`
   * 登录后，网址后会显示 `token=？？？？？`，复制等于号 `=` 后面的所有内容。
2. **获取 UA**：
   * 在手机浏览器中打开：`https://tool.ip138.com/useragent/`
   * 复制 **“客户端获取的UserAgent”** 下方显示的内容。

### 方式一：直接运行 EXE（推荐）

1. 前往 [Releases](https://github.com/PoorKid1112/PangguaiHelper/releases) 页面下载最新版 `胖乖生活积分助手.exe`。
2. 双击运行，填入 Token 和其他选项，点击“开始执行”即可。
3. **完全无需安装 Python 或任何库**，Windows 7 及以上系统直接可用。

### 方式二：从源码运行

#### 环境要求

* Python 3.7+
* 依赖库：`requests`（见 `requirements.txt`）

```shell
# 克隆仓库
git clone https://github.com/PoorKid1112/PangguaiHelper.git
cd PangguaiHelper

# 安装依赖
pip install -r requirements.txt

# 运行程序
python 胖乖生活积分助手.py
