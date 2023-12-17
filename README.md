<p align="center">
  <a href="https://github.com/yanglbme/gitee-pages-action">
    <img src="./images/logo.png" alt="gitee-pages-action">
  </a>
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/yanglbme/gitee-pages-action?color=42b883&style=flat-square" alt="license"></a>
  <a href="../../releases"><img src="https://img.shields.io/github/v/release/yanglbme/gitee-pages-action?color=42b883&style=flat-square" alt="release"></a>
  <a href="#谁在使用"><img src="https://shields.io/badge/who's-using-42b883?style=flat-square" alt="users"></a>
  <a href="#错误及解决方案"><img src="https://shields.io/badge/faq-here-42b883?style=flat-square" alt="users"></a>
  <a href="https://github.com/yanglbme/gitee-pages-action"><img src="https://shields.io/badge/%E2%AD%90-GitHub-42b883?style=flat-square" alt="github"></a>
  <a href="https://gitee.com/yanglbme/gitee-pages-action"><img src="https://shields.io/badge/%E2%AD%90-Gitee-42b883?style=flat-square" alt="gitee"></a><br>
  <a href="https://github.com/yanglbme/gitee-pages-action/stargazers"><img src="https://img.shields.io/github/stars/yanglbme/gitee-pages-action?color=42b883&logo=github&style=flat-square" alt="stars"></a>
  <a href="https://github.com/yanglbme/gitee-pages-action/network/members"><img src="https://img.shields.io/github/forks/yanglbme/gitee-pages-action?color=42b883&logo=github&style=flat-square" alt="forks"></a>
</p>

<h1 align="center">Gitee Pages Action</h1>

由于 Gitee Pages 的访问速度很快，很多朋友会选择 Gitee Pages 部署项目（如：个人博客、开源项目国内镜像站点）。但是它不像 GitHub Pages 那样，一提交代码就能自动更新 Pages，因为 Gitee 的自动部署属于 Gitee Pages Pro 的服务。

为了实现 Gitee Pages 的自动部署，我开发了 [Gitee Pages Action](https://github.com/marketplace/actions/gitee-pages-action) ，只需要在 GitHub 项目的 Settings 页面下配置 keys，然后在 `.github/workflows/` 下创建一个工作流，引入一些配置参数即可。欢迎 Star ⭐ 关注本项目。

欢迎体验，若有使用上的问题，也欢迎随时提交 [Issues](https://github.com/yanglbme/gitee-pages-action/issues) 反馈。

注：

1. 首次需要**手动**登录 Gitee ，点击“启动”进行 Gitee Pages 服务的部署。
1. 由于 Gitee 改版，使用 Gitee Pages 前需要先完成实名认证。

## 入参

| 参数             | 描述                         | 是否必传 | 默认值   | 示例                            |
| ---------------- | ---------------------------- | -------- | -------- | ------------------------------- |
| `gitee-username` | Gitee 用户名                 | 是       | -        | `yanglbme`                      |
| `gitee-password` | Gitee 密码                   | 是       | -        | `${{ secrets.GITEE_PASSWORD }}` |
| `gitee-repo`     | Gitee 仓库（严格区分大小写） | 是       | -        | `doocs/leetcode`                |
| `branch`         | 要部署的分支（分支必须存在） | 否       | `master` | `main`                          |
| `directory`      | 要部署的分支上的目录         | 否       |          | `src`                           |
| `https`          | 是否强制使用 HTTPS           | 否       | `true`   | `false`                         |

## 完整示例

### 1. 创建 workflow

在你的 GitHub 项目 `.github/workflows/` 文件夹下创建一个 `.yml` 文件，如 `sync.yml`，内容如下：

```yml
name: Sync

on:
  push:
    branches: [main]
  workflow_dispatch:

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
          source-repo: git@github.com:doocs/leetcode.git
          # 注意替换为你的 Gitee 目标仓库地址
          destination-repo: git@gitee.com:Doocs/leetcode.git

      - name: Build Gitee Pages
        uses: yanglbme/gitee-pages-action@main
        with:
          # 注意替换为你的 Gitee 用户名
          gitee-username: yanglbme
          # 注意在 Settings->Secrets 配置 GITEE_PASSWORD
          gitee-password: ${{ secrets.GITEE_PASSWORD }}
          # 注意替换为你的 Gitee 仓库，仓库名严格区分大小写，请准确填写，否则会出错
          gitee-repo: doocs/leetcode
          # 要部署的分支，默认是 master，若是其他分支，则需要指定（指定的分支必须存在）
          branch: main
```

注：

1. 这里我先使用 [wearerequired/git-mirror-action](https://github.com/wearerequired/git-mirror-action) 将 GitHub 仓库同步到 Gitee 仓库，再使用 [yanglbme/gitee-pages-action](https://github.com/yanglbme/gitee-pages-action) 实现 Gitee Pages 的自动部署。如果你已经通过其它的方式，将代码 push 至 Gitee 了，那么可以不使用 [wearerequired/git-mirror-action](https://github.com/wearerequired/git-mirror-action)，也不需要配置 `GITEE_RSA_PRIVATE_KEY`。
1. `branch` 参数默认是 `master`，如果你是部署在 `gh-pages`(或者 `main`) 分支等等，务必指定 `branch: gh-pages`(或者 `branch: main`)。
1. `branch` 对应的分支，必须在仓库中实际存在，请不要随意（不）指定分支，否则可能导致 Gitee Pages 站点出现 404 无法访问的情况。
1. 对于 `gitee-repo` 参数，如果你的项目在 Gitee 的地址为 https://gitee.com/用户名/xxx ，那么 `gitee-repo` 就填写为 `用户名/xxx`。[#54](https://github.com/yanglbme/gitee-pages-action/issues/54)
1. 对于 workflow 的触发事件，你可以根据项目实际情况，指定为其它的触发事件。比如：
   ```bash
   on:
     push:
       branches: [main, master]
   ```
   更多触发事件，请参考 [Events that trigger workflows](https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows)

### 2. 配置密钥

密钥的配置步骤如下（可展开看示例图）：

<details>
<summary>a. 在命令行终端或 Git Bash 使用命令 <code>ssh-keygen -t rsa -C "youremail@example.com"</code> 生成 SSH Key，注意替换为自己的邮箱。生成的 <code>id_rsa</code> 是私钥，<code>id_rsa.pub</code> 是公钥。(⚠️注意此处不要设置密码，生成的公私钥用于下面 GitHub / Gitee 的配置，以保证公私钥成对，否则从 GitHub -> Gitee 的同步将会失败。)</summary>
<img src="./images/gen_ssh_key.png" alt="gen_ssh_key">
</details>
<details>
<summary>b. 在 GitHub 项目的「Settings -> Secrets」路径下配置好命名为 <code>GITEE_RSA_PRIVATE_KEY</code> 和 <code>GITEE_PASSWORD</code> 的两个密钥。其中：<code>GITEE_RSA_PRIVATE_KEY</code> 存放 <code>id_rsa</code> 私钥；<code>GITEE_PASSWORD</code> 存放 Gitee 帐号的密码。</summary>
<img src="./images/add_secrets.png" alt="add_secrets">
</details>
<details>
<summary>c. 在 GitHub 的个人设置页面「<a href="https://github.com/settings/keys">Settings -> SSH and GPG keys</a>」配置 SSH 公钥（即：<code>id_rsa.pub</code>），命名随意。</summary>
<img src="./images/add_ssh_key_github.png" alt="add_ssh_key_github">
</details>
<details>
<summary>d. 在 Gitee 的个人设置页面「<a href="https://gitee.com/profile/sshkeys">安全设置 -> SSH 公钥</a>」配置 SSH 公钥（即：<code>id_rsa.pub</code>），命名随意。</summary>
<img src="./images/add_ssh_key_gitee.png" alt="add_ssh_key_gitee">
</details>

### 3. 关注 Gitee 公众号

关注 Gitee 官方公众号，并绑定个人 Gitee 帐号，用于接收帐号登录通知、以及绕过短信验证码校验，见[错误及解决方案](#错误及解决方案) 第 3 点。

### 4. 运行结果

如果一切配置正常，并成功触发 [Gitee Pages Action](https://github.com/marketplace/actions/gitee-pages-action) ，Gitee Pages Action 会打印出成功的结果。并且，我们会在 Gitee 公众号收到一条登录通知。这是 Gitee Pages Action 程序帮我们登录到 Gitee 官网，并为我们点击了项目的部署按钮。

```bash
Run yanglbme/gitee-pages-action@main
  with:
    gitee-username: yanglbme
    gitee-password: ***
    gitee-repo: doocs/leetcode
    branch: main
    https: true
/usr/bin/docker run --name e28490f27de0ee43bb49109a40cea0e43202d2_d4911a --label e28490 --workdir /github/workspace --rm -e INPUT_GITEE-USERNAME -e INPUT_GITEE*** INPUT_GITEE-REPO -e INPUT_BRANCH -e INPUT_DIRECTORY -e INPUT_HTTPS -e HOME -e GITHUB_JOB -e GITHUB_REF -e GITHUB_SHA -e GITHUB_REPOSITORY -e GITHUB_REPOSITORY_OWNER -e GITHUB_RUN_ID -e GITHUB_RUN_NUMBER -e GITHUB_RETENTION_DAYS -e GITHUB_RUN_ATTEMPT -e GITHUB_ACTOR -e GITHUB_WORKFLOW -e GITHUB_HEAD_REF -e GITHUB_BASE_REF -e GITHUB_EVENT_NAME -e GITHUB_SERVER_URL -e GITHUB_API_URL -e GITHUB_GRAPHQL_URL -e GITHUB_REF_NAME -e GITHUB_REF_PROTECTED -e GITHUB_REF_TYPE -e GITHUB_WORKSPACE -e GITHUB_ACTION -e GITHUB_EVENT_PATH -e GITHUB_ACTION_REPOSITORY -e GITHUB_ACTION_REF -e GITHUB_PATH -e GITHUB_ENV -e RUNNER_OS -e RUNNER_ARCH -e RUNNER_NAME -e RUNNER_TOOL_CACHE -e RUNNER_TEMP -e RUNNER_WORKSPACE -e ACTIONS_RUNTIME_URL -e ACTIONS_RUNTIME_TOKEN -e ACTIONS_CACHE_URL -e GITHUB_ACTIONS=true -e CI=true -v "/var/run/docker.sock":"/var/run/docker.sock" -v "/home/runner/work/_temp/_github_home":"/github/home" -v "/home/runner/work/_temp/_github_workflow":"/github/workflow" -v "/home/runner/work/_temp/_runner_file_commands":"/github/file_commands" -v "/home/runner/work/leetcode/leetcode":"/github/workspace" e28490:f27de0ee43bb49109a40cea0e43202d2
[2021-11-27 20:16:30] Welcome to use Gitee Pages Action ❤

📕 Getting Started Guide: https://github.com/marketplace/actions/gitee-pages-action
📣 Maintained by Yang Libin: https://github.com/yanglbme

[2021-11-27 20:16:34] Login successfully
[2021-11-27 20:16:35] Rebuild Gitee Pages successfully
[2021-11-27 20:16:35] Success, thanks for using @yanglbme/gitee-pages-action!
```

<img src="./images/action.png" alt="action_result">

<img src="./images/wechat_notification.jpg" alt="add_ssh_key_gitee" style="width: 750px; height: 1334px;" />

## 错误及解决方案

| #   | 错误                                                                                                                                                                                                                                                                                                                                                   | 解决方案                                                                                                                                                                                                                                                          |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Error: Wrong username or password, login failed .                                                                                                                                                                                                                                                                                                      | 帐号或密码错误，请检查参数 `gitee-username`、`gitee-password`是否准确配置。                                                                                                                                                                                       |
| 2   | Error: Need captcha validation, please visit https://gitee.com/login, login to validate your account.                                                                                                                                                                                                                                                  | 需要图片验证码校验。可以手动登录 Gitee 官方，校验验证码。                                                                                                                                                                                                         |
| 3   | Error: Need phone captcha validation, please follow wechat official account "Gitee" to bind account to turn off authentication.                                                                                                                                                                                                                        | 需要短信验证码校验。可以关注 Gitee 微信公众号，并绑定 Gitee 帐号，接收登录提示。[#6](https://github.com/yanglbme/gitee-pages-action/issues/6)                                                                                                                     |
| 4   | Error: Do not deploy frequently, try again one minute later.                                                                                                                                                                                                                                                                                           | 短期内频繁部署 Gitee Pages 导致，可以稍后再触发自动部署。                                                                                                                                                                                                         |
| 5   | Error: Deploy error occurred, please re-run job or check your input `gitee-repo`.                                                                                                                                                                                                                                                                                    | `gitee-repo` 参数格式如：`doocs/leetcode`，并且严格区分大小写，请准确填写。[#10](https://github.com/yanglbme/gitee-pages-action/issues/10)                                                                                                                        |
| 6   | Error: Unknown error occurred in login method, resp: ...                                                                                                                                                                                                                                                                                               | 登录出现未知错误，请在 [issues](https://github.com/yanglbme/gitee-pages-action/issues) 区反馈。                                                                                                                                                                   |
| 7   | Error: Rebuild page error, status code: xxx                                                                                                                                                                                                                                                                                                            | 更新 Pages 时状态码异常，请尝试再次触发 Action 执行。也可能为 gitee pages 未初始化，第一次需要手动部署 gitee pages。                                                                                                                                              |
| 8   | Error: HTTPSConnectionPool(host='gitee.com', port=443): Read timed out. (read timeout=6)<br><br>Error: HTTPSConnectionPool(host='gitee.com', port=443): Max retries exceeded with url: /login (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x7f6c889d42e8>, 'Connection to gitee.com timed out. (connect timeout=6)')) | 网络请求出错，请尝试 Re-run jobs 。[#27](https://github.com/yanglbme/gitee-pages-action/issues/27)                                                                                                                                                                |
| 9   | Error: The repository owner is not authenticated and is not allowed to deploy pages services.                                                                                                                                                                                                                                                          | 仓库持有者未实名认证，不允许部署 pages 服务。                                                                                                                                                                                                                     |
| 10  | git@github.com: Permission denied (publickey).<br>fatal: Could not read from remote repository.<br>Please make sure you have the correct access rights and the repository exists..                                                                                                                                                                     | 先尝试 Re-run job。[#56](https://github.com/yanglbme/gitee-pages-action/issues/56) <br>若仍旧失败，可能是 SSH 公私钥配置有问题，或是使用了带密码的私钥，请参照上文提及的密钥配置步骤进行相应配置。[#29](https://github.com/yanglbme/gitee-pages-action/issues/29) |
| 11  | Hexo Gitee Pages 自动部署站点问题。                                                                                                                                                                                                                                                                                                                    | [@No5972](https://github.com/No5972) 详细给出了一种解决方案。[#34](https://github.com/yanglbme/gitee-pages-action/issues/34)                                                                                                                                      |
| 12  | "/root/.ssh/id_rsa": invalid format.                                                                                                                                                                                                                                                                                                                   | 操作系统环境不同，生成 ssh key 的方式可能有所差别，尝试添加 `-m PEM` 参数试试。[#49](https://github.com/yanglbme/gitee-pages-action/issues/49)                                                                                                                    |
| ... | ...                                                                                                                                                                                                                                                                                                                                                    | ...                                                                                                                                                                                                                                                               |

## 谁在使用

<table>
  <tr>
    <td align="center" style="width: 80px;">
      <a href="https://github.com/antvis">
        <img src="./images/antv.png" style="width: 40px;" alt="蚂蚁金服"><br>
        <sub>蚂蚁金服 - 数据可视化</sub>
      </a>
    </td>
    <td align="center" style="width: 80px;">
      <a href="https://github.com/doocs">
        <img src="./images/doocs.png" style="width: 40px;" alt="Doocs"><br>
        <sub>Doocs 技术社区</sub>
      </a>
    </td>
     <td align="center" style="width: 80px;">
      <a href="https://github.com/Kaiyiwing/qwerty-learner">
        <img src="./images/qwerty-learner-logo.svg" style="width: 40px;" alt="Qwerty Learner"><br>
        <sub>Qwerty Learner</sub>
      </a>
    </td>
  </tr>
  <tr>
    <td style="width: 80px; text-align: left;">
      <ul>
        <li><a href="https://github.com/antvis/g">antvis/g</a></li>
        <li><a href="https://github.com/antvis/F2">antvis/F2</a></li>
        <li><a href="https://github.com/antvis/G6">antvis/G6</a></li>
        <li><a href="https://github.com/antvis/L7">antvis/L7</a></li>
        <li><a href="https://github.com/antvis/G2Plot">antvis/G2Plot</a></li>
        <li><a href="https://github.com/antvis/Graphin">antvis/Graphin</a></li>
        <li><a href="https://github.com/antvis/antvis.github.io">antvis/antvis.github.io</a></li>
      </ul>
    </td>
    <td style="width: 80px; text-align: left;">
      <ul>
        <li><a href="https://github.com/doocs/jvm">doocs/jvm</a></li>
        <li><a href="https://github.com/doocs/leetcode">doocs/leetcode</a></li>
        <li><a href="https://github.com/doocs/advanced-java">doocs/advanced-java</a></li>
        <li><a href="https://github.com/doocs/doocs.github.io">doocs/doocs.github.io</a></li>
        <li><a href="https://github.com/doocs/source-code-hunter">doocs/source-code-hunter</a></li>
      </ul>
    </td>
    <td style="width: 80px; text-align: left;">
      <ul>
        <li><a href="https://github.com/Kaiyiwing/qwerty-learner" style="white-space: nowrap">Qwerty Learner</a></li>
        <li><a href="https://github.com/Kaiyiwing/qwerty-learner-vscode" style="white-space: nowrap">Qwerty Learner VSCode</a></li>
      </ul>
    </td>
  </tr>
</table>

查看更多用户，请访问 https://cs.github.com/?scopeName=All+repos&scope=&q=yanglbme%2Fgitee-pages-action

## 联系我

对于 Gitee Pages Action 有任何的疑问，还可以通过以下方式找到我。

<table>
  <tr>
    <td align="center" style="width: 260px;">
      <img src="https://cdn-doocs.oss-cn-shenzhen.aliyuncs.com/gh/doocs/images/qrcode-for-doocs.png" style="width: 400px;"><br>
    </td>
    <td align="center" style="width: 260px;">
      <img src="https://cdn-doocs.oss-cn-shenzhen.aliyuncs.com/gh/doocs/images/qrcode-for-yanglbme.png" style="width: 400px;"><br>
    </td>
  </tr>
</table>

## 许可证

MIT
