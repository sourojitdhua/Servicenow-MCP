<div align="center">

# 🚀 ServiceNow MCP Server

### *Enterprise-Grade ServiceNow Automation via Model Context Protocol*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)
[![ServiceNow](https://img.shields.io/badge/ServiceNow-Ready-00A1E0.svg)](https://www.servicenow.com/)

**A comprehensive, production-ready MCP server that brings the full power of ServiceNow to your AI agents and automation workflows.**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

**snow-mcp** is a powerful Model Context Protocol (MCP) server that provides seamless integration with ServiceNow. Built for developers, automation engineers, and AI practitioners, it enables sophisticated ServiceNow operations through a unified, intuitive interface.

Whether you're building AI agents, automating ITSM workflows, or creating intelligent ServiceNow applications, snow-mcp eliminates the complexity of direct REST API interactions while providing enterprise-grade reliability and extensibility.

### 💡 Why snow-mcp?

- **🎨 AI-Native Design**: Purpose-built for AI agents and LLM-powered automation
- **🔧 106 Pre-Built Tools**: Comprehensive coverage of ITSM, ITOM, and App Dev operations
- **⚡ Production-Ready**: Robust error handling, retry logic, and input validation
- **🧩 Modular Architecture**: Clean, extensible design for easy customization
- **📚 Self-Documenting**: Built-in CLI for tool discovery and exploration
- **🤖 Claude Desktop Ready**: Seamless integration with Claude and other MCP clients

---

## ✨ Features

### 🎯 **Comprehensive Tool Library**
Over 100 specialized tools organized into logical modules:

- **📋 Incident Management**: Create, update, query, and resolve incidents
- **🔄 Change Management**: Full change request lifecycle management
- **🛒 Service Catalog**: Catalog item and request management
- **👥 User & Group Management**: User provisioning and group operations
- **📊 Project & Agile**: Project tracking and agile board management
- **🔍 Knowledge Base**: Article creation and management
- **📝 Request Management**: Service request handling
- **🏗️ CMDB Management**: Configuration item CRUD and relationship queries
- **🐛 Problem Management**: Problem records and known error tracking
- **⏱️ SLA Management**: SLA definitions, task SLAs, and breach monitoring
- **🗃️ Generic Table CRUD**: Create, update, delete, and batch-update any table

### 🛡️ **Enterprise Features**

- **Robust Authentication**: Secure basic auth with role-based access control
- **Rate Limit Handling**: Intelligent retry logic with exponential backoff
- **Input Validation**: Pydantic-powered schemas ensure data integrity
- **Error Handling**: Comprehensive error messages and logging
- **Type Safety**: Full type hints for better IDE support

### 🔌 **Integration Ready**

- **MCP Protocol**: Standard Model Context Protocol implementation
- **Claude Desktop**: Native support for Claude Desktop integration
- **Python Ecosystem**: Standard pip installation and packaging
- **Environment Variables**: Secure credential management via `.env` files

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- ServiceNow instance with API access
- Valid ServiceNow credentials with appropriate roles

### Install via pip

```bash
pip install snow-mcp
```

### Install from source

```bash
git clone https://github.com/yourusername/ServicenowMCP.git
cd ServicenowMCP
pip install -e .
```

---

## 🚀 Quick Start

### 1. Configure Credentials

Create a `.env` file in your project root:

```env
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

### 2. Run the Server

```bash
snow-mcp
```

### 3. Explore Available Tools

```bash
snow-mcp --list-tools
```

### 4. Use with Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "servicenow": {
      "command": "snow-mcp",
      "env": {
        "SERVICENOW_INSTANCE": "your-instance.service-now.com",
        "SERVICENOW_USERNAME": "your-username",
        "SERVICENOW_PASSWORD": "your-password"
      }
    }
  }
}
```

---

## 🔐 Authentication & Permissions

### Required ServiceNow Roles

Ensure your API user has the appropriate roles:

| Role | Purpose | Required For |
|------|---------|--------------|
| `itil` | ITSM Operations | Incidents, Changes, Requests |
| `catalog_admin` | Catalog Management | Service Catalog Operations |
| `user_admin` | User Management | User & Group Operations |
| `admin` | Full Access | All Administrative Operations |

### Security Best Practices

- ✅ Use environment variables for credentials
- ✅ Regularly rotate passwords and API keys
- ✅ Monitor API usage and access logs
- ✅ Restrict instance access to authorized networks
- ✅ Use service accounts with minimal required permissions

---

## 📖 Documentation

For detailed documentation, examples, and advanced usage, see:

- **[Quickstart.md](Quickstart.md)** - Complete quickstart guide with roadmap and examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

---

## 🛠️ Development

### Project Structure

```
ServicenowMCP/
├── src/
│   └── servicenow_mcp_server/
│       ├── server.py          # Main MCP server
│       ├── tools/             # Tool modules
│       └── utils/             # Utility functions
├── test/                      # Test suite
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Running Tests

```bash
pytest test/
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

```bash
git clone https://github.com/yourusername/ServicenowMCP.git
cd ServicenowMCP
pip install -e ".[dev]"
```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sourojit Dhua**

- 📧 Email: sourojit.dhua@gmail.com
- 💼 GitHub: [@sourojitdhua](https://github.com/sourojitdhua)

---

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast MCP server framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [HTTPX](https://www.python-httpx.org/) - HTTP client

---

## 📊 Changelog

### v0.2.0 (Current)
- 🔧 106 tools (up from 60+): added CMDB, Problem, SLA management and generic table CRUD
- 🛡️ SSL verification enabled by default; configurable via `SERVICENOW_VERIFY_SSL`
- 🔄 Exponential-backoff retry with `MAX_RETRIES` and `API_TIMEOUT` env vars
- 🚦 Rate-limit handling (429 + `Retry-After` header)
- ⚡ Typed exception hierarchy replacing generic error dicts
- 🔒 Removed hardcoded password in user creation; uses `secrets.token_urlsafe`
- 🧹 Deduplicated shared `BaseToolParams` model (was copied 16x)
- 📝 Structured logging from `LOG_LEVEL` env var

### v0.1.1
- ✨ Enhanced MCP protocol implementation
- 🐛 Bug fixes and performance improvements
- 📚 Improved documentation

### v0.1.0
- 🎉 Initial release with 60+ tools (now 106 in v0.2.0)
- ✅ Support for ITSM, ITOM, and App Dev operations
- 📖 Complete documentation and examples

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ by Sourojit Dhua

</div>
