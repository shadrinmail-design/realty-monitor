import json, os
from datetime import datetime
from typing import Dict, Optional, Tuple

class AlertState:
    THRESHOLDS = [25, 15, 10, 5, 2]
    def __init__(self, data_dir='/root/realty-monitor/data'):
        self.state_file = os.path.join(data_dir, 'alert_state.json')
        os.makedirs(data_dir, exist_ok=True)
    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f: return json.load(f)
            except: return {}
        return {}
    def save_state(self, state):
        with open(self.state_file, 'w') as f: json.dump(state, f, ensure_ascii=False, indent=2)
    def get_threshold_for_quantity(self, quantity):
        crossed = [t for t in self.THRESHOLDS if quantity < t]
        return min(crossed) if crossed else None
    def should_alert(self, url, name, qty):
        state = self.load_state()
        cur_thr = self.get_threshold_for_quantity(qty)
        if not cur_thr:
            if url in state: del state[url]; self.save_state(state)
            return False, None
        last_thr = state.get(url, {}).get('last_alert_threshold')
        if last_thr is None or cur_thr < last_thr:
            state[url] = {'project_name': name, 'last_alert_threshold': cur_thr, 'last_alert_date': datetime.now().isoformat(), 'last_quantity': qty}
            self.save_state(state)
            return True, cur_thr
        if url in state: state[url]['last_quantity']=qty; state[url]['last_check_date']=datetime.now().isoformat(); self.save_state(state)
        return False, None
