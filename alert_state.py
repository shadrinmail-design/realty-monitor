import json, os
from datetime import datetime
from typing import Dict, Optional, Tuple

class AlertState:
    THRESHOLDS = [25, 15, 10, 5, 2]

    def __init__(self, data_dir='/root/realty-monitor/data'):
        self.state_file = os.path.join(data_dir, 'alert_state.json')
        self.sales_state_file = os.path.join(data_dir, 'alert_sales_state.json')
        os.makedirs(data_dir, exist_ok=True)

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_state(self, state):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_sales_state(self):
        if os.path.exists(self.sales_state_file):
            try:
                with open(self.sales_state_file) as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_sales_state(self, state):
        with open(self.sales_state_file, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def get_threshold_for_quantity(self, quantity):
        crossed = [t for t in self.THRESHOLDS if quantity < t]
        return min(crossed) if crossed else None

    def should_alert(self, url, name, qty):
        state = self.load_state()
        cur_thr = self.get_threshold_for_quantity(qty)

        if not cur_thr:
            if url in state:
                del state[url]
                self.save_state(state)
            return False, None

        last_thr = state.get(url, {}).get('last_alert_threshold')

        if last_thr is None or cur_thr < last_thr:
            state[url] = {
                'project_name': name,
                'last_alert_threshold': cur_thr,
                'last_alert_date': datetime.now().isoformat(),
                'last_quantity': qty
            }
            self.save_state(state)
            return True, cur_thr

        if url in state:
            state[url]['last_quantity'] = qty
            state[url]['last_check_date'] = datetime.now().isoformat()
            self.save_state(state)

        return False, None

    def should_alert_high_sales(self, url, name, sold_count, days):
        """
        Checks if high sales alert should be sent.
        Returns True only if sold count increased since last alert.
        """
        state = self.load_sales_state()
        alert_key = f'{url}_{days}d'

        # If no record or sold count increased - send alert
        if alert_key not in state:
            state[alert_key] = {
                'project_name': name,
                'url': url,
                'sold_count': sold_count,
                'last_alert_date': datetime.now().isoformat(),
                'days': days
            }
            self.save_sales_state(state)
            return True

        last_sold = state[alert_key].get('sold_count', 0)

        # Send alert only if more sold than last time
        if sold_count > last_sold:
            state[alert_key] = {
                'project_name': name,
                'url': url,
                'sold_count': sold_count,
                'last_alert_date': datetime.now().isoformat(),
                'days': days
            }
            self.save_sales_state(state)
            return True

        # Update last check date
        state[alert_key]['last_check_date'] = datetime.now().isoformat()
        self.save_sales_state(state)

        return False
