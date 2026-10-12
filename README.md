# Investors Static Site

这个目录是给 `github.io` 用的静态站编译层，不会修改原始 Obsidian vault。

## Source Of Truth

- canonical 内容库在外部 Obsidian vault
- 静态站 repo 只负责把 vault 编译到 `src/content/docs/`
- 正确流程永远是：`raw -> Obsidian wiki -> site compile -> deploy`
- 不要把站点生成稿当成主版本直接维护

## 技术栈

- Astro
- Starlight
- Python 编译脚本 `scripts/compile_site.py`

## 内容来源

- 编译脚本只读一个外部 Obsidian vault
- 通过环境变量 `INVESTORS_VAULT` 指定该 vault 根目录
- 将内容编译到 `src/content/docs/`

## 日常工作流

1. 在 Obsidian vault 的 `raw/` 中引入新材料。
2. 先更新 vault 里的 `wiki/` 页面，并完成内容审核。
3. 设置环境变量并重新编译站点：

```bash
export INVESTORS_VAULT=/path/to/your/obsidian-vault
npm run compile
```

4. 本地预览：

```bash
npm run dev
```

5. 确认站点无误后，再提交到 GitHub 触发部署。

## 本地启动

```bash
npm install
npm run dev
```

## GitHub Pages

- 当前 `astro.config.mjs` 预设：
  - `site: https://erpeng.github.io`
  - `base: /investor-masters`
- 如果仓库名变化，需要同步修改 `base`

线上地址：

- `https://erpeng.github.io/investor-masters`

部署工作流在 `.github/workflows/deploy.yml`。

### Akre 13F evidence snapshot

The Akre report uses the immutable snapshot at
`$INVESTORS_VAULT/raw/data/akre-13f-20261012.json`. It retains all 16 SEC
filings for 15 report periods, cover totals, timestamped quotes, and issuer
split references. Regenerate the report and the institution's four-quarter
holdings section with:

```bash
python3 scripts/generate_akre_13f_trend.py --vault "$INVESTORS_VAULT"
python3 -m unittest discover -s tests -p 'test_akre_13f.py' -v
```

`--data` accepts a separately archived snapshot; do not overwrite existing
`raw/` evidence. Refreshing to another report period also requires updating
the report's dated interpretation and candidate ranking, the quarterly
comparison page, and linked company notes. Attribution is an endpoint
share/price decomposition, not trading cash flow. Ambiguous overlapping
`NEW HOLDINGS` amendments fail instead of being silently summed.

Akre sources use named URLs so adding these materials does not renumber the
144 existing source pages. The compiler also exposes their source audits.
