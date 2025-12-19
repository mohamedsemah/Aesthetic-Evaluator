import os
import json
import asyncio
import traceback
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import difflib
import logging

from llm_clients import LLMClient
from aesthetics_analyzer import AestheticsAnalyzer
from code_processor import CodeProcessor

logger = logging.getLogger(__name__)


class EnhancedRemediationService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.aesthetics_analyzer = AestheticsAnalyzer()
        self.code_processor = CodeProcessor()

        # Enhanced remediation prompt template
        self.remediation_prompt = """
You are an expert design developer specializing in aesthetic improvements and visual design fixes for web and mobile interfaces.

**TASK**: Fix the specific aesthetic issue below while preserving all existing functionality and improving visual design quality.

**FILE INFORMATION**:
- File: {filename}
- Framework: {framework}
- File Type: {file_type}

**AESTHETIC ISSUE**:
- Issue ID: {issue_id}
- Aesthetic Principle: {principle_id}
- Severity Level: {severity}
- Category: {category}
- Description: {description}
- Impact: {impact}
- Design Impact: {design_impact}

**PROBLEMATIC CODE** (Lines {line_numbers}):
```{file_type}
{code_snippet}
```

**SURROUNDING CODE CONTEXT**:
```{file_type}
{code_context}
```

**RECOMMENDED SOLUTION**:
{recommendation}

**REQUIREMENTS**:
1. Fix ONLY the specific aesthetic issue mentioned above
2. Preserve all existing functionality and styling
3. Follow modern design principles and best practices
4. Consider visual design constraints (readability, consistency, modern patterns)
5. Add comments explaining the aesthetic improvement
6. Ensure the fix improves visual appeal and user experience

**CRITICAL INSTRUCTIONS**:
- Return ONLY valid JSON
- Do NOT include the full file content (too large for JSON)
- Return only the specific changes made
- Keep response under 4000 characters

**OUTPUT FORMAT** (valid JSON only):
{{
  "success": true,
  "changes": [
    {{
      "line_number": {line_numbers},
      "original": "exact original problematic code",
      "fixed": "exact fixed code with aesthetic improvement",
      "explanation": "detailed explanation of what was changed and why",
      "aesthetic_principle": "which aesthetic principle this addresses",
      "design_improvement": "specific design benefit this provides"
    }}
  ],
  "validation": {{
    "design_improvement": "explanation of how this fix improves visual design quality",
    "testing_instructions": "how to test this fix visually",
    "user_experience": "how this improves user experience and visual appeal",
    "potential_side_effects": "any potential visual impacts to consider"
  }},
  "fix_confidence": 0.95,
  "estimated_impact": "description of visual design and user experience improvement"
}}

**CRITICAL**: Return ONLY valid JSON. Do NOT include full file content. Focus on the specific fix only.
"""

    async def get_enhanced_remediation(
            self,
            session_id: str,
            issue_id: str,
            model: str,
            analysis_sessions: Dict
    ) -> Dict[str, Any]:
        """
        Enhanced remediation with full context and validation
        """
        try:
            logger.info(f"Starting enhanced remediation for issue {issue_id} with model {model}")

            if session_id not in analysis_sessions:
                logger.error(f"Session {session_id} not found")
                return {
                    "success": False,
                    "error": f"Session {session_id} not found",
                    "stage": "session_lookup"
                }

            session = analysis_sessions[session_id]
            logger.info(f"Session found, keys: {list(session.keys())}")

            # Step 1: Find the original issue with full context
            logger.info("Step 1: Finding issue in session...")
            issue_details = self._find_issue_in_session(session, issue_id)

            if not issue_details:
                logger.error(f"Issue {issue_id} not found in session analysis results")

                # Debug: List all available issue IDs
                all_issue_ids = []
                analysis_results = session.get('analysis_results', {})
                for model_name, model_results in analysis_results.items():
                    if isinstance(model_results, list):
                        for file_result in model_results:
                            for issue in file_result.get('issues', []):
                                all_issue_ids.append(issue.get('issue_id', 'NO_ID'))

                logger.info(f"Available issue IDs: {all_issue_ids}")

                return {
                    "success": False,
                    "error": f"Issue {issue_id} not found in session analysis results. Available IDs: {all_issue_ids[:5]}",
                    "stage": "issue_lookup",
                    "available_issues": all_issue_ids[:10]  # Return first 10 for debugging
                }

            logger.info(
                f"Issue details found: {issue_details.get('principle_id', 'No principle')} in file {issue_details.get('file_name', 'No file')}")

            # Step 2: Read the current file content
            logger.info("Step 2: Reading file content...")
            file_path_str = issue_details.get('file_path', '')

            if not file_path_str:
                logger.error("No file path found in issue details")
                return {
                    "success": False,
                    "error": "No file path found in issue details",
                    "stage": "file_path_missing"
                }

            file_path = Path(file_path_str)
            logger.info(f"File path: {file_path}")

            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "stage": "file_access"
                }

            try:
                content, metadata = self.code_processor.read_file_content(file_path)
                if not content:
                    logger.error("Failed to read file content or content is empty")
                    return {
                        "success": False,
                        "error": "Failed to read file content or content is empty",
                        "stage": "file_reading"
                    }
                logger.info(f"File content read successfully: {len(content)} characters")
            except Exception as e:
                logger.error(f"Error reading file content: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error reading file content: {str(e)}",
                    "stage": "file_reading"
                }

            # Step 3: Create enhanced prompt with full context
            logger.info("Step 3: Creating enhanced prompt...")
            try:
                enhanced_prompt = self._create_enhanced_prompt(
                    issue_details, content, file_path
                )
                logger.info(f"Enhanced prompt created: {len(enhanced_prompt)} characters")
            except Exception as e:
                logger.error(f"Error creating enhanced prompt: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error creating enhanced prompt: {str(e)}",
                    "stage": "prompt_creation"
                }

            # Step 4: Get LLM remediation
            logger.info(f"Step 4: Requesting enhanced remediation from {model}...")
            try:
                remediation_result = await self.llm_client._call_model(enhanced_prompt, model)
                logger.info(
                    f"LLM response received, keys: {list(remediation_result.keys()) if isinstance(remediation_result, dict) else 'Not a dict'}")
            except Exception as e:
                logger.error(f"Error calling LLM model: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error calling LLM model: {str(e)}",
                    "stage": "llm_processing"
                }

            # Step 5: Validate and enhance the result
            logger.info("Step 5: Validating remediation result...")
            if remediation_result.get("success") and remediation_result.get("changes"):
                try:
                    # Since we're not getting full fixed_code, we'll apply the changes to create it
                    fixed_content = self._apply_changes_to_content(content, remediation_result.get("changes", []))
                    remediation_result["fixed_code"] = fixed_content

                    # Validate the fix
                    validation_result = await self._validate_remediation(
                        content,
                        fixed_content,
                        issue_details,
                        file_path
                    )
                    remediation_result.update(validation_result)

                    # Create backup of original file
                    backup_path = self.code_processor.create_backup(
                        file_path,
                        Path(f"temp_sessions/{session_id}/backups")
                    )
                    remediation_result["backup_path"] = str(backup_path)

                    # Generate detailed diff
                    diff_result = self.code_processor.generate_diff(
                        content,
                        fixed_content,
                        file_path
                    )
                    remediation_result["diff"] = diff_result

                    logger.info("Validation and enhancement completed successfully")

                except Exception as e:
                    logger.error(f"Error in validation step: {str(e)}")
                    remediation_result["validation_error"] = str(e)

            else:
                logger.warning("LLM did not return valid remediation result")
                remediation_result = {
                    "success": False,
                    "error": "LLM failed to generate valid remediation",
                    "stage": "llm_processing",
                    "raw_response": remediation_result
                }

            logger.info(f"Enhanced remediation completed with success: {remediation_result.get('success', False)}")
            return remediation_result

        except Exception as e:
            logger.error(f"Enhanced remediation failed with unexpected error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "stage": "unexpected_error",
                "traceback": traceback.format_exc()
            }

    def _find_issue_in_session(self, session: Dict, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Find the original issue details from session analysis results
        """
        try:
            analysis_results = session.get('analysis_results', {})
            logger.info(f"Searching for issue {issue_id} in session with {len(analysis_results)} models")

            for model, model_results in analysis_results.items():
                logger.info(f"Checking model {model}, type: {type(model_results)}")

                if isinstance(model_results, list):
                    logger.info(f"Model {model} has {len(model_results)} file results")

                    for file_idx, file_result in enumerate(model_results):
                        file_info = file_result.get('file_info', {})
                        issues = file_result.get('issues', [])
                        logger.info(f"File {file_idx}: {file_info.get('name', 'Unknown')} has {len(issues)} issues")

                        for issue_idx, issue in enumerate(issues):
                            current_issue_id = issue.get('issue_id', '')
                            logger.info(f"Issue {issue_idx}: ID={current_issue_id}")

                            if current_issue_id == issue_id:
                                logger.info(f"Found matching issue {issue_id} in model {model}")

                                # Create a copy to avoid modifying original
                                enhanced_issue = issue.copy()

                                # Enhance with file information
                                enhanced_issue['file_path'] = file_info.get('path', '')
                                enhanced_issue['file_name'] = file_info.get('name', '')
                                enhanced_issue['detection_model'] = model

                                logger.info(f"Enhanced issue with file_path: {enhanced_issue['file_path']}")
                                return enhanced_issue
                else:
                    logger.warning(f"Model {model} results is not a list: {type(model_results)}")

            logger.warning(f"Issue {issue_id} not found in any model results")
            return None

        except Exception as e:
            logger.error(f"Error in _find_issue_in_session: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _create_enhanced_prompt(
            self,
            issue_details: Dict[str, Any],
            content: str,
            file_path: Path
    ) -> str:
        """
        Create comprehensive remediation prompt with full context
        """
        try:
            # Extract file information with safe defaults
            filename = file_path.name
            file_type = self._get_file_type(filename)

            # Safe access to design context
            design_context = issue_details.get('design_context', {})
            patterns_found = design_context.get('patterns_found', [])
            framework = patterns_found[0] if patterns_found else 'unknown'

            # Create numbered code
            numbered_code = self.llm_client._create_numbered_code(content)

            # Safe access to line numbers with defaults
            line_numbers = issue_details.get('line_numbers', [])
            if not isinstance(line_numbers, list):
                line_numbers = []

            # Extract code context around the issue
            try:
                code_context = self._extract_enhanced_context(content, line_numbers)
            except Exception as e:
                logger.warning(f"Error extracting code context: {str(e)}")
                code_context = "Code context not available"

            # Format line numbers for display with safe handling
            if line_numbers:
                line_numbers_str = ", ".join(map(str, line_numbers))
            else:
                line_numbers_str = "Not specified"

            # Safe access to all issue details with defaults
            issue_id = issue_details.get('issue_id', 'Unknown')
            principle_id = issue_details.get('principle_id', 'Unknown principle')
            severity = issue_details.get('severity', 'medium')
            category = issue_details.get('category', 'unknown')
            description = issue_details.get('description', 'No description available')
            impact = issue_details.get('impact', 'Impact not specified')
            design_impact = issue_details.get('design_impact', 'medium')
            code_snippet = issue_details.get('code_snippet', 'Code snippet not available')
            recommendation = issue_details.get('recommendation', 'No specific recommendation provided')

            logger.info(f"Creating prompt for {issue_id}, lines: {line_numbers_str}, framework: {framework}")

            formatted_prompt = self.remediation_prompt.format(
                filename=filename,
                framework=framework,
                file_type=file_type,
                issue_id=issue_id,
                principle_id=principle_id,
                severity=severity,
                category=category,
                description=description,
                impact=impact,
                design_impact=design_impact,
                line_numbers=line_numbers_str,
                code_snippet=code_snippet,
                code_context=code_context,
                recommendation=recommendation,
                numbered_code=numbered_code
            )

            logger.info(f"Enhanced prompt created successfully: {len(formatted_prompt)} characters")
            return formatted_prompt

        except Exception as e:
            logger.error(f"Error in _create_enhanced_prompt: {str(e)}")
            logger.error(
                f"Issue details keys: {list(issue_details.keys()) if isinstance(issue_details, dict) else 'Not a dict'}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise e

    def _extract_enhanced_context(self, content: str, line_numbers: List[int]) -> str:
        """
        Extract enhanced code context around problematic lines
        """
        try:
            if not line_numbers:
                logger.warning("No line numbers provided for context extraction")
                return "No specific line context available"

            lines = content.split('\n')
            if not lines:
                logger.warning("Content has no lines")
                return "No content available"

            logger.info(f"Extracting context for lines {line_numbers} from {len(lines)} total lines")

            context_window = 5

            # Ensure we have valid line numbers
            valid_line_numbers = [ln for ln in line_numbers if isinstance(ln, int) and 1 <= ln <= len(lines)]

            if not valid_line_numbers:
                logger.warning(f"No valid line numbers in range 1-{len(lines)}: {line_numbers}")
                return f"Line numbers {line_numbers} are out of range for file with {len(lines)} lines"

            min_line = max(0, min(valid_line_numbers) - context_window)
            max_line = min(len(lines), max(valid_line_numbers) + context_window)

            logger.info(f"Context window: lines {min_line + 1}-{max_line}")

            context_lines = []
            for i in range(min_line, max_line):
                line_num = i + 1
                line_content = lines[i] if i < len(lines) else ""
                marker = " >>> " if line_num in valid_line_numbers else "     "
                context_lines.append(f"{line_num:4d}:{marker}{line_content}")

            return '\n'.join(context_lines)

        except Exception as e:
            logger.error(f"Error extracting context: {str(e)}")
            return f"Error extracting context: {str(e)}"

    async def _validate_remediation(
            self,
            original_content: str,
            fixed_content: str,
            issue_details: Dict[str, Any],
            file_path: Path
    ) -> Dict[str, Any]:
        """
        Validate that the remediation actually fixes the aesthetic issue
        """
        validation_result = {
            "validation_passed": False,
            "validation_details": {},
            "design_recheck": {},
            "quality_score": 0.0
        }

        try:
            # 1. Basic syntax validation
            syntax_validation = self.code_processor.validate_fixed_code(
                original_content, fixed_content, file_path
            )
            validation_result["validation_details"]["syntax"] = syntax_validation

            # 2. Check if the specific issue is addressed
            issue_addressed = self._check_issue_resolution(
                original_content, fixed_content, issue_details
            )
            validation_result["validation_details"]["issue_addressed"] = issue_addressed

            # 3. Re-run aesthetics analysis on fixed code (mini-analysis)
            design_recheck = await self._recheck_aesthetics(
                fixed_content, issue_details, file_path
            )
            validation_result["design_recheck"] = design_recheck

            # 4. Calculate overall quality score
            validation_result["quality_score"] = self._calculate_remediation_quality(
                syntax_validation,
                issue_addressed,
                design_recheck
            )

            # 5. Determine if validation passed
            validation_result["validation_passed"] = (
                    syntax_validation.get("syntax_valid", False) and
                    issue_addressed.get("likely_resolved", False) and
                    validation_result["quality_score"] >= 0.7
            )

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            validation_result["validation_details"]["error"] = str(e)

        return validation_result

    def _check_issue_resolution(
            self,
            original_content: str,
            fixed_content: str,
            issue_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if the specific aesthetic issue has been addressed
        """
        principle_id = issue_details.get('principle_id', '')
        category = issue_details.get('category', '')

        # Define patterns that indicate issue resolution for different aesthetic principles
        resolution_patterns = {
            'COLOR_001': {
                'patterns': [r'#[0-9a-fA-F]{3,6}', r'rgb\s*\(', r'rgba\s*\('],
                'description': 'Color values improved'
            },
            'COLOR_002': {
                'patterns': [r'var\(--[a-z-]+-color', r'--[a-z-]+-color'],
                'description': 'CSS variables for colors added'
            },
            'SPACING_001': {
                'patterns': [r'\d+px'],
                'description': 'Spacing values adjusted to 8px grid'
            },
            'SPACING_002': {
                'patterns': [r'margin\s*:', r'padding\s*:', r'gap\s*:'],
                'description': 'Consistent spacing applied'
            },
            'TYPOGRAPHY_001': {
                'patterns': [r'font-size\s*:', r'font-weight\s*:'],
                'description': 'Typography hierarchy improved'
            },
            'TYPOGRAPHY_002': {
                'patterns': [r'font-size\s*:\s*1[2-9]px|font-size\s*:\s*[2-9]\d+px'],
                'description': 'Readable font sizes applied'
            },
            'HIERARCHY_001': {
                'patterns': [r'font-size\s*:', r'font-weight\s*:'],
                'description': 'Visual hierarchy improved'
            },
            'MODERN_001': {
                'patterns': [r'box-shadow', r'border-radius'],
                'description': 'Modern design patterns added'
            }
        }

        if principle_id in resolution_patterns:
            patterns = resolution_patterns[principle_id]['patterns']
            description = resolution_patterns[principle_id]['description']
        elif category in ['color', 'spacing', 'typography', 'hierarchy', 'modern_patterns']:
            # Category-based patterns
            category_patterns = {
                'color': [r'var\(--[a-z-]+-color', r'#[0-9a-fA-F]{3,6}'],
                'spacing': [r'margin|padding|gap'],
                'typography': [r'font-size|font-weight|line-height'],
                'hierarchy': [r'font-size|font-weight'],
                'modern_patterns': [r'box-shadow|border-radius'],
            }
            patterns = category_patterns.get(category, [])
            description = f'{category.title()} improvements applied'
        else:
            patterns = []
            description = 'General improvements detected'

            # Check if any of the resolution patterns are present in fixed code but not original
            improvements_found = []
            for pattern in patterns:
                import re
                if (re.search(pattern, fixed_content, re.IGNORECASE) and
                        not re.search(pattern, original_content, re.IGNORECASE)):
                    improvements_found.append(pattern)

            return {
                "likely_resolved": len(improvements_found) > 0,
                "improvements_found": improvements_found,
                "resolution_description": description,
                "confidence": len(improvements_found) / len(patterns)
            }

        # Fallback: check for general improvements
        general_improvements = [
            "// FIXED", "// AESTHETIC FIX", "border-radius", "box-shadow",
            "var(--", "font-size", "margin", "padding", "color:"
        ]

        found_improvements = [
            imp for imp in general_improvements
            if imp.lower() in fixed_content.lower() and imp.lower() not in original_content.lower()
        ]

        return {
            "likely_resolved": len(found_improvements) > 0,
            "improvements_found": found_improvements,
            "resolution_description": "General aesthetic improvements detected",
            "confidence": 0.5 if found_improvements else 0.1
        }

    async def _recheck_aesthetics(
            self,
            fixed_content: str,
            issue_details: Dict[str, Any],
            file_path: Path
    ) -> Dict[str, Any]:
        """
        Re-run aesthetics analysis on fixed code to verify issue resolution
        """
        try:
            # Create a mini file info for analysis
            file_info = {
                "name": file_path.name,
                "path": str(file_path),
                "size": len(fixed_content),
                "type": self._get_file_type(file_path.name)
            }

            # Run static analysis on fixed code
            static_issues = self.aesthetics_analyzer._perform_static_analysis(fixed_content, file_info)

            # Check if the specific issue still exists
            original_issue_id = issue_details.get('issue_id', '')
            similar_issues = [
                issue for issue in static_issues
                if self._is_similar_issue(issue, issue_details)
            ]

            return {
                "total_static_issues": len(static_issues),
                "similar_issues_remaining": len(similar_issues),
                "likely_fixed": len(similar_issues) == 0,
                "remaining_issues": similar_issues[:3],  # Show first 3 if any
                "improvement_score": 1.0 if len(similar_issues) == 0 else 0.3
            }

        except Exception as e:
            logger.error(f"Aesthetics recheck failed: {str(e)}")
            return {
                "error": str(e),
                "improvement_score": 0.5  # Neutral score if recheck fails
            }

    def _is_similar_issue(self, new_issue: Dict, original_issue: Dict) -> bool:
        """
        Check if a new issue is similar to the original issue being fixed
        """
        # Compare aesthetic principles
        new_principle = new_issue.get('principle_id', '')
        original_principle = original_issue.get('principle_id', '')

        if new_principle == original_principle:
            return True

        # Compare line numbers (with some tolerance)
        new_lines = set(new_issue.get('line_numbers', []))
        original_lines = set(original_issue.get('line_numbers', []))

        if new_lines.intersection(original_lines):
            return True

        return False

    def _calculate_remediation_quality(
            self,
            syntax_validation: Dict,
            issue_addressed: Dict,
            design_recheck: Dict
    ) -> float:
        """
        Calculate overall quality score for the remediation
        """
        score = 0.0

        # Syntax validation (30%)
        if syntax_validation.get("syntax_valid", False):
            score += 0.3

        # Issue resolution (40%)
        resolution_confidence = issue_addressed.get("confidence", 0)
        score += 0.4 * resolution_confidence

        # Design improvement (30%)
        improvement_score = design_recheck.get("improvement_score", 0)
        score += 0.3 * improvement_score

        return min(1.0, score)

    def _apply_changes_to_content(self, original_content: str, changes: List[Dict[str, Any]]) -> str:
        """
        Apply the specified changes to the original content
        """
        try:
            lines = original_content.split('\n')
            modified_content = original_content

            # Sort changes by line number (descending) to avoid line number shifts
            sorted_changes = sorted(changes, key=lambda x: x.get('line_number', 0), reverse=True)

            for change in sorted_changes:
                line_number = change.get('line_number')
                original_line = change.get('original', '')
                fixed_line = change.get('fixed', '')

                if line_number and 1 <= line_number <= len(lines):
                    # Replace the specific line
                    if original_line and original_line.strip() in lines[line_number - 1]:
                        # Replace the original line with the fixed version
                        lines[line_number - 1] = lines[line_number - 1].replace(
                            original_line.strip(),
                            fixed_line.strip()
                        )
                    else:
                        # If exact match not found, replace the entire line
                        lines[line_number - 1] = fixed_line

            return '\n'.join(lines)

        except Exception as e:
            logger.error(f"Error applying changes to content: {str(e)}")
            return original_content

    def _get_file_type(self, filename: str) -> str:
        """Get file type for syntax highlighting with safe defaults"""
        try:
            if not filename or not isinstance(filename, str):
                return 'text'

            ext = Path(filename).suffix.lower()
            type_map = {
                '.html': 'html', '.htm': 'html',
                '.css': 'css',
                '.js': 'javascript', '.jsx': 'javascript',
                '.ts': 'typescript', '.tsx': 'typescript',
                '.xml': 'xml', '.py': 'python',
                '.java': 'java', '.kt': 'kotlin',
                '.swift': 'swift', '.cpp': 'cpp',
                '.c': 'c', '.h': 'c'
            }
            return type_map.get(ext, 'text')
        except Exception as e:
            logger.warning(f"Error determining file type for {filename}: {str(e)}")
            return 'text'

    async def preview_remediation(
            self,
            session_id: str,
            issue_id: str,
            model: str,
            analysis_sessions: Dict
    ) -> Dict[str, Any]:
        """
        Generate a preview of the proposed remediation without applying it
        """
        remediation_result = await self.get_enhanced_remediation(
            session_id, issue_id, model, analysis_sessions
        )

        if remediation_result.get("success"):
            # Don't apply the fix, just return the preview
            return {
                "success": True,
                "preview": True,
                "changes": remediation_result.get("changes", []),
                "diff": remediation_result.get("diff", {}),
                "validation": remediation_result.get("validation", {}),
                "quality_score": remediation_result.get("quality_score", 0),
                "estimated_impact": remediation_result.get("estimated_impact", "")
            }
        else:
            return remediation_result

    async def apply_remediation(
            self,
            session_id: str,
            issue_id: str,
            model: str,
            analysis_sessions: Dict,
            force_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Apply the remediation after validation
        """
        remediation_result = await self.get_enhanced_remediation(
            session_id, issue_id, model, analysis_sessions
        )

        if not remediation_result.get("success"):
            return remediation_result

        # Check quality score
        quality_score = remediation_result.get("quality_score", 0)
        if quality_score < 0.7 and not force_apply:
            return {
                "success": False,
                "error": f"Remediation quality score ({quality_score:.2f}) below threshold (0.7)",
                "quality_score": quality_score,
                "suggestion": "Review the proposed changes or try a different model",
                "remediation_preview": remediation_result
            }

        # Apply the fix
        try:
            session = analysis_sessions[session_id]
            issue_details = self._find_issue_in_session(session, issue_id)
            file_path = Path(issue_details['file_path'])

            # Write the fixed content to file
            fixed_content = remediation_result["fixed_code"]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            # Store successful remediation in session
            if "remediations" not in session:
                session["remediations"] = {}

            session["remediations"][issue_id] = {
                "model": model,
                "result": remediation_result,
                "timestamp": datetime.now().isoformat(),
                "applied": True,
                "quality_score": quality_score
            }

            return {
                "success": True,
                "applied": True,
                "issue_id": issue_id,
                "model": model,
                "quality_score": quality_score,
                "changes_applied": len(remediation_result.get("changes", [])),
                "backup_path": remediation_result.get("backup_path"),
                "validation": remediation_result.get("validation", {})
            }

        except Exception as e:
            logger.error(f"Failed to apply remediation: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to apply remediation: {str(e)}",
                "stage": "file_writing"
            }

    async def rollback_remediation(
            self,
            session_id: str,
            issue_id: str,
            analysis_sessions: Dict
    ) -> Dict[str, Any]:
        """
        Rollback a previously applied remediation
        """
        try:
            session = analysis_sessions[session_id]

            if "remediations" not in session or issue_id not in session["remediations"]:
                return {
                    "success": False,
                    "error": "No remediation found for this issue"
                }

            remediation = session["remediations"][issue_id]
            backup_path = Path(remediation["result"].get("backup_path", ""))

            if not backup_path.exists():
                return {
                    "success": False,
                    "error": "Backup file not found - cannot rollback"
                }

            # Find original file path
            issue_details = self._find_issue_in_session(session, issue_id)
            if not issue_details:
                return {
                    "success": False,
                    "error": "Original issue details not found"
                }

            original_file_path = Path(issue_details['file_path'])

            # Restore from backup
            import shutil
            shutil.copy2(backup_path, original_file_path)

            # Mark as rolled back
            session["remediations"][issue_id]["rolled_back"] = True
            session["remediations"][issue_id]["rollback_timestamp"] = datetime.now().isoformat()

            return {
                "success": True,
                "message": "Remediation successfully rolled back",
                "issue_id": issue_id,
                "restored_from": str(backup_path)
            }

        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return {
                "success": False,
                "error": f"Rollback failed: {str(e)}"
            }