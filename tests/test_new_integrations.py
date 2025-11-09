"""
Tests for new integrations: Copilot Search and LangChain
"""
import pytest
from megabot.integrations import CopilotSearchIntegration, LangChainIntegration


class TestCopilotSearchIntegration:
    """Test Copilot Search integration"""
    
    def test_copilot_search_creation(self):
        """Test creating Copilot Search integration"""
        config = {
            'copilot_search': {
                'endpoint': 'https://api.bing.microsoft.com/v7.0/search',
                'max_results': 10,
                'safe_search': 'Moderate'
            }
        }
        integration = CopilotSearchIntegration('test-api-key', config)
        
        assert integration.name == "Copilot Search (Bing)"
        assert integration.is_available()
        assert integration.max_results == 10
        assert integration.safe_search == 'Moderate'
    
    @pytest.mark.asyncio
    async def test_copilot_search_query(self):
        """Test Copilot Search query"""
        config = {'copilot_search': {}}
        integration = CopilotSearchIntegration('test-api-key', config)
        
        result = await integration.query("What is quantum computing?")
        
        assert 'answer' in result
        assert 'web_results' in result
        assert 'sources' in result
        assert 'confidence' in result
        assert result['search_type'] == 'hybrid'
    
    @pytest.mark.asyncio
    async def test_copilot_search_research(self):
        """Test Copilot Search research"""
        config = {'copilot_search': {}}
        integration = CopilotSearchIntegration('test-api-key', config)
        
        result = await integration.research("Artificial Intelligence", depth="medium")
        
        assert 'topic' in result
        assert 'findings' in result
        assert 'synthesis' in result
        assert 'sources' in result
        assert 'related_topics' in result
        assert result['depth'] == 'medium'
    
    @pytest.mark.asyncio
    async def test_copilot_search_without_api_key(self):
        """Test Copilot Search without API key"""
        config = {'copilot_search': {}}
        integration = CopilotSearchIntegration('', config)
        
        result = await integration.query("test query")
        
        assert 'error' in result
        assert not integration.is_available()
    
    def test_copilot_search_capabilities(self):
        """Test Copilot Search capabilities"""
        config = {'copilot_search': {}}
        integration = CopilotSearchIntegration('test-api-key', config)
        
        capabilities = integration.get_capabilities()
        
        assert "query" in capabilities
        assert "research" in capabilities
        assert "web_search" in capabilities
        assert "generative_answers" in capabilities
        assert "source_attribution" in capabilities
    
    @pytest.mark.asyncio
    async def test_copilot_search_depth_levels(self):
        """Test different research depth levels"""
        config = {'copilot_search': {}}
        integration = CopilotSearchIntegration('test-api-key', config)
        
        # Test shallow depth
        result_shallow = await integration.research("AI", depth="shallow")
        assert result_shallow['depth'] == 'shallow'
        
        # Test medium depth
        result_medium = await integration.research("AI", depth="medium")
        assert result_medium['depth'] == 'medium'
        
        # Test deep depth
        result_deep = await integration.research("AI", depth="deep")
        assert result_deep['depth'] == 'deep'


class TestLangChainIntegration:
    """Test LangChain integration"""
    
    def test_langchain_creation(self):
        """Test creating LangChain integration"""
        config = {
            'langchain': {
                'llm_provider': 'openai',
                'temperature': 0.7,
                'max_tokens': 2000,
                'enable_memory': True,
                'enable_tools': True
            }
        }
        integration = LangChainIntegration('test-api-key', config)
        
        assert integration.name == "LangChain"
        assert integration.is_available()
        assert integration.llm_provider == 'openai'
        assert integration.temperature == 0.7
        assert integration.enable_memory
        assert integration.enable_tools
    
    @pytest.mark.asyncio
    async def test_langchain_query(self):
        """Test LangChain query"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        result = await integration.query("Explain machine learning")
        
        assert 'response' in result
        assert 'chain_type' in result
        assert 'metadata' in result
        assert result['chain_type'] == 'llm_chain'
    
    @pytest.mark.asyncio
    async def test_langchain_query_with_chain_type(self):
        """Test LangChain query with specific chain type"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        context = {'chain_type': 'agent_executor'}
        result = await integration.query("Complex question", context=context)
        
        assert result['chain_type'] == 'agent_executor'
        assert 'intermediate_steps' in result
        assert len(result['intermediate_steps']) > 0
    
    @pytest.mark.asyncio
    async def test_langchain_research(self):
        """Test LangChain research"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        result = await integration.research("Neural Networks", depth="medium")
        
        assert 'topic' in result
        assert 'findings' in result
        assert 'reasoning_steps' in result
        assert 'synthesis' in result
        assert 'sources' in result
        assert result['depth'] == 'medium'
    
    @pytest.mark.asyncio
    async def test_langchain_without_api_key(self):
        """Test LangChain without API key"""
        config = {'langchain': {}}
        integration = LangChainIntegration('', config)
        
        result = await integration.query("test query")
        
        assert 'error' in result
        assert not integration.is_available()
    
    def test_langchain_capabilities(self):
        """Test LangChain capabilities"""
        config = {
            'langchain': {
                'enable_tools': True
            }
        }
        integration = LangChainIntegration('test-api-key', config)
        
        capabilities = integration.get_capabilities()
        
        assert "query" in capabilities
        assert "research" in capabilities
        assert "chain_composition" in capabilities
        assert "conversational_memory" in capabilities
        assert "agent_reasoning" in capabilities
        assert "web_search" in capabilities
        assert "calculator" in capabilities
    
    def test_langchain_chain_types(self):
        """Test supported chain types"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        assert 'llm_chain' in integration.chain_types
        assert 'sequential_chain' in integration.chain_types
        assert 'conversation_chain' in integration.chain_types
        assert 'retrieval_qa' in integration.chain_types
        assert 'agent_executor' in integration.chain_types
    
    def test_langchain_create_chain(self):
        """Test creating a chain"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        result = integration.create_chain('sequential_chain')
        
        assert result['chain_type'] == 'sequential_chain'
        assert result['status'] == 'created'
        assert 'capabilities' in result
    
    def test_langchain_create_invalid_chain(self):
        """Test creating invalid chain type"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        result = integration.create_chain('invalid_chain_type')
        
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_langchain_research_depths(self):
        """Test different research depths"""
        config = {'langchain': {}}
        integration = LangChainIntegration('test-api-key', config)
        
        # Test shallow
        result_shallow = await integration.research("Topic", depth="shallow")
        assert len(result_shallow['reasoning_steps']) == 2
        
        # Test medium
        result_medium = await integration.research("Topic", depth="medium")
        assert len(result_medium['reasoning_steps']) == 4
        
        # Test deep
        result_deep = await integration.research("Topic", depth="deep")
        assert len(result_deep['reasoning_steps']) == 6


class TestCombinedIntegrations:
    """Test combined usage of Copilot Search and LangChain"""
    
    @pytest.mark.asyncio
    async def test_combined_query(self):
        """Test using both integrations together"""
        config = {
            'copilot_search': {},
            'langchain': {}
        }
        
        search = CopilotSearchIntegration('test-key-1', config)
        langchain = LangChainIntegration('test-key-2', config)
        
        # Get search results
        search_result = await search.query("AI trends")
        assert 'answer' in search_result
        
        # Process with LangChain
        chain_result = await langchain.query("Synthesize findings")
        assert 'response' in chain_result
    
    @pytest.mark.asyncio
    async def test_combined_research(self):
        """Test combined research workflow"""
        config = {
            'copilot_search': {},
            'langchain': {}
        }
        
        search = CopilotSearchIntegration('test-key-1', config)
        langchain = LangChainIntegration('test-key-2', config)
        
        # Research with Copilot Search
        search_findings = await search.research("Blockchain", depth="medium")
        assert len(search_findings['findings']) > 0
        
        # Synthesize with LangChain
        synthesis = await langchain.research("Blockchain", depth="medium")
        assert 'synthesis' in synthesis
    
    def test_combined_capabilities(self):
        """Test combined capabilities"""
        config = {
            'copilot_search': {},
            'langchain': {'enable_tools': True}
        }
        
        search = CopilotSearchIntegration('test-key-1', config)
        langchain = LangChainIntegration('test-key-2', config)
        
        search_caps = set(search.get_capabilities())
        langchain_caps = set(langchain.get_capabilities())
        
        # Combined capabilities
        all_caps = search_caps.union(langchain_caps)
        
        assert "web_search" in all_caps
        assert "generative_answers" in all_caps
        assert "chain_composition" in all_caps
        assert "agent_reasoning" in all_caps
