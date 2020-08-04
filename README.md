<p align="center">
  <a href="https://github.com/yanglbme/gitee-pages-action">
    <img src="./images/logo.png">
  </a>
</p>
<h1 align="center">Gitee Pages Action</h1>

<div align="center">

[![actions status](https://github.com/yanglbme/gitee-pages-action/workflows/Lint/badge.svg)](https://github.com/yanglbme/gitee-pages-action/actions) [![release](https://img.shields.io/github/v/release/yanglbme/gitee-pages-action.svg)](../../releases) [![license](https://badgen.net/github/license/yanglbme/gitee-pages-action)](./LICENSE) [![PRs Welcome](https://badgen.net/badge/PRs/welcome/green)](../../pulls)

</div>

使用 `GitHub Pages` 时，每当项目有更新，GitHub 会自动帮我们重新部署 `GitHub Pages`。对于国内的 `Gitee Pages`，一般情况下无法自动部署，除非我们开通 `Gitee Pages Pro` 功能。而 `Pro` 功能的开通，需要满足以下其中一个条件：

- 花钱开通 `Pro` 功能，￥99/年。
- Gitee 项目足够优秀，得到 Gitee 官方的推荐，那么 Gitee 就会提示“您的项目为推荐项目，已自动为您开通 `Gitee Pages Pro`”。

为了帮助更多朋友实现 `Gitee Pages` 的自动部署，我开发了 [Gitee Pages Action](https://github.com/marketplace/actions/gitee-pages-action)，只需要在项目的 `Settings` 页面下配置 keys，然后在 `.github/workflows/` 下创建一个工作流，引入一些配置参数即可。若有使用上的问题，欢迎随时在 [Issues](https://github.com/yanglbme/gitee-pages-action/issues) 反馈。

注：首次需要手动登录 Gitee 点击构建。

## 入参

|  参数  |  描述  |  是否必传  |  默认值  |
|---|---|---|---|
| `gitee-username` | Gitee 用户名 | 是 | - |
| `gitee-password` | Gitee 密码 | 是 | - |
| `gitee-repo` | Gitee 仓库 | 是 | - |
| `branch` | 构建的分支 | 否 | `master` |
| `directory` | 构建的目录 | 否 | '' |
| `https` | 是否强制 HTTPS | 否 | `true` |

## 示例

以下是一个完整示例。

在你的 GitHub 仓库 `.github/workflows/` 文件夹下创建一个 `sync.yml` 文件，内容如下：

```yml
name: Sync

on:
  push:
    branches: [ master ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Sync to Gitee
      uses: wearerequired/git-mirror-action@master
      env:
          # 注意在 Settings->Secrets 配置 GITEE_RSA_PRIVATE_KEY
          SSH_PRIVATE_KEY: ${{ secrets.GITEE_RSA_PRIVATE_KEY }}
      with:
          # 注意替换为你的 GitHub 源仓库地址
          source-repo: "git@github.com:doocs/advanced-java.git"
          # 注意替换为你的 Gitee 目标仓库地址
          destination-repo: "git@gitee.com:Doocs/advanced-java.git"

    - name: Build Gitee Pages
      uses: yanglbme/gitee-pages-action@master
      with:
          # 注意替换为你的 Gitee 用户名
          gitee-username: yanglbme
          # 注意在 Settings->Secrets 配置 GITEE_PASSWORD
          gitee-password: ${{ secrets.GITEE_PASSWORD }}
          # 注意替换为你的 Gitee 仓库
          gitee-repo: doocs/advanced-java
```

先使用 [`wearerequired/git-mirror-action`](https://github.com/wearerequired/git-mirror-action) 将 GitHub 仓库同步到 Gitee 仓库，再使用 [`yanglbme/gitee-pages-action`](https://github.com/yanglbme/gitee-pages-action) 实现 Gitee Pages 的自动部署。

请确保在 GitHub 项目的 `Settings` -> `Secrets` 路径下配置好 `GITEE_RSA_PRIVATE_KEY` 以及 `GITEE_PASSWORD` 两个密钥。其中：

- `GITEE_RSA_PRIVATE_KEY`: 存放你的 `id_rsa` 私钥。
- `GITEE_PASSWORD`: 存放你的 Gitee 账户密码。

![](/images/add_secrets.png)

如果一切配置正常，并成功触发 [Gitee Pages Action](https://github.com/marketplace/actions/gitee-pages-action) ，我们可能会收到一封来自 Gitee 的告警邮件/站内信。放心，这是 GitHub Action 程序帮我们登录到 Gitee 官网，并为我们点击了项目的部署按钮。

![](/images/gitee_warn.png)

注：如果在使用过程中遇到了 Gitee 短信验证码导致 Gitee Pages Action 无法自动登录部署 Pages，请参考 [#6](https://github.com/yanglbme/gitee-pages-action/issues/6)。

## 谁在使用

<table>
    <tr>
      <td align="center" style="width: 80px;">
        <a href="https://github.com/antvis">
          <img src="./images/antv.png" style="width: 40px;"><br>
          <sub>蚂蚁金服 - 数据可视化</sub>
        </a>
      </td>
      <td align="center" style="width: 80px;">
        <a href="https://github.com/doocs">
          <img src="./images/doocs.png" style="width: 40px;"><br>
          <sub>Doocs技术社区</sub>
        </a>
      </td>
      <td align="center" style="width: 80px;">
        <a href="https://github.com/youzan">
          <img src="./images/youzan.jpg" style="width: 40px;"><br>
          <sub>有赞</sub>
        </a>
      </td>
    </tr>
    <tr>
        <td align="left" style="width: 80px;">
            <ul>
                <li><a href="https://github.com/antvis/g">antvis/g</a></li>
                <li><a href="https://github.com/antvis/F2">antvis/F2</a></li>
                <li><a href="https://github.com/antvis/G6">antvis/G6</a></li>
                <li><a href="https://github.com/antvis/L7">antvis/L7</a></li>
                <li><a href="https://github.com/antvis/Graphin">antvis/Graphin</a></li>
                <li><a href="https://github.com/antvis/G2Plot">antvis/G2Plot</a></li>
                <li><a href="https://github.com/antvis/antvis.github.io">antvis/antvis.github.io</a></li>
            </ul>
        </td>
        <td align="left" style="width: 80px;">
            <ul>
                <li><a href="https://github.com/doocs/jvm">doocs/jvm</a></li>
                <li><a href="https://github.com/doocs/leetcode">doocs/leetcode</a></li>
                <li><a href="https://github.com/doocs/advanced-java">doocs/advanced-java</a></li>
                <li><a href="https://github.com/doocs/doocs.github.io">doocs/doocs.github.io</a></li>
                <li><a href="https://github.com/doocs/source-code-hunter">doocs/source-code-hunter</a></li>
            </ul>
        </td>
        <td align="left" style="width: 80px;">
            <ul>
                <li><a href="https://github.com/youzan/vant-weapp">youzan/vant-weapp</a></li>
                <li><a href="https://github.com/youzan/vant">youzan/vant</a></li>
            </ul>
        </td>
    </tr>
</table>

## 许可证

[MIT](LICENSE)
