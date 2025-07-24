#!/usr/bin/env python3
"""
Markdown Generator for Vehicle Parameters Documentation
Generates Mark-compatible markdown files for Confluence integration
"""

import os
import yaml
import jinja2
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkdownGenerator:
    """Generate markdown documentation from YAML parameter and protocol files"""
    
    def __init__(self, 
                 parameters_file: str = "data/parameters.yaml",
                 protocols_file: str = "data/protocols.yaml",
                 output_dir: str = "output/markdown",
                 templates_dir: str = "templates/markdown"):
        
        self.parameters_file = parameters_file
        self.protocols_file = protocols_file
        self.output_dir = Path(output_dir)
        self.templates_dir = templates_dir
        
        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "details").mkdir(exist_ok=True)
        (self.output_dir / "protocols").mkdir(exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['truncate'] = self._truncate_filter
        
        # Load data
        self.parameters_data = self._load_yaml(self.parameters_file)
        self.protocols_data = self._load_yaml(self.protocols_file)
        
        logger.info(f"Loaded {len(self.parameters_data.get('parameters', []))} parameters")
        logger.info(f"Loaded {len(self.protocols_data.get('protocol_groups', []))} protocol groups")
    
    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load YAML file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    def _truncate_filter(self, text: str, length: int = 100) -> str:
        """Jinja2 filter to truncate text"""
        if len(text) <= length:
            return text
        return text[:length] + "..."
    
    def _get_template_context(self) -> Dict[str, Any]:
        """Get common template context"""
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0.0',
            'source_files': [self.parameters_file, self.protocols_file],
            'validation_status': 'All data validated before generation'
        }
    
    def _get_protocol_for_parameter(self, protocol_reference: str) -> List[Dict[str, Any]]:
        """Get protocol details for a parameter"""
        protocols = []
        
        # Find protocol group
        for group in self.protocols_data.get('protocol_groups', []):
            if group.get('group_name') == protocol_reference:
                group_id = group.get('id')
                
                # Find protocols in this group
                for protocol in self.protocols_data.get('protocols', []):
                    if protocol.get('group_id') == group_id:
                        protocols.append(protocol)
                break
        
        return protocols
    
    def _get_protocol_abbr_for_parameter(self, protocol_reference: str) -> str:
        """Get the first protocol abbreviation for a parameter"""
        protocols = self._get_protocol_for_parameter(protocol_reference)
        if protocols:
            return protocols[0].get('abbr', 'N/A')
        return 'N/A'
    
    def _get_related_fields_for_parameter(self, param_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get breadcrumb, VG5, and abbr fields for a parameter"""
        related = {
            'breadcrumb_fields': [],
            'vg5_fields': [],
            'abbr_metrics': []
        }
        
        # Get breadcrumb fields
        for field in self.parameters_data.get('breadcrumb_fields', []):
            if field.get('parameter_id') == param_id:
                related['breadcrumb_fields'].append(field)
        
        # Get VG5 fields
        for field in self.parameters_data.get('vg5_fields', []):
            if field.get('parameter_id') == param_id:
                related['vg5_fields'].append(field)
        
        # Get abbreviation metrics
        for field in self.parameters_data.get('abbr_metrics', []):
            if field.get('parameter_id') == param_id:
                related['abbr_metrics'].append(field)
        
        return related
    
    def _get_related_parameters(self, current_param: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get parameters related by category or protocol"""
        related = []
        current_id = current_param.get('id')
        current_category = current_param.get('reason_added')
        current_protocol = current_param.get('protocol_reference')
        
        for param in self.parameters_data.get('parameters', []):
            if param.get('id') == current_id:
                continue
            
            # Related by category or protocol
            if (param.get('reason_added') == current_category or 
                param.get('protocol_reference') == current_protocol):
                related.append(param)
        
        return related[:5]  # Limit to 5 related parameters
    
    def _get_navigation_for_parameter(self, current_param: Dict[str, Any]) -> Dict[str, Any]:
        """Get previous/next navigation for parameter"""
        parameters = self.parameters_data.get('parameters', [])
        current_id = current_param.get('id')
        
        # Sort by ID to get consistent navigation
        sorted_params = sorted(parameters, key=lambda x: x.get('id', 0))
        
        navigation = {'previous': None, 'next': None}
        
        for i, param in enumerate(sorted_params):
            if param.get('id') == current_id:
                if i > 0:
                    navigation['previous'] = sorted_params[i-1]
                if i < len(sorted_params) - 1:
                    navigation['next'] = sorted_params[i+1]
                break
        
        return navigation
    
    def generate_parameters_overview(self) -> None:
        """Generate main parameters overview markdown"""
        logger.info("Generating parameters overview...")
        
        template = self.jinja_env.get_template('parameters_overview.md.j2')
        
        # Enhance parameters with protocol abbreviations
        enhanced_parameters = []
        for param in self.parameters_data.get('parameters', []):
            enhanced_param = param.copy()
            enhanced_param['protocol_abbr'] = self._get_protocol_abbr_for_parameter(param.get('protocol_reference', ''))
            enhanced_parameters.append(enhanced_param)
        
        context = self._get_template_context()
        context.update({
            'title': 'Vehicle Parameters Overview',
            'parameters': enhanced_parameters,
            'navigation_links': [
                {'text': 'Protocol Groups', 'url': 'protocols.md'},
                {'text': 'Search Index', 'url': 'search_index.md'}
            ]
        })
        
        output = template.render(**context)
        
        output_file = self.output_dir / "parameters.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        logger.info(f"Generated parameters overview: {output_file}")
    
    def generate_parameter_details(self) -> None:
        """Generate individual parameter detail pages"""
        logger.info("Generating parameter detail pages...")
        
        template = self.jinja_env.get_template('parameter_detail.md.j2')
        
        for param in self.parameters_data.get('parameters', []):
            param_id = param.get('id')
            param_name = param.get('field_name', '').lower().replace(' ', '_').replace('-', '_').replace('___', '_').replace('__', '_')
            
            # Get related information
            protocols = self._get_protocol_for_parameter(param.get('protocol_reference', ''))
            related_fields = self._get_related_fields_for_parameter(param_id)
            related_parameters = self._get_related_parameters(param)
            navigation = self._get_navigation_for_parameter(param)
            
            context = self._get_template_context()
            context.update({
                'title': f"{param.get('field_name')} Parameter",
                'parameter': param,
                'protocols': protocols,
                'related_parameters': related_parameters,
                'navigation': navigation,
                **related_fields
            })
            
            output = template.render(**context)
            
            output_file = self.output_dir / "details" / f"{param_name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        
        logger.info(f"Generated {len(self.parameters_data.get('parameters', []))} parameter detail pages")
    
    def generate_protocols_overview(self) -> None:
        """Generate main protocols overview markdown"""
        logger.info("Generating protocols overview...")
        
        context = self._get_template_context()
        
        protocols_content = f'''<!-- Mark headers for Confluence integration -->
<ac:structured-macro ac:name="info">
<ac:parameter name="title">Vehicle Protocols Overview</ac:parameter>
<ac:rich-text-body>
<p>Auto-generated from vehicle parameters YAML - Last updated: {context['timestamp']}</p>
</ac:rich-text-body>
</ac:structured-macro>

# Vehicle Protocols Overview

## Summary
- **Total Protocol Groups:** {len(self.protocols_data.get('protocol_groups', []))}
- **Total Individual Protocols:** {len(self.protocols_data.get('protocols', []))}
- **Last Updated:** {context['timestamp']}
- **Validation Status:** {context['validation_status']}

## Protocol Groups Table

| Group ID | Protocol Group | Standard | Parameter Reference | Protocol Count | Details |
|----------|----------------|----------|-------------------|----------------|---------|
'''
        
        for group in self.protocols_data.get('protocol_groups', []):
            group_id = group.get('id', '')
            group_name = group.get('group_name', '')
            param_ref = group.get('parameter_reference', '')
            
            # Count protocols in this group
            protocol_count = len([p for p in self.protocols_data.get('protocols', []) 
                                if p.get('group_id') == group_id])
            
            # Get protocol standard (from first protocol in group)
            standard = 'N/A'
            for protocol in self.protocols_data.get('protocols', []):
                if protocol.get('group_id') == group_id:
                    standard = protocol.get('protocol_standard', 'N/A')
                    break
            
            protocols_content += f"| {group_id} | {group_name} | {standard} | {param_ref} | {protocol_count} | [View Details](protocols/{group_name}.md) |\n"
        
        protocols_content += f'''

## Navigation
- [Parameters Overview](parameters.md)
- [Search Index](search_index.md)

---
*Generated by Vehicle Parameters Validation System v{context['version']}*
*Source files: {', '.join(context['source_files'])}*
'''
        
        output_file = self.output_dir / "protocols.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(protocols_content)
        
        logger.info(f"Generated protocols overview: {output_file}")
    
    def generate_protocol_detail_pages(self) -> None:
        """Generate individual protocol detail pages"""
        logger.info("Generating protocol detail pages...")
        
        for group in self.protocols_data.get('protocol_groups', []):
            group_name = group.get('group_name', '')
            group_id = group.get('id')
            
            # Get protocols in this group
            group_protocols = [p for p in self.protocols_data.get('protocols', []) 
                             if p.get('group_id') == group_id]
            
            if not group_protocols:
                continue
            
            # Generate protocol detail page
            content = self._generate_protocol_detail_content(group, group_protocols)
            
            output_file = self.output_dir / "protocols" / f"{group_name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated {len(self.protocols_data.get('protocol_groups', []))} protocol detail pages")
    
    def _generate_protocol_detail_content(self, group: Dict[str, Any], protocols: List[Dict[str, Any]]) -> str:
        """Generate protocol detail page content"""
        context = self._get_template_context()
        group_name = group.get('group_name', '')
        param_ref = group.get('parameter_reference', '')
        
        content = f'''<!-- Mark headers for Confluence integration -->
<ac:structured-macro ac:name="info">
<ac:parameter name="title">{group_name} Protocol Details</ac:parameter>
<ac:rich-text-body>
<p>Auto-generated from vehicle parameters YAML - Last updated: {context['timestamp']}</p>
</ac:rich-text-body>
</ac:structured-macro>

# {group_name} Protocol Details

## Overview
- **Protocol Group:** {group_name}
- **Parameter Reference:** [{param_ref}](../details/{param_ref.lower().replace(' ', '_').replace('-', '_')}.md)
- **Protocol Count:** {len(protocols)}

## Protocol Details

| ABBR | Protocol | Standard | PGN/PID | SPN | Precision | Range | Units |
|------|----------|----------|---------|-----|-----------|-------|-------|
'''
        
        for protocol in protocols:
            abbr = protocol.get('abbr', 'N/A')
            standard = protocol.get('protocol_standard', 'N/A')
            pgn_pid = protocol.get('pgn_pid', 'N/A')
            spn = protocol.get('spn', 'N/A')
            precision = protocol.get('precision', 'N/A')
            spec_range = protocol.get('spec_range', 'N/A')
            units = protocol.get('units', 'N/A')
            
            content += f"| {abbr} | {abbr} | {standard} | {pgn_pid} | {spn} | {precision} | {spec_range} | {units} |\n"
        
        content += f'''

## Navigation
- [← Back to Protocols Overview](../protocols.md)
- [→ View All Parameters](../parameters.md)

---
*Generated by Vehicle Parameters Validation System v{context['version']}*
*Source files: {', '.join(context['source_files'])}*
'''
        
        return content
    
    def generate_all_markdown(self) -> None:
        """Generate all markdown files"""
        logger.info("Starting markdown generation...")
        
        try:
            self.generate_parameters_overview()
            self.generate_parameter_details()
            self.generate_protocols_overview()
            self.generate_protocol_detail_pages()
            
            logger.info(" All markdown files generated successfully!")
            logger.info(f"Output directory: {self.output_dir}")
            
        except Exception as e:
            logger.error(f" Error generating markdown: {e}")
            raise

def main():
    """Main function for standalone execution"""
    generator = MarkdownGenerator()
    generator.generate_all_markdown()

if __name__ == "__main__":
    main()