# Gitee Pages action
使用模拟登录，自动部署 Gitee Pages。

> 未完成。

## 入参

|  参数  |  描述  |  是否必传  |  默认值  |
|---|---|---|---|
| `gitee-repo` | Gitee 仓库 | 是 | - |
| `gitee-login-cookie` | Gitee 登录后的 cookie | 是 | - |
| `branch` | 构建的分支 | 否 | `master` |
| `directory` | 构建的目录 | 否 | '' |
| `https` | 是否强制 HTTPS | 否 | `false` |

## 例子
```yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
        
    - name: Sync to Gitee
      uses: wearerequired/git-mirror-action@master
      env:
          SSH_PRIVATE_KEY: ${{ secrets.GITEE_RSA_PRIVATE_KEY }}
      with:
          source-repo: "git@github.com:doocs/advanced-java.git"
          destination-repo: "git@gitee.com:Doocs/advanced-java.git"

    - name: Rebuild Gitee Pages
      uses: yanglbme/gitee-pages-action@v1.0.0
      with:
          repository: doocs/advanced-java
          cookie: ${{ secrets.GITEE_COOKIE }}
          branch: master
```

请到 `Settings` -> `Secrets` 配置 `GITEE_RSA_PRIVATE_KEY` 和 `GITEE_COOKIE`。其中：

- `GITEE_RSA_PRIVATE_KEY`: 存放你的 `id_rsa` 私钥。
- `GITEE_COOKIE`: 存放你登录 Gitee 后的 Cookie。

![](/images/add_secret_key.png)
