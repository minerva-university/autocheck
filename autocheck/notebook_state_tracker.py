import datetime


TRACKING = False
TRACKING_URL = 'http://127.0.0.1:5000'


class NotebookStateTracker:

    post_url_pattern = TRACKING_URL + '/hologram/%(id)s'

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
            self.request_futures = [
                self.request_session.post(
                    self.post_url_pattern % {'id': self.kernel_id},
                    json={'timestamp': datetime.datetime.utcnow().isoformat()})]

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
        self.request_futures.append(
            self.request_session.post(
                self.post_url_pattern % {'id': self.kernel_id},
                json={'inputs': new_input_cells, 'outputs': new_output_cells,
                      'timestamp': datetime.datetime.utcnow().isoformat()}))


notebook_state_tracker = NotebookStateTracker()
