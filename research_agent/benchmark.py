"""
Benchmark script to measure Research Agent cycle performance.
Runs a single cycle and reports timing for each phase.
"""

import sys
import time
import asyncio
import logging

sys.path.insert(0, '.')

from research_agent.config import get_config
from research_agent.orchestrator import ResearchOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def benchmark_single_cycle():
    """Run a single research cycle and measure timing."""
    config = get_config()
    config.max_research_cycles = 1  # Only 1 cycle
    config.research_interval = 0    # No delay between cycles
    
    orchestrator = ResearchOrchestrator(config)
    
    topic = "heritability intelligence twin study GWAS polygenic scores"
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Single Cycle Performance Test")
    print(f"Topic: {topic}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    try:
        # Time the cycle
        cycle_start = time.time()
        
        # Run just one cycle manually
        orchestrator.current_topic = topic
        orchestrator.running = True
        
        # Create session
        from research_agent.models import ResearchSession, now_iso, gen_id
        session = ResearchSession(id=gen_id(), topic=topic, start_time=now_iso(), status="active")
        orchestrator.db.save_session(session.to_dict())
        orchestrator.current_session = orchestrator.db.get_session(session.id)
        
        # Run the cycle
        await orchestrator._run_cycle(1)
        
        cycle_end = time.time()
        cycle_time = cycle_end - cycle_start
        
        print(f"\n{'='*60}")
        print(f"BENCHMARK RESULTS")
        print(f"{'='*60}")
        print(f"Total Cycle Time: {cycle_time:.2f} seconds")
        print(f"Total Cycle Time: {cycle_time/60:.1f} minutes")
        print(f"{'='*60}\n")
        
        # Get stats
        stats = orchestrator.db.get_stats()
        print(f"Database Stats:")
        print(f"  Sources: {stats.get('sources', 0)}")
        print(f"  Facts: {stats.get('facts', 0)}")
        print(f"  Hypotheses: {stats.get('hypotheses', 0)}")
        print(f"  Evidence: {stats.get('evidence', 0)}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await orchestrator._cleanup()
    
    return cycle_time


if __name__ == "__main__":
    cycle_time = asyncio.run(benchmark_single_cycle())
    print(f"\nFinal benchmark: {cycle_time:.2f}s per cycle")
