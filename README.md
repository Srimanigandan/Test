# Automotive Embedded Build System with GitHub Copilot + MCP

This project demonstrates a complete **automotive embedded build system** using Gradle with custom processes, integrated with **GitHub Copilot** and **Model Context Protocol (MCP)** for intelligent build assistance.

## 🚗 Project Overview

### Build System Features
- **Header Generation**: Automatically generates `config.h` and `version.h` from templates
- **C Compilation**: Compiles C source files with automotive-specific flags (MISRA-C compliance)
- **Static Analysis**: Performs automotive compliance checks and generates reports
- **Interdependent Processes**: Each process depends on the previous one and logs detailed information

### AI Integration Features
- **GitHub Copilot + MCP**: Intelligent build assistance powered by learned patterns
- **Real-time Learning**: Continuously learns from build processes and user interactions
- **Pattern Recognition**: Identifies common errors and suggests solutions
- **Predictive Analysis**: Predicts potential build issues before they occur

## 📁 Project Structure

```
automotive-embedded-build/
├── build.gradle                    # Main Gradle build configuration
├── src/
│   ├── main/
│   │   ├── c/                      # C source files
│   │   │   ├── main.c              # Main automotive application
│   │   │   └── utils.c             # Utility functions
│   │   └── templates/              # Header templates
│   │       ├── config.h.template   # Configuration header template
│   │       └── version.h.template  # Version header template
├── mcp/                            # MCP server implementation
│   ├── gradle_mcp_server.py       # Main MCP server for Gradle
│   ├── learning_engine.py         # AI learning engine
│   └── models/                     # Learned patterns storage
├── .vscode/
│   └── mcp.json                    # MCP configuration for VS Code
├── logs/                           # Build process logs
├── reports/                        # Static analysis reports
├── setup.py                       # Project setup script
└── README.md                       # This file
```

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or create the project
git clone <repository-url>
cd automotive-embedded-build

# Run the setup script
python setup.py

# Or manual setup:
chmod +x gradlew
pip install scikit-learn numpy mcp asyncio
```

### 2. Run the Build System

```bash
# Run complete automotive build
./gradlew automotiveBuild

# Or run individual tasks
./gradlew generateHeaders
./gradlew compileC  
./gradlew staticAnalysis
```

### 3. Start MCP Server

```bash
# Start the MCP server for GitHub Copilot integration
python mcp/gradle_mcp_server.py
```

### 4. Configure VS Code + GitHub Copilot

1. Open the project in VS Code
2. Install GitHub Copilot extension
3. The MCP configuration is already set up in `.vscode/mcp.json`
4. Open GitHub Copilot Chat and ask build-related questions!

## 🔧 Build Processes Explained

### 1. Header Generation (`generateHeaders`)

**What it does:**
- Generates `config.h` from template with build configuration
- Generates `version.h` with version information  
- Applies automotive-specific settings

**Input:** Template files in `src/main/templates/`
**Output:** Generated headers in `build/generated/headers/`
**Logs:** Process details to `logs/build-process.json`

**Example generated config.h:**
```c
#define BUILD_NUMBER "1.0"
#define AUTOMOTIVE_COMPLIANCE_LEVEL 2
#define CAN_BUS_ENABLED 1
#define MISRA_C_ENABLED 1
```

### 2. C Compilation (`compileC`)

**What it does:**
- Compiles C source files with automotive flags
- Uses generated headers from previous step
- Applies MISRA-C compliance settings

**Automotive-specific flags:**
```bash
gcc -c -std=c99 -Wall -Wextra -Werror -DAUTOMOTIVE_BUILD
```

**Input:** C files in `src/main/c/` + generated headers
**Output:** Object files in `build/compiled/`
**Logs:** Compilation results and errors

### 3. Static Analysis (`staticAnalysis`)

**What it does:**
- Performs automotive compliance checks
- Validates MISRA-C rules
- Checks for proper error handling
- Generates detailed reports

**Checks performed:**
- ✅ No `goto` statements (MISRA-C compliance)
- ✅ Proper header inclusion (`config.h` required)
- ✅ Automotive build flags usage
- ✅ Function return value validation
- ✅ Code complexity analysis

**Output:** Detailed report in `reports/static-analysis-report.txt`

## 🤖 GitHub Copilot + MCP Integration

### Available MCP Tools

The MCP server provides these tools to GitHub Copilot:

#### 1. `get_build_status`
Get current build status and statistics

**Example usage in Copilot Chat:**
> "What's the current build status?"

#### 2. `analyze_build_logs` 
Analyze build logs for patterns and issues

**Example usage:**
> "Analyze the compilation logs for the last few builds"

#### 3. `run_gradle_task`
Execute Gradle tasks and monitor execution

**Example usage:**
> "Run the static analysis task"

#### 4. `get_build_recommendations`
Get recommendations based on issue descriptions

**Example usage:**
> "I'm getting compilation errors, what should I check?"

### Sample Copilot Conversations

**🔍 Troubleshooting:**
```
User: "My build is failing with header errors"

Copilot: Let me check your build logs and provide recommendations.
[Uses MCP to analyze logs]

Based on the analysis, I see header generation issues. Here's what to try:
1. Run `gradle generateHeaders` to regenerate header files
2. Check that template files exist in src/main/templates/
3. Verify build directory permissions

The similar issue from 2 days ago was resolved by regenerating headers.
```

**📊 Performance Analysis:**
```
User: "Why is my build slow today?"

Copilot: [Uses MCP to analyze performance patterns]

I notice your builds are 40% slower than usual. This matches the pattern 
from last week when the system was under high load. Recommendations:
1. Try running with --parallel flag
2. Clean build cache: gradle clean  
3. Current time (2 PM) typically shows slower builds - consider off-peak hours
```

**🔮 Predictive Assistance:**
```
User: "Starting a compilation task"

Copilot: [Uses MCP to predict potential issues]

Based on recent patterns, there's a 30% chance of header inclusion errors
in the compileC task. I recommend:
1. Verify config.h is included in all C files
2. Check that the generateHeaders task completed successfully
3. Review the last static analysis report for warnings
```

## 🧠 Learning Engine

The system continuously learns from build processes:

### What it learns:
- **Error Patterns**: Common compilation, linking, and static analysis errors
- **Success Patterns**: Optimal build configurations and timing
- **Performance Patterns**: Build duration trends and resource usage
- **Resolution Patterns**: Which solutions work for specific problems

### How it helps:
- **Predictive Analysis**: Warns about potential issues before they occur
- **Intelligent Recommendations**: Suggests solutions based on similar past issues
- **Performance Optimization**: Recommends optimal build timing and settings
- **Pattern Recognition**: Identifies recurring problems and their root causes

### Learning Data Storage:
- Patterns stored in `mcp/models/build_patterns.pkl`
- Automatic learning from each build execution
- Privacy-focused: All learning happens locally

## 📋 Available Gradle Tasks

### Automotive Group Tasks:
```bash
gradle generateHeaders    # Generate C header files from templates
gradle compileC          # Compile C source files with automotive flags  
gradle staticAnalysis    # Perform static analysis and compliance checks
gradle automotiveBuild   # Complete automotive build process
```

### Utility Tasks:
```bash
gradle clean             # Clean build artifacts
gradle tasks --all       # List all available tasks
gradle setupLogDir       # Ensure logs directory exists
```

## 🔍 Monitoring and Logs

### Build Logs Location:
- **Process Logs**: `logs/build-process.json` (JSON format for MCP parsing)
- **Static Analysis**: `reports/static-analysis-report.txt`
- **Gradle Logs**: Standard Gradle output

### Log Format Example:
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "task": "compileC", 
  "status": "SUCCESS",
  "sourceFiles": ["/path/to/main.c", "/path/to/utils.c"],
  "outputDir": "/path/to/build/compiled",
  "duration": 5000,
  "errors": [],
  "warnings": []
}
```

## 🛠 Customization

### Adding New Custom Processes

1. **Add Gradle Task:**
```gradle
task myCustomTask {
    group = 'automotive'
    description = 'My custom automotive process'
    
    doLast {
        // Custom process logic
        
        // Log for MCP learning
        def processLog = [
            timestamp: new Date().toInstant().toString(),
            task: 'myCustomTask',
            status: 'SUCCESS',
            // ... other details
        ]
        file("logs/build-process.json") << groovy.json.JsonBuilder(processLog).toPrettyString() + "\n"
    }
}
```

2. **Update MCP Server:**
Add handling for the new task in `mcp/gradle_mcp_server.py`

3. **Extend Learning Engine:**
Add new patterns in `mcp/learning_engine.py`

### Adding New Error Types

In `learning_engine.py`, extend the `_classify_error_type` method:
```python
def _classify_error_type(self, error_text: str) -> str:
    error_lower = error_text.lower()
    
    if 'my_custom_error' in error_lower:
        return 'my_custom_error_type'
    # ... existing patterns
```

## 🔐 Security Considerations

- **Local Processing**: All AI learning happens locally, no data sent to external services
- **File Permissions**: Build processes respect file system permissions
- **Code Isolation**: C compilation uses standard automotive safety flags
- **MCP Security**: MCP server runs with limited permissions

## 🚨 Troubleshooting

### Common Issues:

**1. "Permission denied" errors:**
```bash
chmod +x gradlew
sudo chown -R $USER:$USER .
```

**2. "Python module not found":**
```bash
pip install scikit-learn numpy mcp
export PYTHONPATH=.:$PYTHONPATH
```

**3. "GCC not found":**
```bash
# Ubuntu/Debian:
sudo apt-get install gcc build-essential

# macOS:
xcode-select --install
```

**4. MCP server not starting:**
```bash
# Check dependencies
python -c "import mcp, sklearn, numpy"

# Run server directly
cd mcp && python gradle_mcp_server.py
```

### Getting Help:

1. **Check build logs**: `logs/build-process.json`
2. **Ask GitHub Copilot**: "What's wrong with my build?"
3. **Run diagnostics**: `python setup.py` (includes MCP server test)
4. **Clean build**: `./gradlew clean automotiveBuild`

## 🎯 Example Workflows

### Typical Development Workflow:

1. **Start development session:**
   ```bash
   # Start MCP server
   python mcp/gradle_mcp_server.py &
   
   # Open VS Code with Copilot
   code .
   ```

2. **Make code changes**
3. **Ask Copilot for build guidance:**
   > "Should I run a build now? Any potential issues?"

4. **Run build with Copilot assistance:**
   > "Run the automotive build and analyze any issues"

5. **Review results:**
   > "Analyze the latest build results and suggest improvements"

### Debugging Workflow:

1. **Build fails**
2. **Ask Copilot:**
   > "My build failed, what went wrong?"

3. **Copilot analyzes logs and suggests solutions**
4. **Apply fixes**
5. **Copilot learns from the resolution**

## 📈 Benefits Demonstrated

### Without MCP + Copilot:
- Manual error analysis
- No pattern recognition
- Reactive troubleshooting
- Isolated knowledge

### With MCP + Copilot:
- ✅ **Intelligent assistance**: AI understands your specific build system
- ✅ **Predictive analysis**: Warns before problems occur  
- ✅ **Pattern learning**: Gets smarter with each build
- ✅ **Context-aware**: Knows your project history and patterns
- ✅ **Automated recommendations**: Suggests specific solutions
- ✅ **Performance optimization**: Optimizes build timing and resources

## 🔮 Future Enhancements

- **Multi-language support**: Add support for C++, Rust automotive builds
- **Advanced ML models**: Implement deep learning for pattern recognition
- **Integration APIs**: Connect with automotive toolchains (AUTOSAR, etc.)
- **Real-time monitoring**: Live build process monitoring and intervention
- **Team learning**: Share patterns across development teams
- **Compliance automation**: Automated ISO 26262 compliance checking

---

## 📞 Support

For questions about this automotive build system:

1. Ask GitHub Copilot using the MCP integration
2. Check the learning engine statistics: `python -c "from mcp.learning_engine import BuildPatternLearner; print(BuildPatternLearner().get_statistics())"`
3. Review build logs in `logs/` directory
4. Test MCP server: `python setup.py`

**Happy Building! 🚗⚡**