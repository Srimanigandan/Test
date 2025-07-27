#!/usr/bin/env python3
"""
Gradle MCP Server for Automotive Build System
Monitors Gradle build processes and provides assistance to GitHub Copilot
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# MCP server implementation
import mcp
from mcp.server import McpServer, NotificationOptions
from mcp.server.models import InitializeResult
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
    Resource,
    GetResourceRequest,
    GetResourceResult,
    ListResourcesRequest,
    ListResourcesResult,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradleBuildMonitor:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logs_dir = self.project_root / "logs"
        self.build_history = []
        self.current_processes = {}
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load existing build history
        self._load_build_history()
    
    def _load_build_history(self):
        """Load build history from logs"""
        build_log_file = self.logs_dir / "build-process.json"
        if build_log_file.exists():
            try:
                with open(build_log_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        # Handle multiple JSON objects in file
                        for line in content.split('\n'):
                            if line.strip():
                                try:
                                    self.build_history.append(json.loads(line))
                                except json.JSONDecodeError:
                                    continue
            except Exception as e:
                logger.error(f"Error loading build history: {e}")
    
    async def get_build_status(self) -> Dict[str, Any]:
        """Get current build status"""
        return {
            "project_root": str(self.project_root),
            "logs_directory": str(self.logs_dir),
            "build_history_count": len(self.build_history),
            "active_processes": len(self.current_processes),
            "last_build": self.build_history[-1] if self.build_history else None
        }
    
    async def analyze_build_logs(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze build logs for patterns and issues"""
        relevant_entries = self.build_history
        
        if task_name:
            relevant_entries = [
                entry for entry in self.build_history 
                if entry.get('task') == task_name
            ]
        
        if not relevant_entries:
            return {"message": "No build logs found", "entries": []}
        
        # Analyze patterns
        analysis = {
            "total_builds": len(relevant_entries),
            "successful_builds": len([e for e in relevant_entries if e.get('status') == 'SUCCESS']),
            "failed_builds": len([e for e in relevant_entries if e.get('status') == 'FAILED']),
            "warnings": len([e for e in relevant_entries if e.get('status') == 'WARNINGS']),
            "common_errors": self._extract_common_errors(relevant_entries),
            "performance_trends": self._analyze_performance(relevant_entries),
            "recent_entries": relevant_entries[-5:] if relevant_entries else []
        }
        
        return analysis
    
    def _extract_common_errors(self, entries: List[Dict]) -> List[Dict]:
        """Extract and categorize common errors"""
        errors = []
        for entry in entries:
            if entry.get('status') == 'FAILED' and 'errors' in entry:
                for error in entry['errors']:
                    errors.append({
                        "timestamp": entry.get('timestamp'),
                        "task": entry.get('task'),
                        "error": error
                    })
        
        # Group similar errors
        error_patterns = {}
        for error in errors:
            error_text = str(error.get('error', ''))
            # Simple pattern matching
            if 'compilation' in error_text.lower():
                key = 'compilation_errors'
            elif 'missing' in error_text.lower():
                key = 'missing_dependencies'
            elif 'permission' in error_text.lower():
                key = 'permission_errors'
            else:
                key = 'other_errors'
            
            if key not in error_patterns:
                error_patterns[key] = []
            error_patterns[key].append(error)
        
        return error_patterns
    
    def _analyze_performance(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyze build performance trends"""
        durations = [
            entry.get('duration', 0) for entry in entries 
            if 'duration' in entry and entry['duration'] > 0
        ]
        
        if not durations:
            return {"message": "No performance data available"}
        
        return {
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "recent_trend": durations[-5:] if len(durations) >= 5 else durations
        }
    
    async def run_gradle_task(self, task: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a Gradle task and monitor its execution"""
        cmd = ["./gradlew", task]
        if args:
            cmd.extend(args)
        
        try:
            logger.info(f"Running Gradle task: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            result = {
                "task": task,
                "command": ' '.join(cmd),
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error running Gradle task {task}: {e}")
            return {
                "task": task,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_build_recommendations(self, issue_description: str) -> Dict[str, Any]:
        """Provide build recommendations based on learned patterns"""
        recommendations = []
        
        # Analyze issue description for keywords
        issue_lower = issue_description.lower()
        
        # Common patterns and solutions
        if "compilation" in issue_lower or "compile" in issue_lower:
            recommendations.extend([
                "Check if all header files are properly included",
                "Verify that config.h is included in all C files",
                "Ensure AUTOMOTIVE_BUILD flag is properly set",
                "Check for missing function declarations"
            ])
        
        if "header" in issue_lower or "include" in issue_lower:
            recommendations.extend([
                "Run 'gradle generateHeaders' to regenerate header files",
                "Check template files in src/main/templates/",
                "Verify build directory permissions"
            ])
        
        if "static analysis" in issue_lower or "violations" in issue_lower:
            recommendations.extend([
                "Review MISRA-C compliance issues",
                "Check for goto statements (not allowed in automotive code)",
                "Ensure proper error handling in all functions",
                "Verify automotive-specific coding standards"
            ])
        
        if "performance" in issue_lower or "slow" in issue_lower:
            recommendations.extend([
                "Consider running build with --parallel flag",
                "Clean build directory: gradle clean",
                "Check system resources and disk space"
            ])
        
        # Look for similar issues in history
        similar_issues = self._find_similar_historical_issues(issue_description)
        
        return {
            "recommendations": recommendations,
            "similar_historical_issues": similar_issues,
            "suggested_commands": self._suggest_gradle_commands(issue_description)
        }
    
    def _find_similar_historical_issues(self, issue: str) -> List[Dict]:
        """Find similar issues from build history"""
        similar = []
        issue_words = set(issue.lower().split())
        
        for entry in self.build_history:
            if entry.get('status') in ['FAILED', 'WARNINGS']:
                # Simple text similarity
                entry_text = str(entry).lower()
                entry_words = set(entry_text.split())
                
                # Calculate similarity (Jaccard index)
                intersection = len(issue_words.intersection(entry_words))
                union = len(issue_words.union(entry_words))
                
                if union > 0:
                    similarity = intersection / union
                    if similarity > 0.1:  # 10% similarity threshold
                        similar.append({
                            "entry": entry,
                            "similarity": similarity
                        })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)[:3]
    
    def _suggest_gradle_commands(self, issue: str) -> List[str]:
        """Suggest relevant Gradle commands based on issue"""
        commands = []
        issue_lower = issue.lower()
        
        if "clean" in issue_lower:
            commands.append("gradle clean")
        
        if "header" in issue_lower:
            commands.append("gradle generateHeaders")
        
        if "compile" in issue_lower:
            commands.append("gradle compileC")
        
        if "analysis" in issue_lower:
            commands.append("gradle staticAnalysis")
        
        if "build" in issue_lower:
            commands.append("gradle automotiveBuild")
        
        # Default suggestions
        if not commands:
            commands.extend([
                "gradle tasks --all",
                "gradle automotiveBuild",
                "gradle clean build"
            ])
        
        return commands


# MCP Server setup
server = McpServer("gradle-automotive-build")

# Global monitor instance
build_monitor = GradleBuildMonitor()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for the MCP server"""
    return [
        Tool(
            name="get_build_status",
            description="Get current Gradle build status and statistics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="analyze_build_logs",
            description="Analyze build logs for patterns and issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "Optional: Specific task to analyze (e.g., 'compileC', 'staticAnalysis')"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="run_gradle_task",
            description="Execute a Gradle task and monitor its execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The Gradle task to run (e.g., 'automotiveBuild', 'clean')"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional arguments for the Gradle task"
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="get_build_recommendations",
            description="Get build recommendations based on issues or error descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_description": {
                        "type": "string",
                        "description": "Description of the build issue or error"
                    }
                },
                "required": ["issue_description"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from MCP clients"""
    
    try:
        if name == "get_build_status":
            result = await build_monitor.get_build_status()
            return [TextContent(
                type="text",
                text=f"Build Status:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "analyze_build_logs":
            task_name = arguments.get("task_name")
            result = await build_monitor.analyze_build_logs(task_name)
            return [TextContent(
                type="text",
                text=f"Build Log Analysis:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "run_gradle_task":
            task = arguments.get("task")
            args = arguments.get("args", [])
            result = await build_monitor.run_gradle_task(task, args)
            return [TextContent(
                type="text",
                text=f"Gradle Task Execution:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "get_build_recommendations":
            issue_description = arguments.get("issue_description", "")
            result = await build_monitor.get_build_recommendations(issue_description)
            return [TextContent(
                type="text",
                text=f"Build Recommendations:\n{json.dumps(result, indent=2)}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="gradle://build-logs",
            name="Build Logs",
            description="Access to Gradle build logs and history",
            mimeType="application/json"
        ),
        Resource(
            uri="gradle://static-analysis-report",
            name="Static Analysis Report",
            description="Latest static analysis report",
            mimeType="text/plain"
        )
    ]

@server.get_resource()
async def handle_get_resource(uri: str) -> GetResourceResult:
    """Get resource content"""
    if uri == "gradle://build-logs":
        return GetResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=json.dumps(build_monitor.build_history, indent=2)
                )
            ]
        )
    elif uri == "gradle://static-analysis-report":
        report_file = build_monitor.project_root / "reports" / "static-analysis-report.txt"
        if report_file.exists():
            return GetResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=report_file.read_text()
                    )
                ]
            )
        else:
            return GetResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text="Static analysis report not found. Run 'gradle staticAnalysis' first."
                    )
                ]
            )
    
    raise ValueError(f"Unknown resource: {uri}")

async def main():
    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializeResult(
                protocolVersion="2024-11-05",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())