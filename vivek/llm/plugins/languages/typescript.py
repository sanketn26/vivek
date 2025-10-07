"""TypeScript Language Plugin implementation."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field

from vivek.llm.plugins.base.language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


@dataclass
class TypeScriptConventions(LanguageConventions):
    """TypeScript-specific conventions and best practices."""

    def __post_init__(self):
        if not self.language:
            self.language = "typescript"
        if not self.extensions:
            self.extensions = [".ts", ".tsx", ".js", ".jsx"]

        # Naming conventions
        if not self.naming_conventions:
            self.naming_conventions = {
                "camelCase": "functions, variables, methods, object properties",
                "PascalCase": "classes, interfaces, types, enums",
                "SCREAMING_SNAKE_CASE": "constants",
                "kebab-case": "file names (for some frameworks)"
            }

        # Import and dependency management
        if not self.import_style:
            self.import_style = "Use ES6 imports with explicit imports from modules"
        if not self.dependency_management:
            self.dependency_management = "Use npm or yarn with package.json and semantic versioning"

        # Code style and formatting
        if not self.code_style:
            self.code_style = "Follow TypeScript style guidelines with strict mode enabled"
        if not self.formatting_rules:
            self.formatting_rules = {
                "quotes": "single quotes preferred",
                "semicolons": "ASI (Automatic Semicolon Insertion)",
                "line_endings": "Unix (LF)",
                "trailing_comma": "ES5 style for compatibility"
            }

        # Error handling
        if not self.error_handling:
            self.error_handling = "Use typed errors and proper async/await error handling"
        if not self.exception_types:
            self.exception_types = [
                "Error", "TypeError", "ReferenceError", "SyntaxError",
                "RangeError", "URIError", "EvalError", "AggregateError"
            ]

        # Documentation
        if not self.documentation_style:
            self.documentation_style = "JSDoc comments for public APIs with @param, @returns, @throws"
        if not self.comment_conventions:
            self.comment_conventions = {
                "file": "/* */ block comments at top of file",
                "function": "/** */ JSDoc comments for public functions",
                "inline": "// comments for complex logic",
                "TODO": "// TODO: comments for future improvements"
            }

        # Type system
        if not self.type_system:
            self.type_system = "Static typing with structural type system and type inference"
        if not self.type_annotations:
            self.type_annotations = "Use explicit types, interfaces, generics, and union types"

        # Testing
        if not self.testing_frameworks:
            self.testing_frameworks = ["Jest", "Mocha", "Jasmine", "Cypress"]
        if not self.testing_patterns:
            self.testing_patterns = {
                "naming": "*.test.ts, *.spec.ts files with describe/it blocks",
                "assertions": "Use assertion libraries like Jest or Chai",
                "mocks": "Use Jest mocking or Sinon for test doubles",
                "coverage": "Aim for >80% test coverage with Istanbul"
            }

        # Project structure
        if not self.project_structure:
            self.project_structure = {
                "src": "Main source code directory",
                "tests": "Test files and fixtures",
                "dist": "Compiled JavaScript output",
                "node_modules": "NPM dependencies",
                "package.json": "Project configuration and dependencies"
            }
        if not self.entry_points:
            self.entry_points = ["index.ts", "main.ts", "app.ts"]

        # Idioms and best practices
        if not self.idioms:
            self.idioms = [
                "Use async/await for asynchronous operations",
                "Prefer const over let, avoid var",
                "Use destructuring for object and array access",
                "Leverage TypeScript's type inference where possible",
                "Use optional chaining and nullish coalescing operators"
            ]
        if not self.best_practices:
            self.best_practices = [
                "Enable strict mode in TypeScript configuration",
                "Use interfaces for object shapes and API contracts",
                "Handle null and undefined values explicitly",
                "Write comprehensive JSDoc comments for public APIs",
                "Use generic types for reusable components",
                "Prefer composition over inheritance",
                "Implement proper error boundaries in React applications",
                "Use ESLint and Prettier for code quality"
            ]


class TypeScriptLanguagePlugin(LanguagePlugin):
    """TypeScript language plugin with comprehensive TypeScript-specific behavior."""

    def __init__(self):
        super().__init__("typescript")

    @property
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports."""
        return ["typescript", "ts", "tsx", "javascript", "js", "jsx"]

    @property
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports."""
        return [Mode.CODER.value, Mode.ARCHITECT.value, Mode.PEER.value, Mode.SDET.value]

    @property
    def name(self) -> str:
        """Human-readable name for this plugin."""
        return "TypeScript Language Assistant"

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0.0"

    def get_conventions(self) -> TypeScriptConventions:
        """Get TypeScript-specific conventions for this plugin."""
        if not self._conventions:
            self._conventions = TypeScriptConventions(language=self.language)
        return self._conventions

    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a TypeScript and mode-specific executor instance."""
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor
        from vivek.llm.peer_executor import PeerExecutor
        from vivek.llm.sdet_executor import SDETExecutor

        mode_lower = mode.lower()

        class TypeScriptLanguageExecutor:
            """TypeScript-aware executor wrapper with language-specific prompts."""

            def __init__(self, base_executor, language_plugin):
                self.base_executor = base_executor
                self.language_plugin = language_plugin
                self.language = "typescript"
                self.mode = mode_lower

                # Set language-specific prompt
                if hasattr(base_executor, 'mode_prompt'):
                    base_executor.mode_prompt = f"TypeScript {mode_lower.title()} Mode: {self._get_mode_specific_prompt(mode_lower)}"

            def _get_mode_specific_prompt(self, mode: str) -> str:
                """Get TypeScript-specific prompt for the mode."""
                mode_instructions = self.language_plugin.get_language_specific_instructions(mode)
                return f"Follow TypeScript best practices. {mode_instructions}"

            def __getattr__(self, name):
                """Delegate all other attributes to the base executor."""
                return getattr(self.base_executor, name)

        if mode_lower == Mode.CODER.value:
            base_executor = CoderExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.ARCHITECT.value:
            base_executor = ArchitectExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.PEER.value:
            base_executor = PeerExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.SDET.value:
            base_executor = SDETExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        else:
            raise ValueError(f"Unsupported mode for TypeScript plugin: {mode}")

    def get_language_specific_instructions(self, mode: str) -> str:
        """Get TypeScript-specific instructions for the given mode."""
        base_instructions = f"""**TypeScript Language Requirements for {mode.title()} Mode:**

Follow TypeScript conventions:
- Use strict type checking with no implicit any types
- Define interfaces for object shapes and API responses
- Include JSDoc comments for public APIs
- Handle async/await patterns correctly
- Use ES6+ features (const/let, arrow functions, destructuring)

"""

        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return base_instructions + """
**Coding Requirements:**
- Use explicit type annotations for function parameters and return values
- Implement proper error handling with typed errors
- Use generic types for reusable components and utilities
- Follow the single responsibility principle
- Write unit tests for all functions"""
        elif mode_lower == Mode.ARCHITECT.value:
            return base_instructions + """
**Architecture Requirements:**
- Design type-safe APIs and data contracts
- Consider module boundaries and dependency injection
- Plan for scalability with proper abstractions
- Document API interfaces and integration patterns
- Consider deployment and build strategies"""
        elif mode_lower == Mode.PEER.value:
            return base_instructions + """
**Code Review Requirements:**
- Check for type safety and proper TypeScript usage
- Verify proper error handling and edge cases
- Ensure comprehensive JSDoc coverage
- Review for security vulnerabilities (input validation, XSS prevention)
- Check for appropriate testing coverage"""
        elif mode_lower == Mode.SDET.value:
            return base_instructions + """
**Testing Requirements:**
- Write comprehensive unit tests using Jest or similar framework
- Include integration and end-to-end tests
- Test edge cases and error conditions with proper mocking
- Use type-safe test utilities and fixtures
- Aim for >80% test coverage"""
        else:
            return base_instructions

    def get_code_example(self, mode: str, context: Optional[str] = None) -> str:
        """Get a TypeScript-specific code example for the given mode."""
        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return self._get_typescript_coder_example()
        elif mode_lower == Mode.ARCHITECT.value:
            return self._get_typescript_architect_example()
        elif mode_lower == Mode.PEER.value:
            return self._get_typescript_peer_example()
        elif mode_lower == Mode.SDET.value:
            return self._get_typescript_sdet_example()
        else:
            return self._get_typescript_coder_example()

    def _get_typescript_coder_example(self) -> str:
        """Get TypeScript coder example."""
        return """// File: data-processor.ts
// [NEW] or [MODIFIED]

/**
 * Configuration options for data processing
 */
interface ProcessingOptions {
  /** Optional output path for processed data */
  outputPath?: string;
  /** Whether to validate input data strictly */
  validateData?: boolean;
  /** Maximum number of items to process */
  maxItems?: number;
}

/**
 * Result of data processing operation
 */
interface ProcessingResult<T = any> {
  /** Whether the operation was successful */
  success: boolean;
  /** Number of items processed */
  count: number;
  /** Processed data items */
  data: T[];
  /** Any errors encountered during processing */
  errors: string[];
  /** Timestamp of completion */
  timestamp: Date;
}

/**
 * Custom error class for processing failures
 */
class DataProcessingError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly originalError?: Error
  ) {
    super(message);
    this.name = 'DataProcessingError';
  }
}

/**
 * Service class for processing JSON data with TypeScript best practices
 */
class DataProcessor {
  private readonly outputDir: string;

  constructor(outputDir: string = './output') {
    this.outputDir = outputDir;
  }

  /**
   * Process JSON data with comprehensive error handling and type safety
   * @param jsonData - JSON string to process
   * @param options - Processing configuration options
   * @returns Promise resolving to processing result
   * @throws {DataProcessingError} If processing fails
   */
  async processJsonData<T = any>(
    jsonData: string,
    options: ProcessingOptions = {}
  ): Promise<ProcessingResult<T>> {
    const result: ProcessingResult<T> = {
      success: false,
      count: 0,
      data: [],
      errors: [],
      timestamp: new Date()
    };

    try {
      // Parse JSON data with validation
      const rawData: unknown = JSON.parse(jsonData);

      // Validate and normalize input data
      const dataArray = this.validateAndNormalizeInput(rawData, options);
      if (!dataArray) {
        throw new DataProcessingError(
          'Input data must be an array when validation is enabled',
          'INVALID_INPUT_FORMAT'
        );
      }

      // Process data with optional limit
      const itemsToProcess = options.maxItems
        ? dataArray.slice(0, options.maxItems)
        : dataArray;

      const processedData: T[] = [];

      for (const item of itemsToProcess) {
        try {
          const processedItem = await this.processItem<T>(item);
          processedData.push(processedItem);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          result.errors.push(`Failed to process item: ${errorMessage}`);
        }
      }

      // Save to file if output path provided
      if (options.outputPath) {
        await this.saveToFile(options.outputPath, {
          processed: processedData,
          count: processedData.length,
          timestamp: result.timestamp.toISOString()
        });
      }

      result.success = result.errors.length === 0;
      result.count = processedData.length;
      result.data = processedData;

    } catch (error) {
      if (error instanceof SyntaxError) {
        throw new DataProcessingError(
          `Invalid JSON data: ${error.message}`,
          'JSON_PARSE_ERROR',
          error
        );
      }

      if (error instanceof DataProcessingError) {
        throw error;
      }

      throw new DataProcessingError(
        `Processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'PROCESSING_ERROR',
        error instanceof Error ? error : undefined
      );
    }

    return result;
  }

  /**
   * Validate and normalize input data to array format
   */
  private validateAndNormalizeInput(
    data: unknown,
    options: ProcessingOptions
  ): any[] | null {
    if (options.validateData === false) {
      return Array.isArray(data) ? data : [data];
    }

    if (!Array.isArray(data)) {
      return null;
    }

    return data;
  }

  /**
   * Process a single data item
   */
  private async processItem<T>(item: any): Promise<T> {
    // Validate item structure
    if (typeof item !== 'object' || item === null) {
      throw new DataProcessingError(
        'Item must be a non-null object',
        'INVALID_ITEM_FORMAT'
      );
    }

    if (!('id' in item)) {
      throw new DataProcessingError(
        'Item must have an id property',
        'MISSING_ID_PROPERTY'
      );
    }

    // Process the item (this is where business logic would go)
    return {
      ...item,
      processed: true,
      processedAt: new Date().toISOString()
    } as T;
  }

  /**
   * Save processed data to file
   */
  private async saveToFile(filePath: string, data: any): Promise<void> {
    const fs = await import('fs/promises');
    const path = await import('path');

    const dir = path.dirname(filePath);
    await fs.mkdir(dir, { recursive: true });

    const jsonData = JSON.stringify(data, null, 2);
    await fs.writeFile(filePath, jsonData, 'utf-8');
  }
}

// Export for use in other modules
export {
  DataProcessor,
  ProcessingResult,
  ProcessingOptions,
  DataProcessingError
};

// Example usage and utility functions
export async function processLargeDataset(
  filePath: string,
  options: ProcessingOptions = {}
): Promise<ProcessingResult> {
  const fs = await import('fs/promises');

  try {
    const fileContent = await fs.readFile(filePath, 'utf-8');
    const processor = new DataProcessor();

    return await processor.processJsonData(fileContent, {
      validateData: true,
      ...options
    });
  } catch (error) {
    throw new DataProcessingError(
      `Failed to process dataset: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'FILE_PROCESSING_ERROR',
      error instanceof Error ? error : undefined
    );
  }
}"""

    def _get_typescript_architect_example(self) -> str:
        """Get TypeScript architecture example."""
        return """// File: src/data-pipeline/index.ts
// [NEW] or [MODIFIED]

/**
 * Data Pipeline Architecture Module
 *
 * This module demonstrates enterprise-grade TypeScript architecture
 * with proper separation of concerns, dependency injection, and
 * comprehensive error handling.
 */

// Core abstractions and interfaces
export interface IDataSource {
  /**
   * Read data from the source
   */
  readData(): Promise<string>;

  /**
   * Write processed data back to source
   */
  writeData(data: string): Promise<void>;

  /**
   * Get source metadata
   */
  getMetadata(): Promise<SourceMetadata>;
}

export interface IDataProcessor {
  /**
   * Process data and return transformed result
   */
  process(data: string): Promise<string>;

  /**
   * Get processor capabilities and requirements
   */
  getCapabilities(): ProcessorCapabilities;
}

export interface IPipelineMonitor {
  /**
   * Record pipeline metrics
   */
  recordMetrics(metrics: PipelineMetrics): void;

  /**
   * Record error occurrence
   */
  recordError(error: PipelineError): void;

  /**
   * Get pipeline health status
   */
  getHealthStatus(): Promise<HealthStatus>;
}

// Domain models
export interface SourceMetadata {
  readonly format: string;
  readonly size: number;
  readonly lastModified: Date;
  readonly encoding?: string;
}

export interface ProcessorCapabilities {
  readonly supportedFormats: string[];
  readonly maxDataSize: number;
  readonly requiresPreprocessing: boolean;
  readonly outputFormats: string[];
}

export interface PipelineMetrics {
  readonly processingTime: number;
  readonly itemsProcessed: number;
  readonly throughput: number;
  readonly memoryUsage: number;
}

export interface PipelineError {
  readonly code: string;
  readonly message: string;
  readonly timestamp: Date;
  readonly context?: Record<string, unknown>;
}

export interface HealthStatus {
  readonly status: 'healthy' | 'degraded' | 'unhealthy';
  readonly checks: HealthCheck[];
}

export interface HealthCheck {
  readonly name: string;
  readonly status: 'pass' | 'fail' | 'warn';
  readonly message?: string;
  readonly timestamp: Date;
}

// Custom error classes for better error handling
export class PipelineError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly originalError?: Error,
    public readonly context?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'PipelineError';
  }
}

export class ConfigurationError extends PipelineError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, 'CONFIG_ERROR', undefined, context);
    this.name = 'ConfigurationError';
  }
}

// Configuration system
export interface PipelineConfig {
  readonly input: DataSourceConfig;
  readonly output: DataSourceConfig;
  readonly processing: ProcessingConfig;
  readonly monitoring?: MonitoringConfig;
}

export interface DataSourceConfig {
  readonly type: 'file' | 'http' | 'database' | 'stream';
  readonly connection: Record<string, unknown>;
  readonly options?: Record<string, unknown>;
}

export interface ProcessingConfig {
  readonly chunkSize: number;
  readonly maxConcurrency: number;
  readonly retryAttempts: number;
  readonly timeout: number;
}

export interface MonitoringConfig {
  readonly metricsEnabled: boolean;
  readonly healthCheckInterval: number;
  readonly alertThresholds: Record<string, number>;
}

// Core pipeline implementation
export class DataPipeline {
  private readonly config: PipelineConfig;
  private readonly dataSource: IDataSource;
  private readonly processor: IDataProcessor;
  private readonly monitor?: IPipelineMonitor;

  constructor(
    config: PipelineConfig,
    dataSource: IDataSource,
    processor: IDataProcessor,
    monitor?: IPipelineMonitor
  ) {
    this.config = this.validateConfig(config);
    this.dataSource = dataSource;
    this.processor = processor;
    this.monitor = monitor;
  }

  /**
   * Execute the complete data pipeline
   */
  async execute(): Promise<ExecutionResult> {
    const startTime = Date.now();
    const executionId = this.generateExecutionId();

    try {
      // Health check before execution
      if (this.monitor) {
        const health = await this.monitor.getHealthStatus();
        if (health.status === 'unhealthy') {
          throw new PipelineError(
            'Pipeline is unhealthy and cannot execute',
            'UNHEALTHY_PIPELINE'
          );
        }
      }

      // Read source data
      const rawData = await this.dataSource.readData();

      // Process data in chunks
      const processedChunks = await this.processInChunks(rawData);

      // Combine results
      const resultData = this.combineChunks(processedChunks);

      // Write output
      await this.dataSource.writeData(resultData);

      // Record successful execution
      const processingTime = Date.now() - startTime;
      const metrics: PipelineMetrics = {
        processingTime,
        itemsProcessed: processedChunks.length,
        throughput: processedChunks.length / (processingTime / 1000),
        memoryUsage: this.getMemoryUsage()
      };

      if (this.monitor) {
        this.monitor.recordMetrics(metrics);
      }

      return {
        success: true,
        executionId,
        processingTime,
        itemsProcessed: processedChunks.length,
        errors: []
      };

    } catch (error) {
      const processingTime = Date.now() - startTime;

      // Record error
      if (this.monitor && error instanceof Error) {
        this.monitor.recordError({
          code: error.name,
          message: error.message,
          timestamp: new Date(),
          context: { executionId, processingTime }
        });
      }

      return {
        success: false,
        executionId,
        processingTime,
        itemsProcessed: 0,
        errors: [error instanceof Error ? error.message : 'Unknown error']
      };
    }
  }

  private validateConfig(config: PipelineConfig): PipelineConfig {
    if (config.processing.chunkSize <= 0) {
      throw new ConfigurationError(
        'Chunk size must be positive',
        { chunkSize: config.processing.chunkSize }
      );
    }

    if (config.processing.maxConcurrency < 1) {
      throw new ConfigurationError(
        'Max concurrency must be at least 1',
        { maxConcurrency: config.processing.maxConcurrency }
      );
    }

    return config;
  }

  private generateExecutionId(): string {
    return `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async processInChunks(data: string): Promise<string[]> {
    // Implementation would split data into chunks and process concurrently
    // This is a simplified example
    return [await this.processor.process(data)];
  }

  private combineChunks(chunks: string[]): string {
    // Implementation would combine processed chunks
    return chunks.join('\\n');
  }

  private getMemoryUsage(): number {
    // In Node.js environment, would use process.memoryUsage()
    return 0;
  }
}

// Factory functions for different pipeline types
export class PipelineFactory {
  static createFilePipeline(
    inputPath: string,
    outputPath: string,
    processor: IDataProcessor,
    monitor?: IPipelineMonitor
  ): DataPipeline {
    const config: PipelineConfig = {
      input: {
        type: 'file',
        connection: { path: inputPath }
      },
      output: {
        type: 'file',
        connection: { path: outputPath }
      },
      processing: {
        chunkSize: 1000,
        maxConcurrency: 4,
        retryAttempts: 3,
        timeout: 30000
      }
    };

    const dataSource = new FileDataSource(config.input, config.output);

    return new DataPipeline(config, dataSource, processor, monitor);
  }

  static createHttpPipeline(
    inputUrl: string,
    outputPath: string,
    processor: IDataProcessor,
    monitor?: IPipelineMonitor
  ): DataPipeline {
    const config: PipelineConfig = {
      input: {
        type: 'http',
        connection: { url: inputUrl }
      },
      output: {
        type: 'file',
        connection: { path: outputPath }
      },
      processing: {
        chunkSize: 500,
        maxConcurrency: 2,
        retryAttempts: 5,
        timeout: 60000
      }
    };

    const dataSource = new HttpDataSource(config.input, config.output);

    return new DataPipeline(config, dataSource, processor, monitor);
  }
}

// Example execution function
export interface ExecutionResult {
  readonly success: boolean;
  readonly executionId: string;
  readonly processingTime: number;
  readonly itemsProcessed: number;
  readonly errors: string[];
}

export async function runDataPipeline(
  pipeline: DataPipeline
): Promise<ExecutionResult> {
  console.log('Starting data pipeline execution...');

  const result = await pipeline.execute();

  if (result.success) {
    console.log(`Pipeline completed successfully in ${result.processingTime}ms`);
    console.log(`Processed ${result.itemsProcessed} items`);
  } else {
    console.error('Pipeline failed:', result.errors);
  }

  return result;
}

// Implementation classes (would be in separate files in real project)
class FileDataSource implements IDataSource {
  constructor(
    private readonly inputConfig: DataSourceConfig,
    private readonly outputConfig: DataSourceConfig
  ) {}

  async readData(): Promise<string> {
    // Implementation would read from file
    return '{}';
  }

  async writeData(data: string): Promise<void> {
    // Implementation would write to file
  }

  async getMetadata(): Promise<SourceMetadata> {
    // Implementation would get file metadata
    return {
      format: 'json',
      size: 0,
      lastModified: new Date()
    };
  }
}

class HttpDataSource implements IDataSource {
  constructor(
    private readonly inputConfig: DataSourceConfig,
    private readonly outputConfig: DataSourceConfig
  ) {}

  async readData(): Promise<string> {
    // Implementation would fetch from HTTP endpoint
    return '{}';
  }

  async writeData(data: string): Promise<void> {
    // Implementation would write to file or HTTP endpoint
  }

  async getMetadata(): Promise<SourceMetadata> {
    // Implementation would get HTTP resource metadata
    return {
      format: 'json',
      size: 0,
      lastModified: new Date()
    };
  }
}"""

    def _get_typescript_peer_example(self) -> str:
        """Get TypeScript peer review example."""
        return """// File: services/user-service.ts
// [REVIEW] Peer Review Comments

import { promises as fs } from 'fs';
import * as path from 'path';
import { EventEmitter } from 'events';

/**
 * Configuration for user service
 */
interface UserServiceConfig {
  /** Database connection configuration */
  database: {
    url: string;
    timeout: number;
  };
  /** Cache configuration */
  cache?: {
    ttl: number;
    maxSize: number;
  };
  /** Feature flags */
  features: {
    enableLogging: boolean;
    enableMetrics: boolean;
  };
}

/**
 * User data structure
 */
interface User {
  id: number;
  username: string;
  email: string;
  createdAt: Date;
  preferences?: Record<string, unknown>;
}

/**
 * Service error types
 */
class UserServiceError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = 'UserServiceError';
  }
}

class UserNotFoundError extends UserServiceError {
  constructor(userId: number) {
    super(`User with ID ${userId} not found`, 'USER_NOT_FOUND', 404);
    this.name = 'UserNotFoundError';
  }
}

/**
 * User service with comprehensive TypeScript patterns
 */
class UserService extends EventEmitter {
  private readonly config: UserServiceConfig;
  private cache: Map<string, { data: User; expiry: number }> | null = null;
  private metrics: { requests: number; cacheHits: number; errors: number } = {
    requests: 0,
    cacheHits: 0,
    errors: 0
  };

  constructor(config: UserServiceConfig) {
    super();
    this.config = config;

    if (config.cache) {
      this.cache = new Map();
      this.setupCacheCleanup();
    }

    if (config.features.enableLogging) {
      this.setupLogging();
    }
  }

  /**
   * Retrieve user by ID with caching and error handling
   * @param userId - Unique user identifier
   * @returns Promise resolving to user data
   * @throws {UserNotFoundError} If user is not found
   * @throws {UserServiceError} If service operation fails
   */
  async getUserById(userId: number): Promise<User> {
    if (!Number.isInteger(userId) || userId <= 0) {
      throw new UserServiceError(
        'User ID must be a positive integer',
        'INVALID_USER_ID',
        400
      );
    }

    this.metrics.requests++;
    const startTime = Date.now();

    try {
      // Check cache first if enabled
      if (this.cache) {
        const cached = this.getCachedUser(userId);
        if (cached) {
          this.metrics.cacheHits++;
          this.emit('cache.hit', { userId, source: 'memory' });
          return cached;
        }
      }

      // Fetch from database
      const user = await this.fetchUserFromDatabase(userId);

      if (!user) {
        throw new UserNotFoundError(userId);
      }

      // Cache the result if caching is enabled
      if (this.cache && this.config.cache) {
        this.setCachedUser(userId, user);
      }

      // Record metrics if enabled
      if (this.config.features.enableMetrics) {
        this.recordMetrics('getUserById', Date.now() - startTime, true);
      }

      this.emit('user.retrieved', { userId, duration: Date.now() - startTime });
      return user;

    } catch (error) {
      this.metrics.errors++;

      if (this.config.features.enableMetrics) {
        this.recordMetrics('getUserById', Date.now() - startTime, false);
      }

      if (error instanceof UserNotFoundError || error instanceof UserServiceError) {
        throw error;
      }

      // Wrap unexpected errors
      throw new UserServiceError(
        `Failed to retrieve user: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'USER_RETRIEVAL_FAILED',
        500
      );
    }
  }

  /**
   * Update user data with validation
   * @param userId - User identifier
   * @param updates - Partial user data to update
   * @returns Promise resolving to updated user
   */
  async updateUser(
    userId: number,
    updates: Partial<Pick<User, 'username' | 'email' | 'preferences'>>
  ): Promise<User> {
    // Input validation
    if (updates.username && updates.username.length < 3) {
      throw new UserServiceError(
        'Username must be at least 3 characters long',
        'INVALID_USERNAME_LENGTH',
        400
      );
    }

    if (updates.email && !this.isValidEmail(updates.email)) {
      throw new UserServiceError(
        'Invalid email format',
        'INVALID_EMAIL_FORMAT',
        400
      );
    }

    // Implementation would update database and invalidate cache
    const updatedUser: User = {
      id: userId,
      username: updates.username || 'existing',
      email: updates.email || 'existing@example.com',
      createdAt: new Date(),
      preferences: updates.preferences
    };

    // Invalidate cache for this user
    if (this.cache) {
      this.cache.delete(`user:${userId}`);
    }

    return updatedUser;
  }

  /**
   * Get service health status
   */
  getHealthStatus(): { status: string; metrics: typeof this.metrics } {
    return {
      status: this.metrics.errors > this.metrics.requests * 0.1 ? 'degraded' : 'healthy',
      metrics: { ...this.metrics }
    };
  }

  private getCachedUser(userId: number): User | null {
    if (!this.cache || !this.config.cache) return null;

    const key = `user:${userId}`;
    const cached = this.cache.get(key);

    if (!cached) return null;

    if (Date.now() > cached.expiry) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  private setCachedUser(userId: number, user: User): void {
    if (!this.cache || !this.config.cache) return;

    const key = `user:${userId}`;
    const expiry = Date.now() + (this.config.cache.ttl * 1000);

    this.cache.set(key, { data: user, expiry });
  }

  private setupCacheCleanup(): void {
    // Clean up expired cache entries every 5 minutes
    setInterval(() => {
      if (!this.cache) return;

      const now = Date.now();
      for (const [key, value] of this.cache.entries()) {
        if (now > value.expiry) {
          this.cache.delete(key);
        }
      }
    }, 5 * 60 * 1000);
  }

  private setupLogging(): void {
    this.on('user.retrieved', (event) => {
      console.log(`User ${event.userId} retrieved in ${event.duration}ms`);
    });

    this.on('cache.hit', (event) => {
      console.log(`Cache hit for user ${event.userId} from ${event.source}`);
    });
  }

  private async fetchUserFromDatabase(userId: number): Promise<User | null> {
    // Database implementation would go here
    // This is a placeholder for the actual database query
    return {
      id: userId,
      username: 'sample_user',
      email: 'user@example.com',
      createdAt: new Date()
    };
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private recordMetrics(operation: string, duration: number, success: boolean): void {
    // Implementation would record to metrics service
    console.log(`${operation} completed in ${duration}ms (success: ${success})`);
  }
}

// Peer Review Comments:
// =====================

/**
 * PEER REVIEW: UserService Implementation
 *
 * REVIEWER: Senior TypeScript Developer
 * DATE: 2024-01-15
 * OVERALL SCORE: 8.5/10
 */

// ✅ EXCELLENT:
// - Comprehensive TypeScript usage with strict typing
// - Proper error hierarchy with custom error classes
// - Good use of interfaces for configuration and data models
// - Event-driven architecture with EventEmitter
// - Input validation with meaningful error messages
// - Caching strategy with TTL and cleanup
// - Health check functionality
// - Proper async/await patterns throughout

// ⚠️  NEEDS IMPROVEMENT:
// 1. Missing JSDoc comments for private methods
// 2. Cache implementation uses Map which may not scale well
// 3. No rate limiting or circuit breaker patterns
// 4. Missing unit tests in the same file

// 🔧 SUGGESTED CHANGES:
// - Add JSDoc comments for all private methods
// - Consider using a more robust caching solution (Redis, etc.)
// - Add input sanitization for XSS prevention
// - Implement proper database transaction handling
// - Add integration with monitoring/logging services
// - Consider using a dependency injection container

// 📝 GENERAL ADVICE:
// - Consider extracting interfaces to separate declaration files
// - Add API versioning strategy for future compatibility
// - Implement proper database connection pooling
// - Add request/response logging middleware
// - Consider using TypeScript decorators for cross-cutting concerns

// 🔒 SECURITY CONSIDERATIONS:
// - Validate and sanitize all user inputs
// - Implement proper authentication and authorization
// - Use HTTPS for all external communications
// - Implement rate limiting to prevent abuse
// - Log security events for audit trails

/**
 * APPROVAL STATUS: ✅ APPROVED WITH MINOR REVISIONS
 *
 * Required actions before merge:
// - [ ] Add JSDoc comments for private methods
// - [ ] Add input sanitization for user data
// - [ ] Implement proper error monitoring integration
 */"""

    def _get_typescript_sdet_example(self) -> str:
        """Get TypeScript SDET example."""
        return """// File: tests/user-service.test.ts
// [NEW] or [MODIFIED]

/**
 * Comprehensive test suite for UserService
 *
 * This test suite demonstrates TypeScript testing best practices:
 * - Jest framework with TypeScript support
 * - Comprehensive mocking with proper typing
 * - Test organization and documentation
 * - Edge case and error condition testing
 */

import { EventEmitter } from 'events';
import { UserService, UserServiceError, UserNotFoundError } from '../src/services/user-service';
import type { User, UserServiceConfig } from '../src/services/user-service';

// Mock external dependencies
jest.mock('fs', () => ({
  promises: {
    readFile: jest.fn(),
    writeFile: jest.fn()
  }
}));

// Test fixtures and utilities
const createMockConfig = (overrides: Partial<UserServiceConfig> = {}): UserServiceConfig => ({
  database: {
    url: 'postgresql://localhost:5432/testdb',
    timeout: 5000
  },
  features: {
    enableLogging: true,
    enableMetrics: true
  },
  ...overrides
});

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  createdAt: new Date('2024-01-01T00:00:00.000Z'),
  ...overrides
});

const createUserServiceWithMocks = (config?: Partial<UserServiceConfig>) => {
  const mockConfig = createMockConfig(config);

  // Mock the database call
  const mockFetchUserFromDatabase = jest.fn();

  // Create service instance
  const service = new UserService(mockConfig);

  // Replace the private method for testing
  const originalFetch = (service as any).fetchUserFromDatabase;
  (service as any).fetchUserFromDatabase = mockFetchUserFromDatabase;

  return { service, mockFetchUserFromDatabase };
};

// Test suite
describe('UserService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('constructor', () => {
    it('should initialize with valid configuration', () => {
      const config = createMockConfig();
      const service = new UserService(config);

      expect(service).toBeInstanceOf(EventEmitter);
      expect(service.getHealthStatus().status).toBe('healthy');
    });

    it('should throw error for invalid configuration', () => {
      const invalidConfig = createMockConfig({
        database: { url: '', timeout: -1 }
      });

      expect(() => new UserService(invalidConfig)).toThrow(UserServiceError);
    });

    it('should setup cache when cache configuration is provided', () => {
      const config = createMockConfig({
        cache: {
          ttl: 300,
          maxSize: 100
        }
      });

      const service = new UserService(config);
      expect((service as any).cache).toBeInstanceOf(Map);
    });

    it('should not setup cache when cache configuration is not provided', () => {
      const config = createMockConfig();
      const service = new UserService(config);

      expect((service as any).cache).toBeNull();
    });
  });

  describe('getUserById', () => {
    it('should return user data for valid ID', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser({ id: 42 });

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      const result = await service.getUserById(42);

      expect(result).toEqual(mockUser);
      expect(mockFetchUserFromDatabase).toHaveBeenCalledWith(42);
      expect(mockFetchUserFromDatabase).toHaveBeenCalledTimes(1);
    });

    it('should return null when user not found in database', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();

      mockFetchUserFromDatabase.mockResolvedValue(null);

      await expect(service.getUserById(999)).rejects.toThrow(UserNotFoundError);
    });

    it('should throw UserNotFoundError for non-existent user', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();

      mockFetchUserFromDatabase.mockResolvedValue(null);

      await expect(service.getUserById(999)).rejects.toThrow(UserNotFoundError);

      try {
        await service.getUserById(999);
      } catch (error) {
        expect(error).toBeInstanceOf(UserNotFoundError);
        expect((error as UserNotFoundError).statusCode).toBe(404);
      }
    });

    it('should throw UserServiceError for invalid user ID', async () => {
      const { service } = createUserServiceWithMocks();

      await expect(service.getUserById(0)).rejects.toThrow(UserServiceError);
      await expect(service.getUserById(-1)).rejects.toThrow(UserServiceError);
      await expect(service.getUserById(3.14)).rejects.toThrow(UserServiceError);
    });

    it('should use cache when available and return cached user', async () => {
      const config = createMockConfig({
        cache: { ttl: 300, maxSize: 100 }
      });

      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks(config);
      const mockUser = createMockUser({ id: 123 });

      // First call - should fetch from database
      mockFetchUserFromDatabase.mockResolvedValue(mockUser);
      await service.getUserById(123);

      // Second call - should use cache
      const cachedResult = await service.getUserById(123);

      expect(cachedResult).toEqual(mockUser);
      expect(mockFetchUserFromDatabase).toHaveBeenCalledTimes(1);
    });

    it('should handle database errors gracefully', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const dbError = new Error('Connection timeout');

      mockFetchUserFromDatabase.mockRejectedValue(dbError);

      await expect(service.getUserById(1)).rejects.toThrow(UserServiceError);

      try {
        await service.getUserById(1);
      } catch (error) {
        expect(error).toBeInstanceOf(UserServiceError);
        expect((error as UserServiceError).code).toBe('USER_RETRIEVAL_FAILED');
      }
    });

    it('should emit events during user retrieval', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser();
      const eventSpy = jest.fn();

      service.on('user.retrieved', eventSpy);
      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      await service.getUserById(1);

      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 1,
          duration: expect.any(Number)
        })
      );
    });

    it('should track metrics correctly', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser();

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      await service.getUserById(1);

      const healthStatus = service.getHealthStatus();
      expect(healthStatus.metrics.requests).toBe(1);
      expect(healthStatus.metrics.errors).toBe(0);
      expect(healthStatus.status).toBe('healthy');
    });
  });

  describe('updateUser', () => {
    it('should update user with valid data', async () => {
      const { service } = createUserServiceWithMocks();

      const updates = {
        username: 'newusername',
        email: 'newemail@example.com'
      };

      const result = await service.updateUser(1, updates);

      expect(result.username).toBe(updates.username);
      expect(result.email).toBe(updates.email);
    });

    it('should throw error for invalid username length', async () => {
      const { service } = createUserServiceWithMocks();

      await expect(
        service.updateUser(1, { username: 'ab' })
      ).rejects.toThrow(UserServiceError);
    });

    it('should throw error for invalid email format', async () => {
      const { service } = createUserServiceWithMocks();

      await expect(
        service.updateUser(1, { email: 'invalid-email' })
      ).rejects.toThrow(UserServiceError);
    });

    it('should invalidate cache after update', async () => {
      const config = createMockConfig({
        cache: { ttl: 300, maxSize: 100 }
      });

      const { service } = createUserServiceWithMocks(config);

      // Add user to cache
      await service.getUserById(1);

      // Update user
      await service.updateUser(1, { username: 'updated' });

      // Verify cache was cleared
      expect((service as any).cache.has('user:1')).toBe(false);
    });
  });

  describe('getHealthStatus', () => {
    it('should return healthy status for normal operation', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser();

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      // Make some successful requests
      await service.getUserById(1);
      await service.getUserById(2);

      const health = service.getHealthStatus();
      expect(health.status).toBe('healthy');
      expect(health.metrics.requests).toBe(2);
      expect(health.metrics.errors).toBe(0);
    });

    it('should return degraded status when error rate is high', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();

      mockFetchUserFromDatabase.mockRejectedValue(new Error('Database error'));

      // Make requests that will fail
      try {
        await service.getUserById(1);
      } catch (error) {
        // Expected error
      }

      try {
        await service.getUserById(2);
      } catch (error) {
        // Expected error
      }

      const health = service.getHealthStatus();
      expect(health.status).toBe('degraded');
      expect(health.metrics.requests).toBe(2);
      expect(health.metrics.errors).toBe(2);
    });
  });

  describe('edge cases', () => {
    it('should handle concurrent requests correctly', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser({ id: 1 });

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      // Make concurrent requests
      const promises = [
        service.getUserById(1),
        service.getUserById(1),
        service.getUserById(1)
      ];

      const results = await Promise.all(promises);

      expect(results).toHaveLength(3);
      expect(mockFetchUserFromDatabase).toHaveBeenCalledTimes(1); // Should use cache for subsequent calls
      results.forEach(result => expect(result).toEqual(mockUser));
    });

    it('should handle very large user IDs', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser({ id: Number.MAX_SAFE_INTEGER });

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      const result = await service.getUserById(Number.MAX_SAFE_INTEGER);
      expect(result.id).toBe(Number.MAX_SAFE_INTEGER);
    });

    it('should handle special characters in user data', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const specialUser = createMockUser({
        username: 'user@#$%^&*()',
        email: 'test+special@example.com'
      });

      mockFetchUserFromDatabase.mockResolvedValue(specialUser);

      const result = await service.getUserById(1);
      expect(result.username).toBe('user@#$%^&*()');
      expect(result.email).toBe('test+special@example.com');
    });
  });

  describe('integration tests', () => {
    it('should work with real cache configuration', async () => {
      const config = createMockConfig({
        cache: {
          ttl: 5, // 5 seconds for testing
          maxSize: 10
        }
      });

      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks(config);
      const mockUser = createMockUser({ id: 1 });

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      // First call
      const startTime = Date.now();
      await service.getUserById(1);
      const firstCallTime = Date.now() - startTime;

      // Second call should be faster (cached)
      const secondStartTime = Date.now();
      await service.getUserById(1);
      const secondCallTime = Date.now() - secondStartTime;

      expect(secondCallTime).toBeLessThan(firstCallTime);
      expect(mockFetchUserFromDatabase).toHaveBeenCalledTimes(1);
    });
  });

  describe('performance tests', () => {
    it('should handle large number of requests efficiently', async () => {
      const { service, mockFetchUserFromDatabase } = createUserServiceWithMocks();
      const mockUser = createMockUser();

      mockFetchUserFromDatabase.mockResolvedValue(mockUser);

      const startTime = Date.now();
      const promises = [];

      // Create 100 concurrent requests
      for (let i = 1; i <= 100; i++) {
        promises.push(service.getUserById(i));
      }

      const results = await Promise.all(promises);
      const endTime = Date.now();

      expect(results).toHaveLength(100);
      expect(endTime - startTime).toBeLessThan(5000); // Should complete within 5 seconds
      expect(mockFetchUserFromDatabase).toHaveBeenCalledTimes(100);
    });
  });

  describe('cleanup', () => {
    it('should cleanup cache entries on interval', async () => {
      const config = createMockConfig({
        cache: { ttl: 1, maxSize: 100 } // 1 second TTL for testing
      });

      const { service } = createUserServiceWithMocks(config);

      // Add item to cache
      await service.getUserById(1);

      // Verify cache has item
      expect((service as any).cache.has('user:1')).toBe(true);

      // Fast-forward time past TTL
      jest.advanceTimersByTime(2000);

      // Trigger cleanup (this would normally happen automatically)
      if ((service as any).cache) {
        const now = Date.now();
        for (const [key, value] of (service as any).cache.entries()) {
          if (now > value.expiry) {
            (service as any).cache.delete(key);
          }
        }
      }

      expect((service as any).cache.has('user:1')).toBe(false);
    });
  });
});

/**
 * Test utilities and helpers
 */
export const TestHelpers = {
  createMockConfig,
  createMockUser,
  createUserServiceWithMocks
};

/**
 * Performance benchmarking utilities
 */
export class PerformanceBenchmark {
  static async measureOperation<T>(
    operation: () => Promise<T>
  ): Promise<{ result: T; duration: number }> {
    const startTime = Date.now();
    const result = await operation();
    const duration = Date.now() - startTime;

    return { result, duration };
  }

  static async runLoadTest(
    operation: () => Promise<any>,
    concurrency: number,
    iterations: number
  ): Promise<{
    totalTime: number;
    averageTime: number;
    requestsPerSecond: number;
    errors: number;
  }> {
    const startTime = Date.now();
    let errors = 0;

    const workers = Array(concurrency).fill(null).map(async () => {
      for (let i = 0; i < iterations / concurrency; i++) {
        try {
          await operation();
        } catch (error) {
          errors++;
        }
      }
    });

    await Promise.all(workers);
    const totalTime = Date.now() - startTime;
    const totalOperations = (iterations / concurrency) * concurrency;

    return {
      totalTime,
      averageTime: totalTime / totalOperations,
      requestsPerSecond: (totalOperations / totalTime) * 1000,
      errors
    };
  }
}

/**
 * Example usage of performance benchmarking:
 *
 * ```typescript
 * const { service } = createUserServiceWithMocks();
 *
 * const results = await PerformanceBenchmark.runLoadTest(
 *   () => service.getUserById(1),
 *   10,  // 10 concurrent workers
 *   1000 // 1000 total operations
 * );
 *
 * console.log('Load test results:', results);
 * ```
 */

// Test configuration
export const jestConfig = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  testTimeout: 10000
};

// Test setup file (tests/setup.ts)
export const setupTestEnvironment = (): void => {
  // Global test configuration
  process.env.NODE_ENV = 'test';

  // Mock console methods to reduce noise in tests
  global.console = {
    ...console,
    log: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn()
  };

  // Setup global test utilities
  (global as any).testHelpers = TestHelpers;
  (global as any).performanceBenchmark = PerformanceBenchmark;
};"""