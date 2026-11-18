"""13F route and provenance regressions using an isolated miniature vault."""
import importlib.util
from html.parser import HTMLParser
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("compile_site_13f", ROOT / "scripts/compile_site.py")
site = importlib.util.module_from_spec(spec)
with tempfile.TemporaryDirectory() as import_vault:
    with patch.dict(os.environ, {"INVESTORS_VAULT": import_vault}):
        spec.loader.exec_module(site)

MANAGERS = ("Berkshire", "Himalaya", "HH", "Duquesne", "Appaloosa",
            "Atreides", "Coatue", "Altimeter", "Fundsmith", "Pershing",
            "Akre", "Dorsey", "AKO", "Giverny", "Oakmark", "Third Point", "Kensico",
            "Maverick", "Baupost", "Baillie", "Greenlight", "Lone Pine", "Tudor")


class Compile13FRoutesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.wiki, self.raw, self.docs = root / "wiki", root / "raw", root / "docs"
        for path in (self.raw, self.wiki / "institutions", self.wiki / "sources",
                     self.wiki / "companies", self.wiki / "ten-questions", self.wiki / "dialogues"):
            path.mkdir(parents=True, exist_ok=True)
        self.patches = patch.multiple(site, WIKI_DIR=self.wiki, RAW_DIR=self.raw,
                                      DOCS_DIR=self.docs, INSTITUTION_META={},
                                      SOURCE_SLUG_REGISTRY={"A-first.md": "source-01", "Z-last.md": "source-02"})
        self.patches.start()
        self.addCleanup(self.patches.stop)

    def add_trend(self, manager, latest="2026Q3"):
        path = self.wiki / "institutions" / f"13F趋势-{manager}.md"
        path.write_text(f"---\nlatest_quarter: {latest}\n---\n\n# {manager}\n\n持仓证据。\n", encoding="utf-8")

    def add_source(self, manager):
        name = f"SEC｜{manager}：2022Q4至2026Q3持仓轨迹"
        (self.raw / f"{name}.md").write_text(
            f"---\ntitle: {name}\nsource: https://www.sec.gov/\n---\n\n# {name}\n\n"
            "[原始SEC文件](https://www.sec.gov/example.xml)\n\n核验信息完整保留。\n",
            encoding="utf-8",
        )
        return name

    def link_state(self):
        page_links, page_titles = site.build_link_maps()
        source_links, raw_files = site.build_source_maps()
        return patch.multiple(site, PAGE_LINKS=page_links, PAGE_TITLES=page_titles,
                              SOURCE_LINKS=source_links, RAW_FILES=raw_files)

    def test_trends_render_linked_routes_and_latest_quarter(self):
        for manager in MANAGERS:
            self.add_trend(manager, "2026Q3")
        for quarter in ("2025Q3", "2026Q2", "2026Q3", "2027Q1"):
            (self.wiki / "institutions" / f"13F趋势-{quarter}.md").write_text(
                f"# {quarter}\n\n[[institutions/13F趋势-Berkshire]]\n", encoding="utf-8")
        links, _ = site.build_link_maps()
        with self.link_state():
            site.compile_institutions()
        for manager in MANAGERS:
            route = f"institutions/13f-trends-{manager.lower().replace(' ', '-')}"
            self.assertEqual(links[f"institutions/13F趋势-{manager}"], route)
            text = (self.docs / f"{route}.md").read_text()
            self.assertIn("到 2026Q3", text.split("---", 2)[1])
        for quarter in ("2025Q3", "2026Q2", "2026Q3", "2027Q1"):
            route = f"institutions/13f-trends-{quarter[:4]}-q{quarter[-1]}"
            self.assertEqual(links[f"institutions/13F趋势-{quarter}"], route)
            text = (self.docs / f"{route}.md").read_text()
            self.assertIn("/investor-masters/institutions/13f-trends-berkshire", text)
            self.assertNotIn("[[", text)
        # The date comes from the source metadata, not another hard-coded quarter.
        self.add_trend("Duquesne", "2027Q1")
        with self.link_state():
            site.compile_institutions()
        self.assertIn("到 2027Q1", (self.docs / "institutions/13f-trends-duquesne.md").read_text())
        for manager in MANAGERS[5:]:
            self.add_trend(manager, "2027Q1")
        with self.link_state():
            site.compile_institutions()
        for manager in MANAGERS[5:]:
            self.assertIn("到 2027Q1", (self.docs / f"institutions/13f-trends-{manager.lower().replace(' ', '-')}.md").read_text())

    def test_source_cards_do_not_renumber_existing_sources(self):
        for name in ("A-first.md", "Z-last.md"):
            (self.raw / name).write_text("# Existing source\n\nOriginal evidence.\n")
        before, _ = site.build_source_maps()
        for manager in MANAGERS:
            self.add_source(manager)
        after, _ = site.build_source_maps()
        for key, route in before.items():
            self.assertEqual(after[key], route)
        self.assertEqual(after["A-first.md"], "sources/source-01")
        self.assertEqual(after["Z-last.md"], "sources/source-02")
        for manager in MANAGERS:
            name = f"SEC｜{manager}：2022Q4至2026Q3持仓轨迹.md"
            self.assertEqual(after[name], f"sources/{manager.lower().replace(' ', '-')}-13f-2026q3")

    def test_ordinary_sources_inserted_before_old_files_keep_every_route(self):
        for name in ("A-first.md", "M-new.md", "Z-last.md"):
            (self.raw / name).write_text("# Source\n\nOriginal evidence.\n")
        before, _ = site.build_source_maps()
        self.assertEqual(before["A-first.md"], "sources/source-01")
        self.assertEqual(before["Z-last.md"], "sources/source-02")
        # This ordinary source sorts ahead of all three. A second insertion
        # sorts ahead of the first new one; neither may change earlier routes.
        (self.raw / "0-new.md").write_text("# Inserted before all legacy files\n")
        middle, _ = site.build_source_maps()
        (self.raw / "00-newer.md").write_text("# Another earlier insertion\n")
        after, _ = site.build_source_maps()
        for key, route in before.items():
            self.assertEqual(route, middle[key])
            self.assertEqual(route, after[key])
        self.assertEqual(middle["0-new.md"], after["0-new.md"])
        self.assertRegex(after["M-new.md"], r"^sources/source-[0-9a-f]{16}$")
        with self.link_state():
            site.compile_sources()
        for filename in ("A-first.md", "M-new.md", "Z-last.md", "0-new.md", "00-newer.md"):
            text = (self.docs / (after[filename] + ".md")).read_text()
            self.assertIn(f"**原文件名**: `{filename}`", text)

    def test_audits_compile_with_source_and_trend_links(self):
        for manager in MANAGERS:
            self.add_trend(manager)
            raw_name = self.add_source(manager)
            audit_name = 'Akre-13F-source-audit' if manager == 'Akre' else f'{manager}-13f-source-audit'
            (self.wiki / "sources" / f"{audit_name}.md").write_text(
                f"# {manager}审计\n\n[[raw/{raw_name}]]\n\n"
                f"[[institutions/13F趋势-{manager}]]\n", encoding="utf-8")
        with (self.wiki / "sources/Akre-13F-source-audit.md").open('a') as out:
            out.write("\n保留旧审计。\n")
        links, _ = site.build_link_maps()
        with self.link_state():
            site.compile_sources()
        for manager in MANAGERS:
            slug = f"{manager.lower().replace(' ', '-')}-13f-source-audit"
            audit_name = 'Akre-13F-source-audit' if manager == 'Akre' else f'{manager}-13f-source-audit'
            self.assertEqual(links[f"sources/{audit_name}"], f"sources/{slug}")
            text = (self.docs / "sources" / f"{slug}.md").read_text()
            self.assertIn(f"/investor-masters/sources/{manager.lower().replace(' ', '-')}-13f-2026q3", text)
            self.assertIn(f"/investor-masters/institutions/13f-trends-{manager.lower().replace(' ', '-')}", text)
            self.assertNotIn("[[", text)
            source = (self.docs / "sources" / f"{manager.lower().replace(' ', '-')}-13f-2026q3.md").read_text()
            self.assertIn("https://www.sec.gov/example.xml", source)
            self.assertIn("核验信息完整保留", source)
        self.assertTrue((self.docs / "sources/akre-13f-source-audit.md").exists())
        index = (self.docs / "sources/index.md").read_text()
        self.assertIn("## Akre 材料审计", index)
        self.assertIn("## 13F 季度审计", index)

    def test_company_seed_routes_are_stable(self):
        expected = {"腾讯音乐": "tencent-music", "Sea": "sea", "Oracle": "oracle",
                    "Bending Spoons": "bending-spoons", "Lennar": "lennar",
                    "Delta Air Lines": "delta-air-lines"}
        for name in expected:
            (self.wiki / "companies" / f"{name}.md").write_text(f"# {name}\n")
        links, _ = site.build_link_maps()
        for name, slug in expected.items():
            self.assertEqual(links[f"companies/{name}"], f"companies/{slug}")

    def test_large_tables_retain_every_row_and_quarter_column(self):
        header='| 标的 | ' + ' | '.join(f'季度{i}' for i in range(15)) + ' |\n'
        alignment='|---|'+'---:|'*15+'\n'
        rows=['| 证券'+str(i)+' | '+' | '.join(str(i*100+j) for j in range(15))+' |\n' for i in range(707)]
        source='## 普通证券\n\n'+header+alignment+''.join(rows)+'\n## PUT/CALL\n\n无。\n'
        result=site.split_large_tables(source)
        class Cells(HTMLParser):
            def __init__(self):
                super().__init__(); self.values=[]; self.active=False
            def handle_starttag(self,tag,attrs):
                if tag=='td':self.active=True;self.values.append('')
            def handle_data(self,value):
                if self.active:self.values[-1]+=value
            def handle_endtag(self,tag):
                if tag=='td':self.active=False
        parser=Cells();parser.feed(result)
        expected=[cell.strip() for row in rows for cell in row.strip().strip('|').split('|')]
        self.assertEqual(parser.values,expected)
        self.assertEqual(result.count('<thead>'),3)
        self.assertIn('第 301—600 项',result)
        self.assertIn('第 601—707 项',result)
        self.assertTrue(result.endswith('## PUT/CALL\n\n无。\n'))
        self.assertEqual(site.split_large_tables(result),result)
        small=header+alignment+''.join(rows[:2])
        self.assertEqual(site.split_large_tables(small),small)
        fenced='```md\n'+source+'```\n'
        self.assertEqual(site.split_large_tables(fenced),fenced)
        markup=source.replace('证券0','[证券0](https://example.com)')
        self.assertIn('[证券0](https://example.com)',site.split_large_tables(markup))

    def test_company_preserves_two_batches_and_research_questions(self):
        (self.wiki / "companies/index.md").write_text("# 公司\n")
        source = self.wiki / "companies/Yum! Brands.md"
        source.write_text("# Yum! Brands\n\n## 简介\n餐饮品牌。\n\n## 公司点评\n研究入口。\n\n"
                          "## 2026Q3 13F 首批联动\n首批证据。\n\n"
                          "## 2026Q3 13F 联动\n第二批证据。\n\n"
                          "## 下一步验证\n加盟商回报与门店增长。\n\n## 主要来源\n官方申报。\n")
        with self.link_state():
            site.compile_companies()
        text = (self.docs / "companies/yum-brands.md").read_text()
        for evidence in ("首批证据。", "第二批证据。", "加盟商回报与门店增长。", "官方申报。"):
            self.assertIn(evidence, text)


if __name__ == "__main__":
    unittest.main()
