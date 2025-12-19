import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Tag
import cssutils
import logging

# Suppress CSS parsing warnings
cssutils.log.setLevel(logging.CRITICAL)


class AestheticsAnalyzer:
    def __init__(self):
        self.aesthetic_principles = {
            "COLOR_001": {"name": "Color Harmony", "severity": "high", "category": "color"},
            "COLOR_002": {"name": "Color Palette Consistency", "severity": "high", "category": "color"},
            "COLOR_003": {"name": "Color Contrast for Readability", "severity": "critical", "category": "color"},
            "COLOR_004": {"name": "Color Theory Compliance", "severity": "medium", "category": "color"},
            "SPACING_001": {"name": "8px Grid System", "severity": "high", "category": "spacing"},
            "SPACING_002": {"name": "Consistent Margins/Padding", "severity": "high", "category": "spacing"},
            "SPACING_003": {"name": "Whitespace Balance", "severity": "medium", "category": "spacing"},
            "SPACING_004": {"name": "Layout Spacing Consistency", "severity": "high", "category": "spacing"},
            "TYPOGRAPHY_001": {"name": "Font Hierarchy", "severity": "high", "category": "typography"},
            "TYPOGRAPHY_002": {"name": "Readable Font Sizes", "severity": "critical", "category": "typography"},
            "TYPOGRAPHY_003": {"name": "Line Height Optimization", "severity": "medium", "category": "typography"},
            "TYPOGRAPHY_004": {"name": "Font Pairing", "severity": "medium", "category": "typography"},
            "HIERARCHY_001": {"name": "Size Relationships", "severity": "high", "category": "hierarchy"},
            "HIERARCHY_002": {"name": "Visual Emphasis", "severity": "high", "category": "hierarchy"},
            "HIERARCHY_003": {"name": "Information Architecture", "severity": "medium", "category": "hierarchy"},
            "CONSISTENCY_001": {"name": "Component Patterns", "severity": "high", "category": "consistency"},
            "CONSISTENCY_002": {"name": "Spacing Consistency", "severity": "high", "category": "consistency"},
            "CONSISTENCY_003": {"name": "Color Usage Consistency", "severity": "high", "category": "consistency"},
            "MODERN_001": {"name": "Card Design Patterns", "severity": "medium", "category": "modern_patterns"},
            "MODERN_002": {"name": "Shadow and Depth", "severity": "low", "category": "modern_patterns"},
            "MODERN_003": {"name": "Border Radius Consistency", "severity": "low", "category": "modern_patterns"},
            "MODERN_004": {"name": "Modern UI Patterns", "severity": "medium", "category": "modern_patterns"},
            "BALANCE_001": {"name": "Visual Weight Distribution", "severity": "medium", "category": "balance"},
            "BALANCE_002": {"name": "Layout Balance", "severity": "medium", "category": "balance"},
            "CLUTTER_001": {"name": "Visual Clutter", "severity": "high", "category": "clutter"},
            "CLUTTER_002": {"name": "Unnecessary Elements", "severity": "medium", "category": "clutter"}
        }

        self.design_patterns = {
            "color_values": r'(color|background-color|border-color|fill|stroke)\s*:\s*[^;]+',
            "spacing_values": r'(margin|padding|gap|spacing)\s*:\s*[^;]+',
            "typography": r'(font-size|font-family|font-weight|line-height|letter-spacing)',
            "layout": r'(display|grid|flex|position|align|justify)',
            "modern_effects": r'(box-shadow|border-radius|backdrop-filter|opacity|transform)',
            "visual_hierarchy": r'(font-size|font-weight|color|opacity|transform)'
        }

    def process_llm_result(self, llm_result: Dict[str, Any], file_info: Dict[str, Any],
                           original_code: str) -> Dict[str, Any]:
        """Process and enhance LLM analysis results with improved validation"""
        import logging
        logger = logging.getLogger(__name__)
        
        if llm_result.get("error"):
            return llm_result

        # Enhanced processing of detected issues
        enhanced_issues = []
        llm_issues_count = len(llm_result.get("issues", []))

        for issue in llm_result.get("issues", []):
            enhanced_issue = self._enhance_issue(issue, file_info, original_code)

            # Validate issue accuracy before including
            if self._validate_issue_existence(enhanced_issue, original_code):
                enhanced_issues.append(enhanced_issue)
            else:
                logger.debug(f"Rejected invalid issue: {issue.get('issue_id', 'Unknown')}")

        llm_validated_count = len(enhanced_issues)
        
        # Add static analysis results
        static_issues_count = 0
        try:
            static_issues = self._perform_static_analysis(original_code, file_info)
            static_issues_count = len(static_issues)
            enhanced_issues.extend(static_issues)
            
            if static_issues_count > 0:
                logger.info(
                    f"Static analysis added {static_issues_count} additional issues to {file_info.get('name', 'file')} "
                    f"(LLM: {llm_validated_count}, Static: {static_issues_count}, Total: {len(enhanced_issues)})"
                )
        except Exception as e:
            logger.warning(f"Static analysis failed for {file_info.get('name', 'file')}: {str(e)}")
            # Continue without static analysis

        # Calculate metrics
        metrics = self._calculate_metrics(enhanced_issues)
        
        total_issues = len(enhanced_issues)
        
        # Log summary
        if total_issues > 0:
            logger.info(
                f"Aesthetics processing complete for {file_info.get('name', 'file')}: "
                f"{llm_validated_count} LLM issues (from {llm_issues_count} detected), "
                f"{static_issues_count} static analysis issues, "
                f"{total_issues} total issues"
            )

        return {
            "file_info": file_info,
            "total_issues": total_issues,
            "issues": enhanced_issues,
            "metrics": metrics,
            "llm_result": llm_result,
            "llm_issues_count": llm_validated_count,
            "static_issues_count": static_issues_count
        }

    def _validate_issue_existence(self, issue: Dict[str, Any], original_code: str) -> bool:
        """Validate that an issue actually exists in the code with improved flexibility"""
        lines = original_code.split('\n')
        line_numbers = issue.get('line_numbers', [])
        code_snippet = issue.get('code_snippet', '').strip()

        # If no line numbers provided, try to find the snippet
        if not line_numbers and code_snippet:
            # Search for the snippet in the entire code
            for i, line in enumerate(lines, 1):
                if self._fuzzy_match_code(code_snippet, line):
                    line_numbers = [i]
                    issue['line_numbers'] = line_numbers
                    break

        if not line_numbers:
            # For certain aesthetic principles, we can be more lenient
            principle_id = issue.get('principle_id', '')
            if any(critical in principle_id for critical in ['COLOR_003', 'TYPOGRAPHY_002', 'SPACING_001']):
                # These are critical issues - give them more weight
                return True
            return False

        # Check if at least one line number contains relevant code
        matches = 0
        for line_num in line_numbers:
            if 1 <= line_num <= len(lines):
                line_content = lines[line_num - 1].strip()

                # Multiple validation strategies
                if (code_snippet in line_content or
                        self._fuzzy_match_code(code_snippet, line_content) or
                        self._semantic_match_code(issue, line_content)):
                    matches += 1

        # Lower the threshold for validation - accept if ANY line matches
        return matches > 0

    def _fuzzy_match_code(self, snippet: str, line_content: str) -> bool:
        """Enhanced fuzzy matching for code snippets"""
        # Remove whitespace and normalize
        snippet_clean = re.sub(r'\s+', '', snippet.lower())
        line_clean = re.sub(r'\s+', '', line_content.lower())

        # Direct substring match
        if snippet_clean in line_clean or line_clean in snippet_clean:
            return True

        # Check if key CSS/HTML elements/attributes match
        snippet_elements = re.findall(r'<(\w+)|(\w+)=|class="([^"]+)"|id="([^"]+)"|(\w+)\s*:', snippet.lower())
        line_elements = re.findall(r'<(\w+)|(\w+)=|class="([^"]+)"|id="([^"]+)"|(\w+)\s*:', line_content.lower())

        # Flatten and filter empty strings
        snippet_parts = [part for group in snippet_elements for part in group if part]
        line_parts = [part for group in line_elements for part in group if part]

        # Check overlap
        if snippet_parts and line_parts:
            overlap = set(snippet_parts) & set(line_parts)
            return len(overlap) >= len(snippet_parts) * 0.5

        return False

    def _semantic_match_code(self, issue: Dict[str, Any], line_content: str) -> bool:
        """Semantic matching based on issue type"""
        principle_id = issue.get('principle_id', '')
        category = issue.get('category', '')

        # Define patterns for different aesthetic categories
        semantic_patterns = {
            'COLOR_001': [r'color\s*:', r'background-color\s*:', r'#[0-9a-fA-F]{3,6}', r'rgb\s*\(', r'rgba\s*\('],
            'COLOR_002': [r'color\s*:', r'background-color\s*:', r'#[0-9a-fA-F]{3,6}'],
            'SPACING_001': [r'margin\s*:', r'padding\s*:', r'gap\s*:', r'spacing\s*:'],
            'SPACING_002': [r'margin\s*:', r'padding\s*:', r'gap\s*:'],
            'TYPOGRAPHY_001': [r'font-size\s*:', r'font-weight\s*:', r'font-family\s*:'],
            'TYPOGRAPHY_002': [r'font-size\s*:'],
            'HIERARCHY_001': [r'font-size\s*:', r'font-weight\s*:'],
            'MODERN_001': [r'box-shadow\s*:', r'border-radius\s*:', r'border\s*:'],
        }

        # Extract principle ID prefix
        if principle_id in semantic_patterns:
            return any(re.search(pattern, line_content, re.IGNORECASE)
                       for pattern in semantic_patterns[principle_id])
        
        # Category-based matching
        category_patterns = {
            'color': [r'color\s*:', r'background-color\s*:', r'#[0-9a-fA-F]{3,6}'],
            'spacing': [r'margin\s*:', r'padding\s*:', r'gap\s*:'],
            'typography': [r'font-size\s*:', r'font-family\s*:', r'line-height\s*:'],
            'hierarchy': [r'font-size\s*:', r'font-weight\s*:', r'opacity\s*:'],
        }
        
        if category in category_patterns:
            return any(re.search(pattern, line_content, re.IGNORECASE)
                       for pattern in category_patterns[category])

        return False

    def _enhance_issue(self, issue: Dict[str, Any], file_info: Dict[str, Any],
                       original_code: str) -> Dict[str, Any]:
        """Enhance individual issue with additional context and accurate line detection"""
        enhanced = issue.copy()

        # Improve line number accuracy
        enhanced["line_numbers"] = self._improve_line_accuracy(issue, original_code)

        # Add aesthetic principle details
        principle_id = self._extract_principle_id(issue.get("principle_id", ""))
        if principle_id in self.aesthetic_principles:
            enhanced["principle_details"] = self.aesthetic_principles[principle_id]

        # Extract and validate code snippet with improved accuracy
        line_numbers = enhanced["line_numbers"]
        if line_numbers:
            enhanced["code_context"] = self._extract_accurate_code_context(
                original_code, line_numbers
            )
            # Update code snippet with actual code from validated lines
            enhanced["code_snippet"] = self._extract_precise_code_snippet(
                original_code, line_numbers, issue.get("code_snippet", "")
            )

        # Add design context
        enhanced["design_context"] = self._analyze_design_context(
            enhanced.get("code_snippet", ""), file_info
        )

        # Generate preview data for UI rendering
        enhanced["ui_preview"] = self._generate_ui_preview(enhanced, file_info)

        # Add fix confidence score
        enhanced["fix_confidence"] = self._calculate_fix_confidence(enhanced)

        # Add validation score
        enhanced["validation_score"] = self._calculate_validation_score(enhanced, original_code)

        return enhanced

    def _improve_line_accuracy(self, issue: Dict[str, Any], original_code: str) -> List[int]:
        """Improve line number accuracy using multiple strategies"""
        lines = original_code.split('\n')
        code_snippet = issue.get('code_snippet', '').strip()
        original_line_numbers = issue.get('line_numbers', [])

        if not code_snippet:
            return original_line_numbers

        # Strategy 1: Exact match search
        exact_matches = []
        for i, line in enumerate(lines, 1):
            if code_snippet in line:
                exact_matches.append(i)

        if exact_matches:
            return exact_matches[:3]  # Limit to first 3 matches

        # Strategy 2: Fuzzy search for similar content
        fuzzy_matches = []
        for i, line in enumerate(lines, 1):
            if self._fuzzy_match_code(code_snippet, line):
                fuzzy_matches.append(i)

        if fuzzy_matches:
            return fuzzy_matches[:3]

        # Strategy 3: Search for key elements mentioned in the issue
        element_matches = self._find_related_elements(issue, original_code)
        if element_matches:
            return element_matches[:3]

        # Strategy 4: Return validated original line numbers or search nearby
        validated_lines = []
        for line_num in original_line_numbers:
            if 1 <= line_num <= len(lines):
                # Check a range around the original line number
                for offset in range(-2, 3):  # Check ±2 lines
                    check_line = line_num + offset
                    if 1 <= check_line <= len(lines):
                        if any(keyword in lines[check_line - 1].lower()
                               for keyword in self._extract_keywords_from_issue(issue)):
                            validated_lines.append(check_line)
                            break
                else:
                    validated_lines.append(line_num)  # Keep original if no better match

        return validated_lines if validated_lines else [1]

    def _find_related_elements(self, issue: Dict[str, Any], original_code: str) -> List[int]:
        """Find lines containing elements related to the issue"""
        lines = original_code.split('\n')
        principle_id = issue.get('principle_id', '')
        category = issue.get('category', '')

        # Define search patterns for different aesthetic categories
        search_patterns = {
            'COLOR_001': [r'color\s*:', r'background-color\s*:', r'#[0-9a-fA-F]{3,6}'],
            'COLOR_002': [r'color\s*:', r'background-color\s*:'],
            'SPACING_001': [r'margin\s*:', r'padding\s*:', r'gap\s*:'],
            'SPACING_002': [r'margin\s*:', r'padding\s*:'],
            'TYPOGRAPHY_001': [r'font-size\s*:', r'font-weight\s*:', r'font-family\s*:'],
            'TYPOGRAPHY_002': [r'font-size\s*:'],
            'HIERARCHY_001': [r'font-size\s*:', r'font-weight\s*:'],
            'MODERN_001': [r'box-shadow\s*:', r'border-radius\s*:'],
        }

        if principle_id in search_patterns:
            patterns = search_patterns[principle_id]
        elif category in ['color', 'spacing', 'typography', 'hierarchy']:
            category_patterns = {
                'color': [r'color\s*:', r'background-color\s*:'],
                'spacing': [r'margin\s*:', r'padding\s*:', r'gap\s*:'],
                'typography': [r'font-size\s*:', r'font-family\s*:'],
                'hierarchy': [r'font-size\s*:', r'font-weight\s*:'],
            }
            patterns = category_patterns.get(category, [])
        else:
            return []

        matching_lines = []
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    matching_lines.append(i)
                    break
        return matching_lines

    def _extract_keywords_from_issue(self, issue: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords from issue description"""
        description = issue.get('description', '').lower()
        code_snippet = issue.get('code_snippet', '').lower()
        category = issue.get('category', '').lower()

        # Common CSS/HTML keywords to look for
        keywords = []

        # Extract CSS properties
        css_properties = re.findall(r'(\w+)\s*:', code_snippet)
        keywords.extend(css_properties)

        # Extract HTML tags
        html_tags = re.findall(r'<(\w+)', code_snippet)
        keywords.extend(html_tags)

        # Extract keywords from description
        keyword_patterns = [
            r'\b(color|background|border|fill|stroke)\b',
            r'\b(margin|padding|gap|spacing)\b',
            r'\b(font|typography|text|size|weight)\b',
            r'\b(shadow|radius|border|rounded)\b',
            r'\b(hierarchy|emphasis|contrast)\b'
        ]

        for pattern in keyword_patterns:
            matches = re.findall(pattern, description)
            keywords.extend(matches)

        # Add category-specific keywords
        if category:
            keywords.append(category)

        return list(set(keywords))  # Remove duplicates

    def _extract_accurate_code_context(self, code: str, line_numbers: List[int]) -> Dict[str, Any]:
        """Extract code context with improved accuracy"""
        lines = code.split('\n')

        if not line_numbers:
            return {"lines": [], "start_line": 0, "end_line": 0}

        # Expand context window based on code complexity
        context_window = 3  # Default context
        min_line = max(0, min(line_numbers) - context_window)
        max_line = min(len(lines), max(line_numbers) + context_window)

        context_lines = []
        for i in range(min_line, max_line):
            is_highlighted = (i + 1) in line_numbers
            line_content = lines[i] if i < len(lines) else ""

            context_lines.append({
                "number": i + 1,
                "content": line_content,
                "highlighted": is_highlighted,
                "indentation": len(line_content) - len(line_content.lstrip()),
                "is_empty": not line_content.strip()
            })

        return {
            "lines": context_lines,
            "start_line": min_line + 1,
            "end_line": max_line,
            "highlighted_lines": line_numbers
        }

    def _extract_precise_code_snippet(self, code: str, line_numbers: List[int],
                                      original_snippet: str) -> str:
        """Extract precise code snippet from validated line numbers"""
        lines = code.split('\n')

        if not line_numbers:
            return original_snippet

        # Get the actual lines
        actual_lines = []
        for line_num in line_numbers:
            if 1 <= line_num <= len(lines):
                actual_lines.append(lines[line_num - 1])

        if actual_lines:
            # If we have multiple lines, join them intelligently
            if len(actual_lines) == 1:
                return actual_lines[0].strip()
            else:
                # For multiple lines, preserve important structure
                return '\n'.join(line.rstrip() for line in actual_lines)

        return original_snippet

    def _analyze_design_context(self, code_snippet: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze design-specific context"""
        context = {
            "patterns_found": [],
            "design_relevance": "low",
            "complexity": "low",
            "modern_patterns": []
        }

        # Check for design patterns
        for pattern_name, pattern in self.design_patterns.items():
            if re.search(pattern, code_snippet, re.IGNORECASE):
                context["patterns_found"].append(pattern_name)

        # Check for modern design patterns
        modern_patterns = [
            r'box-shadow',
            r'border-radius',
            r'backdrop-filter',
            r'gradient',
            r'transform',
            r'transition'
        ]

        for pattern in modern_patterns:
            if re.search(pattern, code_snippet, re.IGNORECASE):
                context["modern_patterns"].append(pattern)

        # Assess relevance and complexity
        if len(context["patterns_found"]) > 0:
            context["design_relevance"] = "high"

            if len(context["patterns_found"]) > 3:
                context["complexity"] = "high"
            elif len(context["patterns_found"]) > 1:
                context["complexity"] = "medium"

        return context

    def _generate_ui_preview(self, issue: Dict[str, Any], file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced UI preview data"""
        return {
            "element_type": self._extract_element_type(issue.get("code_snippet", "")),
            "bounding_box": self._estimate_bounding_box(issue),
            "preview_html": self._generate_preview_html(issue, file_info),
            "annotations": self._generate_annotations(issue),
            "design_tree": self._generate_design_tree(issue)
        }

    def _generate_design_tree(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate design tree representation"""
        code_snippet = issue.get("code_snippet", "")

        try:
            soup = BeautifulSoup(code_snippet, 'html.parser')
            element = soup.find()

            if element:
                # Extract design-related attributes
                style = element.get('style', '')
                classes = element.get('class', [])
                
                return {
                    "tag": element.name,
                    "classes": classes if isinstance(classes, list) else [classes],
                    "style": style,
                    "design_properties": self._extract_design_properties(style)
                }
        except Exception:
            pass

        return {"tag": "unknown", "classes": [], "style": "", "design_properties": {}}

    def _extract_design_properties(self, style: str) -> Dict[str, Any]:
        """Extract design properties from inline style"""
        properties = {}
        if not style:
            return properties
        
        # Parse CSS properties
        for prop in style.split(';'):
            if ':' in prop:
                key, value = prop.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key in ['color', 'background-color', 'margin', 'padding', 'font-size', 'font-weight', 'border-radius', 'box-shadow']:
                    properties[key] = value
        
        return properties

    def _extract_element_type(self, code_snippet: str) -> str:
        """Extract element type from code snippet"""
        # Enhanced element type detection
        patterns = [
            (r'<(button|input|a|img|select|textarea|label|div|span|section|article)\b', lambda m: m.group(1)),
            (r'class\s*=\s*["\']([^"\']+)["\']', lambda m: m.group(1).split()[0]),
            (r'<(\w+)', lambda m: m.group(1))
        ]

        for pattern, extractor in patterns:
            match = re.search(pattern, code_snippet, re.IGNORECASE)
            if match:
                return extractor(match)

        return "unknown"

    def _estimate_bounding_box(self, issue: Dict[str, Any]) -> Dict[str, int]:
        """Estimate bounding box with design considerations"""
        element_type = issue.get("ui_preview", {}).get("element_type", "unknown")

        # Design-specific sizing
        size_map = {
            "button": {"width": 120, "height": 44},  # Modern touch target
            "input": {"width": 200, "height": 44},
            "img": {"width": 100, "height": 100},
            "select": {"width": 180, "height": 44},
            "div": {"width": 200, "height": 100},
            "unknown": {"width": 100, "height": 40}
        }

        size = size_map.get(element_type, size_map["unknown"])

        return {
            "x": 100,
            "y": 100,
            "width": size["width"],
            "height": size["height"]
        }

    def _generate_preview_html(self, issue: Dict[str, Any], file_info: Dict[str, Any]) -> str:
        """Generate enhanced HTML preview"""
        code_snippet = issue.get("code_snippet", "")
        principle_id = issue.get("principle_id", "")

        preview = f"""
            <div class="design-preview modern-theme">
                <div class="issue-highlight">
                    <div class="code-snippet">{code_snippet}</div>
                    <div class="violation-marker" data-severity="{issue.get('severity', 'medium')}">
                        <span class="principle-reference">{principle_id}</span>
                    </div>
                </div>
                <div class="issue-annotation">
                    <h4>{principle_id}</h4>
                    <p>{issue.get('description', 'No description')}</p>
                    <div class="design-impact">
                        <span class="category-level">{issue.get('category', 'unknown')}</span>
                        <span class="severity-impact">{issue.get('severity', 'medium')}</span>
                    </div>
                </div>
            </div>
            """

        return preview

    def _generate_annotations(self, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced annotations"""
        annotations = [
            {
                "type": "error",
                "position": {"x": 10, "y": 10},
                "message": issue.get("description", "Design issue"),
                "severity": issue.get("severity", "medium"),
                "category": issue.get("category", "unknown"),
                "design_impact": issue.get("design_impact", "medium")
            }
        ]

        # Add category-specific annotations
        if issue.get("category") == "color":
            annotations.append({
                "type": "warning",
                "position": {"x": 50, "y": 10},
                "message": "Color harmony issue",
                "severity": "high"
            })

        return annotations

    def _calculate_fix_confidence(self, issue: Dict[str, Any]) -> float:
        """Calculate enhanced fix confidence score"""
        base_confidence = 0.7

        # Adjust based on validation score
        validation_score = issue.get("validation_score", 0.5)
        base_confidence *= validation_score

        # Adjust based on severity
        severity = issue.get("severity", "medium")
        if severity == "critical":
            base_confidence += 0.2
        elif severity == "high":
            base_confidence += 0.1

        # Adjust based on static vs LLM analysis
        if issue.get("source") == "static_analysis":
            base_confidence += 0.1

        # Adjust based on code snippet quality
        code_snippet = issue.get("code_snippet", "")
        if len(code_snippet) > 10 and ("{" in code_snippet or "<" in code_snippet):
            base_confidence += 0.1

        return min(1.0, base_confidence)

    def _calculate_validation_score(self, issue: Dict[str, Any], original_code: str) -> float:
        """Calculate a validation score for the issue"""
        score = 0.0

        # Line number accuracy (40% of score)
        line_numbers = issue.get('line_numbers', [])
        if line_numbers:
            lines = original_code.split('\n')
            valid_lines = sum(1 for ln in line_numbers if 1 <= ln <= len(lines))
            score += 0.4 * (valid_lines / len(line_numbers))

        # Code snippet relevance (30% of score)
        code_snippet = issue.get('code_snippet', '')
        if code_snippet and line_numbers:
            if any(code_snippet.strip() in original_code.split('\n')[ln - 1]
                   for ln in line_numbers if 1 <= ln <= len(original_code.split('\n'))):
                score += 0.3

        # Principle specificity (20% of score)
        principle_id = issue.get('principle_id', '')
        if principle_id and principle_id in self.aesthetic_principles:
            score += 0.2

        # Description quality (10% of score)
        description = issue.get('description', '')
        if len(description) > 20 and any(keyword in description.lower()
                                         for keyword in
                                         ['color', 'spacing', 'typography', 'hierarchy', 'design', 'aesthetic']):
            score += 0.1

        return min(score, 1.0)

    def _perform_static_analysis(self, code: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced static analysis with precise line detection"""
        issues = []
        file_type = self._determine_file_type(file_info["name"])

        try:
            if file_type == "html":
                issues.extend(self._analyze_html_enhanced(code, file_info))
            elif file_type == "css":
                issues.extend(self._analyze_css_enhanced(code, file_info))
            elif file_type == "xml":
                issues.extend(self._analyze_xml_enhanced(code, file_info))
            elif file_type in ["jsx", "tsx", "javascript"]:
                issues.extend(self._analyze_react_enhanced(code, file_info))
        except Exception as e:
            print(f"Static analysis error for {file_type}: {str(e)}")
            # Continue without this specific analysis

        return issues

    def _analyze_html_enhanced(self, html_code: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced HTML analysis with precise line detection"""
        issues = []
        lines = html_code.split('\n')

        try:
            soup = BeautifulSoup(html_code, 'html.parser')

            # Check for inline styles (design inconsistency)
            elements_with_inline_styles = soup.find_all(attrs={"style": True})
            for i, elem in enumerate(elements_with_inline_styles):
                elem_line = self._find_element_line_precise(html_code, str(elem))
                issues.append({
                    "issue_id": f"STATIC_CONSISTENCY_001_{i:03d}",
                    "principle_id": "CONSISTENCY_001",
                    "severity": "medium",
                    "description": f"Element with inline styles on line {elem_line} - consider using CSS classes for consistency",
                    "line_numbers": [elem_line],
                    "code_snippet": str(elem),
                    "recommendation": "Move inline styles to CSS classes for better maintainability and consistency",
                    "category": "consistency",
                    "source": "static_analysis"
                })

            # Check for inconsistent spacing in class names
            all_classes = set()
            for elem in soup.find_all(class_=True):
                classes = elem.get('class', [])
                if isinstance(classes, list):
                    all_classes.update(classes)
            
            # Check for hardcoded color values in style attributes
            for i, elem in enumerate(elements_with_inline_styles):
                style = elem.get('style', '')
                if re.search(r'#[0-9a-fA-F]{3,6}', style, re.IGNORECASE):
                    elem_line = self._find_element_line_precise(html_code, str(elem))
                    issues.append({
                        "issue_id": f"STATIC_COLOR_002_{i:03d}",
                        "principle_id": "COLOR_002",
                        "severity": "high",
                        "description": f"Hardcoded color value in inline style on line {elem_line}",
                        "line_numbers": [elem_line],
                        "code_snippet": str(elem),
                        "recommendation": "Use CSS variables or design tokens for color values",
                        "category": "color",
                        "source": "static_analysis"
                    })

        except Exception as e:
            issues.append({
                "issue_id": "STATIC_PARSE_001",
                "principle_id": "CONSISTENCY_001",
                "severity": "high",
                "description": f"HTML parsing error: {str(e)}",
                "line_numbers": [1],
                "code_snippet": "<!-- HTML parsing failed -->",
                "recommendation": "Fix HTML syntax errors",
                "category": "consistency",
                "source": "static_analysis"
            })

        return issues

    def _analyze_css_enhanced(self, css_code: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced CSS analysis for aesthetic issues"""
        issues = []
        lines = css_code.split('\n')

        # Check for inconsistent spacing values (not using 8px grid)
        spacing_values = re.findall(r'(?:margin|padding|gap)\s*:\s*(\d+(?:\.\d+)?)px', css_code, re.IGNORECASE)
        non_grid_values = [v for v in spacing_values if float(v) % 8 != 0]
        
        if non_grid_values:
            for i, value in enumerate(non_grid_values[:5]):  # Limit to first 5
                # Find line with this value
                for line_num, line in enumerate(lines, 1):
                    if value in line and any(prop in line for prop in ['margin', 'padding', 'gap']):
                        issues.append({
                            "issue_id": f"STATIC_SPACING_001_{i:03d}",
                            "principle_id": "SPACING_001",
                            "severity": "high",
                            "description": f"Spacing value {value}px on line {line_num} doesn't follow 8px grid system",
                            "line_numbers": [line_num],
                            "code_snippet": line.strip(),
                            "recommendation": f"Use {round(float(value) / 8) * 8}px (multiple of 8) for consistent spacing",
                            "category": "spacing",
                            "source": "static_analysis"
                        })
                        break

        # Check for inconsistent color values (hardcoded colors)
        color_values = re.findall(r'(?:color|background-color|border-color)\s*:\s*(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\))', css_code, re.IGNORECASE)
        if len(set(color_values)) > 10:  # Too many unique colors
            issues.append({
                "issue_id": "STATIC_COLOR_002_001",
                "principle_id": "COLOR_002",
                "severity": "high",
                "description": f"Too many unique color values ({len(set(color_values))}) - consider using a color palette",
                "line_numbers": [1],
                "code_snippet": "/* Multiple color values detected */",
                "recommendation": "Define a consistent color palette using CSS variables",
                "category": "color",
                "source": "static_analysis"
            })

        # Check for missing modern design patterns
        if not re.search(r'border-radius\s*:', css_code, re.IGNORECASE):
            issues.append({
                "issue_id": "STATIC_MODERN_003_001",
                "principle_id": "MODERN_003",
                "severity": "low",
                "description": "No border-radius found - consider adding rounded corners for modern look",
                "line_numbers": [1],
                "code_snippet": "/* No border-radius styles found */",
                "recommendation": "Add border-radius to buttons, cards, and containers for modern design",
                "category": "modern_patterns",
                "source": "static_analysis"
            })

        # Check for inconsistent font sizes
        font_sizes = re.findall(r'font-size\s*:\s*(\d+(?:\.\d+)?)px', css_code, re.IGNORECASE)
        if font_sizes:
            unique_sizes = set(font_sizes)
            if len(unique_sizes) > 8:  # Too many different font sizes
                issues.append({
                    "issue_id": "STATIC_TYPOGRAPHY_001_001",
                    "principle_id": "TYPOGRAPHY_001",
                    "severity": "high",
                    "description": f"Too many different font sizes ({len(unique_sizes)}) - consider using a typography scale",
                    "line_numbers": [1],
                    "code_snippet": "/* Multiple font sizes detected */",
                    "recommendation": "Define a typography scale (e.g., 12px, 14px, 16px, 20px, 24px, 32px)",
                    "category": "typography",
                    "source": "static_analysis"
                })

        return issues

    def _analyze_xml_enhanced(self, xml_code: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced XML analysis for Android layouts"""
        issues = []

        try:
            # Basic XML validation
            ET.fromstring(xml_code)
        except ET.ParseError as e:
            issues.append({
                "issue_id": "STATIC_XML_PARSE_001",
                "principle_id": "CONSISTENCY_001",
                "severity": "high",
                "description": f"XML parsing error: {str(e)}",
                "line_numbers": [1],
                "code_snippet": "<!-- XML parsing failed -->",
                "recommendation": "Fix XML syntax errors",
                "category": "consistency",
                "source": "static_analysis"
            })

        return issues

    def _analyze_react_enhanced(self, code: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced React/JSX analysis for aesthetic issues"""
        issues = []
        lines = code.split('\n')

        try:
            # Check for inline styles (design inconsistency)
            inline_style_matches = re.finditer(r'style\s*=\s*\{[^}]+\}', code, re.MULTILINE | re.DOTALL)
            for match in inline_style_matches:
                line_num = code[:match.start()].count('\n') + 1
                context = code[match.start():match.end()]

                issues.append({
                    "issue_id": f"STATIC_CONSISTENCY_001_REACT_{line_num}",
                    "principle_id": "CONSISTENCY_001",
                    "severity": "medium",
                    "description": f"Inline styles detected on line {line_num} - consider using CSS classes or styled-components",
                    "line_numbers": [line_num],
                    "code_snippet": context[:100] + "...",
                    "recommendation": "Move styles to CSS classes or styled-components for better maintainability",
                    "category": "consistency",
                    "source": "static_analysis"
                })

            # Check for hardcoded color values
            color_matches = re.finditer(r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)', code, re.IGNORECASE)
            for match in color_matches:
                line_num = code[:match.start()].count('\n') + 1
                if 'color' in code[max(0, match.start()-50):match.start()].lower():
                    issues.append({
                        "issue_id": f"STATIC_COLOR_002_REACT_{line_num}",
                        "principle_id": "COLOR_002",
                        "severity": "high",
                        "description": f"Hardcoded color value on line {line_num}",
                        "line_numbers": [line_num],
                        "code_snippet": lines[line_num - 1] if line_num <= len(lines) else "",
                        "recommendation": "Use design tokens or CSS variables for colors",
                        "category": "color",
                        "source": "static_analysis"
                    })

        except Exception as e:
            print(f"React analysis error: {str(e)}")
            # Continue without React-specific analysis

        return issues

    def _calculate_metrics(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate enhanced design metrics"""
        total_issues = len(issues)

        if total_issues == 0:
            return {
                "total_issues": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "category_breakdown": {"color": 0, "spacing": 0, "typography": 0, "hierarchy": 0, "consistency": 0, "modern_patterns": 0, "balance": 0, "clutter": 0},
                "design_score": 100,
                "validation_quality": 1.0
            }

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        category_counts = {"color": 0, "spacing": 0, "typography": 0, "hierarchy": 0, "consistency": 0, "modern_patterns": 0, "balance": 0, "clutter": 0}

        validation_scores = []

        for issue in issues:
            severity = issue.get("severity", "medium")
            category = issue.get("category", "unknown")
            validation_score = issue.get("validation_score", 0.5)

            if severity in severity_counts:
                severity_counts[severity] += 1
            if category in category_counts:
                category_counts[category] += 1

            validation_scores.append(validation_score)

        # Calculate design score
        critical_issues = severity_counts["critical"] + severity_counts["high"]
        design_score = max(0, 100 - (critical_issues * 5) - (severity_counts["medium"] * 2))

        # Calculate average validation quality
        avg_validation = sum(validation_scores) / len(validation_scores) if validation_scores else 1.0

        return {
            "total_issues": total_issues,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "design_score": design_score,
            "validation_quality": avg_validation
        }

    def _determine_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        ext = Path(filename).suffix.lower()

        type_map = {
            '.html': 'html', '.htm': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.jsx': 'jsx', '.tsx': 'tsx',
            '.js': 'javascript', '.ts': 'typescript',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.c': 'c', '.h': 'c'
        }

        return type_map.get(ext, 'unknown')

    def _extract_principle_id(self, principle_text: str) -> str:
        """Extract aesthetic principle ID from text"""
        # Check if it's already an ID
        if principle_text in self.aesthetic_principles:
            return principle_text
        
        # Try to extract from text
        for principle_id in self.aesthetic_principles.keys():
            if principle_id in principle_text:
                return principle_id
        
        return ""

    def _find_element_line_precise(self, html_code: str, element_str: str) -> int:
        """Find precise line number of HTML element using multiple strategies"""
        lines = html_code.split('\n')

        # Strategy 1: Exact match
        for i, line in enumerate(lines, 1):
            if element_str.strip() in line:
                return i

        # Strategy 2: Parse element and look for key attributes
        try:
            soup = BeautifulSoup(element_str, 'html.parser')
            element = soup.find()
            if element:
                tag_name = element.name

                # Look for opening tag with attributes
                attributes = []
                for attr, value in element.attrs.items():
                    if isinstance(value, list):
                        value = ' '.join(value)
                    attributes.append(f'{attr}="{value}"')

                # Create search patterns
                patterns = [
                    f'<{tag_name}\\b[^>]*>',  # Any opening tag
                    f'<{tag_name}\\s+'  # Tag with space (likely has attributes)
                ]

                # Add attribute-specific patterns
                for attr in attributes:
                    patterns.append(re.escape(attr))

                for i, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            return i
        except Exception:
            pass

        # Strategy 3: Look for tag name
        try:
            soup = BeautifulSoup(element_str, 'html.parser')
            element = soup.find()
            if element:
                tag_name = element.name
                for i, line in enumerate(lines, 1):
                    if f'<{tag_name}' in line.lower():
                        return i
        except Exception:
            pass

        return 1  # Fallback


