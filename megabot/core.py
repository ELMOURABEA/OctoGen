"""
Core OctoGen implementation with Agent HQ integration
"""
import asyncio
from typing import Dict, Any, List, Optional
from .config import Config
from .integrations import (
    CopilotIntegration,
    GeminiIntegration,
    ChatGPTIntegration,
    GrokIntegration
)
from .database import ResearchEngine, DatabaseStorage
from .workflow import TaskScheduler, PermissionManager, AutoUpdateManager
from .utils import get_logger, validate_query, validate_topic, sanitize_input
from .monetization import MonetizationManager
from .advertising import AdvertisingCore
from .agenthq import AgentHQCoordinator


class MegaBot:
    """
    OctoGen - Unified AI agent integrating multiple platforms with Agent HQ
    
    Features:
    - Deep research across multiple AI platforms
    - Database workflow with full permissions
    - Multi-tasking with auto-update capabilities
    - Integration with Co-Pilot, Gemini 2.5 Pro, ChatGPT 5, and Grok 4 Super
    - Agent HQ orchestration with Octopus Brain
    - LangChain and LangGraph integration
    - Cloud and enterprise deployment capabilities
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize OctoGen
        
        Args:
            config: Configuration object (creates default if not provided)
        """
        self.config = config or Config()
        self.logger = get_logger("core")
        
        # Initialize database storage
        self.storage = DatabaseStorage(self.config.get("database.path", "megabot.db"))
        
        # Initialize AI platform integrations
        self.integrations = self._init_integrations()
        
        # Initialize research engine
        self.research_engine = ResearchEngine(self.integrations, self.storage)
        
        # Initialize Agent HQ Coordinator
        self.agent_hq = AgentHQCoordinator(
            self.integrations,
            self.storage,
            self.logger
        )
        
        # Initialize workflow components
        self.permission_manager = PermissionManager(
            self.config.get("workflow.permission_level", "full")
        )
        
        self.task_scheduler = TaskScheduler(
            self.config.get("workflow.max_concurrent_tasks", 10),
            self.storage
        )
        
        self.auto_update_manager = AutoUpdateManager(
            self.integrations,
            self.storage,
            self.config.get("workflow.auto_update_interval", 3600)
        )
        
        # Initialize monetization (if enabled)
        if self.config.get("monetization.enabled", False):
            tier = self.config.get("monetization.tier", "free")
            self.monetization = MonetizationManager(tier)
            self.logger.info(f"Monetization enabled with {tier} tier")
        else:
            self.monetization = None
        
        # Initialize advertising (if enabled)
        if self.config.get("monetization.advertising_enabled", False):
            ad_config = self.config.get("advertising", {})
            self.advertising = AdvertisingCore(ad_config)
            self.advertising.initialize()
            self.logger.info("Advertising core initialized")
        else:
            self.advertising = None
        
        # Track running state
        self.running = False
        self.background_tasks: List[asyncio.Task] = []
        
        self.logger.debug("OctoGen initialized successfully with Agent HQ")
    
    def _init_integrations(self) -> List:
        """Initialize all AI platform integrations"""
        api_keys = self.config.get("api_keys", {})
        
        integrations = [
            CopilotIntegration(api_keys.get("copilot", ""), self.config.config),
            GeminiIntegration(api_keys.get("gemini", ""), self.config.config),
            ChatGPTIntegration(api_keys.get("chatgpt", ""), self.config.config),
            GrokIntegration(api_keys.get("grok", ""), self.config.config)
        ]
        
        return integrations
    
    async def start(self):
        """Start OctoGen with all services"""
        if self.running:
            print("OctoGen is already running")
            return
        
        print("Starting OctoGen with Agent HQ...")
        self.running = True
        
        # Start auto-update service if enabled
        if self.config.get("features.auto_update", True):
            update_task = asyncio.create_task(self.auto_update_manager.start())
            self.background_tasks.append(update_task)
            print("✓ Auto-update service started")
        
        # Get initial updates from all platforms
        if self.config.get("features.document_sync", True):
            await self.sync_documents()
            print("✓ Initial document sync completed")
        
        print(f"✓ OctoGen started with {len([i for i in self.integrations if i.is_available()])} active integrations")
        print(f"  - Platforms: {', '.join([i.platform_name for i in self.integrations if i.is_available()])}")
        print(f"  - Agent HQ: {len(self.agent_hq.list_agents())} agents registered")
        
        return True
    
    async def stop(self):
        """Stop OctoGen and all services"""
        if not self.running:
            return
        
        print("Stopping OctoGen...")
        self.running = False
        
        # Stop auto-update
        await self.auto_update_manager.stop()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        print("✓ OctoGen stopped")
    
    async def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query all AI platforms and aggregate responses
        
        Args:
            prompt: Query prompt
            context: Optional context information
            
        Returns:
            Aggregated responses from all platforms
        """
        # Check monetization limits
        if self.monetization:
            can_query, limit_msg = self.monetization.can_query()
            if not can_query:
                self.logger.warning(f"Query blocked by monetization: {limit_msg}")
                return {"error": limit_msg, "responses": {}}
        
        # Validate input
        is_valid, error_msg = validate_query(prompt)
        if not is_valid:
            self.logger.error(f"Invalid query: {error_msg}")
            return {"error": error_msg, "responses": {}}
        
        # Sanitize input
        prompt = sanitize_input(prompt)
        
        if not self.permission_manager.check_api_access():
            self.logger.warning("API access permission denied")
            return {"error": "API access permission denied"}
        
        self.logger.info(f"Querying all platforms: {prompt[:100]}...")
        print(f"Querying all platforms: {prompt}")
        
        try:
            result = await self.research_engine.query_all_platforms(prompt, context)
            
            # Add synthesis
            result["synthesis"] = self._synthesize_responses(result["responses"])
            
            # Record usage for monetization
            if self.monetization:
                self.monetization.record_query()
            
            self.logger.info(f"Query completed successfully, {len(result['responses'])} platforms responded")
            return result
        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}", exc_info=True)
            return {"error": f"Query failed: {str(e)}", "responses": {}}
    
    async def research(self, topic: str, depth: str = "deep") -> Dict[str, Any]:
        """
        Perform deep research across all platforms
        
        Args:
            topic: Research topic
            depth: Research depth (shallow, medium, deep)
            
        Returns:
            Comprehensive research results
        """
        # Validate topic
        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            self.logger.error(f"Invalid topic: {error_msg}")
            return {"error": error_msg, "platforms_used": [], "synthesis": {}}
        
        # Sanitize input
        topic = sanitize_input(topic)
        
        # Validate depth
        valid_depths = ["shallow", "medium", "deep"]
        if depth not in valid_depths:
            self.logger.warning(f"Invalid depth '{depth}', defaulting to 'medium'")
            depth = "medium"
        
        # Check monetization limits
        if self.monetization:
            can_research, limit_msg = self.monetization.can_research(depth)
            if not can_research:
                self.logger.warning(f"Research blocked by monetization: {limit_msg}")
                return {"error": limit_msg, "platforms_used": [], "synthesis": {}}
        
        if not self.permission_manager.check_research_access():
            self.logger.warning("Research permission denied")
            return {"error": "Research permission denied"}
        
        self.logger.info(f"Performing {depth} research on: {topic}")
        print(f"Performing {depth} research on: {topic}")
        
        try:
            result = await self.research_engine.deep_research(
                topic,
                depth,
                use_cache=self.config.get("database.research_cache_enabled", True)
            )
            
            # Record usage for monetization
            if self.monetization:
                self.monetization.record_research()
            
            self.logger.info(f"Research completed successfully for: {topic}")
            return result
        except Exception as e:
            self.logger.error(f"Research failed: {str(e)}", exc_info=True)
            return {"error": f"Research failed: {str(e)}", "platforms_used": [], "synthesis": {}}
    
    async def sync_documents(self):
        """Synchronize latest documents from all platforms"""
        if not self.permission_manager.check_api_access():
            return {"error": "API access permission denied"}
        
        print("Synchronizing documents from all platforms...")
        await self.auto_update_manager.update_all()
        print("✓ Document sync completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of OctoGen"""
        status = {
            "running": self.running,
            "integrations": {
                "total": len(self.integrations),
                "active": len([i for i in self.integrations if i.is_available()]),
                "platforms": [
                    {
                        "name": i.platform_name,
                        "available": i.is_available(),
                        "capabilities": i.get_capabilities()
                    }
                    for i in self.integrations
                ]
            },
            "permissions": {
                "database": self.permission_manager.check_database_access(),
                "api": self.permission_manager.check_api_access(),
                "workflow": self.permission_manager.check_workflow_execution(),
                "research": self.permission_manager.check_research_access()
            },
            "features": {
                "deep_research": self.config.get("features.deep_research", True),
                "multi_tasking": self.config.get("features.multi_tasking", True),
                "auto_update": self.config.get("features.auto_update", True),
                "document_sync": self.config.get("features.document_sync", True)
            },
            "last_updates": {
                platform: self.auto_update_manager.get_last_update_time(platform)
                for platform in [i.platform_name for i in self.integrations if i.is_available()]
            },
            "agent_hq": self.agent_hq.get_status()
        }
        
        # Add monetization info if enabled
        if self.monetization:
            status["monetization"] = self.monetization.get_tier_info()
        
        # Add advertising info if enabled
        if self.advertising:
            status["advertising"] = self.advertising.get_config()
        
        return status
    
    def get_capabilities(self) -> List[str]:
        """Get all capabilities from all platforms"""
        capabilities = set()
        for integration in self.integrations:
            if integration.is_available():
                capabilities.update(integration.get_capabilities())
        return list(capabilities)
    
    def get_updates(self, platform: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest updates from platforms"""
        if platform:
            return self.auto_update_manager.get_platform_updates(platform, limit)
        return self.auto_update_manager.get_all_updates(limit)
    
    def _synthesize_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize responses from multiple platforms into unified answer"""
        if not responses:
            return {"summary": "No responses available"}
        
        synthesis = {
            "platforms_responded": len(responses),
            "unified_response": f"Combined insights from {len(responses)} AI platforms",
            "key_points": [],
            "confidence_scores": {}
        }
        
        # Extract key information from each platform
        for platform, data in responses.items():
            if "response" in data:
                synthesis["key_points"].append({
                    "platform": platform,
                    "response": data["response"]
                })
            
            if "confidence" in data:
                synthesis["confidence_scores"][platform] = data["confidence"]
        
        # Calculate average confidence
        if synthesis["confidence_scores"]:
            avg_confidence = sum(synthesis["confidence_scores"].values()) / len(synthesis["confidence_scores"])
            synthesis["average_confidence"] = round(avg_confidence, 2)
        
        return synthesis
    
    async def execute_workflow(self, workflow_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a custom workflow
        
        Args:
            workflow_name: Name of the workflow
            **kwargs: Workflow parameters
            
        Returns:
            Workflow execution results
        """
        if not self.permission_manager.check_workflow_execution():
            return {"error": "Workflow execution permission denied"}
        
        # Example workflow implementation
        workflows = {
            "comprehensive_analysis": self._workflow_comprehensive_analysis,
            "multi_platform_query": self._workflow_multi_platform_query,
            "deep_dive_research": self._workflow_deep_dive_research
        }
        
        if workflow_name in workflows:
            return await workflows[workflow_name](**kwargs)
        
        return {"error": f"Unknown workflow: {workflow_name}"}
    
    async def _workflow_comprehensive_analysis(self, topic: str) -> Dict[str, Any]:
        """Comprehensive analysis workflow"""
        results = {}
        
        # Step 1: Deep research
        results["research"] = await self.research(topic, "deep")
        
        # Step 2: Query all platforms
        results["queries"] = await self.query(f"Provide detailed analysis of {topic}")
        
        # Step 3: Synthesis
        results["final_analysis"] = {
            "topic": topic,
            "platforms_used": len(results["queries"]["responses"]),
            "research_findings": len(results["research"].get("findings", {})),
            "summary": f"Comprehensive analysis completed using {len(self.integrations)} AI platforms"
        }
        
        return results
    
    async def _workflow_multi_platform_query(self, query: str) -> Dict[str, Any]:
        """Multi-platform query workflow"""
        return await self.query(query)
    
    async def _workflow_deep_dive_research(self, topics: List[str]) -> Dict[str, Any]:
        """Deep dive research on multiple topics"""
        results = {}
        
        for topic in topics:
            results[topic] = await self.research(topic, "deep")
        
        return {
            "topics_researched": len(topics),
            "results": results
        }
    
    def get_subscription_tiers(self) -> Dict[str, Any]:
        """Get information about available subscription tiers"""
        if self.monetization:
            return MonetizationManager.get_all_tiers()
        return {}
    
    def get_tier_info(self) -> Dict[str, Any]:
        """Get current subscription tier information"""
        if self.monetization:
            return self.monetization.get_tier_info()
        return {"tier": "unlimited", "note": "Monetization not enabled"}
    
    def show_banner_ad(self, position: str = "bottom") -> Dict[str, Any]:
        """
        Show banner advertisement
        
        Args:
            position: Banner position (top, bottom)
        
        Returns:
            Result dictionary
        """
        if self.advertising:
            return self.advertising.show_banner(position)
        return {"status": "disabled", "message": "Advertising not enabled"}
    
    def show_rewarded_ad(self, reward_type: str = "bonus_queries") -> Dict[str, Any]:
        """
        Show rewarded advertisement
        
        Args:
            reward_type: Type of reward (bonus_queries, bonus_research, tier_upgrade)
        
        Returns:
            Result dictionary with reward info
        """
        if self.advertising:
            result = self.advertising.show_rewarded(reward_type)
            
            # Apply reward if successful
            if result.get("status") == "success" and self.monetization:
                reward = result.get("reward", {})
                if reward_type == "bonus_queries":
                    # Apply bonus queries to the user's account
                    amount = reward.get("amount", 1)
                    if hasattr(self.monetization, "add_bonus_queries"):
                        self.monetization.add_bonus_queries(amount)
                        self.logger.info(f"Bonus queries applied: {amount}")
                    else:
                        self.logger.warning("Bonus queries reward not applied: MonetizationManager.add_bonus_queries not implemented")
                elif reward_type == "bonus_research":
                    # Apply bonus research to the user's account
                    amount = reward.get("amount", 1)
                    if hasattr(self.monetization, "add_bonus_research"):
                        self.monetization.add_bonus_research(amount)
                        self.logger.info(f"Bonus research applied: {amount}")
                    else:
                        self.logger.warning("Bonus research reward not applied: MonetizationManager.add_bonus_research not implemented")
            
            return result
        return {"status": "disabled", "message": "Advertising not enabled"}
    
    # ===== Agent HQ Methods =====
    
    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered agents
        
        Args:
            status: Optional filter by status (active, available, inactive)
            
        Returns:
            List of agent information dictionaries
        """
        return self.agent_hq.list_agents(status)
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent information dictionary or None
        """
        return self.agent_hq.get_agent_info(agent_name)
    
    async def orchestrate_agents(
        self,
        task: str,
        agents: Optional[List[str]] = None,
        mode: str = "sequential",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate multiple agents to complete a task
        
        Args:
            task: Task description
            agents: List of agent names (or None for automatic selection)
            mode: Orchestration mode (sequential, parallel, adaptive)
            context: Optional context information
            
        Returns:
            Orchestration results
        """
        return await self.agent_hq.orchestrate(task, agents, mode, context)
    
    async def agent_hq_self_update(self) -> Dict[str, Any]:
        """
        Trigger Agent HQ self-update
        
        Returns:
            Update results
        """
        return await self.agent_hq.self_update()
    
    async def agent_hq_self_build(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent HQ self-build new workflows based on requirements
        
        Args:
            requirements: Build requirements specification
            
        Returns:
            Build results
        """
        return await self.agent_hq.self_build(requirements)
    
    def get_agent_hq_status(self) -> Dict[str, Any]:
        """
        Get Agent HQ status
        
        Returns:
            Status dictionary
        """
        return self.agent_hq.get_status()
    
    async def create_langchain(
        self,
        steps: List[str],
        initial_input: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and execute a LangChain workflow
        
        Args:
            steps: List of chain step descriptions
            initial_input: Initial input for the chain
            context: Optional context information
            
        Returns:
            Execution results
        """
        return await self.agent_hq.langchain.execute_chain_from_steps(
            steps, initial_input, context
        )
    
    async def create_langgraph(
        self,
        steps: List[Dict[str, Any]],
        initial_state: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and execute a LangGraph workflow
        
        Args:
            steps: List of graph step definitions
            initial_state: Initial state for the graph
            context: Optional context information
            
        Returns:
            Execution results
        """
        return await self.agent_hq.langgraph.execute_graph_from_steps(
            steps, initial_state, context
        )
    
    # ===== Octopus Brain Methods =====
    
    def get_all_tentacles(self) -> List[Dict[str, Any]]:
        """
        Get all tentacles (agents) registered in Octopus Brain
        
        Returns:
            List of tentacle information
        """
        return self.agent_hq.octopus_brain.get_all_tentacles()
    
    def get_tentacle_status(self, tentacle_name: str) -> Dict[str, Any]:
        """
        Get status of a specific tentacle
        
        Args:
            tentacle_name: Name of the tentacle
            
        Returns:
            Tentacle status dictionary
        """
        return self.agent_hq.octopus_brain.get_tentacle_status(tentacle_name)
    
    def get_octopus_brain_status(self) -> Dict[str, Any]:
        """
        Get Octopus Brain status
        
        Returns:
            Brain status dictionary
        """
        return self.agent_hq.octopus_brain.get_status()
    
    async def octopus_coordinate(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use Octopus Brain to coordinate tentacles for a task
        
        Args:
            task: Task description
            context: Optional context information
            
        Returns:
            Coordination results
        """
        return await self.agent_hq.octopus_brain.coordinate(task, context)
    
    # ===== Cloud Octopus Methods =====
    
    async def deploy_to_cloud(
        self,
        provider: str,
        regions: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deploy OctoGen to cloud provider
        
        Args:
            provider: Cloud provider (aws, gcp, azure)
            regions: List of regions
            config: Optional deployment configuration
            
        Returns:
            Deployment results
        """
        return await self.agent_hq.cloud_octopus.deploy(provider, regions, config)
    
    async def provision_cloud_storage(
        self,
        storage_types: Dict[str, bool],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provision cloud storage resources
        
        Args:
            storage_types: Dictionary of storage types to provision
            config: Optional storage configuration
            
        Returns:
            Provisioning results
        """
        return await self.agent_hq.cloud_octopus.provision_storage(storage_types, config)
    
    def get_cloud_status(self) -> Dict[str, Any]:
        """
        Get cloud deployment status
        
        Returns:
            Cloud status dictionary
        """
        return self.agent_hq.cloud_octopus.get_status()
    
    # ===== Enterprise Cloud Octogent Methods =====
    
    async def deploy_to_enterprise_cloud(
        self,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy to enterprise cloud infrastructure
        
        Args:
            config: Enterprise deployment configuration
            
        Returns:
            Deployment results
        """
        return await self.agent_hq.enterprise_octogent.deploy_enterprise(config)
    
    async def configure_enterprise_infrastructure(
        self,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure enterprise infrastructure
        
        Args:
            config: Infrastructure configuration
            
        Returns:
            Configuration results
        """
        return await self.agent_hq.enterprise_octogent.configure_infrastructure(config)
    
    def get_enterprise_octogent_status(self) -> Dict[str, Any]:
        """
        Get enterprise octogent status
        
        Returns:
            Status dictionary
        """
        return self.agent_hq.enterprise_octogent.get_status()
    
    def get_enterprise_capacity(self) -> Dict[str, Any]:
        """
        Get enterprise capacity information
        
        Returns:
            Capacity dictionary
        """
        return self.agent_hq.enterprise_octogent.get_capacity()
    
    def estimate_enterprise_costs(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate enterprise deployment costs
        
        Args:
            config: Optional cost configuration
            
        Returns:
            Cost estimation dictionary
        """
        return self.agent_hq.enterprise_octogent.estimate_costs(config)
