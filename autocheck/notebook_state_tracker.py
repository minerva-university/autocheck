import json

'''
Globals for controlling whether tracking is active and where information is
sent. These variables are set here rather than in an environment since the
library typically doesn't get used in an easily configurable environment.
However, you can disable tracking (or change the server URL) right after
importing the library using

import autocheck
autocheck.notebook_state_tracker.notebook_state_tracker.tracking = False

Unfortunately, these variables have to be stored in the library and not in the
environment since we cannot configure Forum Workbooks.
'''
TRACKING = False
TRACKING_URL = ''


'''
Augment the standard JSON encoder to handle the Python Ellipsis type (which is
often used as a placeholder for student inputs) and to convert any type that
cannot be handled to the string 'JSON_ENCODER_FAILURE'. This is to prevent the
encoder from raising an exception that breaks the autocheck call from a Forum
Workbook, resulting in a nasty error message that the student would not expect.
'''
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
    '''
    Store notebook state (input and output cells) and periodically send them
    to the tracking server. All HTTP calls are asynchronous so as not to delay
    providing feedback to the student.
    '''

    def __init__(self):

        try:
            get_ipython()
        except:
            # We're not in an IPython shell or Jupyter notebook; don't track.
            # This is useful for local testing since we don't want tests to be
            # stored in the tracking database.
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
        '''
        Record the platform (operating system, Python kernel, etc.) on which the
        IPython interpreter is running. This is mostly for diagnostic purposes
        and to allow us to distinguish between Forum Workbooks and Jupyter
        notebooks on Google Colab (or other web platforms).
        '''
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
        '''
        Check all previous async HTTP calls and if any of them failed, try to
        send them again.
        '''
        if not self.tracking: return

        failed_requests = [
            f for f in self.request_futures
            if f.result().status_code != 200]
        self.request_futures = []
        if len(failed_requests) > 0:
            # TODO: Resend
            pass

    def process_new_cells(self):
        '''
        Find workbook cells that are not in `self.inputs` and `self.outputs`,
        send them to the tracking server, and add them to `self.inputs` and
        `self.outputs`.
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
        '''
        Send the results of checking a student input to the tracking server.
        '''
        if not self.tracking: return
        self.process_old_futures()

        payload = self.init_json_payload()
        payload['check_result'] = result
        self.post(payload)


notebook_state_tracker = NotebookStateTracker()
