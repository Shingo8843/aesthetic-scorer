from flask import Flask, send_from_directory, request
import os
import subprocess
import configparser

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/results.json')
def get_results():
    return send_from_directory('output', 'results.json')

@app.route('/pruned/<path:path>')
def get_pruned(path):
    return send_from_directory('pruned', path)

@app.route('/pruneconfig.ini')
def get_pruneconfig():
    return send_from_directory('.', 'pruneconfig.ini')

@app.route('/input/<path:path>')
def serve_input(path):
    return send_from_directory('input', path)

@app.route('/save-pruneconfig', methods=['POST'])
def save_pruneconfig():
    try:
        new_config_data = request.get_data(as_text=True)
        new_config_lines = new_config_data.strip().split("\n")

        # Read the existing config file
        with open('pruneconfig.ini', 'r') as f:
            existing_config_lines = f.readlines()

        # Preserve comments and section headers
        section = None
        config_dict = {}
        for line in existing_config_lines:
            stripped_line = line.strip()
            if stripped_line.startswith("["):
                section = stripped_line
                config_dict[section] = []
            elif section:
                config_dict[section].append(line)

        # Ensure PRUNING_RULES section exists
        if '[PRUNING_RULES]' not in config_dict:
            config_dict['[PRUNING_RULES]'] = []

        # Update config with new values
        for line in new_config_lines:
            key, value = line.split("=")
            key, value = key.strip(), value.strip()
            if key and '[PRUNING_RULES]' in config_dict:
                updated = False
                for idx, existing_line in enumerate(config_dict['[PRUNING_RULES]']):
                    if existing_line.strip().startswith(key):
                        config_dict['[PRUNING_RULES]'][idx] = f"{key} = {value}\n"
                        updated = True
                        break
                if not updated:
                    config_dict['[PRUNING_RULES]'].append(f"{key} = {value}\n")

        # Write back the updated config
        with open('pruneconfig.ini', 'w') as f:
            for section, lines in config_dict.items():
                f.write(f"{section}\n")
                for line in lines:
                    f.write(line)

        return 'Prune config saved.'
    except Exception as e:
        print(f"Error saving prune config: {e}")
        return str(e), 500

@app.route('/run-prune')
def run_prune():
    try:
        result = subprocess.run(['python', 'prune.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Prune script stderr: {result.stderr}")
            return result.stderr, 500
    except Exception as e:
        print(f"Error running prune script: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
