# Gitee Pages action
使用模拟登录，自动部署 Gitee Pages。

## 入参

|  参数  |  描述  |  是否必传  |  默认值  |
|---|---|---|---|
| `gitee-repo` | Gitee 仓库 | 是 | - |
| `gitee-login-cookie` | Gitee 登录后的 cookie | 是 | - |
| `branch` | 构建的分支 | 否 | `master` |
| `directory` | 构建的目录 | 否 | '' |
| `https` | 是否强制 HTTPS | 否 | `true` |

## 例子
```yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Sync to Gitee
      uses: wearerequired/git-mirror-action@master
      env:
          SSH_PRIVATE_KEY: ${{ secrets.GITEE_RSA_PRIVATE_KEY }}
      with:
          source-repo: "git@github.com:doocs/advanced-java.git"
          destination-repo: "git@gitee.com:Doocs/advanced-java.git"

    - name: Build Gitee Pages
      uses: yanglbme/gitee-pages-action@v1.0.0
      with:
          gitee-repo: doocs/advanced-java
          gitee-login-cookie: ${{ secrets.GITEE_COOKIE }}
          branch: master
```

先使用 [`wearerequired/git-mirror-action`](https://github.com/wearerequired/git-mirror-action) 将 GitHub 仓库同步到 Gitee 仓库，再使用 [`yanglbme/gitee-pages-action`](https://github.com/yanglbme/gitee-pages-action) 实现 Gitee Pages 的自动部署。

请确保在 GitHub 项目的 `Settings` -> `Secrets` 路径下配置好 `GITEE_RSA_PRIVATE_KEY` 以及 `GITEE_COOKIE` 两个密钥。其中：

- `GITEE_RSA_PRIVATE_KEY`: 存放你的 `id_rsa` 私钥。
- `GITEE_COOKIE`: 存放你登录 Gitee 后的 cookie。

![](/images/add_secret_key.png)

## 许可证
[MIT](LICENSE)