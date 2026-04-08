from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

@app.route('/clickup-to-ninjaone', methods=['POST'])
def clickup_to_ninjaone():
    data = request.json
    
    # Extraer ID NinjaOne
    ninja_id = None
    for field in data.get('custom_fields', []):
        if field.get('name') == 'NinjaOne Ticket ID':
            ninja_id = field.get('value')
            break
    if not ninja_id:
        match = re.search(r'#(\d+)', data.get('name', ''))
        ninja_id = match.group(1) if match else None
    
    if not ninja_id:
        return jsonify({"error": "No ID NinjaOne"}), 400
    
    # Mapear estado
    status_map = {'Done': 'Closed', 'En Progreso': 'In Progress', 'To Do': 'Open'}
    ninja_status = status_map.get(data.get('status', {}).get('name'), 'In Progress')
    
    notes = f"ClickUp: {data.get('status', {}).get('name')}"
    
    # NinjaOne API
    url = f"https://workplace.rmmservice.eu/v2/tickets/{ninja_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('NINJAONE_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {"status": ninja_status, "notes": notes}
    
    response = requests.patch(url, json=payload, headers=headers)
    
    return jsonify({"success": True, "ticket": ninja_id}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
