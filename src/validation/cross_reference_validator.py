"""
Cross-Reference Validator
Validates links and references between parameters.yaml and protocols.yaml files
"""

import yaml
from pathlib import Path


class CrossReferenceValidator:
    """Validates cross-references between parameter and protocol files"""
    
    def __init__(self):
        """Initialize cross-reference validator"""
        pass
    
    def validate_cross_references(self, parameters_file, protocols_file):
        """
        Validate cross-references between parameters and protocols files
        
        Args:
            parameters_file (str): Path to parameters.yaml
            protocols_file (str): Path to protocols.yaml
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            # Load both files
            parameters_data = self._load_yaml_file(parameters_file)
            protocols_data = self._load_yaml_file(protocols_file)
            
            errors = []
            
            # Validate parameter -> protocol references
            param_to_protocol_errors = self._validate_parameter_to_protocol_refs(
                parameters_data, protocols_data
            )
            errors.extend(param_to_protocol_errors)
            
            # Validate protocol -> parameter references
            protocol_to_param_errors = self._validate_protocol_to_parameter_refs(
                parameters_data, protocols_data
            )
            errors.extend(protocol_to_param_errors)
            
            # Validate parameter_id references within parameters file
            internal_ref_errors = self._validate_internal_parameter_refs(parameters_data)
            errors.extend(internal_ref_errors)
            
            # Validate group_id references within protocols file
            internal_protocol_errors = self._validate_internal_protocol_refs(protocols_data)
            errors.extend(internal_protocol_errors)
            
            return len(errors) == 0, errors if errors else ["Cross-reference validation passed"]
            
        except Exception as e:
            return False, [f"Cross-reference validation error: {e}"]
    
    def _load_yaml_file(self, file_path):
        """Load and parse YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error in {file_path}: {e}")
    
    def _validate_parameter_to_protocol_refs(self, parameters_data, protocols_data):
        """Validate parameter protocol_reference fields point to valid protocol groups"""
        errors = []
        
        # Get all protocol group names
        protocol_group_names = set()
        if 'protocol_groups' in protocols_data:
            for group in protocols_data['protocol_groups']:
                group_name = group.get('group_name')
                if group_name:
                    protocol_group_names.add(group_name)
        
        # Check each parameter's protocol_reference
        if 'parameters' in parameters_data:
            for param in parameters_data['parameters']:
                field_name = param.get('field_name', 'Unknown')
                protocol_ref = param.get('protocol_reference')
                
                if protocol_ref:
                    if protocol_ref not in protocol_group_names:
                        errors.append(
                            f"Parameter '{field_name}' references non-existent protocol group '{protocol_ref}'"
                        )
        
        return errors
    
    def _validate_protocol_to_parameter_refs(self, parameters_data, protocols_data):
        """Validate protocol group parameter_reference fields point to valid parameters"""
        errors = []
        
        # Get all parameter field names
        parameter_names = set()
        if 'parameters' in parameters_data:
            for param in parameters_data['parameters']:
                field_name = param.get('field_name')
                if field_name:
                    parameter_names.add(field_name)
        
        # Check each protocol group's parameter_reference
        if 'protocol_groups' in protocols_data:
            for group in protocols_data['protocol_groups']:
                group_name = group.get('group_name', 'Unknown')
                param_ref = group.get('parameter_reference')
                
                if param_ref:
                    if param_ref not in parameter_names:
                        errors.append(
                            f"Protocol group '{group_name}' references non-existent parameter '{param_ref}'"
                        )
        
        return errors
    
    def _validate_internal_parameter_refs(self, parameters_data):
        """Validate parameter_id references within parameters file"""
        errors = []
        
        # Get all parameter IDs
        parameter_ids = set()
        if 'parameters' in parameters_data:
            for param in parameters_data['parameters']:
                param_id = param.get('id')
                if param_id is not None:
                    parameter_ids.add(param_id)
        
        # Check breadcrumb_fields references
        if 'breadcrumb_fields' in parameters_data:
            for i, breadcrumb in enumerate(parameters_data['breadcrumb_fields']):
                param_id = breadcrumb.get('parameter_id')
                if param_id is not None and param_id not in parameter_ids:
                    errors.append(
                        f"Breadcrumb field {i+1} references non-existent parameter ID {param_id}"
                    )
        
        # Check vg5_fields references
        if 'vg5_fields' in parameters_data:
            for i, vg5 in enumerate(parameters_data['vg5_fields']):
                param_id = vg5.get('parameter_id')
                if param_id is not None and param_id not in parameter_ids:
                    errors.append(
                        f"VG5 field {i+1} references non-existent parameter ID {param_id}"
                    )
        
        # Check abbr_metrics references
        if 'abbr_metrics' in parameters_data:
            for i, abbr in enumerate(parameters_data['abbr_metrics']):
                param_id = abbr.get('parameter_id')
                if param_id is not None and param_id not in parameter_ids:
                    errors.append(
                        f"Abbreviation metric {i+1} references non-existent parameter ID {param_id}"
                    )
        
        return errors
    
    def _validate_internal_protocol_refs(self, protocols_data):
        """Validate group_id references within protocols file"""
        errors = []
        
        # Get all protocol group IDs
        group_ids = set()
        if 'protocol_groups' in protocols_data:
            for group in protocols_data['protocol_groups']:
                group_id = group.get('id')
                if group_id is not None:
                    group_ids.add(group_id)
        
        # Check protocols references
        if 'protocols' in protocols_data:
            for i, protocol in enumerate(protocols_data['protocols']):
                group_id = protocol.get('group_id')
                if group_id is not None and group_id not in group_ids:
                    errors.append(
                        f"Protocol {i+1} references non-existent protocol group ID {group_id}"
                    )
        
        return errors
    
    def validate_bidirectional_consistency(self, parameters_file, protocols_file):
        """
        Validate that cross-references are bidirectionally consistent
        
        Args:
            parameters_file (str): Path to parameters.yaml
            protocols_file (str): Path to protocols.yaml
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            parameters_data = self._load_yaml_file(parameters_file)
            protocols_data = self._load_yaml_file(protocols_file)
            
            errors = []
            
            # Build mapping of parameter names to protocol references
            param_to_protocol = {}
            if 'parameters' in parameters_data:
                for param in parameters_data['parameters']:
                    field_name = param.get('field_name')
                    protocol_ref = param.get('protocol_reference')
                    if field_name and protocol_ref:
                        param_to_protocol[field_name] = protocol_ref
            
            # Build mapping of protocol groups to parameter references
            protocol_to_param = {}
            if 'protocol_groups' in protocols_data:
                for group in protocols_data['protocol_groups']:
                    group_name = group.get('group_name')
                    param_ref = group.get('parameter_reference')
                    if group_name and param_ref:
                        protocol_to_param[group_name] = param_ref
            
            # Check bidirectional consistency
            for param_name, protocol_name in param_to_protocol.items():
                # Check if protocol group exists and points back to this parameter
                if protocol_name in protocol_to_param:
                    expected_param = protocol_to_param[protocol_name]
                    if expected_param != param_name:
                        errors.append(
                            f"Bidirectional inconsistency: Parameter '{param_name}' "
                            f"references protocol '{protocol_name}', but protocol "
                            f"references parameter '{expected_param}'"
                        )
                else:
                    errors.append(
                        f"Parameter '{param_name}' references protocol '{protocol_name}' "
                        f"but protocol group does not exist"
                    )
            
            # Check for orphaned protocol groups
            for protocol_name, param_name in protocol_to_param.items():
                if param_name not in param_to_protocol:
                    errors.append(
                        f"Protocol group '{protocol_name}' references parameter "
                        f"'{param_name}' but parameter does not exist"
                    )
                elif param_to_protocol[param_name] != protocol_name:
                    errors.append(
                        f"Protocol group '{protocol_name}' references parameter "
                        f"'{param_name}' but parameter references different protocol"
                    )
            
            return len(errors) == 0, errors if errors else ["Bidirectional consistency validation passed"]
            
        except Exception as e:
            return False, [f"Bidirectional consistency validation error: {e}"]
    
    def get_reference_summary(self, parameters_file, protocols_file):
        """
        Get a summary of all cross-references
        
        Args:
            parameters_file (str): Path to parameters.yaml
            protocols_file (str): Path to protocols.yaml
            
        Returns:
            dict: Summary of references
        """
        try:
            parameters_data = self._load_yaml_file(parameters_file)
            protocols_data = self._load_yaml_file(protocols_file)
            
            summary = {
                'parameter_count': len(parameters_data.get('parameters', [])),
                'protocol_group_count': len(protocols_data.get('protocol_groups', [])),
                'protocol_count': len(protocols_data.get('protocols', [])),
                'breadcrumb_count': len(parameters_data.get('breadcrumb_fields', [])),
                'vg5_count': len(parameters_data.get('vg5_fields', [])),
                'abbr_metrics_count': len(parameters_data.get('abbr_metrics', [])),
                'parameter_to_protocol_refs': {},
                'protocol_to_parameter_refs': {}
            }
            
            # Build reference mappings
            if 'parameters' in parameters_data:
                for param in parameters_data['parameters']:
                    field_name = param.get('field_name')
                    protocol_ref = param.get('protocol_reference')
                    if field_name and protocol_ref:
                        summary['parameter_to_protocol_refs'][field_name] = protocol_ref
            
            if 'protocol_groups' in protocols_data:
                for group in protocols_data['protocol_groups']:
                    group_name = group.get('group_name')
                    param_ref = group.get('parameter_reference')
                    if group_name and param_ref:
                        summary['protocol_to_parameter_refs'][group_name] = param_ref
            
            return summary
            
        except Exception as e:
            return {'error': f"Error generating summary: {e}"}


# Example usage and testing
if __name__ == "__main__":
    # Test the cross-reference validator
    validator = CrossReferenceValidator()
    
    print("Testing Cross-Reference Validator...")
    
    parameters_file = "data/parameters.yaml"
    protocols_file = "data/protocols.yaml"
    
    if Path(parameters_file).exists() and Path(protocols_file).exists():
        # Test cross-references
        is_valid, messages = validator.validate_cross_references(parameters_file, protocols_file)
        print(f"\nCross-References: {'✅ VALID' if is_valid else '❌ INVALID'}")
        for msg in messages:
            print(f"  - {msg}")
        
        # Test bidirectional consistency
        is_consistent, consistency_messages = validator.validate_bidirectional_consistency(
            parameters_file, protocols_file
        )
        print(f"\nBidirectional Consistency: {'✅ VALID' if is_consistent else '❌ INVALID'}")
        for msg in consistency_messages:
            print(f"  - {msg}")
        
        # Get reference summary
        summary = validator.get_reference_summary(parameters_file, protocols_file)
        print(f"\nReference Summary:")
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k} -> {v}")
            else:
                print(f"  {key}: {value}")
    
    else:
        print(f"\nSkipping tests - files not found:")
        print(f"  {parameters_file}: {'✅' if Path(parameters_file).exists() else '❌'}")
        print(f"  {protocols_file}: {'✅' if Path(protocols_file).exists() else '❌'}")