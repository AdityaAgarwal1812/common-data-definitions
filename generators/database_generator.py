"""
Database Generator
Creates SQLite database from validated YAML files
"""

import sqlite3
import yaml
import os
from pathlib import Path


class DatabaseGenerator:
    """Generates SQLite database from YAML files"""
    
    def __init__(self, output_path="output/vehicle_params.db"):
        """Initialize database generator"""
        self.output_path = output_path
        
    def generate_database(self, parameters_file="data/parameters.yaml", protocols_file="data/protocols.yaml"):
        """
        Generate complete SQLite database from YAML files
        
        Args:
            parameters_file (str): Path to parameters.yaml
            protocols_file (str): Path to protocols.yaml
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Load YAML files
            with open(parameters_file, 'r', encoding='utf-8') as f:
                parameters_data = yaml.safe_load(f)
            
            with open(protocols_file, 'r', encoding='utf-8') as f:
                protocols_data = yaml.safe_load(f)
            
            # Ensure output directory exists
            Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Remove existing database
            if os.path.exists(self.output_path):
                os.remove(self.output_path)
            
            # Create database
            conn = sqlite3.connect(self.output_path)
            cursor = conn.cursor()
            
            # Create tables
            self._create_tables(cursor)
            
            # Insert data
            self._insert_parameters_data(cursor, parameters_data)
            self._insert_protocols_data(cursor, protocols_data)
            
            # Commit and close
            conn.commit()
            conn.close()
            
            return True, f"Database created successfully: {self.output_path}"
            
        except Exception as e:
            return False, f"Database generation failed: {e}"
    
    def _create_tables(self, cursor):
        """Create all required tables"""
        
        # Parameters table
        cursor.execute("""
            CREATE TABLE parameters (
                id INTEGER PRIMARY KEY,
                field_name VARCHAR(255) UNIQUE NOT NULL,
                reserved_enum_val INTEGER,
                description TEXT,
                unit TEXT,
                reason_added VARCHAR(255),
                protobuf_field VARCHAR(255),
                protocol_reference VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Breadcrumb fields table
        cursor.execute("""
            CREATE TABLE breadcrumb_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_id INTEGER,
                breadcrumb_link TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parameter_id) REFERENCES parameters(id)
            )
        """)
        
        # VG5 fields table
        cursor.execute("""
            CREATE TABLE vg5_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_id INTEGER,
                vg5_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parameter_id) REFERENCES parameters(id)
            )
        """)
        
        # Abbreviation metrics table
        cursor.execute("""
            CREATE TABLE abbr_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_id INTEGER,
                abbr_value VARCHAR(50),
                abbr_link TEXT,
                metrics_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parameter_id) REFERENCES parameters(id)
            )
        """)
        
        # Protocol groups table
        cursor.execute("""
            CREATE TABLE protocol_groups (
                id INTEGER PRIMARY KEY,
                group_name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                parameter_reference VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Protocols table
        cursor.execute("""
            CREATE TABLE protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                abbr VARCHAR(50),
                protocol_standard VARCHAR(50),
                pgn_pid VARCHAR(100),
                spn VARCHAR(50),
                precision VARCHAR(100),
                spec_range VARCHAR(200),
                max_valid_val VARCHAR(50),
                units VARCHAR(50),
                description TEXT,
                states TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES protocol_groups(id)
            )
        """)
        
        print("Database tables created")
    
    def _insert_parameters_data(self, cursor, data):
        """Insert all parameter-related data"""
        
        # Insert parameters
        if 'parameters' in data:
            for param in data['parameters']:
                cursor.execute("""
                    INSERT INTO parameters (id, field_name, reserved_enum_val, description, unit, 
                                          reason_added, protobuf_field, protocol_reference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    param.get('id'),
                    param.get('field_name'),
                    param.get('reserved_enum_val'),
                    param.get('description'),
                    param.get('unit'),
                    param.get('reason_added'),
                    param.get('protobuf_field'),
                    param.get('protocol_reference')
                ))
            print(f" Inserted {len(data['parameters'])} parameters")
        
        # Insert breadcrumb fields
        if 'breadcrumb_fields' in data:
            for breadcrumb in data['breadcrumb_fields']:
                cursor.execute("""
                    INSERT INTO breadcrumb_fields (parameter_id, breadcrumb_link, note)
                    VALUES (?, ?, ?)
                """, (
                    breadcrumb.get('parameter_id'),
                    breadcrumb.get('breadcrumb_link'),
                    breadcrumb.get('note')
                ))
            print(f" Inserted {len(data['breadcrumb_fields'])} breadcrumb fields")
        
        # Insert VG5 fields
        if 'vg5_fields' in data:
            for vg5 in data['vg5_fields']:
                cursor.execute("""
                    INSERT INTO vg5_fields (parameter_id, vg5_link)
                    VALUES (?, ?)
                """, (
                    vg5.get('parameter_id'),
                    vg5.get('vg5_link')
                ))
            print(f" Inserted {len(data['vg5_fields'])} VG5 fields")
        
        # Insert abbreviation metrics
        if 'abbr_metrics' in data:
            for abbr in data['abbr_metrics']:
                cursor.execute("""
                    INSERT INTO abbr_metrics (parameter_id, abbr_value, abbr_link, metrics_link)
                    VALUES (?, ?, ?, ?)
                """, (
                    abbr.get('parameter_id'),
                    abbr.get('abbr_value'),
                    abbr.get('abbr_link'),
                    abbr.get('metrics_link')
                ))
            print(f" Inserted {len(data['abbr_metrics'])} abbreviation metrics")
    
    def _insert_protocols_data(self, cursor, data):
        """Insert all protocol-related data"""
        
        # Insert protocol groups
        if 'protocol_groups' in data:
            for group in data['protocol_groups']:
                cursor.execute("""
                    INSERT INTO protocol_groups (id, group_name, description, parameter_reference)
                    VALUES (?, ?, ?, ?)
                """, (
                    group.get('id'),
                    group.get('group_name'),
                    group.get('description'),
                    group.get('parameter_reference')
                ))
            print(f" Inserted {len(data['protocol_groups'])} protocol groups")
        
        # Insert protocols
        if 'protocols' in data:
            for protocol in data['protocols']:
                cursor.execute("""
                    INSERT INTO protocols (group_id, abbr, protocol_standard, pgn_pid, spn, 
                                         precision, spec_range, max_valid_val, units, description, states)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    protocol.get('group_id'),
                    protocol.get('abbr'),
                    protocol.get('protocol_standard'),
                    protocol.get('pgn_pid'),
                    protocol.get('spn'),
                    protocol.get('precision'),
                    protocol.get('spec_range'),
                    protocol.get('max_valid_val'),
                    protocol.get('units'),
                    protocol.get('description'),
                    protocol.get('states')
                ))
            print(f" Inserted {len(data['protocols'])} protocols")


# Example usage
if __name__ == "__main__":
    generator = DatabaseGenerator()
    success, message = generator.generate_database()
    print(f"Database generation: {'✅' if success else '❌'} {message}")