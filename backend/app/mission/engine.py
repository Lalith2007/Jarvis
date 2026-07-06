import logging
import time
from datetime import datetime
import concurrent.futures
import threading
from typing import Any, Dict

from app.mission.graph import MissionGraph, MissionNode, NodeStatus
from app.mission.capabilities import capability_manager
from app.mission.events import MissionEvent, MissionEventType
from app.platform.publisher import EventPublisher
from app.reflection.orchestrator import reflection_orchestrator

logger = logging.getLogger(__name__)


class GraphExecutionManager:
    """
    Executes a MissionGraph.
    Manages scheduling, parallel execution, topological sorting, dependencies,
    retries, timeouts, and failures.
    Delegates ALL actual execution to CapabilityManager.
    """

    def execute(self, graph: MissionGraph, mission_id: str, session_id: str | None = None) -> Any:
        start_time = time.time()
        
        # Publish MissionStarted
        EventPublisher.publish(
            subsystem="mission",
            event_type=MissionEventType.MISSION_STARTED.value,
            mission_id=mission_id,
            session_id=session_id,
        )

        completed_nodes: set[str] = set()
        failed_nodes: set[str] = set()
        in_progress_nodes: set[str] = set()
        
        # Build reverse dependency map for quick checking
        node_deps: Dict[str, set[str]] = {
            node_id: set(node.dependencies) for node_id, node in graph.nodes.items()
        }

        # Setup ThreadPool for parallel execution
        # Max workers can be tuned. Using 10 for stress test concurrency.
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures: Dict[concurrent.futures.Future, str] = {}
            
            while len(completed_nodes) + len(failed_nodes) < len(graph.nodes):
                # Find runnable nodes
                runnable_nodes = []
                for node_id, deps in node_deps.items():
                    if node_id not in completed_nodes and node_id not in failed_nodes and node_id not in in_progress_nodes:
                        if deps.issubset(completed_nodes):
                            runnable_nodes.append(node_id)
                        elif deps.intersection(failed_nodes):
                            # Dependency failed, cascade cancellation
                            self._cancel_node(graph.nodes[node_id], mission_id, session_id)
                            failed_nodes.add(node_id)
                
                # Submit runnable nodes
                for node_id in runnable_nodes:
                    node = graph.nodes[node_id]
                    self._queue_node(node, mission_id, session_id)
                    
                    # Merge dependency results into payload
                    for dep_id in node.dependencies:
                        dep_node = graph.nodes[dep_id]
                        if dep_node.result:
                            if isinstance(dep_node.result, dict):
                                node.payload.update(dep_node.result)
                            # Always store under capability ID so downstream can look up
                            # by capability name regardless of result type.
                            node.payload[dep_node.capability] = dep_node.result

                    in_progress_nodes.add(node_id)
                    future = executor.submit(self._execute_node_with_retries, node, mission_id, session_id)
                    futures[future] = node_id

                if not futures:
                    # Deadlock or cascading failure finished
                    break

                # Wait for at least one future to complete
                done, not_done = concurrent.futures.wait(
                    futures.keys(), return_when=concurrent.futures.FIRST_COMPLETED
                )

                for future in done:
                    node_id = futures.pop(future)
                    in_progress_nodes.remove(node_id)
                    try:
                        success = future.result()
                        if success:
                            completed_nodes.add(node_id)
                            graph.successful_nodes += 1
                        else:
                            failed_nodes.add(node_id)
                            graph.failed_nodes += 1
                    except Exception as e:
                        logger.error("Engine error in node %s: %s", node_id, e)
                        failed_nodes.add(node_id)
                        graph.failed_nodes += 1
                        graph.nodes[node_id].status = NodeStatus.FAILED
                        
                        EventPublisher.publish(
                            subsystem="mission",
                            event_type=MissionEventType.NODE_FAILED.value,
                            mission_id=mission_id,
                            session_id=session_id,
                            payload={"node_id": node_id, "error": str(e)}
                        )

                # Stop execution if any node fails (fail-fast)
                if failed_nodes:
                    for n in graph.nodes.values():
                        if n.status in (NodeStatus.PENDING, NodeStatus.QUEUED):
                            self._cancel_node(n, mission_id, session_id)
                    break

        graph.graph_duration_ms = (time.time() - start_time) * 1000

        # Conclude Mission
        if failed_nodes:
            EventPublisher.publish(
                subsystem="mission",
                event_type=MissionEventType.MISSION_FAILED.value,
                mission_id=mission_id,
                session_id=session_id,
                severity="error",
            )
            final_result = None
        else:
            EventPublisher.publish(
                subsystem="mission",
                event_type=MissionEventType.MISSION_COMPLETED.value,
                mission_id=mission_id,
                session_id=session_id,
            )
            
            # The final result is the result of the Reflector or Executor (the last node in the graph)
            # Find a node with no dependents
            dependents = set()
            for deps in node_deps.values():
                dependents.update(deps)
                
            leaf_nodes = set(graph.nodes.keys()) - dependents
            final_result = None
            if leaf_nodes:
                # Return the result of the first leaf node found
                leaf_node = graph.nodes[list(leaf_nodes)[0]]
                final_result = leaf_node.result

        # Trigger reflection asynchronously in a background thread to prevent latency regression
        # We pass a copy of the mission dict if possible, or just an empty dict for now, 
        # since real mission object isn't directly inside graph execution manager
        threading.Thread(
            target=reflection_orchestrator.reflect,
            args=(mission_id, session_id or "", {}, graph),
            daemon=True
        ).start()

        return final_result

    def _queue_node(self, node: MissionNode, mission_id: str, session_id: str | None):
        node.status = NodeStatus.QUEUED
        EventPublisher.publish(
            subsystem="mission",
            event_type=MissionEventType.NODE_QUEUED.value,
            mission_id=mission_id,
            session_id=session_id,
            payload={"node_id": node.id, "capability": node.capability}
        )

    def _cancel_node(self, node: MissionNode, mission_id: str, session_id: str | None):
        node.status = NodeStatus.CANCELLED
        EventPublisher.publish(
            subsystem="mission",
            event_type=MissionEventType.NODE_CANCELLED.value,
            mission_id=mission_id,
            session_id=session_id,
            payload={"node_id": node.id}
        )

    def _execute_node_with_retries(self, node: MissionNode, mission_id: str, session_id: str | None) -> bool:
        retries = 0
        max_attempts = node.retry_count + 1

        while retries < max_attempts:
            try:
                start_time = time.time()
                node.status = NodeStatus.RUNNING
                node.started_at = datetime.now()
                
                EventPublisher.publish(
                    subsystem="mission",
                    event_type=MissionEventType.NODE_STARTED.value,
                    mission_id=mission_id,
                    session_id=session_id,
                    payload={"node_id": node.id, "attempt": retries + 1}
                )

                # Execute via CapabilityManager
                # Implementing simple timeout via ThreadPool internally or just assuming CapabilityManager respects timeouts
                result = capability_manager.execute(node)
                
                execution_time = (time.time() - start_time) * 1000
                node.execution_time_ms = execution_time
                node.capability_latency = execution_time
                node.completed_at = datetime.now()
                node.status = NodeStatus.COMPLETED
                node.result = result

                EventPublisher.publish(
                    subsystem="mission",
                    event_type=MissionEventType.NODE_COMPLETED.value,
                    mission_id=mission_id,
                    session_id=session_id,
                    payload={"node_id": node.id, "execution_time_ms": execution_time}
                )
                return True

            except Exception as e:
                logger.exception("Node %s execution error: %s", node.id, e)
                retries += 1
                if retries >= max_attempts:
                    node.status = NodeStatus.FAILED
                    node.completed_at = datetime.now()
                    EventPublisher.publish(
                        subsystem="mission",
                        event_type=MissionEventType.NODE_FAILED.value,
                        mission_id=mission_id,
                        session_id=session_id,
                        severity="error",
                        payload={"node_id": node.id, "error": str(e), "attempt": retries}
                    )
                    return False
        return False


graph_execution_manager = GraphExecutionManager()
