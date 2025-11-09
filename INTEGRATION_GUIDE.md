# Integration Guide: Copilot Search & LangChain

This guide covers the new integrations added to MEGA-Bot: Copilot Search and LangChain.

## Overview

MEGA-Bot now includes two powerful new integrations:

1. **Copilot Search** - Bing AI-powered search that seamlessly blends traditional and generative search
2. **LangChain** - Advanced AI orchestration with chain composition and agent-based reasoning

## Copilot Search Integration

### Features

- **Hybrid Search**: Combines traditional web search with AI-generated answers
- **Intelligent Curation**: Provides carefully curated information from across the web
- **Source Attribution**: Proper citations to support a healthy web ecosystem
- **Multiple Search Types**: Web, news, images, videos

### Configuration

Add your Bing Search API key to `.env`:

```bash
BING_SEARCH_API_KEY=your-bing-search-api-key-here
```

Configure in `config.json`:

```json
{
  "copilot_search": {
    "enabled": true,
    "endpoint": "https://api.bing.microsoft.com/v7.0/search",
    "max_results": 10,
    "safe_search": "Moderate"
  }
}
```

### Usage

#### Basic Query

```python
from megabot import MegaBot, Config
import asyncio

async def search_example():
    config = Config()
    config.set("copilot_search.enabled", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    # Perform hybrid search
    result = await bot.query("What are the latest AI trends?")
    
    print("AI Answer:", result['answer'])
    print("Web Results:", result['web_results'])
    print("Sources:", result['sources'])
    
    await bot.stop()

asyncio.run(search_example())
```

#### Deep Research

```python
async def research_example():
    config = Config()
    config.set("copilot_search.enabled", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    # Perform deep research
    result = await bot.research("Quantum Computing", depth="deep")
    
    print("Topic:", result['topic'])
    print("Findings:", result['findings'])
    print("Synthesis:", result['synthesis'])
    print("Sources:", result['sources'])
    print("Related Topics:", result['related_topics'])
    
    await bot.stop()
```

### Capabilities

- `query` - Hybrid search with AI answers
- `research` - Deep research with synthesis
- `web_search` - Traditional web search
- `generative_answers` - AI-generated responses
- `source_attribution` - Proper citations
- `related_topics` - Topic exploration
- `news_search` - Latest news
- `image_search` - Image results
- `video_search` - Video content

## LangChain Integration

### Features

- **Chain Composition**: Multiple chain types for different use cases
- **Conversational Memory**: Context preservation across interactions
- **Agent-Based Reasoning**: Tool-augmented agents for complex tasks
- **Document Q&A**: Retrieval-based question answering
- **Multi-Step Workflows**: Sequential processing pipelines

### Configuration

Add your LLM API key to `.env`:

```bash
LANGCHAIN_API_KEY=your-llm-api-key-here
```

Configure in `config.json`:

```json
{
  "langchain": {
    "enabled": true,
    "llm_provider": "openai",
    "temperature": 0.7,
    "max_tokens": 2000,
    "enable_memory": true,
    "enable_tools": true
  }
}
```

### Usage

#### LLM Chain (Simple)

```python
from megabot import MegaBot, Config
import asyncio

async def llm_chain_example():
    config = Config()
    config.set("langchain.enabled", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    # Simple LLM query
    result = await bot.query("Explain neural networks")
    
    print("Response:", result['response'])
    
    await bot.stop()
```

#### Sequential Chain

```python
async def sequential_chain_example():
    config = Config()
    config.set("langchain.enabled", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    # Multi-step processing
    context = {'chain_type': 'sequential_chain'}
    result = await bot.query("Analyze and summarize this topic", context=context)
    
    print("Result:", result['response'])
    
    await bot.stop()
```

#### Conversational Chain with Memory

```python
async def conversation_example():
    config = Config()
    config.set("langchain.enabled", True)
    config.set("langchain.enable_memory", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    context = {'chain_type': 'conversation_chain'}
    
    # First message
    result1 = await bot.query("Tell me about Python", context=context)
    print("Response 1:", result1['response'])
    
    # Follow-up (memory preserved)
    result2 = await bot.query("What are its main features?", context=context)
    print("Response 2:", result2['response'])
    
    await bot.stop()
```

#### Retrieval QA

```python
async def retrieval_qa_example():
    config = Config()
    config.set("langchain.enabled", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    context = {'chain_type': 'retrieval_qa'}
    result = await bot.query("What is machine learning?", context=context)
    
    print("Answer:", result['response'])
    print("Sources:", result['sources'])
    
    await bot.stop()
```

#### Agent with Tools

```python
async def agent_example():
    config = Config()
    config.set("langchain.enabled", True)
    config.set("langchain.enable_tools", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    context = {'chain_type': 'agent_executor'}
    result = await bot.query("Research and calculate ROI", context=context)
    
    print("Response:", result['response'])
    print("Reasoning Steps:", result['intermediate_steps'])
    
    await bot.stop()
```

### Chain Types

1. **llm_chain**: Direct LLM inference with prompt formatting
2. **sequential_chain**: Multi-step processing pipeline
3. **conversation_chain**: Context-aware conversations with memory
4. **retrieval_qa**: Document-based question answering
5. **agent_executor**: Reasoning with tool usage

### Capabilities

- `query` - Text generation and inference
- `research` - Multi-step research with reasoning
- `chain_composition` - Combine multiple chains
- `conversational_memory` - Context preservation
- `document_qa` - Document-based Q&A
- `agent_reasoning` - Tool-augmented reasoning
- `tool_usage` - External tool integration
- `web_search` - Web search tool
- `calculator` - Math calculations
- `python_repl` - Python code execution
- `api_calls` - External API integration

## Combined Usage

Use both integrations together for maximum power:

```python
async def combined_example():
    config = Config()
    config.set("copilot_search.enabled", True)
    config.set("langchain.enabled", True)
    config.set("langchain.enable_tools", True)
    
    bot = MegaBot(config)
    await bot.start()
    
    # Step 1: Gather information with Copilot Search
    search_result = await bot.query("Latest AI trends")
    
    # Step 2: Synthesize with LangChain agent
    context = {'chain_type': 'agent_executor'}
    synthesis = await bot.query(
        f"Analyze these findings: {search_result['synthesis']}", 
        context=context
    )
    
    print("Web Results:", search_result['web_results'])
    print("AI Synthesis:", synthesis['response'])
    print("Reasoning:", synthesis['intermediate_steps'])
    
    await bot.stop()
```

## Multi-Language Support

### Python (Native)

MEGA-Bot is built in Python 3.8+ with full async/await support:

```python
# Native Python
from megabot import MegaBot, Config
import asyncio

async def main():
    bot = MegaBot(Config())
    await bot.start()
    result = await bot.query("prompt")
    await bot.stop()

asyncio.run(main())
```

### Java Interoperability

Use `py4j` for Python-Java bridge:

```bash
pip install py4j
```

Python bridge server:

```python
from py4j.java_gateway import JavaGateway, GatewayParameters

class PythonBridge:
    def __init__(self):
        self.bot = MegaBot(Config())
    
    def query(self, prompt):
        return asyncio.run(self.bot.query(prompt))

gateway = JavaGateway(gateway_parameters=GatewayParameters(port=25333))
python_bridge = PythonBridge()
gateway.entry_point = python_bridge
gateway.start()
```

Java client:

```java
import py4j.GatewayServer;

public class MegaBotClient {
    public static void main(String[] args) {
        GatewayServer server = new GatewayServer(new PythonBridge());
        server.start();
        
        // Call Python functions
        String result = pythonBridge.query("What is AI?");
        System.out.println(result);
    }
}
```

### JavaScript/Node.js Interoperability

#### Option 1: python-shell

```bash
npm install python-shell
```

```javascript
const { PythonShell } = require('python-shell');

let options = {
  mode: 'json',
  pythonPath: 'python3',
  scriptPath: './megabot',
  args: ['--query', 'What is AI?']
};

PythonShell.run('main.py', options, (err, results) => {
  if (err) throw err;
  console.log(results);
});
```

#### Option 2: child_process

```javascript
const { spawn } = require('child_process');

const python = spawn('python3', [
  'main.py',
  '--query', 'What is AI?'
]);

python.stdout.on('data', (data) => {
  console.log(`Result: ${data}`);
});

python.stderr.on('data', (data) => {
  console.error(`Error: ${data}`);
});
```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific integration tests:

```bash
pytest tests/test_new_integrations.py -v
```

## Examples

See the following example files:

- `examples/langchain_copilot_search_example.py` - Comprehensive demo
- `examples/basic_usage.py` - Basic MEGA-Bot usage
- `examples/advanced_research.py` - Advanced research
- `examples/workflow_automation.py` - Workflow automation

## Requirements

### Python

- Python 3.8+
- See `requirements.txt` for dependencies

### LangChain Dependencies (Optional)

```bash
pip install langchain langchain-community langchain-openai
```

### Java Bridge (Optional)

```bash
pip install py4j
```

### Node.js Bridge (Optional)

```bash
npm install python-shell
```

## Troubleshooting

### Copilot Search Not Working

1. Check your Bing Search API key in `.env`
2. Verify `copilot_search.enabled` is `true` in config
3. Check API rate limits

### LangChain Not Working

1. Check your LLM API key in `.env`
2. Verify `langchain.enabled` is `true` in config
3. Check LLM provider configuration
4. Verify LangChain packages are installed

### Java Bridge Issues

1. Ensure `py4j` is installed
2. Check port 25333 is available
3. Verify Java and Python are compatible versions

### Node.js Bridge Issues

1. Ensure `python-shell` is installed
2. Verify Python path is correct
3. Check script paths are absolute

## Security

- Never commit API keys to version control
- Use `.env` file for sensitive configuration
- Review GitHub Actions permissions
- Keep dependencies up to date

## Support

For issues and questions:

1. Check the documentation
2. Review example files
3. Open an issue on GitHub
4. Consult the community

## License

MIT License - See LICENSE file for details
