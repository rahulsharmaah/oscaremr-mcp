const sidebars = {
  docs: [
    'index',
    'installation',
    'one-click-install',
    'configuration',
    'architecture',
    {
      type: 'category',
      label: 'MCP Clients',
      items: ['clients/codex', 'clients/claude-code', 'clients/cursor'],
    },
    'tools',
    'EXPOSE_OSCAR_WSL_MARIADB',
    'security',
    'contributing',
  ],
};

module.exports = sidebars;
