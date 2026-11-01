"""Background runner for the Research Agent - 3 cycles."""
import sys
import asyncio
import logging
from datetime import datetime

sys.path.insert(0, '.')

from research_agent.utf8_logging import ensure_utf8, make_utf8_stream_handler

ensure_utf8()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_agent/data/agent_output.log', encoding='utf-8'),
        make_utf8_stream_handler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    from research_agent.orchestrator import ResearchOrchestrator
    from research_agent.config import get_config
    
    logger.info(f"=== Background Agent Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    config = get_config()
    config.max_research_cycles = 3
    
    orchestrator = ResearchOrchestrator(config)
    
    try:
        await orchestrator.start('heritability of intelligence and embryo selection')
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
    finally:
        logger.info(f"=== Background Agent Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user; exiting cleanly.")
        sys.exit(0)
