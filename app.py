#!/usr/bin/env python3
"""
Enhanced Vehicle Parameters API with Validation
Original UI + Enhanced validation system
"""

import sys
import os
from pathlib import Path
import json

# Add validation system to path
sys.path.insert(0, 'src')

# Import Flask functionality (same as original)
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import yaml
import sqlite3

# Import new validation system
from validation.main_validator import MainValidator

# Flask app setup (same as original)
app = Flask(__name__)
api = Api(app, version='1.0', title='Vehicle Parameters API', 
          description='Enhanced with Validation - Parameters & Protocols',
          doc='/docs')

# Use the validated database
DATABASE_NAME = 'output/vehicle_params.db'

# ============================================================================
# NEW VALIDATION FUNCTIONS (Added functionality)
# ============================================================================

def validate_yaml_files():
    """Validate YAML files before any database operations"""
    try:
        validator = MainValidator()
        results = validator.validate_all(
            parameters_file='data/parameters.yaml',
            protocols_file='data/protocols.yaml',
            verbose=False
        )
        return results
    except Exception as e:
        return {'overall_valid': False, 'errors': [str(e)]}

def ensure_database_exists():
    """Ensure validated database exists"""
    if not Path(DATABASE_NAME).exists():
        print("🔧 Database not found, generating from validated YAML...")
        
        try:
            from generators.database_generator import DatabaseGenerator
            
            generator = DatabaseGenerator(DATABASE_NAME)
            success, message = generator.generate_database(
                'data/parameters.yaml',
                'data/protocols.yaml'
            )
            
            if success:
                print(f"{message}")
                return True
            else:
                print(f" {message}")
                return False
        except Exception as e:
            print(f" Database generation error: {e}")
            return False
    else:
        return True

def add_new_parameter_with_validation(new_parameter_data):
    """Add new parameter with validation"""
    try:
        # Step 1: Validate new data first
        validator = MainValidator()
        is_valid, error_messages = validator.validate_new_parameter_data(new_parameter_data)
        
        if not is_valid:
            return False, error_messages
        
        # Step 2: Add to YAML file
        with open('data/parameters.yaml', 'r', encoding='utf-8') as f:
            existing_data = yaml.safe_load(f)
        
        # Check for duplicates
        existing_ids = [p['id'] for p in existing_data.get('parameters', [])]
        existing_names = [p['field_name'] for p in existing_data.get('parameters', [])]
        
        for param in new_parameter_data.get('parameters', []):
            if param['id'] in existing_ids:
                return False, [f"Parameter ID {param['id']} already exists"]
            if param['field_name'] in existing_names:
                return False, [f"Parameter name '{param['field_name']}' already exists"]
        
        # Add new data
        if 'parameters' in new_parameter_data:
            existing_data.setdefault('parameters', []).extend(new_parameter_data['parameters'])
        
        if 'breadcrumb_fields' in new_parameter_data:
            existing_data.setdefault('breadcrumb_fields', []).extend(new_parameter_data['breadcrumb_fields'])
        
        if 'vg5_fields' in new_parameter_data:
            existing_data.setdefault('vg5_fields', []).extend(new_parameter_data['vg5_fields'])
        
        if 'abbr_metrics' in new_parameter_data:
            existing_data.setdefault('abbr_metrics', []).extend(new_parameter_data['abbr_metrics'])
        
        # Write back to YAML
        with open('data/parameters.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print("✅ Successfully added new parameter to YAML")
        
        # Step 3: Regenerate database
        regenerate_database()
        
        return True, ["Parameter added successfully and database regenerated"]
        
    except Exception as e:
        return False, [f"Error adding parameter: {e}"]

def regenerate_database():
    """Regenerate database after YAML changes"""
    try:
        from generators.database_generator import DatabaseGenerator
        
        generator = DatabaseGenerator(DATABASE_NAME)
        success, message = generator.generate_database(
            'data/parameters.yaml',
            'data/protocols.yaml'
        )
        
        if success:
            print(f" Database regenerated: {message}")
        else:
            print(f" Database regeneration failed: {message}")
    except Exception as e:
        print(f" Database regeneration error: {e}")

def add_new_protocol_with_validation(new_protocol_data):
    """Add new protocol with validation"""
    try:
        # Step 1: Validate new data first
        validator = MainValidator()
        is_valid, error_messages = validator.validate_new_protocol_data(new_protocol_data)
        
        if not is_valid:
            return False, error_messages
        
        # Step 2: Add to YAML file
        with open('data/protocols.yaml', 'r', encoding='utf-8') as f:
            existing_data = yaml.safe_load(f)
        
        # Check for duplicates in protocol groups
        existing_group_ids = [g['id'] for g in existing_data.get('protocol_groups', [])]
        existing_group_names = [g['group_name'] for g in existing_data.get('protocol_groups', [])]
        
        for group in new_protocol_data.get('protocol_groups', []):
            if group['id'] in existing_group_ids:
                return False, [f"Protocol group ID {group['id']} already exists"]
            if group['group_name'] in existing_group_names:
                return False, [f"Protocol group name '{group['group_name']}' already exists"]
        
        # Add new data
        if 'protocol_groups' in new_protocol_data:
            existing_data.setdefault('protocol_groups', []).extend(new_protocol_data['protocol_groups'])
        
        if 'protocols' in new_protocol_data:
            existing_data.setdefault('protocols', []).extend(new_protocol_data['protocols'])
        
        # Write back to YAML
        with open('data/protocols.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print(" Successfully added new protocol to YAML")
        
        # Step 3: Regenerate database
        regenerate_database()
        
        return True, ["Protocol added successfully and database regenerated"]
        
    except Exception as e:
        return False, [f"Error adding protocol: {e}"]

def load_example_protocol_file():
    """Load and validate example protocol file"""
    try:
        with open('data/examples/new_protocol_example.yaml', 'r', encoding='utf-8') as f:
            example_data = yaml.safe_load(f)
        return example_data
    except Exception as e:
        return None

# ============================================================================
# ORIGINAL DATABASE FUNCTIONS (Preserved from original app.py)
# ============================================================================

def get_parameter_complete_data(field_name):
    """Get complete parameter data by linking parameters and protocols"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get parameter basic info
        cursor.execute("SELECT * FROM parameters WHERE field_name = ?", (field_name,))
        parameter = cursor.fetchone()
        
        if not parameter:
            return None
        
        param_id = parameter['id']
        protocol_reference = parameter['protocol_reference']
        
        # Get parameter-related data
        cursor.execute("SELECT * FROM breadcrumb_fields WHERE parameter_id = ?", (param_id,))
        breadcrumbs = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM vg5_fields WHERE parameter_id = ?", (param_id,))
        vg5_fields = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM abbr_metrics WHERE parameter_id = ?", (param_id,))
        abbr_metrics = [dict(row) for row in cursor.fetchall()]
        
        # Get protocol data by linking through protocol_reference
        cursor.execute("""
            SELECT p.*, pg.group_name, pg.description as group_description
            FROM protocols p
            JOIN protocol_groups pg ON p.group_id = pg.id
            WHERE pg.group_name = ?
        """, (protocol_reference,))
        protocols = [dict(row) for row in cursor.fetchall()]
        
        # Merge all data
        result = dict(parameter)
        result['breadcrumb_fields'] = breadcrumbs
        result['vg5_fields'] = vg5_fields
        result['abbr_metrics'] = abbr_metrics
        result['protocols'] = protocols
        
        return result
        
    except Exception as e:
        print(f" Database query error: {e}")
        return None
    finally:
        conn.close()

def get_all_parameters():
    """Get all parameter names and descriptions"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT field_name, description, protocol_reference FROM parameters ORDER BY id")
        parameters = [dict(row) for row in cursor.fetchall()]
        return parameters
    except Exception as e:
        print(f" Database query error: {e}")
        return []
    finally:
        conn.close()

# ============================================================================
# ORIGINAL SWAGGER MODELS (Preserved from original app.py)
# ============================================================================

parameter_model = api.model('Parameter', {
    'id': fields.Integer(description='Parameter ID'),
    'field_name': fields.String(description='Parameter name'),
    'reserved_enum_val': fields.Integer(description='Reserved enum value'),
    'description': fields.String(description='Parameter description'),
    'unit': fields.String(description='Unit specification'),
    'reason_added': fields.String(description='Reason for adding'),
    'protobuf_field': fields.String(description='Protobuf field name'),
    'protocol_reference': fields.String(description='Reference to protocol group'),
    'breadcrumb_fields': fields.List(fields.Raw, description='Breadcrumb field information'),
    'vg5_fields': fields.List(fields.Raw, description='VG5 field information'),
    'abbr_metrics': fields.List(fields.Raw, description='Abbreviation and metrics information'),
    'protocols': fields.List(fields.Raw, description='Protocol specifications from separate file')
})

# ============================================================================
# ORIGINAL API ROUTES (Preserved from original app.py)
# ============================================================================

@api.route('/parameters')
class ParametersList(Resource):
    def get(self):
        """Get all available parameters with protocol references"""
        parameters = get_all_parameters()
        
        # Add documentation links
        for param in parameters:
            field_name_url = param['field_name'].lower().replace(' ', '_')
            param['documentation_link'] = f"/docs/{field_name_url}"
            param['api_link'] = f"/parameters/{field_name_url}"
        
        return {
            'message': 'Available vehicle parameters from validated YAML files',
            'parameters': parameters,
            'total_count': len(parameters),
            'source_files': ['data/parameters.yaml', 'data/protocols.yaml'],
            'validation_status': 'All data validated before database creation'
        }

@api.route('/parameters/<string:field_name>')
class ParameterDetail(Resource):
    @api.marshal_with(parameter_model)
    def get(self, field_name):
        """Get complete parameter data with linked protocol information"""
        # Convert URL parameter back to proper field name
        proper_field_name = field_name.replace('_', ' ').title()
        
        data = get_parameter_complete_data(proper_field_name)
        if not data:
            api.abort(404, f"Parameter '{proper_field_name}' not found")
        
        return data

@api.route('/protocols')
class ProtocolsList(Resource):
    def get(self):
        """Get all protocol groups and their protocols"""
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT pg.*, COUNT(p.id) as protocol_count
                FROM protocol_groups pg
                LEFT JOIN protocols p ON pg.id = p.group_id
                GROUP BY pg.id
            """)
            groups = [dict(row) for row in cursor.fetchall()]
            
            return {
                'message': 'Available protocol groups from protocols.yaml',
                'protocol_groups': groups,
                'total_groups': len(groups)
            }
        except Exception as e:
            return {'error': f"Database query error: {e}"}, 500
        finally:
            conn.close()

@api.route('/protocols/<string:group_name>')
class ProtocolGroupDetail(Resource):
    def get(self, group_name):
        """Get detailed protocols for a specific group"""
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT p.*, pg.group_name, pg.description as group_description, pg.parameter_reference
                FROM protocols p
                JOIN protocol_groups pg ON p.group_id = pg.id
                WHERE pg.group_name = ?
            """, (group_name,))
            protocols = [dict(row) for row in cursor.fetchall()]
            
            if not protocols:
                api.abort(404, f"Protocol group '{group_name}' not found")
            
            return {
                'group_name': group_name,
                'parameter_reference': protocols[0]['parameter_reference'],
                'protocols': protocols,
                'protocol_count': len(protocols)
            }
        except Exception as e:
            return {'error': f"Database query error: {e}"}, 500
        finally:
            conn.close()

# ============================================================================
# NEW ENHANCED API ROUTES (Added functionality)
# ============================================================================


def load_example_parameter_file():
    """Load and validate example parameter file"""
    try:
        with open('data/examples/new_parameter_example.yaml', 'r', encoding='utf-8') as f:
            example_data = yaml.safe_load(f)
        return example_data
    except Exception as e:
        return None

def load_example_protocol_file():
    """Load and validate example protocol file"""
    try:
        with open('data/examples/new_protocol_example.yaml', 'r', encoding='utf-8') as f:
            example_data = yaml.safe_load(f)
        return example_data
    except Exception as e:
        return None


@api.route('/validate')
class ValidateData(Resource):
    def get(self):
        """Validate current YAML files"""
        try:
            results = validate_yaml_files()
            return {
                'overall_valid': results.get('overall_valid', False),
                'errors': results.get('errors', []),
                'warnings': results.get('warnings', []),
                'validation_duration': results.get('validation_duration_seconds', 0),
                'validation_steps': results.get('summary', {}),
                'timestamp': results.get('validation_timestamp', 'unknown')
            }
        except Exception as e:
            return {'error': f'Validation failed: {str(e)}'}, 500



@api.route('/add-parameter-from-file')
class AddParameterFromFile(Resource):
    def post(self):
        """Add parameter from example file with validation"""
        try:
            # Load example parameter file
            example_data = load_example_parameter_file()
            
            if not example_data:
                return {
                    'status': 'error',
                    'message': 'Could not load data/examples/new_parameter_example.yaml'
                }, 400
            
            # Validate current YAML files first
            validation_results = validate_yaml_files()
            if not validation_results.get('overall_valid', False):
                return {
                    'status': 'error',
                    'message': 'Current YAML files have validation errors',
                    'errors': validation_results.get('errors', [])
                }, 400
            
            # Add parameter with validation
            success, messages = add_new_parameter_with_validation(example_data)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Parameter from example file added successfully with validation',
                    'parameter': example_data['parameters'][0] if 'parameters' in example_data else None,
                    'validation_messages': messages,
                    'next_steps': [
                        'Parameter added to data/parameters.yaml',
                        'Database regenerated with new parameter',
                        'Validation passed for all files'
                    ]
                }
            else:
                return {
                    'status': 'error', 
                    'message': 'Parameter validation or addition failed',
                    'errors': messages
                }, 400
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }, 500
    
    def get(self):
        """Get example parameter file content"""
        try:
            example_data = load_example_parameter_file()
            if example_data:
                return {
                    'message': 'Example parameter file content',
                    'file_path': 'data/examples/new_parameter_example.yaml',
                    'content': example_data,
                    'usage': 'POST to this endpoint to add this parameter with validation'
                }
            else:
                return {
                    'message': 'Example file not found',
                    'file_path': 'data/examples/new_parameter_example.yaml',
                    'note': 'Create this file to test parameter addition'
                }, 404
        except Exception as e:
            return {'error': str(e)}, 500




@api.route('/add-protocol-from-file')
class AddProtocolFromFile(Resource):
    def post(self):
        """Add protocol from example file with validation"""
        try:
            # Load example protocol file
            example_data = load_example_protocol_file()
            
            if not example_data:
                return {
                    'status': 'error',
                    'message': 'Could not load data/examples/new_protocol_example.yaml'
                }, 400
            
            # Validate current YAML files first
            validation_results = validate_yaml_files()
            if not validation_results.get('overall_valid', False):
                return {
                    'status': 'error',
                    'message': 'Current YAML files have validation errors',
                    'errors': validation_results.get('errors', [])
                }, 400
            
            # Add protocol with validation
            success, messages = add_new_protocol_with_validation(example_data)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Protocol from example file added successfully with validation',
                    'protocol_groups': example_data.get('protocol_groups', []),
                    'protocols': example_data.get('protocols', []),
                    'validation_messages': messages,
                    'next_steps': [
                        'Protocol added to data/protocols.yaml',
                        'Database regenerated with new protocol',
                        'Validation passed for all files'
                    ]
                }
            else:
                return {
                    'status': 'error', 
                    'message': 'Protocol validation or addition failed',
                    'errors': messages
                }, 400
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }, 500
    
    def get(self):
        """Get example protocol file content"""
        try:
            example_data = load_example_protocol_file()
            if example_data:
                return {
                    'message': 'Example protocol file content',
                    'file_path': 'data/examples/new_protocol_example.yaml',
                    'content': example_data,
                    'usage': 'POST to this endpoint to add this protocol with validation'
                }
            else:
                return {
                    'message': 'Example file not found',
                    'file_path': 'data/examples/new_protocol_example.yaml',
                    'note': 'Create this file to test protocol addition'
                }, 404
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/status')
class SystemStatus(Resource):
    def get(self):
        """Get system status with validation info"""
        validation_results = validate_yaml_files()
        
        return {
            'status': 'running',
            'message': 'Vehicle Parameters API is running',
            'validation_system': 'active',
            'database': 'connected' if Path(DATABASE_NAME).exists() else 'not found',
            'yaml_files': {
                'parameters': Path('data/parameters.yaml').exists(),
                'protocols': Path('data/protocols.yaml').exists()
            },
            'current_validation_status': {
                'overall_valid': validation_results.get('overall_valid', False),
                'error_count': len(validation_results.get('errors', [])),
                'warning_count': len(validation_results.get('warnings', []))
            }
        }

# ============================================================================
# ORIGINAL DOCUMENTATION ROUTES (Preserved from original app.py)
# ============================================================================

@app.route('/docs/<string:field_name>')
def parameter_docs(field_name):
    """Custom documentation page for specific parameter"""
    proper_field_name = field_name.replace('_', ' ').title()
    
    data = get_parameter_complete_data(proper_field_name)
    if not data:
        return f"Parameter '{proper_field_name}' not found", 404
    
    # Generate HTML documentation (SAME AS ORIGINAL)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{proper_field_name} - Vehicle Parameter Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .section {{ margin: 20px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 5px; }}
            .api-section {{ background: #e8f5e9; border-left-color: #27ae60; }}
            .protocol-section {{ background: #fff3cd; border-left-color: #ffc107; }}
            .protocol-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            .protocol-table th, .protocol-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .protocol-table th {{ background-color: #f2f2f2; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .nav-links {{ text-align: center; margin-bottom: 20px; }}
            .nav-links a {{ margin: 0 15px; padding: 10px 20px; background: #3498db; color: white; border-radius: 5px; text-decoration: none; }}
            pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; white-space: pre-wrap; }}
            .source-info {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .validation-info {{ background: #cff4fc; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-links">
                <a href="/docs/">🏠 All Parameters</a>
                <a href="/docs">📊 Swagger API</a>
                <a href="/protocols">🔗 Protocol Groups</a>
                <a href="/validate">✅ Validate YAML</a>
            </div>
            
            <div class="source-info">
                <strong>📄 Data Sources:</strong> data/parameters.yaml + data/protocols.yaml (validated files)
            </div>
            
            <div class="validation-info">
                <strong>✅ Validation Status:</strong> All data validated with JSON Schema + Custom Logic + Cross-References
            </div>
            
            <div class="header">
                <h1>{proper_field_name}</h1>
                <p><strong>ID:</strong> {data['id']}</p>
                <p><strong>Reserved Enum Val:</strong> {data['reserved_enum_val']}</p>
                <p><strong>Description:</strong> {data['description']}</p>
                <pre><strong>Unit:</strong> {data['unit']}</pre>
                <p><strong>Reason Added:</strong> {data['reason_added']}</p>
                <p><strong>Protobuf Field:</strong> {data['protobuf_field']}</p>
                <p><strong>Protocol Reference:</strong> {data['protocol_reference']}</p>
            </div>
            
            <div class="section api-section">
                <h3>🚀 API Endpoints</h3>
                <p><strong>Get Parameter Data:</strong></p>
                <code>GET /parameters/{field_name.lower()}</code>
                <br><br>
                <p><strong>Get Protocol Data:</strong></p>
                <code>GET /protocols/{data['protocol_reference']}</code>
                <br><br>
                <p><strong>Validate YAML Files:</strong></p>
                <code>GET /validate</code>
                <br><br>
                <a href="/parameters/{field_name.lower()}" target="_blank">🔗 Try Parameter API</a>
                <a href="/protocols/{data['protocol_reference']}" target="_blank" style="margin-left: 15px;">🔗 Try Protocol API</a>
                <a href="/validate" target="_blank" style="margin-left: 15px;">✅ Validate YAML</a>
            </div>
            
            <div class="section">
                <h3>📋 Breadcrumb Fields</h3>
    """
    
    for breadcrumb in data['breadcrumb_fields']:
        html += f"""
                <p><strong>Link:</strong> <a href="{breadcrumb['breadcrumb_link']}" target="_blank">{breadcrumb['breadcrumb_link']}</a></p>
                <p><strong>Note:</strong> {breadcrumb['note']}</p>
                <hr>
        """
    
    html += """
            </div>
            
            <div class="section">
                <h3>🔗 VG5 Fields</h3>
    """
    
    for vg5 in data['vg5_fields']:
        html += f"""
                <p><a href="{vg5['vg5_link']}" target="_blank">{vg5['vg5_link']}</a></p>
        """
    
    html += """
            </div>
            
            <div class="section">
                <h3>📊 Abbreviations & Metrics</h3>
    """
    
    for abbr in data['abbr_metrics']:
        html += f"""
                <p><strong>{abbr['abbr_value']}:</strong> 
                   <a href="{abbr['abbr_link']}" target="_blank">Documentation</a> | 
                   <a href="{abbr['metrics_link']}" target="_blank">Metrics Dashboard</a>
                </p>
        """
    
    html += f"""
            </div>
            
            <div class="section protocol-section">
                <h3>📡 Protocol Details (from protocols.yaml)</h3>
                <p><strong>Protocol Group:</strong> {data['protocol_reference']}</p>
                <table class="protocol-table">
                    <thead>
                        <tr>
                            <th>Standard</th>
                            <th>PGN/PID</th>
                            <th>SPN</th>
                            <th>Precision</th>
                            <th>Range</th>
                            <th>Max Valid</th>
                            <th>Units</th>
                            <th>Description</th>
                            <th>States</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for protocol in data['protocols']:
        states_display = protocol['states'].replace('\n', '<br>') if protocol['states'] else '-'
        html += f"""
                        <tr>
                            <td>{protocol['protocol_standard']}</td>
                            <td>{protocol['pgn_pid']}</td>
                            <td>{protocol['spn']}</td>
                            <td>{protocol['precision']}</td>
                            <td>{protocol['spec_range']}</td>
                            <td>{protocol['max_valid_val']}</td>
                            <td>{protocol['units']}</td>
                            <td>{protocol['description']}</td>
                            <td>{states_display}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/docs/')
def main_docs():
    """Main documentation page with links to all parameters"""
    parameters = get_all_parameters()
    
    # Get validation status
    validation_results = validate_yaml_files()
    validation_status = "✅ Valid" if validation_results.get('overall_valid', False) else "❌ Invalid"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vehicle Parameters Documentation - Enhanced with Validation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: #34495e; color: white; padding: 20px; border-radius: 5px; margin-bottom: 30px; text-align: center; }}
            .param-card {{ margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #3498db; }}
            .param-card a {{ color: #3498db; text-decoration: none; font-weight: bold; font-size: 18px; }}
            .param-card a:hover {{ text-decoration: underline; }}
            .description {{ margin-top: 10px; color: #666; }}
            .protocol-ref {{ margin-top: 5px; font-size: 12px; color: #888; }}
            .stats {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .validation-panel {{ background: #cff4fc; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .add-param-panel {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .btn {{ padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; text-decoration: none; margin: 5px; display: inline-block; }}
            .btn-success {{ background: #27ae60; }}
            .btn-warning {{ background: #f39c12; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 Vehicle Parameters Documentation</h1>
                <p>Enhanced with Validation System</p>
                <a href="/docs" class="btn">📊 Swagger API Documentation</a>
                <a href="/protocols" class="btn">🔗 Protocol Groups</a>
                <a href="/validate" class="btn btn-success">✅ Validate YAML</a>
                <a href="/status" class="btn btn-warning">📊 System Status</a>
            </div>
            
            <div class="validation-panel">
                <h3>🔍 Validation Status</h3>
                <p><strong>Current Status:</strong> {validation_status}</p>
                <p><strong>Error Count:</strong> {len(validation_results.get('errors', []))}</p>
                <p><strong>Warning Count:</strong> {len(validation_results.get('warnings', []))}</p>
                <a href="/validate" class="btn btn-success">🔍 Check Validation Details</a>
            </div>
            
            <div class="add-param-panel">
                <h3>➕ Add New Parameter</h3>
                <p>Add new parameters from example file with full validation</p>
                <a href="/add-parameter-from-file" class="btn btn-warning">📄 View Parameter Example</a>
                <button onclick="addParameterFromFile()" class="btn btn-success">➕ Add Parameter from File</button>
            </div>
            
            <div class="add-param-panel">
                <h3>🔧 Add New Protocol</h3>
                <p>Add new protocols from example file with full validation</p>
                <a href="/add-protocol-from-file" class="btn btn-warning">📄 View Protocol Example</a>
                <button onclick="addProtocolFromFile()" class="btn btn-success">🔧 Add Protocol from File</button>
            
                
                <script>
                function addParameterFromFile() {{
                    if (confirm('Add parameter from data/examples/new_parameter_example.yaml?')) {{
                        fetch('/add-parameter-from-file', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }}
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.status === 'success') {{
                                alert('Parameter added successfully!\\n\\n' + data.message + '\\n\\nParameter: ' + data.parameter.field_name);
                                location.reload();
                            }} else {{
                                alert('Error adding parameter:\\n\\n' + data.message + '\\n\\nErrors: ' + JSON.stringify(data.errors, null, 2));
                            }}
                        }})
                        .catch(error => alert('Error: ' + error));
                    }}
                }}
                
                function addProtocolFromFile() {{
                    if (confirm('Add protocol from data/examples/new_protocol_example.yaml?')) {{
                        fetch('/add-protocol-from-file', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }}
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.status === 'success') {{
                                alert('Protocol added successfully!\\n\\n' + data.message + '\\n\\nProtocol Groups: ' + data.protocol_groups.length);
                                location.reload();
                            }} else {{
                                alert('Error adding protocol:\\n\\n' + data.message + '\\n\\nErrors: ' + JSON.stringify(data.errors, null, 2));
                            }}
                        }})
                        .catch(error => alert('Error: ' + error));
                    }}
                }}
                </script>
            </div>
            
            <div class="stats">
                <h3>📊 Statistics</h3>
                <p><strong>Total Parameters:</strong> {len(parameters)}</p>
                <p><strong>Data Sources:</strong> data/parameters.yaml + data/protocols.yaml</p>
                <p><strong>Validation:</strong> JSON Schema + Custom Logic + Cross-References</p>
            </div>
    """
    
    for param in parameters:
        field_name_url = param['field_name'].lower().replace(' ', '_')
        html += f"""
            <div class="param-card">
                <a href="/docs/{field_name_url}">{param['field_name']}</a>
                <div class="description">{param['description']}</div>
                <div class="protocol-ref">Protocol Reference: {param['protocol_reference']}</div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

# ============================================================================
# ORIGINAL INITIALIZATION (Preserved from original app.py)
# ============================================================================

def initialize_database():
    """Initialize database from validated YAML files"""
    print(" Initializing Vehicle Parameters Database with Enhanced Validation...")
    
    # Step 1: Validate YAML files first
    print("🔍 Validating YAML files...")
    validation_results = validate_yaml_files()
    if validation_results.get('overall_valid', False):
        print(" YAML validation passed")
    else:
        print(" YAML validation has issues:")
        for error in validation_results.get('errors', []):
            print(f"  - {error}")
    
    # Step 2: Ensure database exists
    print(" Checking database...")
    if ensure_database_exists():
        print(" Database ready")
    else:
        print(" Database issues detected")
    
    print(" Database initialization completed!")
    return True

if __name__ == '__main__':
    print(" Vehicle Parameters API - Enhanced with Validation System")
    print("=" * 80)
    
    # Initialize database on startup
    if initialize_database():
        print()
        print(" Available URLs:")
        print("   Main Documentation: http://localhost:5000/docs/")
        print("   Swagger API:        http://localhost:5000/docs")
        print("   Protocol Groups:    http://localhost:5000/protocols")
        print("   Validation Status:  http://localhost:5000/validate")
        print("   System Status:      http://localhost:5000/status")
        print("   Add Parameter:      http://localhost:5000/add-parameter-from-file")
        print("   Add Protocol:       http://localhost:5000/add-protocol-from-file")
        print()
       
        print(" API Endpoints:")
        print("   All Parameters:     http://localhost:5000/parameters")
        print("   All Protocols:      http://localhost:5000/protocols")
        print("   Engine Speed Data:  http://localhost:5000/parameters/engine_speed")
        print("   Engine Protocols:   http://localhost:5000/protocols/ESPD_protocols")
        print("   Road Speed Data:    http://localhost:5000/parameters/road_speed")
        print("   Road Protocols:     http://localhost:5000/protocols/RSPD_protocols")
        print()
        print(" Test Commands:")
        print("   curl http://localhost:5000/parameters")
        print("   curl http://localhost:5000/protocols")
        print("   curl http://localhost:5000/validate")
        print("   curl http://localhost:5000/status")
        print("   curl http://localhost:5000/add-parameter-from-file")
        print("   curl http://localhost:5000/add-protocol-from-file")
        print("   curl -X POST http://localhost:5000/add-parameter-from-file")
        print("   curl -X POST http://localhost:5000/add-protocol-from-file")
        print()
        print(" Features:")
        print("    Original UI and functionality preserved")
        print("    Enhanced validation system (JSON Schema + Custom Logic)")
        print("    Cross-reference validation between files")
        print("    Parameter addition from example file")
        print("    Database auto-regeneration after changes")
        print("    Real-time validation status")
        print("    Professional directory structure")
        print("    CLI validation tools available")
        print("    Custom HTML documentation pages")
        print("    Swagger API documentation")
        print("    Protocol group management")
        print("    Foreign key relationships in database")
        print("    Team workflow support (Parameter + Protocol teams)")
        print("=" * 80)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print(" Failed to start application due to database errors!")