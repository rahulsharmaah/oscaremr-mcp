const config = {
  title: 'OSCAR EMR MCP Server',
  tagline: 'Guarded local MCP access for OSCAR EMR MariaDB/MySQL databases.',
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
    metadata: [
      {
        name: 'description',
        content:
          'OSCAR EMR MCP Server is a local Model Context Protocol server for safe, guarded access to OSCAR EMR MariaDB/MySQL databases from Codex, Claude Code, Cursor, and other AI agents.',
      },
      {
        name: 'keywords',
        content:
          'OSCAR EMR MCP, OSCAR EMR database, Oscar EMR, Oscar Yammer, Oscar DB MCP, OSCAR MariaDB, OSCAR MySQL, Model Context Protocol, MCP server, AI agent database access, Codex MCP, Claude Code MCP, Cursor MCP',
      },
      {property: 'og:type', content: 'website'},
      {property: 'og:site_name', content: 'OSCAR EMR MCP Server'},
      {
        property: 'og:description',
        content:
          'Safe local MCP access for OSCAR EMR MariaDB/MySQL databases, with read-only inspection tools and explicit confirmed admin actions.',
      },
      {name: 'twitter:card', content: 'summary'},
    ],
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
  headTags: [
    {
      tagName: 'script',
      attributes: {
        type: 'application/ld+json',
      },
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'OSCAR EMR MCP Server',
        alternateName: ['Oscar EMR MCP', 'Oscar DB MCP', 'Oscar Yammer MCP'],
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Windows, macOS, Linux',
        url: 'https://rahulsharmaah.github.io/oscaremr-mcp/',
        codeRepository: 'https://github.com/rahulsharmaah/oscaremr-mcp',
        description:
          'A local Model Context Protocol server for safe, guarded access to OSCAR EMR MariaDB/MySQL databases from AI coding agents.',
        keywords:
          'OSCAR EMR MCP, OSCAR EMR database, Oscar EMR, Oscar Yammer, OSCAR MariaDB, OSCAR MySQL, MCP server, Model Context Protocol',
      }),
    },
  ],
};

module.exports = config;
