#!/usr/bin/env python3
"""
Auto-merge pending parameter/protocol files into main YAML files
"""

import os
import yaml
import glob

def merge_pending_parameters():
    """Merge pending parameters into main parameters.yaml"""
    
    # Load main parameters file
    with open('data/parameters.yaml', 'r') as f:
        main_data = yaml.safe_load(f)
    
    # Find all pending parameter files
    pending_files = glob.glob('data/pending_parameters/*.yaml')
    
    for pending_file in pending_files:
        print(f"Processing: {pending_file}")
        
        with open(pending_file, 'r') as f:
            pending_data = yaml.safe_load(f)
        
        # Merge data
        if 'parameters' in pending_data:
            main_data['parameters'].extend(pending_data['parameters'])
        
        if 'breadcrumb_fields' in pending_data:
            main_data['breadcrumb_fields'].extend(pending_data['breadcrumb_fields'])
        
        if 'vg5_fields' in pending_data:
            main_data['vg5_fields'].extend(pending_data['vg5_fields'])
        
        if 'abbr_metrics' in pending_data:
            main_data['abbr_metrics'].extend(pending_data['abbr_metrics'])
        
        # Delete processed file
        os.remove(pending_file)
    
    # Save updated main file
    with open('data/parameters.yaml', 'w') as f:
        yaml.dump(main_data, f, default_flow_style=False, sort_keys=False)

def merge_pending_protocols():
    """Merge pending protocols into main protocols.yaml"""
    
    # Load main protocols file
    with open('data/protocols.yaml', 'r') as f:
        main_data = yaml.safe_load(f)
    
    # Find all pending protocol files
    pending_files = glob.glob('data/pending_protocols/*.yaml')
    
    for pending_file in pending_files:
        print(f"Processing: {pending_file}")
        
        with open(pending_file, 'r') as f:
            pending_data = yaml.safe_load(f)
        
        # Merge data
        if 'protocol_groups' in pending_data:
            main_data['protocol_groups'].extend(pending_data['protocol_groups'])
        
        if 'protocols' in pending_data:
            main_data['protocols'].extend(pending_data['protocols'])
        
        # Delete processed file
        os.remove(pending_file)
    
    # Save updated main file
    with open('data/protocols.yaml', 'w') as f:
        yaml.dump(main_data, f, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    print("🔄 Auto-merging pending files...")
    merge_pending_parameters()
    merge_pending_protocols()
    print("✅ Auto-merge complete!")