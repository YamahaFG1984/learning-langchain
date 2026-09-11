# Learning LangChain Code Examples

This repository contains code examples (in python and javascript) from each chapter of the book ["Learning LangChain: Building AI and LLM Applications with LangChain and LangGraph"](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) published by O'Reilly Media.

To run the examples, you can clone the repository and run the examples in your preferred language folders.

---

## 📚 中文图解教程（docs/）

本仓库附带一套全 11 章的中文精读教程，逐章讲解概念、配大量机制图，并给出与本仓库代码一一对应的可运行示例。

在本地打开 [`docs/index.html`](docs/index.html) 即可阅读（纯静态页面，无需任何构建步骤）：

```bash
# macOS
open docs/index.html
# Linux
xdg-open docs/index.html
# 或者起一个本地服务器
python -m http.server 8000 --directory docs
```

左侧栏顶部的开关切换 Python / JavaScript 示例代码，右下角的按钮切换深浅色，选择都会记住。页面只用系统字体、不依赖任何外部资源，离线也能正常显示；窄屏下侧栏收进左上角的菜单按钮。

想改内容的话：正文片段在 `docs/_src/`，页面外壳（侧边栏、本章目录、图号、上一章 / 下一章）由 `docs/build.py` 统一生成——

```bash
python docs/build.py          # 全部重建
python docs/build.py ch03     # 只重建第 3 章
```

## ⬆️ Upgraded to LangChain 1.x / LangGraph 1.x

The book was written against LangChain 0.2/0.3. All code in this repository has been
migrated to **LangChain 1.x and LangGraph 1.x**, and verified to import cleanly against
the current releases. The most important changes:

| Book (0.3) | Now (1.x) |
| --- | --- |
| `langchain.indexes` | `langchain_classic.indexes` |
| `langchain.chains.*` | `langchain_classic.chains.*` |
| `langchain.retrievers.*` | `langchain_classic.retrievers.*` |
| `langchain.storage.InMemoryStore` | `langchain_core.stores.InMemoryStore` |
| `langchain.utils.math` | `langchain_classic.utils.math` |
| `langchain.hub` | `langchain_classic.hub` |
| `langchain.schema` / `langchain.text_splitter` | `langchain_core.messages` / `langchain_text_splitters` |
| `langchain_core.pydantic_v1` | `pydantic` |
| `MemorySaver` | `InMemorySaver` |
| `StateGraph(S, input=…, output=…)` | `StateGraph(S, input_schema=…, output_schema=…)` |
| `StateGraph(S, config_schema=…)` | `StateGraph(S, context_schema=…)` |
| `retriever.get_relevant_documents(q)` | `retriever.invoke(q)` |
| `duckduckgo-search` | `ddgs` |
| JS: `langchain/<deep/path>` | `@langchain/classic/<deep/path>` |

Model names were also refreshed (`gpt-3.5-turbo` → `gpt-4.1-mini`, `gpt-4`/`gpt-4o` → `gpt-4.1`,
embeddings pinned to `text-embedding-3-small`). A handful of book snippets that could not run
as printed were fixed as well — most notably the Chapter 7 supervisor graph, the Chapter 7
subgraph example (missing `START` edge), the Chapter 8 examples (which were empty stubs and are
now complete, runnable programs sharing `ch8/py/agent.py`), and two Chapter 10 bugs.

**Python 3.10+ is now required.**

---

## Table of Contents

- [中文图解教程](#-中文图解教程docs)
- [Upgraded to LangChain 1.x](#️-upgraded-to-langchain-1x--langgraph-1x)
- [Quick Start](#quick-start)
  - [Environment variables setup](#environment-variables-setup)
  - [Running the chapter examples](#running-the-chapter-examples)
- [Repository Structure](#repository-structure)
- [Chapter-wise Examples](#chapter-wise-examples)
- [Docker Setup and Usage](#docker-setup-and-usage)
    - [Installing Docker](#installing-docker)
    - [Running the PostgreSQL Container](#running-the-postgresql-container)
    - [Troubleshooting Docker](#troubleshooting-docker)
- [Setting up Chinook.db with SQLite](#setting-up-chinookdb-with-sqlite)
- [General Troubleshooting](#general-troubleshooting)

## Quick Start

### Environment variables setup

First, we need the environment variables required to run the examples in this repository.

You can find the full list in the `.env.example` file. Copy this file to a `.env` and fill in the values:

```bash
cp .env.example .env
```

- **OPENAI_API_KEY**: You can get your key [here](https://platform.openai.com/account/api-keys). This will enable you to run the examples that require an OpenAI model.

- **LANGCHAIN_API_KEY**: You can get your key by creating an account [here](https://smith.langchain.com/). This will enable you to interact with the LangSmith tracing and debugging tools.

- **LANGCHAIN_TRACING_V2=true**: This is required to enable visual tracing and debugging in LangSmith for the examples.

If you want to run the production example in chapter 9, you need a Supabase account and a Supabase API key:

1. To register for a Supabase account, go to [supabase.com](https://supabase.com) and sign up.
2. Once you have an account, create a new project then navigate to the settings section.
3. In the settings section, navigate to the API section to see your keys.
4. Copy the project URL and service_role key and add them to the `.env` file as values for `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.

### Running the chapter examples

#### For Python examples:

If you haven't installed Python on your system, install it first as per the instructions [here](https://www.python.org/downloads/). **Python 3.10 or newer is required** (3.11+ if you want to run the LangGraph dev server in Chapter 9).

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:

For MacOS/Linux:
```bash
source .venv/bin/activate
```

For Windows:
```bash
.venv\Scripts\activate
```

After activation, your terminal prompt should prefix with (venv), indicating that the virtual environment is active.

3. Install the dependencies in the pyproject.toml file:
```bash
pip install -e .
```

4. Verify the installation:
```bash
pip list
```

5. Run an example to see the output:
```bash
python ch2/py/a-text-loader.py
```

#### For JavaScript examples:

If you haven't installed Node.js on your system, install it first as per the instructions [here](https://nodejs.org/).

1. Install the dependencies in the package.json file:
```bash
npm install
```

2. Run the example to see the output:
```bash
node ch2/js/a-text-loader.js
```

## Repository Structure

The repository is structured as follows:

```
├── .env.example          # Example environment variables
├── learning-langchain    # Root directory
│   ├── ch1               # Chapter 1 examples
│   │   ├── js            # JavaScript examples
│   │   │   ├── a-llm.js  # Example file
│   │   │   └── ...
│   │   └── py            # Python examples
│   │       ├── a-llm.py  # Example file
│   │       └── ...
│   ├── ch2               # Chapter 2 examples
│   │   ├── js            # JavaScript examples
│   │   │   └── ...
│   │   └── py            # Python examples
│   │       └── ...
│   ├── ...               # Remaining chapters
│   ├── test.pdf          # Test PDF file
│   ├── test.txt          # Test text file
│   ├── package.json      # JavaScript dependencies
│   ├── pyproject.toml    # Python dependencies
│   └── README.md         # This file
└── ...
```

Each chapter (ch1, ch2, etc.) contains subdirectories `js` and `py` for JavaScript and Python examples, respectively.

## Chapter-wise Examples

Here's a brief overview of the code examples available for each chapter:

### Chapter 1: Introduction to LangChain

Demonstrates basic usage of LLMs, Chat models, prompts, and output parsers.

Files:
- `ch1/js/*.js`: JavaScript examples
- `ch1/py/*.py`: Python examples

### Chapter 2: Document Loading and Data Transformation

Covers loading data from various sources (text files, web pages, PDFs), splitting text into chunks, and creating embeddings.

Files:
- `ch2/js/*.js`: JavaScript examples
- `ch2/py/*.py`: Python examples

### Chapter 3: Retrieval

Explores different retrieval strategies, including basic RAG, query rewriting, multi-query, RAG fusion, and self-query.

Files:
- `ch3/js/*.js`: JavaScript examples
- `ch3/py/*.py`: Python examples

### Chapter 4: Memory

Demonstrates how to add memory to your chains and agents, including simple memory, state graphs, persistent memory, and message trimming/filtering/merging.

Files:
- `ch4/js/*.js`: JavaScript examples
- `ch4/py/*.py`: Python examples

### Chapter 5: Chatbots

Shows how to build chatbots using LangGraph, including basic chatbots, SQL generators, and multi-RAG chatbots.

Files:
- `ch5/js/*.js`: JavaScript examples
- `ch5/py/*.py`: Python examples

### Chapter 6: Agents

Covers building agents with tools, including basic agents, forcing the first tool, and using many tools.

Files:
- `ch6/js/*.js`: JavaScript examples
- `ch6/py/*.py`: Python examples

### Chapter 7: Subgraphs

Explores how to use subgraphs to create more complex agents, including reflection, direct subgraphs, function subgraphs, and supervisors.

Files:
- `ch7/js/*.js`: JavaScript examples
- `ch7/py/*.py`: Python examples

### Chapter 8: Productionizing LangGraph

Demonstrates how to productionize LangGraph applications, including structured output, streaming output, interruption, authorization, resuming, editing state, and forking.

Files:
- `ch8/js/*.js`: JavaScript examples
- `ch8/py/*.py`: Python examples

### Chapter 9: Deployment

Provides examples of deploying LangGraph applications.

Files:
- `ch9/js/*`: JavaScript examples
- `ch9/py/*`: Python examples

#### Running the Local Development Server

You can run the local development server for either JavaScript or Python implementations from the root directory:

##### For JavaScript:
```bash
# Using npm script
npm run langgraph:dev
```

##### For Python:
```bash
pip install -U "langgraph-cli[inmem]"      # requires Python 3.11+
langgraph dev -c ch9/py/langgraph.json --verbose
```

The server starts on <http://localhost:2024>; its OpenAPI docs live at `/docs`, and LangGraph
Studio opens automatically.

### Chapter 10: Evaluation

Shows how to evaluate LangChain applications, including agent evaluation for RAG and SQL, and creating datasets.

Files:
- `ch10/js/*.js`: JavaScript examples
- `ch10/py/*.py`: Python examples

## Docker Setup and Usage

Several examples in this repository require Docker to be installed and running to set up a PostgreSQL database with the pgvector extension. This section provides guidance on setting up Docker and running the PostgreSQL container.


### Installing Docker
1. Download Docker Desktop:

Go to the Docker [website](https://www.docker.com/get-started/) and download the appropriate version for your operating system (Windows, macOS, or Linux).

2. Install Docker Desktop:

- Windows: Double-click the downloaded installer and follow the on-screen instructions. You may need to enable virtualization in your BIOS settings.

- macOS: Drag the Docker icon to the Applications folder and double-click to start.

- Linux: Follow the instructions provided on the Docker website for your specific distribution.

3. Start Docker Desktop:

After installation, start Docker Desktop. On Windows and macOS, it will run in the system tray. On Linux, you may need to start it manually.

4. Verify the installation:

To check if Docker is installed, run:
```bash
docker --version
```


### Running the PostgreSQL Container

Run the Docker command:

Open a terminal or command prompt and run the following command to start the PostgreSQL container with the pgvector extension:

```bash
docker run \
    --name pgvector-container \
    -e POSTGRES_USER=langchain \
    -e POSTGRES_PASSWORD=langchain \
    -e POSTGRES_DB=langchain \
    -p 6024:5432 \
    -d pgvector/pgvector:pg16
```

Explanation of the command:

- `docker run`: Starts a new container.
- `--name pgvector-container`: Assigns the name "pgvector-container" to the container.
- `-e POSTGRES_USER=langchain`: Sets the PostgreSQL user to "langchain".
- `-e POSTGRES_PASSWORD=langchain`: Sets the PostgreSQL password to "langchain".
- `-e POSTGRES_DB=langchain`: Sets the default database name to "langchain".
- `-p 6024:5432`: Maps port 6024 on your host machine to port 5432 in the container (PostgreSQL's default port).
- `-d pgvector/pgvector:pg16`: Specifies the image to use (pgvector/pgvector:pg16), which includes PostgreSQL 16 and the pgvector extension.

#### Verify the Container is Running:

Run the following command to list running containers:

```bash
docker ps
```

You should see the "pgvector-container" listed with a status of "Up".

#### Accessing the PostgreSQL Database:

You can now access the PostgreSQL database from your code using the following connection string:

```
postgresql://langchain:langchain@localhost:6024/langchain
```

### Troubleshooting Docker

#### Docker Desktop Not Starting:

- **Windows**: Ensure that virtualization is enabled in your BIOS settings. Check the Docker Desktop logs for any specific error messages.
- **macOS**: Make sure you have granted Docker Desktop the necessary permissions in System Preferences.
- **Linux**: Ensure that the Docker daemon is running and that your user has the necessary permissions to run Docker commands.

#### Container Not Running:

Check the container logs for any errors:

```bash
docker logs pgvector-container
```

Look for error messages related to PostgreSQL startup or pgvector initialization.

#### Port Conflict:

If port 6024 is already in use, you can change the port mapping in the docker run command to an available port. For example, `-p 6025:5432`.

#### Image Not Found:

Ensure that you have an internet connection and that the pgvector/pgvector:pg16 image is available on Docker Hub.

#### Permissions Issues:

On Linux, you may encounter permissions issues when running Docker commands. Ensure that your user is part of the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### General Docker Troubleshooting:

- Restart Docker Desktop
- Update Docker Desktop to the latest version
- Check the Docker documentation for troubleshooting tips specific to your operating system

### Setting up Chinook.db with SQLite

Some examples in Chapter 3 and Chapter 10 use the Chinook database, a sample database for a digital media store, with SQLite. Here's how to set it up:

#### Download the Chinook Database Schema:

Open a terminal or command prompt and use curl to download the Chinook databas:

```bash
curl -s https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql | sqlite3 Chinook.db
```

This will create a file called `Chinook.db` in the current directory.

#### Verify the Setup:

You can verify that the database is set up correctly by connecting to it using the sqlite3 tool and running a simple query:

```bash
sqlite3 Chinook.db
```

Then, inside the sqlite3 prompt, run:

```sql
SELECT * FROM Artist LIMIT 10;
```

If the setup is successful, you should see the first 10 rows from the Artist table.

#### Place Chinook.db in the Correct Directory:

Ensure that the Chinook.db file is located in the same directory as the code examples that use it.

## General Troubleshooting

### Dependency Conflicts:

If you encounter errors related to conflicting dependencies, try creating a fresh virtual environment and reinstalling the dependencies.

Ensure that your package.json or pyproject.toml files specify compatible versions of the libraries.

### PgVector Vector Store Installation or Connection Errors:

#### Errors for Python:

If you can't find `psycopg` or `psycopg_binary`: Try to reinstall psycopg with the `[binary]` extra, which includes pre-compiled binaries and necessary dependencies:

```bash
pip install psycopg[binary]
```

Then run the file again.

If you're having issues connecting to Postgres via Docker, you can try some alternative vector stores:

1. Use the memory vector store instead: This is a simple vector store that stores vectors in memory. It is not persistent and will be lost when the program is terminated. Here's the [API for Python](https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/memory) and [docs for Javascript](https://js.langchain.com/docs/modules/data_connection/vectorstores/integrations/memory).

2. You can also use Chroma-- an AI-native open-source vector database. You can install Chroma as per the instructions for [Python](https://python.langchain.com/docs/integrations/vectorstores/chroma) or [Javascript](https://js.langchain.com/docs/modules/data_connection/vectorstores/integrations/chroma).














