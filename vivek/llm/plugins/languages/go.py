"""Go Language Plugin implementation."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field

from vivek.llm.plugins.base.language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


@dataclass
class GoConventions(LanguageConventions):
    """Go-specific conventions and best practices."""

    def __post_init__(self):
        if not self.language:
            self.language = "go"
        if not self.extensions:
            self.extensions = [".go"]

        # Naming conventions
        if not self.naming_conventions:
            self.naming_conventions = {
                "CamelCase": "Exported types, functions, constants, variables",
                "camelCase": "Unexported types, functions, variables",
                "ALL_CAPS": "Constants (for exported) or SCREAMING_SNAKE_CASE",
                "snake_case": "Never used in Go"
            }

        # Import and dependency management
        if not self.import_style:
            self.import_style = "Use fully qualified import paths with standard library, third-party, and local imports in separate groups"
        if not self.dependency_management:
            self.dependency_management = "Use Go modules (go.mod) with semantic versioning and go.sum for dependency lock"

        # Code style and formatting
        if not self.code_style:
            self.code_style = "Follow gofmt and go vet guidelines with effective Go patterns"
        if not self.formatting_rules:
            self.formatting_rules = {
                "formatting": "Use gofmt for consistent formatting",
                "imports": "Group imports: standard library, blank line, third-party, blank line, local",
                "line_length": "No strict limit, but prefer readable lines",
                "naming": "Follow Go naming conventions strictly"
            }

        # Error handling
        if not self.error_handling:
            self.error_handling = "Use explicit error returns and check errors immediately"
        if not self.exception_types:
            self.exception_types = [
                "error interface", "fmt.Errorf", "errors.New", "errors.Wrap",
                "errors.Cause", "errors.Is", "errors.As"
            ]

        # Documentation
        if not self.documentation_style:
            self.documentation_style = "Use godoc with comments starting with the name of the thing being documented"
        if not self.comment_conventions:
            self.comment_conventions = {
                "package": "Package comment before package declaration",
                "exported": "Comments for all exported types and functions",
                "internal": "// comments for complex logic",
                "TODO": "// TODO: comments for future improvements"
            }

        # Type system
        if not self.type_system:
            self.type_system = "Static typing with structural typing and duck typing for interfaces"
        if not self.type_annotations:
            self.type_annotations = "Use explicit types, interfaces, and struct composition"

        # Testing
        if not self.testing_frameworks:
            self.testing_frameworks = ["testing package", "testify", "ginkgo", "goconvey"]
        if not self.testing_patterns:
            self.testing_patterns = {
                "naming": "*_test.go files with Test* functions",
                "assertions": "Use standard testing.T methods or testify/assert",
                "benchmarks": "Benchmark* functions for performance tests",
                "examples": "Example* functions for documentation"
            }

        # Project structure
        if not self.project_structure:
            self.project_structure = {
                "cmd": "Main applications for the project",
                "pkg": "Library code that's ok to use by external applications",
                "internal": "Private application and library code",
                "api": "OpenAPI/Swagger specs, protocol definition files",
                "configs": "Configuration file templates or default configs",
                "scripts": "Scripts to perform various build, install, analysis, etc operations"
            }
        if not self.entry_points:
            self.entry_points = ["main.go", "cmd/*/main.go"]

        # Idioms and best practices
        if not self.idioms:
            self.idioms = [
                "Use slices over arrays when possible",
                "Prefer composition over inheritance",
                "Handle errors explicitly, don't ignore them",
                "Use interfaces for abstraction and testability",
                "Write tests alongside production code"
            ]
        if not self.best_practices:
            self.best_practices = [
                "Write clear, readable code that follows Go idioms",
                "Use gofmt to format all code consistently",
                "Run go vet to catch common mistakes",
                "Write tests for all public functions and methods",
                "Use meaningful variable and function names",
                "Keep functions small and focused on a single purpose",
                "Use struct composition and embedding appropriately",
                "Handle all error conditions explicitly"
            ]


class GoLanguagePlugin(LanguagePlugin):
    """Go language plugin with comprehensive Go-specific behavior."""

    def __init__(self):
        super().__init__("go")

    @property
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports."""
        return ["go", "golang"]

    @property
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports."""
        return [Mode.CODER.value, Mode.ARCHITECT.value, Mode.PEER.value, Mode.SDET.value]

    @property
    def name(self) -> str:
        """Human-readable name for this plugin."""
        return "Go Language Assistant"

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0.0"

    def get_conventions(self) -> GoConventions:
        """Get Go-specific conventions for this plugin."""
        if not self._conventions:
            self._conventions = GoConventions(language=self.language)
        return self._conventions

    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a Go and mode-specific executor instance."""
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor
        from vivek.llm.peer_executor import PeerExecutor
        from vivek.llm.sdet_executor import SDETExecutor

        mode_lower = mode.lower()

        class GoLanguageExecutor:
            """Go-aware executor wrapper with language-specific prompts."""

            def __init__(self, base_executor, language_plugin):
                self.base_executor = base_executor
                self.language_plugin = language_plugin
                self.language = "go"
                self.mode = mode_lower

                # Set language-specific prompt
                if hasattr(base_executor, 'mode_prompt'):
                    base_executor.mode_prompt = f"Go {mode_lower.title()} Mode: {self._get_mode_specific_prompt(mode_lower)}"

            def _get_mode_specific_prompt(self, mode: str) -> str:
                """Get Go-specific prompt for the mode."""
                mode_instructions = self.language_plugin.get_language_specific_instructions(mode)
                return f"Follow Go best practices. {mode_instructions}"

            def __getattr__(self, name):
                """Delegate all other attributes to the base executor."""
                return getattr(self.base_executor, name)

        if mode_lower == Mode.CODER.value:
            base_executor = CoderExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.ARCHITECT.value:
            base_executor = ArchitectExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.PEER.value:
            base_executor = PeerExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.SDET.value:
            base_executor = SDETExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        else:
            raise ValueError(f"Unsupported mode for Go plugin: {mode}")

    def get_language_specific_instructions(self, mode: str) -> str:
        """Get Go-specific instructions for the given mode."""
        base_instructions = f"""**Go Language Requirements for {mode.title()} Mode:**

Follow Go conventions:
- Use gofmt for consistent formatting and go vet for common mistakes
- Handle errors explicitly, never ignore them
- Use interfaces for abstraction and testability
- Follow Go naming conventions (CamelCase for exported identifiers)
- Write clear, idiomatic Go code

"""

        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return base_instructions + """
**Coding Requirements:**
- Use explicit error handling with error returns
- Implement interfaces for better testability
- Use struct composition and embedding appropriately
- Write comprehensive tests for all public functions
- Follow the standard Go project layout"""
        elif mode_lower == Mode.ARCHITECT.value:
            return base_instructions + """
**Architecture Requirements:**
- Design concurrent programs using goroutines and channels
- Plan for scalability with proper package organization
- Consider context.Context for cancellation and timeouts
- Document public APIs and design patterns
- Consider deployment and containerization strategies"""
        elif mode_lower == Mode.PEER.value:
            return base_instructions + """
**Code Review Requirements:**
- Check for proper error handling and no ignored errors
- Verify idiomatic Go code patterns and conventions
- Ensure comprehensive test coverage
- Review for security vulnerabilities and race conditions
- Check for appropriate use of interfaces and abstractions"""
        elif mode_lower == Mode.SDET.value:
            return base_instructions + """
**Testing Requirements:**
- Write comprehensive unit tests using the testing package
- Include benchmark tests for performance-critical code
- Test error conditions and edge cases thoroughly
- Use table-driven tests for multiple scenarios
- Aim for >80% test coverage"""
        else:
            return base_instructions

    def get_code_example(self, mode: str, context: Optional[str] = None) -> str:
        """Get a Go-specific code example for the given mode."""
        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return self._get_go_coder_example()
        elif mode_lower == Mode.ARCHITECT.value:
            return self._get_go_architect_example()
        elif mode_lower == Mode.PEER.value:
            return self._get_go_peer_example()
        elif mode_lower == Mode.SDET.value:
            return self._get_go_sdet_example()
        else:
            return self._get_go_coder_example()

    def _get_go_coder_example(self) -> str:
        """Get Go coder example."""
        return """// File: data_processor.go
// [NEW] or [MODIFIED]

// Package processor provides data processing functionality with proper error handling
package processor

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"
)

// ProcessingOptions configures data processing behavior
type ProcessingOptions struct {
	// OutputPath specifies where to save processed data
	OutputPath string
	// ValidateInput enables strict input validation
	ValidateInput bool
	// MaxItems limits the number of items to process
	MaxItems int
	// Timeout sets the maximum processing time
	Timeout time.Duration
}

// ProcessingResult contains the result of data processing
type ProcessingResult struct {
	// Success indicates if processing completed successfully
	Success bool `json:"success"`
	// Count is the number of items processed
	Count int `json:"count"`
	// Data contains the processed items
	Data []interface{} `json:"data"`
	// Errors contains any errors encountered during processing
	Errors []string `json:"errors"`
	// ProcessingTime is the total time taken for processing
	ProcessingTime time.Duration `json:"processing_time"`
}

// DataProcessingError represents a processing-specific error
type DataProcessingError struct {
	Code    string
	Message string
	Err     error
}

func (e *DataProcessingError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

func (e *DataProcessingError) Unwrap() error {
	return e.Err
}

// IsDataProcessingError checks if an error is a DataProcessingError
func IsDataProcessingError(err error) bool {
	_, ok := err.(*DataProcessingError)
	return ok
}

// Processor handles JSON data processing with comprehensive error handling
type Processor struct {
	outputDir string
}

// New creates a new Processor instance
func New(outputDir string) (*Processor, error) {
	if outputDir == "" {
		return nil, &DataProcessingError{
			Code:    "INVALID_OUTPUT_DIR",
			Message: "output directory cannot be empty",
		}
	}

	// Ensure output directory exists
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return nil, &DataProcessingError{
			Code:    "OUTPUT_DIR_CREATION_FAILED",
			Message: "failed to create output directory",
			Err:     err,
		}
	}

	return &Processor{
		outputDir: outputDir,
	}, nil
}

// ProcessJSONData processes JSON data with proper error handling and validation
func (p *Processor) ProcessJSONData(ctx context.Context, jsonData string, opts ProcessingOptions) (*ProcessingResult, error) {
	startTime := time.Now()
	result := &ProcessingResult{
		Success: false,
		Count:   0,
		Data:    []interface{}{},
		Errors:  []string{},
	}

	// Apply default timeout if not set
	if opts.Timeout == 0 {
		opts.Timeout = 30 * time.Second
	}

	// Create context with timeout
	ctx, cancel := context.WithTimeout(ctx, opts.Timeout)
	defer cancel()

	// Channel for processing results
	done := make(chan struct{})
	var processErr error

	go func() {
		defer close(done)
		processErr = p.processData(jsonData, opts, result)
	}()

	select {
	case <-done:
		// Processing completed
	case <-ctx.Done():
		return nil, &DataProcessingError{
			Code:    "PROCESSING_TIMEOUT",
			Message: "processing timed out",
			Err:     ctx.Err(),
		}
	}

	if processErr != nil {
		return nil, processErr
	}

	result.Success = len(result.Errors) == 0
	result.ProcessingTime = time.Since(startTime)

	return result, nil
}

// processData handles the actual data processing logic
func (p *Processor) processData(jsonData string, opts ProcessingOptions, result *ProcessingResult) error {
	// Parse JSON data
	var rawData interface{}
	if err := json.Unmarshal([]byte(jsonData), &rawData); err != nil {
		return &DataProcessingError{
			Code:    "JSON_PARSE_ERROR",
			Message: "failed to parse JSON data",
			Err:     err,
		}
	}

	// Validate and normalize input data
	dataArray, err := p.validateAndNormalizeInput(rawData, opts)
	if err != nil {
		return err
	}

	// Process items with optional limit
	itemsToProcess := dataArray
	if opts.MaxItems > 0 && len(dataArray) > opts.MaxItems {
		itemsToProcess = dataArray[:opts.MaxItems]
	}

	for i, item := range itemsToProcess {
		// Check context cancellation
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		processedItem, err := p.processItem(item)
		if err != nil {
			result.Errors = append(result.Errors, fmt.Sprintf("item %d: %v", i, err))
			continue
		}

		result.Data = append(result.Data, processedItem)
	}

	result.Count = len(result.Data)

	// Save to file if output path provided
	if opts.OutputPath != "" {
		if err := p.saveToFile(opts.OutputPath, result); err != nil {
			result.Errors = append(result.Errors, fmt.Sprintf("failed to save output: %v", err))
		}
	}

	return nil
}

// validateAndNormalizeInput validates and converts input to array format
func (p *Processor) validateAndNormalizeInput(data interface{}, opts ProcessingOptions) ([]interface{}, error) {
	switch v := data.(type) {
	case []interface{}:
		if opts.ValidateInput {
			for i, item := range v {
				if err := p.validateItem(item); err != nil {
					return nil, &DataProcessingError{
						Code:    "INVALID_ITEM",
						Message: fmt.Sprintf("item %d is invalid", i),
						Err:     err,
					}
				}
			}
		}
		return v, nil

	case map[string]interface{}:
		if opts.ValidateInput {
			return nil, &DataProcessingError{
				Code:    "INVALID_INPUT_FORMAT",
				Message: "input must be an array when validation is enabled",
			}
		}
		return []interface{}{v}, nil

	default:
		if opts.ValidateInput {
			return nil, &DataProcessingError{
				Code:    "INVALID_INPUT_TYPE",
				Message: "input must be an array or object",
			}
		}
		return []interface{}{v}, nil
	}
}

// validateItem validates a single data item
func (p *Processor) validateItem(item interface{}) error {
	itemMap, ok := item.(map[string]interface{})
	if !ok {
		return fmt.Errorf("item must be an object")
	}

	if _, hasID := itemMap["id"]; !hasID {
		return fmt.Errorf("item must have an id field")
	}

	return nil
}

// processItem processes a single validated item
func (p *Processor) processItem(item interface{}) (interface{}, error) {
	itemMap, ok := item.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("item must be an object")
	}

	// Add processing metadata
	processedItem := make(map[string]interface{})
	for k, v := range itemMap {
		processedItem[k] = v
	}

	processedItem["processed"] = true
	processedItem["processed_at"] = time.Now().Format(time.RFC3339)

	return processedItem, nil
}

// saveToFile saves processed data to a file
func (p *Processor) saveToFile(filename string, result *ProcessingResult) error {
	outputPath := filepath.Join(p.outputDir, filename)

	file, err := os.Create(outputPath)
	if err != nil {
		return &DataProcessingError{
			Code:    "FILE_CREATE_ERROR",
			Message: "failed to create output file",
			Err:     err,
		}
	}
	defer file.Close()

	// Create output data structure
	outputData := struct {
		ProcessedData []interface{} `json:"processed_data"`
		Count         int           `json:"count"`
		Timestamp     string        `json:"timestamp"`
	}{
		ProcessedData: result.Data,
		Count:         result.Count,
		Timestamp:     time.Now().Format(time.RFC3339),
	}

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")

	if err := encoder.Encode(outputData); err != nil {
		return &DataProcessingError{
			Code:    "FILE_WRITE_ERROR",
			Message: "failed to write data to file",
			Err:     err,
		}
	}

	return nil
}

// ProcessLargeDataset processes a large dataset from a file
func ProcessLargeDataset(ctx context.Context, filePath string, opts ProcessingOptions) (*ProcessingResult, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, &DataProcessingError{
			Code:    "FILE_OPEN_ERROR",
			Message: "failed to open input file",
			Err:     err,
		}
	}
	defer file.Close()

	data, err := io.ReadAll(file)
	if err != nil {
		return nil, &DataProcessingError{
			Code:    "FILE_READ_ERROR",
			Message: "failed to read input file",
			Err:     err,
		}
	}

	processor, err := New(filepath.Dir(opts.OutputPath))
	if err != nil {
		return nil, err
	}

	return processor.ProcessJSONData(ctx, string(data), opts)
}

// MustProcessJSONData processes JSON data and panics on error (for cases where errors are unexpected)
func (p *Processor) MustProcessJSONData(ctx context.Context, jsonData string, opts ProcessingOptions) *ProcessingResult {
	result, err := p.ProcessJSONData(ctx, jsonData, opts)
	if err != nil {
		panic(fmt.Sprintf("unexpected processing error: %v", err))
	}
	return result
}"""

    def _get_go_architect_example(self) -> str:
        """Get Go architecture example."""
        return """// File: internal/data_pipeline/pipeline.go
// [NEW] or [MODIFIED]

// Package pipeline provides a scalable data processing pipeline with proper architecture patterns
package pipeline

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// DataSource defines the interface for data sources
type DataSource interface {
	// ReadData reads data from the source
	ReadData(ctx context.Context) ([]byte, error)

	// WriteData writes processed data back to the source
	WriteData(ctx context.Context, data []byte) error

	// Metadata returns information about the data source
	Metadata() DataSourceMetadata
}

// DataProcessor defines the interface for data processors
type DataProcessor interface {
	// Process processes data and returns the result
	Process(ctx context.Context, data []byte) ([]byte, error)

	// Capabilities returns the capabilities of this processor
	Capabilities() ProcessorCapabilities
}

// PipelineMonitor defines the interface for pipeline monitoring
type PipelineMonitor interface {
	// RecordMetrics records pipeline execution metrics
	RecordMetrics(metrics ExecutionMetrics)

	// RecordError records an error that occurred during execution
	RecordError(err PipelineError)

	// HealthCheck performs a health check on the pipeline
	HealthCheck(ctx context.Context) HealthStatus
}

// DataSourceMetadata contains metadata about a data source
type DataSourceMetadata struct {
	Format      string
	Size        int64
	LastModified time.Time
	Encoding    string
}

// ProcessorCapabilities describes what a processor can do
type ProcessorCapabilities struct {
	SupportedFormats []string
	MaxDataSize      int64
	RequiresPreprocessing bool
	OutputFormats    []string
}

// ExecutionMetrics contains metrics about pipeline execution
type ExecutionMetrics struct {
	ExecutionID   string
	StartTime     time.Time
	EndTime       time.Time
	Duration      time.Duration
	ItemsProcessed int64
	Throughput    float64 // items per second
	MemoryUsage   int64
	ErrorCount    int
}

// PipelineError represents an error that occurred in the pipeline
type PipelineError struct {
	Code      string
	Message   string
	Timestamp time.Time
	Context   map[string]interface{}
}

// HealthStatus represents the health status of the pipeline
type HealthStatus struct {
	Status    string
	Timestamp time.Time
	Checks    []HealthCheck
}

// HealthCheck represents an individual health check
type HealthCheck struct {
	Name      string
	Status    string
	Message   string
	Timestamp time.Time
}

// Config holds configuration for the pipeline
type Config struct {
	Input         DataSourceConfig
	Output        DataSourceConfig
	Processing    ProcessingConfig
	Monitoring    *MonitoringConfig
}

// DataSourceConfig configures a data source
type DataSourceConfig struct {
	Type       string
	Connection map[string]interface{}
	Options    map[string]interface{}
}

// ProcessingConfig configures data processing
type ProcessingConfig struct {
	ChunkSize       int
	MaxConcurrency  int
	RetryAttempts   int
	Timeout         time.Duration
	BufferSize      int
}

// MonitoringConfig configures monitoring and metrics
type MonitoringConfig struct {
	MetricsEnabled      bool
	HealthCheckInterval time.Duration
	AlertThresholds     map[string]float64
}

// Pipeline is the main pipeline orchestrator
type Pipeline struct {
	config    Config
	source    DataSource
	processor DataProcessor
	monitor   PipelineMonitor
	metrics   ExecutionMetrics
	mu        sync.RWMutex
}

// New creates a new pipeline instance
func New(config Config, source DataSource, processor DataProcessor, monitor PipelineMonitor) (*Pipeline, error) {
	if err := validateConfig(config); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	return &Pipeline{
		config:    config,
		source:    source,
		processor: processor,
		monitor:   monitor,
		metrics: ExecutionMetrics{
			ExecutionID: generateExecutionID(),
		},
	}, nil
}

// Execute runs the complete data pipeline
func (p *Pipeline) Execute(ctx context.Context) (*ExecutionResult, error) {
	p.mu.Lock()
	p.metrics.StartTime = time.Now()
	p.mu.Unlock()

	result := &ExecutionResult{
		ExecutionID: p.metrics.ExecutionID,
		Success:     false,
		StartTime:   p.metrics.StartTime,
	}

	defer func() {
		p.mu.Lock()
		p.metrics.EndTime = time.Now()
		p.metrics.Duration = p.metrics.EndTime.Sub(p.metrics.StartTime)
		if p.metrics.Duration > 0 {
			p.metrics.Throughput = float64(p.metrics.ItemsProcessed) / p.metrics.Duration.Seconds()
		}
		p.mu.Unlock()

		if p.monitor != nil {
			p.monitor.RecordMetrics(p.metrics)
		}
	}()

	// Health check before execution
	if p.monitor != nil {
		health := p.monitor.HealthCheck(ctx)
		if health.Status != "healthy" {
			return nil, &PipelineError{
				Code:      "PIPELINE_UNHEALTHY",
				Message:   "pipeline is unhealthy",
				Timestamp: time.Now(),
			}
		}
	}

	// Read data from source
	data, err := p.source.ReadData(ctx)
	if err != nil {
		p.recordError("DATA_READ_ERROR", err)
		return nil, fmt.Errorf("failed to read data: %w", err)
	}

	// Process data in chunks
	processedChunks, err := p.processInChunks(ctx, data)
	if err != nil {
		p.recordError("PROCESSING_ERROR", err)
		return nil, fmt.Errorf("failed to process data: %w", err)
	}

	// Combine processed chunks
	resultData := p.combineChunks(processedChunks)
	result.ItemsProcessed = int64(len(processedChunks))

	// Write results to output
	if err := p.source.WriteData(ctx, resultData); err != nil {
		p.recordError("DATA_WRITE_ERROR", err)
		return nil, fmt.Errorf("failed to write data: %w", err)
	}

	result.Success = true
	result.EndTime = time.Now()
	result.Duration = result.EndTime.Sub(result.StartTime)

	return result, nil
}

// processInChunks processes data in concurrent chunks
func (p *Pipeline) processInChunks(ctx context.Context, data []byte) ([][]byte, error) {
	chunkSize := p.config.Processing.ChunkSize
	if chunkSize <= 0 {
		chunkSize = 1000 // default chunk size
	}

	// Split data into chunks
	var chunks [][]byte
	for i := 0; i < len(data); i += chunkSize {
		end := i + chunkSize
		if end > len(data) {
			end = len(data)
		}
		chunks = append(chunks, data[i:end])
	}

	// Process chunks concurrently
	type chunkResult struct {
		data []byte
		err  error
	}

	results := make(chan chunkResult, len(chunks))
	var wg sync.WaitGroup

	// Limit concurrency
	semaphore := make(chan struct{}, p.config.Processing.MaxConcurrency)

	for _, chunk := range chunks {
		wg.Add(1)
		go func(c []byte) {
			defer wg.Done()

			// Acquire semaphore
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			processed, err := p.processor.Process(ctx, c)
			results <- chunkResult{data: processed, err: err}
		}(chunk)
	}

	// Wait for all goroutines to complete
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results
	var processedChunks [][]byte
	var errors []error

	for result := range results {
		if result.err != nil {
			errors = append(errors, result.err)
			continue
		}
		processedChunks = append(processedChunks, result.data)
		p.mu.Lock()
		p.metrics.ItemsProcessed++
		p.mu.Unlock()
	}

	if len(errors) > 0 {
		return nil, fmt.Errorf("processing failed for %d chunks: %v", len(errors), errors[0])
	}

	return processedChunks, nil
}

// combineChunks combines processed chunks back together
func (p *Pipeline) combineChunks(chunks [][]byte) []byte {
	var result []byte
	for _, chunk := range chunks {
		result = append(result, chunk...)
		result = append(result, '\n')
	}
	return result
}

// recordError records an error in the metrics
func (p *Pipeline) recordError(code string, err error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	p.metrics.ErrorCount++

	if p.monitor != nil {
		p.monitor.RecordError(PipelineError{
			Code:      code,
			Message:   err.Error(),
			Timestamp: time.Now(),
		})
	}
}

// validateConfig validates the pipeline configuration
func validateConfig(config Config) error {
	if config.Processing.ChunkSize <= 0 {
		return fmt.Errorf("chunk size must be positive")
	}

	if config.Processing.MaxConcurrency < 1 {
		return fmt.Errorf("max concurrency must be at least 1")
	}

	if config.Processing.Timeout < 0 {
		return fmt.Errorf("timeout cannot be negative")
	}

	return nil
}

// generateExecutionID generates a unique execution ID
func generateExecutionID() string {
	return fmt.Sprintf("exec_%d_%d", time.Now().Unix(), time.Now().UnixNano()%1000000)
}

// ExecutionResult contains the result of pipeline execution
type ExecutionResult struct {
	ExecutionID     string
	Success         bool
	StartTime       time.Time
	EndTime         time.Time
	Duration        time.Duration
	ItemsProcessed  int64
	Errors          []string
}

// GetMetrics returns the current execution metrics
func (p *Pipeline) GetMetrics() ExecutionMetrics {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.metrics
}

// Factory functions for creating pipelines

// FilePipeline creates a pipeline that reads from and writes to files
func FilePipeline(inputPath, outputPath string, processor DataProcessor, monitor PipelineMonitor) (*Pipeline, error) {
	config := Config{
		Input: DataSourceConfig{
			Type: "file",
			Connection: map[string]interface{}{
				"path": inputPath,
			},
		},
		Output: DataSourceConfig{
			Type: "file",
			Connection: map[string]interface{}{
				"path": outputPath,
			},
		},
		Processing: ProcessingConfig{
			ChunkSize:      1000,
			MaxConcurrency: 4,
			RetryAttempts:  3,
			Timeout:        30 * time.Second,
			BufferSize:     100,
		},
		Monitoring: &MonitoringConfig{
			MetricsEnabled:      true,
			HealthCheckInterval: 1 * time.Minute,
			AlertThresholds: map[string]float64{
				"error_rate": 0.1,
				"latency":    5000.0,
			},
		},
	}

	source := NewFileDataSource(config.Input, config.Output)
	return New(config, source, processor, monitor)
}

// NetworkPipeline creates a pipeline that reads from HTTP and writes to files
func NetworkPipeline(inputURL, outputPath string, processor DataProcessor, monitor PipelineMonitor) (*Pipeline, error) {
	config := Config{
		Input: DataSourceConfig{
			Type: "http",
			Connection: map[string]interface{}{
				"url": inputURL,
			},
		},
		Output: DataSourceConfig{
			Type: "file",
			Connection: map[string]interface{}{
				"path": outputPath,
			},
		},
		Processing: ProcessingConfig{
			ChunkSize:      500,
			MaxConcurrency: 2,
			RetryAttempts:  5,
			Timeout:        60 * time.Second,
			BufferSize:     50,
		},
		Monitoring: &MonitoringConfig{
			MetricsEnabled:      true,
			HealthCheckInterval: 30 * time.Second,
			AlertThresholds: map[string]float64{
				"error_rate": 0.05,
				"latency":    10000.0,
			},
		},
	}

	source := NewHTTPDataSource(config.Input, config.Output)
	return New(config, source, processor, monitor)
}

// RunPipeline is a convenience function for running a pipeline
func RunPipeline(ctx context.Context, pipeline *Pipeline) *ExecutionResult {
	result, err := pipeline.Execute(ctx)
	if err != nil {
		// In a real application, you'd want better error handling here
		panic(fmt.Sprintf("pipeline execution failed: %v", err))
	}
	return result
}

// FileDataSource implements DataSource for file operations
type FileDataSource struct {
	inputConfig  DataSourceConfig
	outputConfig DataSourceConfig
}

// NewFileDataSource creates a new file data source
func NewFileDataSource(input, output DataSourceConfig) *FileDataSource {
	return &FileDataSource{
		inputConfig:  input,
		outputConfig: output,
	}
}

func (f *FileDataSource) ReadData(ctx context.Context) ([]byte, error) {
	path, ok := f.inputConfig.Connection["path"].(string)
	if !ok {
		return nil, fmt.Errorf("invalid path in input configuration")
	}

	// Implementation would read file
	return []byte("{}"), nil
}

func (f *FileDataSource) WriteData(ctx context.Context, data []byte) error {
	path, ok := f.outputConfig.Connection["path"].(string)
	if !ok {
		return fmt.Errorf("invalid path in output configuration")
	}

	// Implementation would write file
	return nil
}

func (f *FileDataSource) Metadata() DataSourceMetadata {
	// Implementation would get file metadata
	return DataSourceMetadata{
		Format:       "json",
		Size:         0,
		LastModified: time.Now(),
	}
}

// HTTPDataSource implements DataSource for HTTP operations
type HTTPDataSource struct {
	inputConfig  DataSourceConfig
	outputConfig DataSourceConfig
}

// NewHTTPDataSource creates a new HTTP data source
func NewHTTPDataSource(input, output DataSourceConfig) *HTTPDataSource {
	return &HTTPDataSource{
		inputConfig:  input,
		outputConfig: output,
	}
}

func (h *HTTPDataSource) ReadData(ctx context.Context) ([]byte, error) {
	url, ok := h.inputConfig.Connection["url"].(string)
	if !ok {
		return nil, fmt.Errorf("invalid URL in input configuration")
	}

	// Implementation would fetch from HTTP endpoint
	return []byte("{}"), nil
}

func (h *HTTPDataSource) WriteData(ctx context.Context, data []byte) error {
	path, ok := h.outputConfig.Connection["path"].(string)
	if !ok {
		return fmt.Errorf("invalid path in output configuration")
	}

	// Implementation would write file or HTTP endpoint
	return nil
}

func (h *HTTPDataSource) Metadata() DataSourceMetadata {
	// Implementation would get HTTP resource metadata
	return DataSourceMetadata{
		Format:       "json",
		Size:         0,
		LastModified: time.Now(),
	}
}"""

    def _get_go_peer_example(self) -> str:
        """Get Go peer review example."""
        return """// File: services/user_service.go
// [REVIEW] Peer Review Comments

package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/pkg/errors"
	"go.uber.org/zap"
)

// UserServiceConfig holds configuration for the user service
type UserServiceConfig struct {
	Database DatabaseConfig `json:"database"`
	Cache    CacheConfig    `json:"cache"`
	Features FeatureFlags   `json:"features"`
}

// DatabaseConfig configures database connection
type DatabaseConfig struct {
	URL      string        `json:"url"`
	Timeout  time.Duration `json:"timeout"`
	MaxConns int           `json:"max_connections"`
}

// CacheConfig configures cache settings
type CacheConfig struct {
	TTL     time.Duration `json:"ttl"`
	MaxSize int           `json:"max_size"`
}

// FeatureFlags control service behavior
type FeatureFlags struct {
	EnableLogging bool `json:"enable_logging"`
	EnableMetrics bool `json:"enable_metrics"`
	EnableTracing bool `json:"enable_tracing"`
}

// User represents a user in the system
type User struct {
	ID        int64                  `json:"id" db:"id"`
	Username  string                 `json:"username" db:"username"`
	Email     string                 `json:"email" db:"email"`
	CreatedAt time.Time              `json:"created_at" db:"created_at"`
	Preferences map[string]interface{} `json:"preferences" db:"preferences"`
}

// UserService handles user-related operations with comprehensive error handling
type UserService struct {
	db       *sql.DB
	cache    *redis.Client
	logger   *zap.Logger
	config   UserServiceConfig
	metrics  MetricsCollector

	// Guards against concurrent cache operations
	cacheMutex sync.RWMutex
}

// UserServiceError represents a service-specific error
type UserServiceError struct {
	Code       string                 `json:"code"`
	Message    string                 `json:"message"`
	StatusCode int                    `json:"status_code"`
	Cause      error                  `json:"cause,omitempty"`
	Context    map[string]interface{} `json:"context,omitempty"`
}

func (e *UserServiceError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Cause)
	}
	return e.Message
}

func (e *UserServiceError) Unwrap() error {
	return e.Cause
}

// NewUserServiceError creates a new UserServiceError
func NewUserServiceError(code, message string, statusCode int, cause error) *UserServiceError {
	return &UserServiceError{
		Code:       code,
		Message:    message,
		StatusCode: statusCode,
		Cause:      cause,
	}
}

// UserNotFoundError indicates a user was not found
type UserNotFoundError struct {
	UserID int64
}

func (e *UserNotFoundError) Error() string {
	return fmt.Sprintf("user with ID %d not found", e.UserID)
}

// IsUserNotFoundError checks if an error is a UserNotFoundError
func IsUserNotFoundError(err error) bool {
	_, ok := err.(*UserNotFoundError)
	return ok
}

// New creates a new UserService instance
func New(db *sql.DB, cache *redis.Client, logger *zap.Logger, config UserServiceConfig) (*UserService, error) {
	if db == nil {
		return nil, NewUserServiceError("INVALID_DB", "database connection cannot be nil", http.StatusInternalServerError, nil)
	}

	if logger == nil {
		return nil, NewUserServiceError("INVALID_LOGGER", "logger cannot be nil", http.StatusInternalServerError, nil)
	}

	service := &UserService{
		db:      db,
		cache:   cache,
		logger:  logger,
		config:  config,
		metrics: NewMetricsCollector(config.Features.EnableMetrics),
	}

	// Initialize cache if configured
	if cache != nil {
		if err := service.initializeCache(); err != nil {
			logger.Warn("Failed to initialize cache", zap.Error(err))
		}
	}

	return service, nil
}

// GetUserByID retrieves a user by ID with caching and comprehensive error handling
func (s *UserService) GetUserByID(ctx context.Context, userID int64) (*User, error) {
	start := time.Now()
	s.metrics.IncrementRequests()

	if userID <= 0 {
		s.metrics.IncrementErrors()
		return nil, NewUserServiceError(
			"INVALID_USER_ID",
			"user ID must be positive",
			http.StatusBadRequest,
			nil,
		)
	}

	// Check cache first if available
	if s.cache != nil {
		if cachedUser, err := s.getCachedUser(ctx, userID); err == nil && cachedUser != nil {
			s.metrics.IncrementCacheHits()
			s.logger.Info("Cache hit",
				zap.Int64("user_id", userID),
				zap.Duration("duration", time.Since(start)),
			)
			return cachedUser, nil
		}
	}

	// Fetch from database
	user, err := s.fetchUserFromDB(ctx, userID)
	if err != nil {
		s.metrics.IncrementErrors()
		s.logger.Error("Failed to fetch user from database",
			zap.Int64("user_id", userID),
			zap.Error(err),
			zap.Duration("duration", time.Since(start)),
		)

		// Return specific error types for better error handling
		if errors.Is(err, sql.ErrNoRows) {
			return nil, &UserNotFoundError{UserID: userID}
		}

		return nil, NewUserServiceError(
			"USER_FETCH_FAILED",
			"failed to retrieve user",
			http.StatusInternalServerError,
			err,
		)
	}

	// Cache the result if caching is enabled
	if s.cache != nil {
		if err := s.setCachedUser(ctx, userID, user); err != nil {
			s.logger.Warn("Failed to cache user",
				zap.Int64("user_id", userID),
				zap.Error(err),
			)
		}
	}

	s.logger.Info("User retrieved successfully",
		zap.Int64("user_id", userID),
		zap.Duration("duration", time.Since(start)),
	)

	return user, nil
}

// UpdateUser updates user information with validation and cache invalidation
func (s *UserService) UpdateUser(ctx context.Context, userID int64, updates UserUpdate) (*User, error) {
	start := time.Now()
	s.metrics.IncrementRequests()

	if userID <= 0 {
		s.metrics.IncrementErrors()
		return nil, NewUserServiceError(
			"INVALID_USER_ID",
			"user ID must be positive",
			http.StatusBadRequest,
			nil,
		)
	}

	// Validate updates
	if err := s.validateUserUpdates(updates); err != nil {
		s.metrics.IncrementErrors()
		return nil, err
	}

	// Update in database
	user, err := s.updateUserInDB(ctx, userID, updates)
	if err != nil {
		s.metrics.IncrementErrors()
		s.logger.Error("Failed to update user in database",
			zap.Int64("user_id", userID),
			zap.Error(err),
			zap.Duration("duration", time.Since(start)),
		)

		return nil, NewUserServiceError(
			"USER_UPDATE_FAILED",
			"failed to update user",
			http.StatusInternalServerError,
			err,
		)
	}

	// Invalidate cache for this user
	if s.cache != nil {
		s.invalidateCachedUser(ctx, userID)
	}

	s.logger.Info("User updated successfully",
		zap.Int64("user_id", userID),
		zap.Duration("duration", time.Since(start)),
	)

	return user, nil
}

// GetHealthStatus returns the current health status of the service
func (s *UserService) GetHealthStatus() ServiceHealth {
	return ServiceHealth{
		Status:    s.determineHealthStatus(),
		Timestamp: time.Now(),
		Metrics:   s.metrics.GetCurrentMetrics(),
		Checks: []HealthCheck{
			{
				Name:      "database",
				Status:    s.checkDatabaseConnection(),
				Timestamp: time.Now(),
			},
			{
				Name:      "cache",
				Status:    s.checkCacheConnection(),
				Timestamp: time.Now(),
			},
		},
	}
}

// Private methods

func (s *UserService) initializeCache() error {
	ctx := context.Background()

	// Test cache connection
	if _, err := s.cache.Ping(ctx).Result(); err != nil {
		return NewUserServiceError(
			"CACHE_CONNECTION_FAILED",
			"failed to connect to cache",
			http.StatusInternalServerError,
			err,
		)
	}

	s.logger.Info("Cache initialized successfully")
	return nil
}

func (s *UserService) getCachedUser(ctx context.Context, userID int64) (*User, error) {
	s.cacheMutex.RLock()
	defer s.cacheMutex.RUnlock()

	key := fmt.Sprintf("user:%d", userID)
	val, err := s.cache.Get(ctx, key).Result()
	if err != nil {
		if errors.Is(err, redis.Nil) {
			return nil, nil // Cache miss
		}
		return nil, err
	}

	var user User
	if err := json.Unmarshal([]byte(val), &user); err != nil {
		return nil, err
	}

	return &user, nil
}

func (s *UserService) setCachedUser(ctx context.Context, userID int64, user *User) error {
	s.cacheMutex.Lock()
	defer s.cacheMutex.Unlock()

	key := fmt.Sprintf("user:%d", userID)
	data, err := json.Marshal(user)
	if err != nil {
		return err
	}

	ttl := s.config.Cache.TTL
	if ttl == 0 {
		ttl = 5 * time.Minute // default TTL
	}

	return s.cache.Set(ctx, key, data, ttl).Err()
}

func (s *UserService) invalidateCachedUser(ctx context.Context, userID int64) {
	s.cacheMutex.Lock()
	defer s.cacheMutex.Unlock()

	key := fmt.Sprintf("user:%d", userID)
	if err := s.cache.Del(ctx, key).Err(); err != nil {
		s.logger.Warn("Failed to invalidate cached user",
			zap.Int64("user_id", userID),
			zap.Error(err),
		)
	}
}

func (s *UserService) fetchUserFromDB(ctx context.Context, userID int64) (*User, error) {
	query := `SELECT id, username, email, created_at, preferences FROM users WHERE id = $1`

	user := &User{}
	var preferencesJSON sql.NullString

	err := s.db.QueryRowContext(ctx, query, userID).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.CreatedAt,
		&preferencesJSON,
	)
	if err != nil {
		return nil, err
	}

	// Parse preferences JSON if present
	if preferencesJSON.Valid {
		if err := json.Unmarshal([]byte(preferencesJSON.String), &user.Preferences); err != nil {
			s.logger.Warn("Failed to parse user preferences",
				zap.Int64("user_id", userID),
				zap.Error(err),
			)
		}
	}

	return user, nil
}

func (s *UserService) updateUserInDB(ctx context.Context, userID int64, updates UserUpdate) (*User, error) {
	// Implementation would update user in database
	// This is a simplified example
	return &User{
		ID:        userID,
		Username:  updates.Username,
		Email:     updates.Email,
		CreatedAt: time.Now(),
	}, nil
}

func (s *UserService) validateUserUpdates(updates UserUpdate) error {
	if updates.Username != "" && len(updates.Username) < 3 {
		return NewUserServiceError(
			"INVALID_USERNAME",
			"username must be at least 3 characters long",
			http.StatusBadRequest,
			nil,
		)
	}

	if updates.Email != "" && !isValidEmail(updates.Email) {
		return NewUserServiceError(
			"INVALID_EMAIL",
			"invalid email format",
			http.StatusBadRequest,
			nil,
		)
	}

	return nil
}

func (s *UserService) determineHealthStatus() string {
	metrics := s.metrics.GetCurrentMetrics()

	if metrics.ErrorRate > 0.1 {
		return "degraded"
	}

	if metrics.ErrorRate > 0.05 {
		return "warning"
	}

	return "healthy"
}

func (s *UserService) checkDatabaseConnection() string {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := s.db.PingContext(ctx); err != nil {
		return "unhealthy"
	}

	return "healthy"
}

func (s *UserService) checkCacheConnection() string {
	if s.cache == nil {
		return "not_configured"
	}

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	if _, err := s.cache.Ping(ctx).Result(); err != nil {
		return "unhealthy"
	}

	return "healthy"
}

func isValidEmail(email string) bool {
	// Simple email validation - in production, use a proper validation library
	return len(email) > 5 && contains(email, "@") && contains(email, ".")
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && s[len(s)-len(substr):] != substr &&
		   (len(s) == len(substr) && s == substr ||
		    contains(s[:len(s)-1], substr))
}

// Supporting types

type UserUpdate struct {
	Username string `json:"username"`
	Email    string `json:"email"`
}

type ServiceHealth struct {
	Status    string                 `json:"status"`
	Timestamp time.Time              `json:"timestamp"`
	Metrics   map[string]interface{} `json:"metrics"`
	Checks    []HealthCheck          `json:"checks"`
}

type HealthCheck struct {
	Name      string    `json:"name"`
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
}

type MetricsCollector interface {
	IncrementRequests()
	IncrementErrors()
	IncrementCacheHits()
	GetCurrentMetrics() map[string]interface{}
}

type DefaultMetricsCollector struct {
	mu           sync.RWMutex
	requests     int64
	errors       int64
	cacheHits    int64
	startTime    time.Time
}

func NewMetricsCollector(enabled bool) MetricsCollector {
	if !enabled {
		return &NoOpMetricsCollector{}
	}

	return &DefaultMetricsCollector{
		startTime: time.Now(),
	}
}

func (m *DefaultMetricsCollector) IncrementRequests() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.requests++
}

func (m *DefaultMetricsCollector) IncrementErrors() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.errors++
}

func (m *DefaultMetricsCollector) IncrementCacheHits() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.cacheHits++
}

func (m *DefaultMetricsCollector) GetCurrentMetrics() map[string]interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()

	uptime := time.Since(m.startTime)
	errorRate := float64(0)
	if m.requests > 0 {
		errorRate = float64(m.errors) / float64(m.requests)
	}

	return map[string]interface{}{
		"requests":     m.requests,
		"errors":       m.errors,
		"cache_hits":   m.cacheHits,
		"error_rate":   errorRate,
		"uptime":       uptime.String(),
	}
}

type NoOpMetricsCollector struct{}

func (m *NoOpMetricsCollector) IncrementRequests()     {}
func (m *NoOpMetricsCollector) IncrementErrors()       {}
func (m *NoOpMetricsCollector) IncrementCacheHits()    {}
func (m *NoOpMetricsCollector) GetCurrentMetrics() map[string]interface{} {
	return map[string]interface{}{}
}

// Peer Review Comments:
// =====================

/**
 * PEER REVIEW: UserService Implementation
 *
 * REVIEWER: Senior Go Developer
 * DATE: 2024-01-15
 * OVERALL SCORE: 9.2/10
 */

// ✅ EXCELLENT:
// - Comprehensive error handling with custom error types
// - Proper use of interfaces for testability and abstraction
// - Good separation of concerns and single responsibility
// - Excellent use of context for cancellation and timeouts
// - Proper caching strategy with mutex protection
// - Health check functionality for monitoring
// - Structured logging with zap
// - Input validation with meaningful error messages
// - Metrics collection for observability
// - Clean, idiomatic Go code following best practices

// ⚠️  NEEDS IMPROVEMENT:
// 1. Some private methods could have better documentation
// 2. Cache implementation could use Redis more efficiently
// 3. Consider using sqlx or similar for better database operations
// 4. Some magic numbers should be constants

// 🔧 SUGGESTED CHANGES:
// - Add constants for default values (TTL, timeouts, etc.)
// - Consider using a more sophisticated caching strategy
// - Add integration tests with real database/cache
// - Implement proper database transaction handling
// - Add request tracing with OpenTelemetry
// - Consider using a dependency injection container

// 📝 GENERAL ADVICE:
// - Consider extracting interfaces to separate files
// - Add API versioning strategy for future compatibility
// - Implement proper database connection pooling
// - Add structured configuration with validation
// - Consider using Go 1.18+ features like generics where appropriate

// 🔒 SECURITY CONSIDERATIONS:
// - Validate and sanitize all user inputs
// - Implement proper authentication and authorization
// - Use parameterized queries to prevent SQL injection
// - Implement rate limiting to prevent abuse
// - Log security events for audit trails

/**
 * APPROVAL STATUS: ✅ APPROVED WITH MINOR REVISIONS
 *
 * Required actions before merge:
// - [ ] Add constants for magic numbers and default values
// - [ ] Add input sanitization for user data
// - [ ] Implement proper database transaction handling
 * - [ ] Add structured configuration validation
 */"""

    def _get_go_sdet_example(self) -> str:
        """Get Go SDET example."""
        return """// File: services/user_service_test.go
// [NEW] or [MODIFIED]

// Package services provides comprehensive tests for the user service
package services

import (
	"context"
	"database/sql"
	"testing"
	"time"

	"github.com/go-redis/redismock/v8"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
	"go.uber.org/zap/zaptest"
)

// MockDB is a mock implementation of sql.DB for testing
type MockDB struct {
	mock.Mock
}

func (m *MockDB) QueryRowContext(ctx context.Context, query string, args ...interface{}) *sql.Row {
	call := m.Called(ctx, query, args)
	return call.Get(0).(*sql.Row)
}

func (m *MockDB) PingContext(ctx context.Context) error {
	call := m.Called(ctx)
	return call.Error(0)
}

// TestUserServiceSuite is a comprehensive test suite for UserService
type TestUserServiceSuite struct {
	suite.Suite
	service *UserService
	mockDB  *MockDB
	cache   redismock.ClientMock
	logger  *zap.Logger
	config  UserServiceConfig
}

// SetupTest runs before each test
func (suite *TestUserServiceSuite) SetupTest() {
	suite.mockDB = new(MockDB)
	suite.cache = redismock.NewMock()
	suite.logger = zaptest.NewLogger(suite.T())

	suite.config = UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test://localhost",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Cache: CacheConfig{
			TTL:     5 * time.Minute,
			MaxSize: 100,
		},
		Features: FeatureFlags{
			EnableLogging: true,
			EnableMetrics: true,
			EnableTracing: false,
		},
	}

	service, err := New(suite.mockDB, suite.cache.Client, suite.logger, suite.config)
	require.NoError(suite.T(), err)
	suite.service = service
}

// TearDownTest runs after each test
func (suite *TestUserServiceSuite) TearDownTest() {
	suite.cache.Clear()
}

// TestGetUserByID tests the GetUserByID method
func (suite *TestUserServiceSuite) TestGetUserByID() {
	ctx := context.Background()
	userID := int64(123)

	expectedUser := &User{
		ID:       userID,
		Username: "testuser",
		Email:    "test@example.com",
		CreatedAt: time.Now(),
	}

	// Setup database mock expectations
	suite.mockDB.On("QueryRowContext", ctx, "SELECT id, username, email, created_at, preferences FROM users WHERE id = $1", userID).
		Return(sql.RowFromContext(ctx, []interface{}{expectedUser.ID, expectedUser.Username, expectedUser.Email, expectedUser.CreatedAt, nil}))

	// Test successful user retrieval
	user, err := suite.service.GetUserByID(ctx, userID)
	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), expectedUser.ID, user.ID)
	assert.Equal(suite.T(), expectedUser.Username, user.Username)
	assert.Equal(suite.T(), expectedUser.Email, user.Email)

	suite.mockDB.AssertExpectations(suite.T())
}

// TestGetUserByIDWithCache tests caching functionality
func (suite *TestUserServiceSuite) TestGetUserByIDWithCache() {
	ctx := context.Background()
	userID := int64(456)

	expectedUser := &User{
		ID:       userID,
		Username: "cacheduser",
		Email:    "cached@example.com",
		CreatedAt: time.Now(),
	}

	// Setup cache expectations for cache hit
	userJSON, _ := json.Marshal(expectedUser)
	suite.cache.ExpectGet(fmt.Sprintf("user:%d", userID)).SetVal(string(userJSON))

	// Test cache hit
	user, err := suite.service.GetUserByID(ctx, userID)
	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), expectedUser.ID, user.ID)

	// Verify database was not called (cache hit)
	suite.mockDB.AssertNotCalled(suite.T(), "QueryRowContext")
}

// TestGetUserByIDNotFound tests user not found scenario
func (suite *TestUserServiceSuite) TestGetUserByIDNotFound() {
	ctx := context.Background()
	userID := int64(999)

	// Setup database mock to return no rows
	suite.mockDB.On("QueryRowContext", ctx, "SELECT id, username, email, created_at, preferences FROM users WHERE id = $1", userID).
		Return(sql.RowFromContext(ctx, nil))

	// Test user not found
	user, err := suite.service.GetUserByID(ctx, userID)
	assert.Nil(suite.T(), user)
	assert.True(suite.T(), IsUserNotFoundError(err))

	var notFoundErr *UserNotFoundError
	assert.ErrorAs(suite.T(), err, &notFoundErr)
	assert.Equal(suite.T(), userID, notFoundErr.UserID)

	suite.mockDB.AssertExpectations(suite.T())
}

// TestGetUserByIDInvalidID tests invalid user ID validation
func (suite *TestUserServiceSuite) TestGetUserByIDInvalidID() {
	ctx := context.Background()

	testCases := []struct {
		name   string
		userID int64
	}{
		{"zero ID", 0},
		{"negative ID", -1},
		{"very large negative ID", -999999},
	}

	for _, tc := range testCases {
		suite.Run(tc.name, func() {
			user, err := suite.service.GetUserByID(ctx, tc.userID)
			assert.Nil(suite.T(), user)
			assert.Error(suite.T(), err)

			var serviceErr *UserServiceError
			assert.ErrorAs(suite.T(), err, &serviceErr)
			assert.Equal(suite.T(), "INVALID_USER_ID", serviceErr.Code)
			assert.Equal(suite.T(), http.StatusBadRequest, serviceErr.StatusCode)
		})
	}
}

// TestUpdateUser tests the UpdateUser method
func (suite *TestUserServiceSuite) TestUpdateUser() {
	ctx := context.Background()
	userID := int64(123)

	updates := UserUpdate{
		Username: "newusername",
		Email:    "newemail@example.com",
	}

	// Setup cache expectations for cache invalidation
	suite.cache.ExpectDel(fmt.Sprintf("user:%d", userID)).SetVal(1)

	// Test successful update
	user, err := suite.service.UpdateUser(ctx, userID, updates)
	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), userID, user.ID)
	assert.Equal(suite.T(), updates.Username, user.Username)
	assert.Equal(suite.T(), updates.Email, user.Email)

	suite.cache.AssertExpectations(suite.T())
}

// TestUpdateUserValidation tests input validation for UpdateUser
func (suite *TestUserServiceSuite) TestUpdateUserValidation() {
	ctx := context.Background()
	userID := int64(123)

	testCases := []struct {
		name    string
		updates UserUpdate
		wantErr string
	}{
		{
			name: "username too short",
			updates: UserUpdate{
				Username: "ab",
				Email:    "valid@example.com",
			},
			wantErr: "INVALID_USERNAME",
		},
		{
			name: "invalid email format",
			updates: UserUpdate{
				Username: "validusername",
				Email:    "invalid-email",
			},
			wantErr: "INVALID_EMAIL",
		},
	}

	for _, tc := range testCases {
		suite.Run(tc.name, func() {
			user, err := suite.service.UpdateUser(ctx, userID, tc.updates)
			assert.Nil(suite.T(), user)
			assert.Error(suite.T(), err)

			var serviceErr *UserServiceError
			assert.ErrorAs(suite.T(), err, &serviceErr)
			assert.Equal(suite.T(), tc.wantErr, serviceErr.Code)
		})
	}
}

// TestGetHealthStatus tests the health check functionality
func (suite *TestUserServiceSuite) TestGetHealthStatus() {
	// Setup database mock for health check
	suite.mockDB.On("PingContext", mock.AnythingOfType("*context.timerCtx")).
		Return(nil)

	health := suite.service.GetHealthStatus()
	assert.Equal(suite.T(), "healthy", health.Status)
	assert.NotZero(suite.T(), health.Timestamp)
	assert.NotEmpty(suite.T(), health.Checks)
	assert.Len(suite.T(), health.Checks, 2)

	// Check database health check
	dbCheck := findHealthCheck(health.Checks, "database")
	assert.NotNil(suite.T(), dbCheck)
	assert.Equal(suite.T(), "healthy", dbCheck.Status)

	// Check cache health check
	cacheCheck := findHealthCheck(health.Checks, "cache")
	assert.NotNil(suite.T(), cacheCheck)
	assert.Equal(suite.T(), "healthy", cacheCheck.Status)

	suite.mockDB.AssertExpectations(suite.T())
}

// BenchmarkGetUserByID benchmarks the GetUserByID method
func BenchmarkGetUserByID(b *testing.B) {
	// Setup test environment
	db, mock, err := sqlmock.New()
	require.NoError(b, err)
	defer db.Close()

	cache, _ := redismock.NewMock()
	logger := zaptest.NewLogger(b)

	config := UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test://localhost",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Cache: CacheConfig{
			TTL:     5 * time.Minute,
			MaxSize: 100,
		},
		Features: FeatureFlags{
			EnableLogging: false,
			EnableMetrics: false,
			EnableTracing: false,
		},
	}

	service, err := New(db, cache.Client, logger, config)
	require.NoError(b, err)

	ctx := context.Background()
	userID := int64(123)

	// Setup mock expectations
	rows := sqlmock.NewRows([]string{"id", "username", "email", "created_at", "preferences"}).
		AddRow(userID, "testuser", "test@example.com", time.Now(), nil)

	mock.ExpectQuery("SELECT id, username, email, created_at, preferences FROM users WHERE id = \\$1").
		WithArgs(userID).
		WillReturnRows(rows)

	b.ResetTimer()

	// Run benchmark
	for i := 0; i < b.N; i++ {
		_, err := service.GetUserByID(ctx, userID)
		if err != nil {
			b.Fatal(err)
		}
	}
}

// BenchmarkGetUserByIDWithCache benchmarks cached user retrieval
func BenchmarkGetUserByIDWithCache(b *testing.B) {
	// Setup test environment
	db, _, err := sqlmock.New()
	require.NoError(b, err)
	defer db.Close()

	cache, cacheMock := redismock.NewMock()
	logger := zaptest.NewLogger(b)

	config := UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test://localhost",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Cache: CacheConfig{
			TTL:     5 * time.Minute,
			MaxSize: 100,
		},
		Features: FeatureFlags{
			EnableLogging: false,
			EnableMetrics: false,
			EnableTracing: false,
		},
	}

	service, err := New(db, cache.Client, logger, config)
	require.NoError(b, err)

	ctx := context.Background()
	userID := int64(123)

	expectedUser := &User{
		ID:       userID,
		Username: "cacheduser",
		Email:    "cached@example.com",
		CreatedAt: time.Now(),
	}

	// Setup cache expectations for cache hit
	userJSON, _ := json.Marshal(expectedUser)
	cacheMock.ExpectGet(fmt.Sprintf("user:%d", userID)).SetVal(string(userJSON))

	b.ResetTimer()

	// Run benchmark
	for i := 0; i < b.N; i++ {
		_, err := service.GetUserByID(ctx, userID)
		if err != nil {
			b.Fatal(err)
		}
	}
}

// Table-driven tests for comprehensive coverage

func TestUserServiceValidation(t *testing.T) {
	testCases := []struct {
		name        string
		userID      int64
		expectError bool
		errorCode   string
	}{
		{"valid ID", 1, false, ""},
		{"zero ID", 0, true, "INVALID_USER_ID"},
		{"negative ID", -1, true, "INVALID_USER_ID"},
		{"large valid ID", 9223372036854775807, false, ""},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Setup test environment similar to suite tests
			db, mock, err := sqlmock.New()
			require.NoError(t, err)
			defer db.Close()

			cache, _ := redismock.NewMock()
			logger := zaptest.NewLogger(t)

			config := UserServiceConfig{
				Database: DatabaseConfig{
					URL:      "test://localhost",
					Timeout:  5 * time.Second,
					MaxConns: 10,
				},
				Features: FeatureFlags{
					EnableLogging: false,
					EnableMetrics: false,
					EnableTracing: false,
				},
			}

			service, err := New(db, cache.Client, logger, config)
			require.NoError(t, err)

			ctx := context.Background()
			user, err := service.GetUserByID(ctx, tc.userID)

			if tc.expectError {
				assert.Error(t, err)
				if tc.errorCode != "" {
					var serviceErr *UserServiceError
					assert.ErrorAs(t, err, &serviceErr)
					assert.Equal(t, tc.errorCode, serviceErr.Code)
				}
				assert.Nil(t, user)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, user)
			}
		})
	}
}

// Integration test example (requires actual database)
func TestUserServiceIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	// Setup real database connection
	db, err := sql.Open("postgres", "test-connection-string")
	require.NoError(t, err)
	defer db.Close()

	// Setup real Redis connection
	cache := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})
	defer cache.Close()

	logger := zaptest.NewLogger(t)

	config := UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test-connection-string",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Cache: CacheConfig{
			TTL:     5 * time.Minute,
			MaxSize: 100,
		},
		Features: FeatureFlags{
			EnableLogging: true,
			EnableMetrics: true,
			EnableTracing: false,
		},
	}

	service, err := New(db, cache, logger, config)
	require.NoError(t, err)

	ctx := context.Background()

	// Test complete user lifecycle
	t.Run("Complete User Lifecycle", func(t *testing.T) {
		// This would test the complete flow with real database operations
		// Including user creation, retrieval, update, and deletion
		t.Skip("Integration test implementation would go here")
	})
}

// Test helper functions

func findHealthCheck(checks []HealthCheck, name string) *HealthCheck {
	for _, check := range checks {
		if check.Name == name {
			return &check
		}
	}
	return nil
}

// Example tests for documentation

func ExampleUserService_GetUserByID() {
	// Setup test environment
	db, mock, _ := sqlmock.New()
	defer db.Close()

	cache, _ := redismock.NewMock()
	logger := zap.NewNop()

	config := UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test://localhost",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Features: FeatureFlags{
			EnableLogging: false,
			EnableMetrics: false,
			EnableTracing: false,
		},
	}

	service, _ := New(db, cache.Client, logger, config)

	ctx := context.Background()
	userID := int64(123)

	// Setup mock expectations
	rows := sqlmock.NewRows([]string{"id", "username", "email", "created_at", "preferences"}).
		AddRow(userID, "exampleuser", "user@example.com", time.Now(), nil)

	mock.ExpectQuery("SELECT id, username, email, created_at, preferences FROM users WHERE id = \\$1").
		WithArgs(userID).
		WillReturnRows(rows)

	// Example usage
	user, err := service.GetUserByID(ctx, userID)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Retrieved user: %s (%s)\n", user.Username, user.Email)

	// Output: Retrieved user: exampleuser (user@example.com)
}

// Test configuration and utilities

// TestMain sets up global test configuration
func TestMain(m *testing.M) {
	// Setup test database
	setupTestDatabase()

	// Setup test cache
	setupTestCache()

	// Run tests
	code := m.Run()

	// Cleanup
	cleanupTestResources()

	os.Exit(code)
}

func setupTestDatabase() {
	// Implementation would setup test database
}

func setupTestCache() {
	// Implementation would setup test cache
}

func cleanupTestResources() {
	// Implementation would cleanup test resources
}

// Performance test utilities

func TestUserServiceLoad(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	// Setup test environment
	db, mock, err := sqlmock.New()
	require.NoError(t, err)
	defer db.Close()

	cache, _ := redismock.NewMock()
	logger := zaptest.NewLogger(t)

	config := UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test://localhost",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Features: FeatureFlags{
			EnableLogging: false,
			EnableMetrics: false,
			EnableTracing: false,
		},
	}

	service, err := New(db, cache.Client, logger, config)
	require.NoError(t, err)

	ctx := context.Background()

	// Setup mock for multiple calls
	rows := sqlmock.NewRows([]string{"id", "username", "email", "created_at", "preferences"}).
		AddRow(1, "user1", "user1@example.com", time.Now(), nil)

	mock.ExpectQuery("SELECT id, username, email, created_at, preferences FROM users WHERE id = \\$1").
		Maybe().
		WillReturnRows(rows)

	// Test concurrent access
	const numGoroutines = 100
	const requestsPerGoroutine = 10

	results := make(chan error, numGoroutines*requestsPerGoroutine)

	// Start multiple goroutines making concurrent requests
	for i := 0; i < numGoroutines; i++ {
		go func(routineID int) {
			for j := 0; j < requestsPerGoroutine; j++ {
				userID := int64(routineID*requestsPerGoroutine + j + 1)

				// Update mock expectations for each request
				mock.ExpectQuery("SELECT id, username, email, created_at, preferences FROM users WHERE id = \\$1").
					WithArgs(userID).
					WillReturnRows(rows)

				_, err := service.GetUserByID(ctx, userID)
				results <- err
			}
		}(i)
	}

	// Collect results
	errorCount := 0
	for i := 0; i < numGoroutines*requestsPerGoroutine; i++ {
		err := <-results
		if err != nil {
			errorCount++
		}
	}

	assert.Equal(t, 0, errorCount, "Expected no errors in load test")
}

// Test coverage requirements
func TestCoverageRequirements(t *testing.T) {
	// This test ensures we maintain good test coverage
	// In a real project, you might use a coverage tool to verify this

	testFiles := []string{
		"user_service_test.go",
		"user_service_integration_test.go",
		"user_service_benchmark_test.go",
	}

	for _, file := range testFiles {
		assert.FileExists(t, file, "Test file %s should exist", file)
	}
}

// Test utilities for common operations

// CreateTestUser creates a test user with default values
func CreateTestUser(id int64) *User {
	return &User{
		ID:       id,
		Username: fmt.Sprintf("testuser%d", id),
		Email:    fmt.Sprintf("testuser%d@example.com", id),
		CreatedAt: time.Now(),
	}
}

// SetupTestService creates a test service with mocked dependencies
func SetupTestService(t *testing.T) (*UserService, *MockDB, redismock.ClientMock) {
	mockDB := new(MockDB)
	cache, cacheMock := redismock.NewMock()
	logger := zaptest.NewLogger(t)

	config := UserServiceConfig{
		Database: DatabaseConfig{
			URL:      "test://localhost",
			Timeout:  5 * time.Second,
			MaxConns: 10,
		},
		Features: FeatureFlags{
			EnableLogging: false,
			EnableMetrics: false,
			EnableTracing: false,
		},
	}

	service, err := New(mockDB, cache.Client, logger, config)
	require.NoError(t, err)

	return service, mockDB, cacheMock
}

// AssertUserEquals compares two users for equality
func AssertUserEquals(t *testing.T, expected, actual *User) {
	assert.Equal(t, expected.ID, actual.ID)
	assert.Equal(t, expected.Username, actual.Username)
	assert.Equal(t, expected.Email, actual.Email)
	assert.True(t, expected.CreatedAt.Sub(actual.CreatedAt) < time.Second)
}

// Required imports for the test file
import (
	"context"
	"fmt"
	"net/http"
	"os"
	"testing"
	"time"

	"database/sql"
	"encoding/json"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/go-redis/redis/v8"
	"github.com/go-redis/redismock/v8"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
	"go.uber.org/zap"
	"go.uber.org/zap/zaptest"
)"""