import json


TRACKING = True
TRACKING_URL = 'https://minerva-autocheck-1.herokuapp.com'


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is Ellipsis:
            return '...'
        else:
            try:
                return super().default(self, obj)
            except:
                try:
                    return str(obj)
                except:
                    return 'JSON_ENCODER_FAILURE'


class NotebookStateTracker:

    def __init__(self):

        try:
            get_ipython()
        except:
            # We're not in an IPython shell or Jupyter notebook; don't track.
            self.tracking = False
        else:
            self.tracking = TRACKING

        if self.tracking:
            from uuid import uuid4
            from requests_futures.sessions import FuturesSession

            self.kernel_id = str(uuid4())
            self.inputs = []
            self.outputs = {}
            self.request_session = FuturesSession()
            self.request_futures = []

            self.post_url = f'{TRACKING_URL}/hologram/{self.kernel_id}'
            self.track_platform()

    def init_json_payload(self):
        import datetime
        return {
            'id': self.kernel_id,
            'timestamp': datetime.datetime.utcnow().isoformat()}

    def post(self, payload):
        self.request_futures.append(
            self.request_session.post(
                self.post_url,
                data=json.dumps(payload, cls=CustomJsonEncoder),
                headers={'Content-Type': 'application/json'}))

    def track_platform(self):
        if not self.tracking: return
        self.process_old_futures()

        import platform
        payload = self.init_json_payload()
        payload['platform'] = {}
        for name in dir(platform):
            try:
                result = getattr(platform, name)()
            except:
                pass
            else:
                payload['platform'][name] = str(result)
        self.post(payload)

    def process_old_futures(self):
        if not self.tracking: return

        failed_requests = [f for f in self.request_futures if f.result().status_code != 200]
        self.request_futures = []
        if len(failed_requests) > 0:
            # TODO: Resend
            pass

    def process_new_cells(self):
        '''
        Find cells that are not yet in `self.inputs` and `self.outputs`, return
        them and add them to inputs and outputs.
        '''
        if not self.tracking: return
        self.process_old_futures()

        ipython_inputs = get_ipython().user_ns.get('_ih', [])
        ipython_outputs = get_ipython().user_ns.get('_oh', {})
        new_input_cells = ipython_inputs[len(self.inputs):]
        self.inputs.extend(new_input_cells)
        new_output_cells = {
            key: ipython_outputs[key]
            for key in set(ipython_outputs.keys()) - set(self.outputs.keys())}
        self.outputs.update(new_output_cells)
        payload = self.init_json_payload()
        payload['inputs'] = new_input_cells
        payload['outputs'] = new_output_cells
        self.post(payload)

    def process_check_result(self, result):
        if not self.tracking: return
        self.process_old_futures()

        payload = self.init_json_payload()
        payload['check_result'] = result
        self.post(payload)


notebook_state_tracker = NotebookStateTracker()
