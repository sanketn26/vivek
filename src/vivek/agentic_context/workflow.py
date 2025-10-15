"""
Workflow with Context Manager Pattern
Automatic context tracking as an overarching concern
"""

import logging
import logging.config
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from datetime import datetime

from vivek.agentic_context.core.context_storage import ContextStorage, ContextCategory
from vivek.agentic_context.retrieval.retrieval_strategies import RetrieverFactory


# Configure logging
def _configure_logging(
    log_level: str = "INFO", log_format: Optional[str] = None
) -> logging.Logger:
    """Configure structured logging for the workflow module"""
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"

    logging_config = {
        "version": 1,
        "formatters": {
            "detailed": {"format": log_format, "datefmt": "%Y-%m-%d %H:%M:%S"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "level": log_level,
            }
        },
        "loggers": {
            "vivek.agentic_context.workflow": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            }
        },
    }

    logging.config.dictConfig(logging_config)
    return logging.getLogger("vivek.agentic_context.workflow")


# Initialize logger
logger = _configure_logging()


# Custom Exception Classes
class ContextError(Exception):
    """Base exception for context-related errors"""

    pass


class ValidationError(ContextError):
    """Exception raised for validation errors in context parameters"""

    pass


class StorageError(ContextError):
    """Exception raised for storage operation errors"""

    pass


class RetrievalError(ContextError):
    """Exception raised for retrieval operation errors"""

    pass


class ContextCleanupError(ContextError):
    """Exception raised during context cleanup operations"""

    pass


def _validate_required_params(**kwargs) -> None:
    """Validate that required parameters are provided and not empty"""
    for param_name, value in kwargs.items():
        if value is None:
            raise ValidationError(f"Required parameter '{param_name}' cannot be None")
        if isinstance(value, str) and not value.strip():
            raise ValidationError(f"Required parameter '{param_name}' cannot be empty")
        if isinstance(value, (list, tuple)) and len(value) == 0:
            raise ValidationError(
                f"Required parameter '{param_name}' cannot be empty list"
            )


def _safe_execute_operation(operation_name: str, operation_func, *args, **kwargs):
    """Safely execute an operation with error handling and logging"""
    try:
        logger.debug(f"Starting operation: {operation_name}")
        result = operation_func(*args, **kwargs)
        logger.debug(f"Completed operation: {operation_name}")
        return result
    except Exception as e:
        logger.error(f"Error in operation '{operation_name}': {str(e)}", exc_info=True)
        raise


class TaskContext:
    """
    Task execution context - automatically managed
    Provides context for current task execution
    """

    def __init__(
        self,
        task_id: str,
        description: str,
        tags: List[str],
        storage: ContextStorage,
        retriever,
        config: Dict[str, Any],
    ):
        # Input validation with detailed logging
        logger.info(f"Initializing TaskContext for task_id: {task_id}")

        try:
            # Validate required parameters
            _validate_required_params(
                task_id=task_id,
                description=description,
                tags=tags,
                storage=storage,
                retriever=retriever,
                config=config,
            )

            # Validate task_id format and uniqueness
            if not isinstance(task_id, str) or not task_id.strip():
                raise ValidationError("task_id must be a non-empty string")
            if not task_id.replace("_", "").replace("-", "").isalnum():
                logger.warning(
                    f"Task ID '{task_id}' contains special characters, consider using alphanumeric only"
                )

            # Validate description
            if len(description.strip()) < 10:
                logger.warning(
                    f"Task description is very short ({len(description.strip())} chars): {description}"
                )

            # Validate tags
            if not isinstance(tags, list):
                raise ValidationError("tags must be a list")
            if len(tags) == 0:
                logger.warning("No tags provided for task")
            if len(tags) > 10:
                logger.warning(
                    f"Large number of tags ({len(tags)}) for task, consider reducing"
                )

            # Validate storage and retriever
            if not hasattr(storage, "build_hierarchical_context"):
                raise ValidationError("storage must be a valid ContextStorage instance")
            if not hasattr(retriever, "retrieve"):
                raise ValidationError("retriever must be a valid retriever instance")

            # Validate config
            if not isinstance(config, dict):
                raise ValidationError("config must be a dictionary")

        except ValidationError as e:
            logger.error(f"TaskContext validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during TaskContext validation: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"TaskContext initialization failed: {str(e)}")

        # Initialize attributes after successful validation
        self.task_id = task_id
        self.description = description
        self.tags = tags
        self._storage = storage
        self._retriever = retriever
        self._config = config
        self._result = None
        self._start_time = datetime.now()

        logger.debug(f"TaskContext initialized successfully for task: {task_id}")

    @property
    def context(self) -> Dict[str, Any]:
        """Get current hierarchical context"""
        return self._storage.build_hierarchical_context()

    def build_prompt(self, include_history: bool = True) -> str:
        """
        Build complete prompt with focused context
        This is what you pass to your LLM
        """
        logger.debug(f"Building prompt for task: {self.task_id}")

        try:
            # Get hierarchical context instead of individual components
            context_data = self._storage.build_hierarchical_context()
            parts = []

            # Session layer
            if context_data.get("session"):
                session = context_data["session"]
                if session.get("original_ask"):
                    parts.append("=== SESSION CONTEXT ===")
                    parts.append(f"Original Request: {session['original_ask']}")
                    if session.get("high_level_plan"):
                        parts.append(f"High-Level Plan: {session['high_level_plan']}")
                    parts.append("")

            # Activity layer
            if context_data.get("activity"):
                activity = context_data["activity"]
                if activity.get("description"):
                    parts.append("=== ACTIVITY CONTEXT ===")
                    parts.append(f"Current Activity: {activity['description']}")
                    if activity.get("mode"):
                        parts.append(f"Mode: {activity['mode']}")
                    if activity.get("component"):
                        parts.append(f"Component: {activity['component']}")
                    if activity.get("planner_analysis"):
                        parts.append(
                            f"Planner Analysis:\n{activity['planner_analysis']}"
                        )
                    parts.append("")

            # Task layer
            if context_data.get("task"):
                task = context_data["task"]
                if task.get("description"):
                    parts.append("=== TASK CONTEXT ===")
                    parts.append(f"Current Task: {task['description']}")
                    if task.get("previous_result"):
                        parts.append(f"Previous Task Result: {task['previous_result']}")
                    parts.append("")

            # Relevant history
            if include_history:
                try:
                    logger.debug(f"Retrieving relevant context for tags: {self.tags}")
                    relevant = self._retriever.retrieve(
                        self.tags,
                        self.description,
                        self._config.get("retrieval", {}).get("max_results", 5),
                    )

                    if relevant:
                        parts.append("=== RELEVANT CONTEXT FROM HISTORY ===")
                        for i, item in enumerate(relevant, 1):
                            try:
                                score = item.get("final_score", item.get("score", 0))
                                parts.append(
                                    f"\n[{i}] {item['category'].upper()} (relevance: {score:.2f})"
                                )
                                parts.append(item["item"]["content"])
                                if item.get("matched_tags"):
                                    parts.append(
                                        f"   Matched tags: {', '.join(item['matched_tags'])}"
                                    )
                            except (KeyError, TypeError) as e:
                                logger.warning(
                                    f"Error processing retrieved item {i}: {str(e)}"
                                )
                                continue
                        parts.append("")
                    else:
                        logger.debug("No relevant context found")

                except Exception as e:
                    logger.error(
                        f"Error retrieving relevant context: {str(e)}", exc_info=True
                    )
                    # Continue without historical context rather than failing completely
                    parts.append("=== RELEVANT CONTEXT FROM HISTORY ===")
                    parts.append(
                        "Unable to retrieve historical context due to an error."
                    )
                    parts.append("")

            parts.append("=== INSTRUCTIONS ===")
            parts.append(
                "Focus on the current task. Use relevant context to inform your implementation."
            )

            prompt = "\n".join(parts)
            logger.debug(
                f"Prompt built successfully for task: {self.task_id}, length: {len(prompt)}"
            )
            return prompt

        except Exception as e:
            logger.error(
                f"Error building prompt for task {self.task_id}: {str(e)}",
                exc_info=True,
            )
            raise RetrievalError(f"Failed to build prompt: {str(e)}")

    def record_action(self, content: str, **metadata):
        """Record an action taken during this task"""
        logger.debug(f"Recording action for task {self.task_id}")

        try:
            _validate_required_params(content=content)

            if not isinstance(content, str) or not content.strip():
                raise ValidationError("Action content must be a non-empty string")

            # Safely execute storage operation
            return _safe_execute_operation(
                f"record_action_{self.task_id}",
                self._storage.add_context,
                ContextCategory.ACTIONS,
                content,
                self.tags,
                **metadata,
            )

        except ValidationError as e:
            logger.error(
                f"Validation error recording action for task {self.task_id}: {str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Error recording action for task {self.task_id}: {str(e)}",
                exc_info=True,
            )
            raise StorageError(f"Failed to record action: {str(e)}")

    def record_decision(self, content: str, **metadata):
        """Record a decision made during this task"""
        logger.debug(f"Recording decision for task {self.task_id}")

        try:
            _validate_required_params(content=content)

            if not isinstance(content, str) or not content.strip():
                raise ValidationError("Decision content must be a non-empty string")

            return _safe_execute_operation(
                f"record_decision_{self.task_id}",
                self._storage.add_context,
                ContextCategory.DECISIONS,
                content,
                self.tags,
                **metadata,
            )

        except ValidationError as e:
            logger.error(
                f"Validation error recording decision for task {self.task_id}: {str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Error recording decision for task {self.task_id}: {str(e)}",
                exc_info=True,
            )
            raise StorageError(f"Failed to record decision: {str(e)}")

    def record_learning(self, content: str, **metadata):
        """Record a lesson learned during this task"""
        logger.debug(f"Recording learning for task {self.task_id}")

        try:
            _validate_required_params(content=content)

            if not isinstance(content, str) or not content.strip():
                raise ValidationError("Learning content must be a non-empty string")

            return _safe_execute_operation(
                f"record_learning_{self.task_id}",
                self._storage.add_context,
                ContextCategory.LEARNINGS,
                content,
                self.tags,
                **metadata,
            )

        except ValidationError as e:
            logger.error(
                f"Validation error recording learning for task {self.task_id}: {str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Error recording learning for task {self.task_id}: {str(e)}",
                exc_info=True,
            )
            raise StorageError(f"Failed to record learning: {str(e)}")

    def set_result(self, result: str):
        """Set task result (called automatically on exit)"""
        logger.debug(f"Setting result for task {self.task_id}")

        try:
            if result is not None and not isinstance(result, str):
                logger.warning(f"Task result is not a string type: {type(result)}")

            self._result = str(result) if result is not None else None
            logger.debug(f"Result set successfully for task {self.task_id}")

        except Exception as e:
            logger.error(
                f"Error setting result for task {self.task_id}: {str(e)}", exc_info=True
            )
            # Don't raise exception here as this might be called during cleanup

    def _finalize(self):
        """Internal: finalize task on context exit"""
        logger.debug(f"Finalizing task {self.task_id}")

        try:
            if self._result:
                # Safely complete the task
                try:
                    _safe_execute_operation(
                        f"complete_task_{self.task_id}",
                        self._storage.complete_task,
                        self.task_id,
                        self._result,
                    )
                except Exception as e:
                    logger.error(
                        f"Error completing task {self.task_id}: {str(e)}", exc_info=True
                    )

                # Safely add result to context
                try:
                    duration = (datetime.now() - self._start_time).total_seconds()
                    _safe_execute_operation(
                        f"add_result_context_{self.task_id}",
                        self._storage.add_context,
                        ContextCategory.RESULTS,
                        self._result,
                        self.tags,
                        duration_seconds=duration,
                    )
                except Exception as e:
                    logger.error(
                        f"Error adding result context for task {self.task_id}: {str(e)}",
                        exc_info=True,
                    )

            logger.info(f"Task {self.task_id} finalized successfully")

        except Exception as e:
            logger.error(
                f"Unexpected error during task finalization for {self.task_id}: {str(e)}",
                exc_info=True,
            )
            # Don't raise exception during finalization to avoid masking original errors


class ActivityContext:
    """
    Activity execution context - automatically managed
    Provides interface for working with activities
    """

    def __init__(
        self,
        activity_id: str,
        description: str,
        tags: List[str],
        mode: str,
        component: str,
        planner_analysis: str,
        storage: ContextStorage,
        retriever,
        config: Dict[str, Any],
    ):
        logger.info(f"Initializing ActivityContext for activity_id: {activity_id}")

        try:
            # Validate required parameters
            _validate_required_params(
                activity_id=activity_id,
                description=description,
                tags=tags,
                mode=mode,
                component=component,
                planner_analysis=planner_analysis,
                storage=storage,
                retriever=retriever,
                config=config,
            )

            # Validate activity_id format
            if not isinstance(activity_id, str) or not activity_id.strip():
                raise ValidationError("activity_id must be a non-empty string")

            # Validate description
            if len(description.strip()) < 10:
                logger.warning(
                    f"Activity description is very short ({len(description.strip())} chars): {description}"
                )

            # Validate mode
            valid_modes = ["coder", "architect", "sdet", "peer", "planner"]
            if mode not in valid_modes:
                logger.warning(f"Mode '{mode}' not in expected modes: {valid_modes}")

            # Validate component
            if not component or not isinstance(component, str):
                raise ValidationError("component must be a non-empty string")

            # Validate planner_analysis
            if len(planner_analysis.strip()) < 20:
                logger.warning(
                    f"Planner analysis is very short ({len(planner_analysis.strip())} chars)"
                )

            # Validate tags
            if not isinstance(tags, list):
                raise ValidationError("tags must be a list")
            if len(tags) == 0:
                logger.warning("No tags provided for activity")

        except ValidationError as e:
            logger.error(f"ActivityContext validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during ActivityContext validation: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"ActivityContext initialization failed: {str(e)}")

        # Initialize attributes after successful validation
        self.activity_id = activity_id
        self.description = description
        self.tags = tags
        self.mode = mode
        self.component = component
        self.planner_analysis = planner_analysis
        self._storage = storage
        self._retriever = retriever
        self._config = config
        self._task_counter = 0

        logger.debug(
            f"ActivityContext initialized successfully for activity: {activity_id}"
        )

    @property
    def context(self) -> Dict[str, Any]:
        """Get current activity context"""
        return self._storage.build_hierarchical_context()

    @contextmanager
    def task(self, description: str, tags: Optional[List[str]] = None, **metadata):
        """
        Create and manage a task within this activity

        Usage:
            with activity.task("Create file", tags=["file", "create"]) as task:
                prompt = task.build_prompt()
                result = llm.generate(prompt)
                task.set_result(result)
        """
        logger.info(f"Creating task in activity {self.activity_id}")

        # Validate input parameters
        try:
            _validate_required_params(description=description)

            if not isinstance(description, str) or not description.strip():
                raise ValidationError("Task description must be a non-empty string")

            if tags is not None and not isinstance(tags, list):
                raise ValidationError("tags must be a list or None")

        except ValidationError as e:
            logger.error(
                f"Task creation validation failed in activity {self.activity_id}: {str(e)}"
            )
            raise

        task_context = None
        task_id = None

        try:
            # Generate task ID and prepare tags
            self._task_counter += 1
            task_id = f"task_{self.activity_id}_{self._task_counter:03d}"
            logger.debug(f"Generated task_id: {task_id}")

            # Inherit activity tags if not provided
            if tags is None:
                task_tags = self.tags[:2]  # Inherit first 2 activity tags
                logger.debug(f"Using inherited tags for task: {task_tags}")
            else:
                # Combine with some activity tags
                task_tags = list(set(tags + self.tags[:2]))
                logger.debug(f"Using combined tags for task: {task_tags}")

            # Create task in storage with error handling
            try:
                _safe_execute_operation(
                    f"create_task_{task_id}",
                    self._storage.create_task,
                    task_id,
                    description,
                    task_tags,
                    **metadata,
                )
                logger.debug(f"Task created in storage: {task_id}")

            except Exception as e:
                logger.error(
                    f"Failed to create task {task_id} in storage: {str(e)}",
                    exc_info=True,
                )
                raise StorageError(f"Failed to create task in storage: {str(e)}")

            # Create context object
            try:
                task_context = TaskContext(
                    task_id,
                    description,
                    task_tags,
                    self._storage,
                    self._retriever,
                    self._config,
                )
                logger.debug(f"TaskContext object created: {task_id}")

            except Exception as e:
                logger.error(
                    f"Failed to create TaskContext object for {task_id}: {str(e)}",
                    exc_info=True,
                )
                # Attempt to clean up the storage entry
                try:
                    # Note: We don't have a direct way to remove a task, so we just log
                    logger.warning(
                        f"Task {task_id} was created in storage but TaskContext creation failed"
                    )
                except Exception as cleanup_error:
                    logger.error(
                        f"Error during cleanup after TaskContext failure: {str(cleanup_error)}"
                    )
                raise ValidationError(f"Failed to create task context: {str(e)}")

            # Yield the task context
            logger.info(f"Yielding task context for: {task_id}")
            yield task_context

        except Exception as e:
            logger.error(
                f"Error in task context manager for {task_id or 'unknown'}: {str(e)}",
                exc_info=True,
            )
            raise

        finally:
            # Automatically finalize on exit with comprehensive error handling
            if task_context is not None:
                try:
                    logger.debug(f"Finalizing task context: {task_id}")
                    task_context._finalize()
                except Exception as e:
                    logger.error(
                        f"Error during task finalization for {task_id}: {str(e)}",
                        exc_info=True,
                    )
                    # Don't raise exception during finalization to avoid masking original errors

            logger.info(
                f"Task context manager completed for activity {self.activity_id}"
            )


class SessionContext:
    """
    Session execution context - automatically managed
    Top-level workflow context
    """

    def __init__(
        self,
        session_id: str,
        original_ask: str,
        high_level_plan: str,
        storage: ContextStorage,
        retriever,
        config: Dict[str, Any],
    ):
        logger.info(f"Initializing SessionContext for session_id: {session_id}")

        try:
            # Validate required parameters
            _validate_required_params(
                session_id=session_id,
                original_ask=original_ask,
                high_level_plan=high_level_plan,
                storage=storage,
                retriever=retriever,
                config=config,
            )

            # Validate session_id format
            if not isinstance(session_id, str) or not session_id.strip():
                raise ValidationError("session_id must be a non-empty string")

            # Validate original_ask
            if len(original_ask.strip()) < 10:
                logger.warning(
                    f"Original ask is very short ({len(original_ask.strip())} chars): {original_ask}"
                )

            # Validate high_level_plan
            if high_level_plan and len(high_level_plan.strip()) < 20:
                logger.warning(
                    f"High level plan is very short ({len(high_level_plan.strip())} chars)"
                )

            # Validate storage and retriever
            if not hasattr(storage, "build_hierarchical_context"):
                raise ValidationError("storage must be a valid ContextStorage instance")
            if not hasattr(retriever, "retrieve"):
                raise ValidationError("retriever must be a valid retriever instance")

            # Validate config
            if not isinstance(config, dict):
                raise ValidationError("config must be a dictionary")

        except ValidationError as e:
            logger.error(f"SessionContext validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during SessionContext validation: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"SessionContext initialization failed: {str(e)}")

        # Initialize attributes after successful validation
        self.session_id = session_id
        self.original_ask = original_ask
        self.high_level_plan = high_level_plan
        self._storage = storage
        self._retriever = retriever
        self._config = config
        self._activity_counter = 0

        logger.debug(
            f"SessionContext initialized successfully for session: {session_id}"
        )

    @property
    def context(self) -> Dict[str, Any]:
        """Get current session context"""
        return self._storage.build_hierarchical_context()

    @contextmanager
    def activity(
        self,
        description: str,
        tags: List[str],
        mode: str,
        component: str,
        planner_analysis: str,
        **metadata,
    ):
        """
        Create and manage an activity within this session

        Usage:
            with session.activity("Build consumer",
                                 tags=["kafka", "consumer"],
                                 mode="coder",
                                 component="consumer",
                                 planner_analysis="...") as activity:

                with activity.task("Create file") as task:
                    # Work here
                    pass
        """
        logger.info(f"Creating activity in session {self.session_id}")

        # Validate input parameters
        try:
            _validate_required_params(
                description=description,
                tags=tags,
                mode=mode,
                component=component,
                planner_analysis=planner_analysis,
            )

            if not isinstance(description, str) or not description.strip():
                raise ValidationError("Activity description must be a non-empty string")
            if not isinstance(tags, list):
                raise ValidationError("tags must be a list")
            if not mode or not isinstance(mode, str):
                raise ValidationError("mode must be a non-empty string")
            if not component or not isinstance(component, str):
                raise ValidationError("component must be a non-empty string")
            if not isinstance(planner_analysis, str) or not planner_analysis.strip():
                raise ValidationError("planner_analysis must be a non-empty string")

            # Validate mode
            valid_modes = ["coder", "architect", "sdet", "peer", "planner"]
            if mode not in valid_modes:
                logger.warning(f"Mode '{mode}' not in expected modes: {valid_modes}")

        except ValidationError as e:
            logger.error(
                f"Activity creation validation failed in session {self.session_id}: {str(e)}"
            )
            raise

        activity_context = None
        activity_id = None

        try:
            # Generate activity ID
            self._activity_counter += 1
            activity_id = f"act_{self._activity_counter:03d}"
            logger.debug(f"Generated activity_id: {activity_id}")

            # Create activity in storage with error handling
            try:
                _safe_execute_operation(
                    f"create_activity_{activity_id}",
                    self._storage.create_activity,
                    activity_id,
                    description,
                    tags,
                    mode,
                    component,
                    planner_analysis,
                    **metadata,
                )
                logger.debug(f"Activity created in storage: {activity_id}")

            except Exception as e:
                logger.error(
                    f"Failed to create activity {activity_id} in storage: {str(e)}",
                    exc_info=True,
                )
                raise StorageError(f"Failed to create activity in storage: {str(e)}")

            # Record planner's decision with error handling
            try:
                _safe_execute_operation(
                    f"record_planner_decision_{activity_id}",
                    self._storage.add_context,
                    ContextCategory.DECISIONS,
                    planner_analysis,
                    tags,
                    activity_id=activity_id,
                )
                logger.debug(f"Planner decision recorded for activity: {activity_id}")

            except Exception as e:
                logger.error(
                    f"Failed to record planner decision for activity {activity_id}: {str(e)}",
                    exc_info=True,
                )
                # Continue despite this error as the activity was created successfully

            # Create context object
            try:
                activity_context = ActivityContext(
                    activity_id,
                    description,
                    tags,
                    mode,
                    component,
                    planner_analysis,
                    self._storage,
                    self._retriever,
                    self._config,
                )
                logger.debug(f"ActivityContext object created: {activity_id}")

            except Exception as e:
                logger.error(
                    f"Failed to create ActivityContext object for {activity_id}: {str(e)}",
                    exc_info=True,
                )
                # Attempt to clean up the storage entry
                try:
                    logger.warning(
                        f"Activity {activity_id} was created in storage but ActivityContext creation failed"
                    )
                except Exception as cleanup_error:
                    logger.error(
                        f"Error during cleanup after ActivityContext failure: {str(cleanup_error)}"
                    )
                raise ValidationError(f"Failed to create activity context: {str(e)}")

            # Yield the activity context
            logger.info(f"Yielding activity context for: {activity_id}")
            yield activity_context

        except Exception as e:
            logger.error(
                f"Error in activity context manager for {activity_id or 'unknown'}: {str(e)}",
                exc_info=True,
            )
            raise

        finally:
            # Automatically finalize on exit with comprehensive error handling
            if activity_context is not None:
                try:
                    logger.debug(
                        f"Activity context manager completed for: {activity_id}"
                    )
                    # Activity auto-completes - no explicit finalization needed
                except Exception as e:
                    logger.error(
                        f"Error during activity cleanup for {activity_id}: {str(e)}",
                        exc_info=True,
                    )

            logger.info(
                f"Activity context manager completed for session {self.session_id}"
            )


class ContextWorkflow:
    """
    Main workflow manager with automatic context tracking

    Usage:
        workflow = ContextWorkflow(config)

        with workflow.session("Build system") as session:
            with session.activity("Build consumer", ...) as activity:
                with activity.task("Create file") as task:
                    prompt = task.build_prompt()
                    result = llm.generate(prompt)
                    task.set_result(result)
    """

    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing ContextWorkflow")

        try:
            # Validate required parameters
            _validate_required_params(config=config)

            if not isinstance(config, dict):
                raise ValidationError("config must be a dictionary")

            # Validate config structure
            if not config:
                logger.warning("Empty config provided, using defaults")

            # Validate storage and retriever creation
            try:
                self.storage = ContextStorage()
                logger.debug("ContextStorage initialized successfully")
            except Exception as e:
                logger.error(
                    f"Failed to initialize ContextStorage: {str(e)}", exc_info=True
                )
                raise StorageError(f"Failed to initialize storage: {str(e)}")

            try:
                self.retriever = RetrieverFactory.create_retriever(self.storage, config)
                logger.debug("Retriever initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize retriever: {str(e)}", exc_info=True)
                raise RetrievalError(f"Failed to initialize retriever: {str(e)}")

            self.config = config
            self._session_counter = 0

            logger.info("ContextWorkflow initialized successfully")

        except (ValidationError, StorageError, RetrievalError):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during ContextWorkflow initialization: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"ContextWorkflow initialization failed: {str(e)}")

    @contextmanager
    def session(
        self, original_ask: str, high_level_plan: Optional[str] = None, **metadata
    ):
        """
        Create and manage a workflow session

        Args:
            original_ask: User's original request
            high_level_plan: High-level plan (optional)

        Usage:
            with workflow.session("Build auth system") as session:
                # Work here
                pass
        """
        logger.info("Creating new workflow session")

        # Validate input parameters
        try:
            _validate_required_params(original_ask=original_ask)

            if not isinstance(original_ask, str) or not original_ask.strip():
                raise ValidationError("original_ask must be a non-empty string")

            if high_level_plan is not None and not isinstance(high_level_plan, str):
                raise ValidationError("high_level_plan must be a string or None")

        except ValidationError as e:
            logger.error(f"Session creation validation failed: {str(e)}")
            raise

        session_context = None
        session_id = None

        try:
            # Generate session ID and prepare high_level_plan
            self._session_counter += 1
            session_id = f"session_{self._session_counter:03d}"
            logger.debug(f"Generated session_id: {session_id}")

            if high_level_plan is None:
                high_level_plan = "To be determined by planner"
                logger.debug("Using default high_level_plan")

            # Create session in storage with error handling
            try:
                _safe_execute_operation(
                    f"create_session_{session_id}",
                    self.storage.create_session,
                    session_id,
                    original_ask,
                    high_level_plan,
                    **metadata,
                )
                logger.debug(f"Session created in storage: {session_id}")

            except Exception as e:
                logger.error(
                    f"Failed to create session {session_id} in storage: {str(e)}",
                    exc_info=True,
                )
                raise StorageError(f"Failed to create session in storage: {str(e)}")

            # Create context object
            try:
                session_context = SessionContext(
                    session_id,
                    original_ask,
                    high_level_plan,
                    self.storage,
                    self.retriever,
                    self.config,
                )
                logger.debug(f"SessionContext object created: {session_id}")

            except Exception as e:
                logger.error(
                    f"Failed to create SessionContext object for {session_id}: {str(e)}",
                    exc_info=True,
                )
                # Attempt to clean up the storage entry
                try:
                    logger.warning(
                        f"Session {session_id} was created in storage but SessionContext creation failed"
                    )
                except Exception as cleanup_error:
                    logger.error(
                        f"Error during cleanup after SessionContext failure: {str(cleanup_error)}"
                    )
                raise ValidationError(f"Failed to create session context: {str(e)}")

            # Yield the session context
            logger.info(f"Yielding session context for: {session_id}")
            yield session_context

        except Exception as e:
            logger.error(
                f"Error in session context manager for {session_id or 'unknown'}: {str(e)}",
                exc_info=True,
            )
            raise

        finally:
            # Session auto-completes - no explicit finalization needed
            logger.info(
                f"Session context manager completed for session {session_id or 'unknown'}"
            )

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        logger.debug("Getting workflow statistics")

        try:
            stats = self.storage.get_statistics()
            logger.debug(f"Retrieved statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting workflow statistics: {str(e)}", exc_info=True)
            raise StorageError(f"Failed to get statistics: {str(e)}")

    def switch_strategy(self, new_strategy: str):
        """Switch retrieval strategy at runtime"""
        logger.info(f"Switching retrieval strategy to: {new_strategy}")

        try:
            _validate_required_params(new_strategy=new_strategy)

            if not isinstance(new_strategy, str) or not new_strategy.strip():
                raise ValidationError("new_strategy must be a non-empty string")

            # Validate that the strategy exists
            try:
                # Test if the strategy can be created
                test_retriever = RetrieverFactory.create_retriever(
                    self.storage, {"retrieval": {"strategy": new_strategy}}
                )
                logger.debug(f"Strategy '{new_strategy}' validated successfully")

            except Exception as e:
                logger.error(
                    f"Invalid retrieval strategy '{new_strategy}': {str(e)}",
                    exc_info=True,
                )
                raise ValidationError(f"Invalid retrieval strategy: {str(e)}")

            # Update config and recreate retriever
            self.config["retrieval"]["strategy"] = new_strategy

            try:
                self.retriever = RetrieverFactory.create_retriever(
                    self.storage, self.config
                )
                logger.info(
                    f"Successfully switched to retrieval strategy: {new_strategy}"
                )
                print(f"✓ Switched to retrieval strategy: {new_strategy}")

            except Exception as e:
                logger.error(
                    f"Failed to create retriever with strategy '{new_strategy}': {str(e)}",
                    exc_info=True,
                )
                raise RetrievalError(f"Failed to switch strategy: {str(e)}")

        except (ValidationError, RetrievalError):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error switching strategy to '{new_strategy}': {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"Failed to switch strategy: {str(e)}")

    def export(self) -> Dict[str, Any]:
        """Export all context for persistence"""
        logger.info("Exporting workflow context")

        try:
            # Safely export sessions
            sessions_data = {}
            try:
                for sid, s in self.storage.sessions.items():
                    sessions_data[sid] = {
                        "session_id": s.session_id,
                        "original_ask": s.original_ask,
                        "high_level_plan": s.high_level_plan,
                        "created_at": s.created_at.isoformat(),
                    }
                logger.debug(f"Exported {len(sessions_data)} sessions")

            except Exception as e:
                logger.error(f"Error exporting sessions: {str(e)}", exc_info=True)
                # Continue with empty sessions data
                sessions_data = {}

            # Safely export context database
            context_data = {}
            try:
                for cat, items in self.storage.context_db.items():
                    context_data[cat.value] = [
                        {
                            "content": item.content,
                            "tags": item.tags,
                            "timestamp": item.timestamp.isoformat(),
                        }
                        for item in items
                    ]
                logger.debug(f"Exported context from {len(context_data)} categories")

            except Exception as e:
                logger.error(
                    f"Error exporting context database: {str(e)}", exc_info=True
                )
                # Continue with empty context data
                context_data = {}

            export_data = {"sessions": sessions_data, "context_db": context_data}

            logger.info(
                f"Successfully exported workflow context ({len(sessions_data)} sessions, {len(context_data)} categories)"
            )
            return export_data

        except Exception as e:
            logger.error(f"Error exporting workflow context: {str(e)}", exc_info=True)
            raise StorageError(f"Failed to export context: {str(e)}")
