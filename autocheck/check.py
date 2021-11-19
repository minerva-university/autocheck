from .notebook_state_tracker import notebook_state_tracker


class Check:

    def __init__(self):
        if not hasattr(self.__class__, 'unique_attempts'):
            self.__class__.unique_attempts = []

    def correct(self):
        print('✅ Success!')
        
    def incorrect(self, show_answer=False):
        if not self.unique_attempt:
            print('😕 It looks like you tried that answer before. Please try again.')
        else:
            print('❌ This answer is incorrect. \nI got this\n')
            print(self.response)
            if show_answer and len(self.__class__.unique_attempts) > 1:
                print('\nbut was expecting this\n')
                print(self.expected_response)
                print('\nPlease try again.')
            else:
                print('\nbut was expecting something else. Please try again.')

    def failure(self):
        print('⚠️ I could not check the answer because there was an error.')
        if self.response is ...:
            print("HINT: It looks like you didn't enter an answer.")
        elif type(self.response).__name__ in ['Xor', 'Not']:
            print("HINT: It looks like you need to use ** to raise to a power (and not ^).")

    def run(self, show_answer=False):
        # Push new IPython inputs and outputs to the tracker
        notebook_state_tracker.process_new_cells()
        # Check the response
        try:
            if self.check():
                self.correct()
            else:
                # Check that this response is not the same as earlier ones
                if self.response not in self.__class__.unique_attempts:
                    self.unique_attempt = True
                    self.__class__.unique_attempts.append(self.response)
                else:
                    self.unique_attempt = False
                self.incorrect(show_answer)
        except:
            import traceback
            traceback.print_exc(limit=0)
            self.failure()
