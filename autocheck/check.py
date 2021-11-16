from .notebook_state_tracker import notebook_state_tracker


class Check:

    def correct(self):
        print('✅ Success!')
        
    def incorrect(self, show_answer=False):
        print('❌ This answer is incorrect. \nI got this\n')
        print(self.response)
        if show_answer:
            print('\nbut was expecting this\n')
            print(self.expected_response)
            print('\nPlease try again.')
        else:
            print('\nbut was expecting something else. Please try again')

    def failure(self):
        print('⚠️ I could not check the answer because there was an error.')
        if self.response is ...:
            print("It looks like you didn't enter an answer.")

    def run(self, show_answer=False):
        notebook_state_tracker.process_new_cells()
        try:
            if self.check():
                self.correct()
            else:
                self.incorrect(show_answer)
        except:
            self.failure()
            raise
