# Investors Static Site

这个目录是给 `github.io` 用的静态站编译层，不会修改原始 Obsidian vault。

## 技术栈

- Astro
- Starlight
- Python 编译脚本 `scripts/compile_site.py`

## 内容来源

- 编译脚本只读读取一个外部 Obsidian vault
- 通过环境变量 `INVESTORS_VAULT` 指定该 vault 根目录
- 将内容编译到 `src/content/docs/`

## 本地工作流

1. 安装 Node.js 20+
2. 安装依赖：

```bash
npm install
```

3. 从 Obsidian vault 重新编译内容：

```bash
export INVESTORS_VAULT=/path/to/your/obsidian-vault
npm run compile
```

4. 本地预览：

```bash
npm run dev
```

## GitHub Pages

- 当前 `astro.config.mjs` 预设：
  - `site: https://erpeng.github.io`
  - `base: /investor-master`
- 如果仓库名变化，需要同步修改 `base`

线上地址：

- `https://erpeng.github.io/investor-master`

部署工作流在 `.github/workflows/deploy.yml`。
