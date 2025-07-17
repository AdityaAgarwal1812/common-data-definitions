"""
Custom Business Logic Validator
Handles validation rules specific to vehicle parameters and protocols
"""

import yaml
from urllib.parse import urlparse
from pathlib import Path


class CustomValidator:
    """Custom validation for business logic and domain-specific rules"""
    
    def __init__(self):
        """Initialize validator with business rules"""
        self.valid_protocol_standards = ['J1939', 'J1587', 'J1979']
        self.valid_reasons = [
            'ELD Mandate', 
            'Driver Performance', 
            'Driver Scorecard', 
            'Safety', 
            'Engine Insight', 
            'Value add for customer',
            'Safety_Monitoring'
        ]
    
    def validate_parameters_business_logic(self, yaml_file_path):
        """
        Validate parameters file against custom business rules
        
        Args:
            yaml_file_path (str): Path to parameters.yaml file
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            errors = []
            
            # Check for duplicate IDs
            if 'parameters' in data:
                errors.extend(self._check_duplicate_parameter_ids(data['parameters']))
                errors.extend(self._check_duplicate_parameter_names(data['parameters']))
                
                # Validate each parameter
                for i, param in enumerate(data['parameters']):
                    param_errors = self._validate_single_parameter(param, i + 1)
                    errors.extend(param_errors)
            
            # Validate breadcrumb fields
            if 'breadcrumb_fields' in data:
                breadcrumb_errors = self._validate_breadcrumb_fields(data['breadcrumb_fields'])
                errors.extend(breadcrumb_errors)
            
            # Validate VG5 fields
            if 'vg5_fields' in data:
                vg5_errors = self._validate_vg5_fields(data['vg5_fields'])
                errors.extend(vg5_errors)
            
            # Validate abbreviation metrics
            if 'abbr_metrics' in data:
                abbr_errors = self._validate_abbr_metrics(data['abbr_metrics'])
                errors.extend(abbr_errors)
            
            return len(errors) == 0, errors if errors else ["Custom validation passed"]
            
        except Exception as e:
            return False, [f"Custom validation error: {e}"]
    
    def validate_protocols_business_logic(self, yaml_file_path):
        """
        Validate protocols file against custom business rules
        
        Args:
            yaml_file_path (str): Path to protocols.yaml file
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            errors = []
            
            # Check protocol groups
            if 'protocol_groups' in data:
                errors.extend(self._check_duplicate_group_ids(data['protocol_groups']))
                errors.extend(self._check_duplicate_group_names(data['protocol_groups']))
            
            # Check protocols
            if 'protocols' in data:
                for i, protocol in enumerate(data['protocols']):
                    protocol_errors = self._validate_single_protocol(protocol, i + 1)
                    errors.extend(protocol_errors)
            
            return len(errors) == 0, errors if errors else ["Custom validation passed"]
            
        except Exception as e:
            return False, [f"Custom validation error: {e}"]
    
    def _check_duplicate_parameter_ids(self, parameters):
        """Check for duplicate parameter IDs"""
        errors = []
        seen_ids = set()
        
        for param in parameters:
            param_id = param.get('id')
            if param_id in seen_ids:
                errors.append(f"Duplicate parameter ID: {param_id}")
            else:
                seen_ids.add(param_id)
        
        return errors
    
    def _check_duplicate_parameter_names(self, parameters):
        """Check for duplicate parameter field names"""
        errors = []
        seen_names = set()
        
        for param in parameters:
            field_name = param.get('field_name')
            if field_name in seen_names:
                errors.append(f"Duplicate parameter field_name: '{field_name}'")
            else:
                seen_names.add(field_name)
        
        return errors
    
    def _validate_single_parameter(self, param, param_num):
        """Validate a single parameter against business rules"""
        errors = []
        field_name = param.get('field_name', f'Parameter {param_num}')
        
        # Validate protobuf field naming convention
        protobuf_field = param.get('protobuf_field', '')
        if protobuf_field and not self._is_valid_snake_case(protobuf_field):
            errors.append(f"Parameter '{field_name}': protobuf_field must be in snake_case")
        
        # Validate reason_added
        reason_added = param.get('reason_added', '')
        if reason_added and reason_added not in self.valid_reasons:
            errors.append(f"Parameter '{field_name}': invalid reason_added '{reason_added}'. Must be one of: {', '.join(self.valid_reasons)}")
        
        # Validate protocol_reference format
        protocol_ref = param.get('protocol_reference', '')
        if protocol_ref and not protocol_ref.endswith('_protocols'):
            errors.append(f"Parameter '{field_name}': protocol_reference must end with '_protocols'")
        
        return errors
    
    def _validate_breadcrumb_fields(self, breadcrumb_fields):
        """Validate breadcrumb fields"""
        errors = []
        
        for i, breadcrumb in enumerate(breadcrumb_fields):
            # Validate URL format and domain
            link = breadcrumb.get('breadcrumb_link', '')
            if link and not self._is_valid_motive_docs_url(link):
                errors.append(f"Breadcrumb {i+1}: invalid URL or not from docs.motive.com domain")
        
        return errors
    
    def _validate_vg5_fields(self, vg5_fields):
        """Validate VG5 fields"""
        errors = []
        
        for i, vg5 in enumerate(vg5_fields):
            # Validate VG5 URL format
            link = vg5.get('vg5_link', '')
            if link and not self._is_valid_vg5_url(link):
                errors.append(f"VG5 field {i+1}: invalid URL or not from docs.motive.com/vg5/ path")
        
        return errors
    
    def _validate_abbr_metrics(self, abbr_metrics):
        """Validate abbreviation metrics"""
        errors = []
        
        for i, abbr in enumerate(abbr_metrics):
            # Validate abbreviation format (2-6 uppercase letters)
            abbr_value = abbr.get('abbr_value', '')
            if abbr_value and not self._is_valid_abbreviation(abbr_value):
                errors.append(f"Abbreviation {i+1}: '{abbr_value}' must be 2-6 uppercase letters")
            
            # Validate abbr_link domain
            abbr_link = abbr.get('abbr_link', '')
            if abbr_link and not self._is_valid_abbr_url(abbr_link):
                errors.append(f"Abbreviation {i+1}: abbr_link must be from docs.motive.com/abbr/ path")
            
            # Validate metrics_link domain
            metrics_link = abbr.get('metrics_link', '')
            if metrics_link and not self._is_valid_metrics_url(metrics_link):
                errors.append(f"Abbreviation {i+1}: metrics_link must be from redash.motive.com domain")
        
        return errors
    
    def _check_duplicate_group_ids(self, protocol_groups):
        """Check for duplicate protocol group IDs"""
        errors = []
        seen_ids = set()
        
        for group in protocol_groups:
            group_id = group.get('id')
            if group_id in seen_ids:
                errors.append(f"Duplicate protocol group ID: {group_id}")
            else:
                seen_ids.add(group_id)
        
        return errors
    
    def _check_duplicate_group_names(self, protocol_groups):
        """Check for duplicate protocol group names"""
        errors = []
        seen_names = set()
        
        for group in protocol_groups:
            group_name = group.get('group_name')
            if group_name in seen_names:
                errors.append(f"Duplicate protocol group name: '{group_name}'")
            else:
                seen_names.add(group_name)
        
        return errors
    
    def _validate_single_protocol(self, protocol, protocol_num):
        """Validate a single protocol against business rules"""
        errors = []
        
        # Validate protocol standard
        standard = protocol.get('protocol_standard', '')
        if standard and standard not in self.valid_protocol_standards:
            errors.append(f"Protocol {protocol_num}: invalid protocol_standard '{standard}'. Must be one of: {', '.join(self.valid_protocol_standards)}")
        
        # Validate abbreviation format
        abbr = protocol.get('abbr', '')
        if abbr and not self._is_valid_abbreviation(abbr):
            errors.append(f"Protocol {protocol_num}: abbreviation '{abbr}' must be 2-6 uppercase letters")
        
        # Validate PGN/PID format based on protocol standard
        if standard == 'J1939':
            pgn_pid = protocol.get('pgn_pid', '')
            if pgn_pid and not pgn_pid.isdigit():
                errors.append(f"Protocol {protocol_num}: J1939 pgn_pid should be numeric (e.g., '61444')")
        
        elif standard == 'J1979':
            pgn_pid = protocol.get('pgn_pid', '')
            if pgn_pid and not self._is_valid_j1979_pid(pgn_pid):
                errors.append(f"Protocol {protocol_num}: J1979 pgn_pid should be hex format (e.g., '0x0C/0xF40C')")
        
        return errors
    
    def _is_valid_snake_case(self, text):
        """Check if text follows snake_case convention"""
        import re
        return bool(re.match(r'^[a-z][a-z0-9_]*[a-z0-9]$', text))
    
    def _is_valid_abbreviation(self, text):
        """Check if text is a valid abbreviation (2-6 uppercase letters)"""
        import re
        return bool(re.match(r'^[A-Z]{2,6}$', text))
    
    def _is_valid_motive_docs_url(self, url):
        """Check if URL is from docs.motive.com domain"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and 'docs.motive.com' in parsed.netloc
        except:
            return False
    
    def _is_valid_vg5_url(self, url):
        """Check if URL is from docs.motive.com/vg5/ path"""
        try:
            parsed = urlparse(url)
            return (parsed.scheme in ['http', 'https'] and 
                   'docs.motive.com' in parsed.netloc and 
                   '/vg5/' in parsed.path)
        except:
            return False
    
    def _is_valid_abbr_url(self, url):
        """Check if URL is from docs.motive.com/abbr/ path"""
        try:
            parsed = urlparse(url)
            return (parsed.scheme in ['http', 'https'] and 
                   'docs.motive.com' in parsed.netloc and 
                   '/abbr/' in parsed.path)
        except:
            return False
    
    def _is_valid_metrics_url(self, url):
        """Check if URL is from redash.motive.com domain"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and 'redash.motive.com' in parsed.netloc
        except:
            return False
    
    def _is_valid_j1979_pid(self, pid):
        """Check if PID follows J1979 hex format"""
        import re
        return bool(re.match(r'^0x[0-9A-F]+(/0x[0-9A-F]+)?$', pid))
    
    def check_url_accessibility(self, url, timeout=5):
        """
        Check if URL is accessible (optional feature)
        Note: Requires 'requests' package. Install with: pip install requests
        
        Args:
            url (str): URL to check
            timeout (int): Request timeout in seconds
            
        Returns:
            tuple: (is_accessible, status_message)
        """
        try:
            # Optional feature - only works if requests is installed
            import requests
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return True, f"URL accessible (status: {response.status_code})"
            else:
                return False, f"URL returned status: {response.status_code}"
        except ImportError:
            return True, "URL accessibility check skipped (requests not installed)"
        except Exception as e:
            return False, f"Error checking URL: {e}"


# Example usage and testing
if __name__ == "__main__":
    # Test the custom validator
    validator = CustomValidator()
    
    print("Testing Custom Validator...")
    
    # Test with sample files (if they exist)
    test_files = [
        ("data/parameters.yaml", validator.validate_parameters_business_logic),
        ("data/protocols.yaml", validator.validate_protocols_business_logic)
    ]
    
    for file_path, validate_func in test_files:
        if Path(file_path).exists():
            is_valid, messages = validate_func(file_path)
            print(f"\n{file_path}: {'✅ VALID' if is_valid else '❌ INVALID'}")
            for msg in messages:
                print(f"  - {msg}")
        else:
            print(f"\n{file_path}: File not found (skipping)")
    
    # Test URL accessibility (example)
    test_url = "https://docs.motive.com"
    is_accessible, status = validator.check_url_accessibility(test_url)
    print(f"\nURL Test ({test_url}): {'✅ ACCESSIBLE' if is_accessible else '❌ NOT ACCESSIBLE'}")
    print(f"  - {status}")