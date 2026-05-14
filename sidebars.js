const sidebars = {
  docs: [
    'index',
    'installation',
    'configuration',
    {
      type: 'category',
      label: 'MCP Clients',
      items: ['clients/codex', 'clients/claude-code'],
    },
    'tools',
    'EXPOSE_OSCAR_WSL_MARIADB',
    'security',
    'contributing',
  ],
};

module.exports = sidebars;
