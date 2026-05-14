const config = {
  title: 'Oscar EMR MCP',
  tagline: 'Guarded local MCP access for OSCAR EMR and Agentic Clinic MariaDB databases.',
  favicon: 'img/oscar-db-mcp-logo.svg',

  url: 'https://rahulsharmaah.github.io',
  baseUrl: '/oscaremr-mcp/',
  organizationName: 'rahulsharmaah',
  projectName: 'oscaremr-mcp',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/rahulsharmaah/oscaremr-mcp/tree/main/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    image: 'img/oscar-db-mcp-logo.svg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Oscar EMR MCP',
      logo: {
        alt: 'Oscar EMR MCP logo',
        src: 'img/oscar-db-mcp-logo.svg',
      },
      items: [
        {to: '/', label: 'Docs', position: 'left'},
        {href: 'https://github.com/rahulsharmaah/oscaremr-mcp', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Installation', to: '/installation'},
            {label: 'Configuration', to: '/configuration'},
            {label: 'Tools', to: '/tools'},
          ],
        },
        {
          title: 'Project',
          items: [
            {label: 'GitHub', href: 'https://github.com/rahulsharmaah/oscaremr-mcp'},
            {label: 'Security', to: '/security'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Oscar EMR MCP.`,
    },
    prism: {
      additionalLanguages: ['powershell', 'bash', 'json', 'python'],
    },
  },
};

module.exports = config;
