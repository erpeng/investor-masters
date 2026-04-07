import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://erpeng.github.io',
  base: '/investor-master',
  integrations: [
    starlight({
      title: 'Investors Wiki',
      description: '把分散的投资访谈、备忘录和机构材料，编译成一个可以持续更新的静态知识库。',
      customCss: ['./src/styles/custom.css'],
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/erpeng/investor-master'
        }
      ],
      sidebar: [
        {
          label: '开始阅读',
          items: [
            { label: '首页', slug: '' },
            { label: '对话与争议', slug: 'dialogues' }
          ]
        },
        {
          label: '投资人',
          autogenerate: { directory: 'investors' }
        },
        {
          label: '机构',
          autogenerate: { directory: 'institutions' }
        },
        {
          label: '公司',
          autogenerate: { directory: 'companies' }
        },
        {
          label: '概念',
          autogenerate: { directory: 'concepts' }
        },
        {
          label: '来源',
          autogenerate: { directory: 'sources' }
        }
      ]
    })
  ]
});
