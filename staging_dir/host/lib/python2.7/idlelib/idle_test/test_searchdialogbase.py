'''Unittests for idlelib/SearchDialogBase.py

Coverage: 99%. The only thing not covered is inconsequential --
testing skipping of suite when self.needwrapbutton is false.

'''
import unittest
from test.test_support import requires
from Tkinter import Tk, Toplevel, Frame, Label, BooleanVar, StringVar
from idlelib import SearchEngine as se
from idlelib import SearchDialogBase as sdb
from idlelib.idle_test.mock_idle import Func
from idlelib.idle_test.mock_tk import Var, Mbox

# The following could help make some tests gui-free.
# However, they currently make radiobutton tests fail.
##def setUpModule():
##    # Replace tk objects used to initialize se.SearchEngine.
##    se.BooleanVar = Var
##    se.StringVar = Var
##
##def tearDownModule():
##    se.BooleanVar = BooleanVar
##    se.StringVar = StringVar

class SearchDialogBaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        del cls.root

    def setUp(self):
        self.engine = se.SearchEngine(self.root)  # None also seems to work
        self.dialog = sdb.SearchDialogBase(root=self.root, engine=self.engine)

    def tearDown(self):
        self.dialog.close()

    def test_open_and_close(self):
        # open calls create_widgets, which needs default_command
        self.dialog.default_command = None

        # Since text parameter of .open is not used in base class,
        # pass dummy 'text' instead of tk.Text().
        self.dialog.open('text')
        self.assertEqual(self.dialog.top.state(), 'normal')
        self.dialog.close()
        self.assertEqual(self.dialog.top.state(), 'withdrawn')

        self.dialog.open('text', searchphrase="hello")
        self.assertEqual(self.dialog.ent.get(), 'hello')
        self.dialog.close()

    def test_create_widgets(self):
        self.dialog.create_entries = Func()
        self.dialog.create_option_buttons = Func()
        self.dialog.create_other_buttons = Func()
        self.dialog.create_command_buttons = Func()

        self.dialog.default_command = None
        self.dialog.create_widgets()

        self.assertTrue(self.dialog.create_entries.called)
        self.assertTrue(self.dialog.create_option_buttons.called)
        self.assertTrue(self.dialog.create_other_buttons.called)
        self.assertTrue(self.dialog.create_command_buttons.called)

    def test_make_entry(self):
        equal = self.assertEqual
        self.dialog.row = 0
        self.dialog.top = Toplevel(self.root)
        entry, label = self.dialog.make_entry("Test:", 'hello')
        equal(label['text'], 'Test:')

        self.assertIn(entry.get(), 'hello')
        egi = entry.grid_info()
        equal(int(egi['row']), 0)
        equal(int(egi['column']), 1)
        equal(int(egi['rowspan']), 1)
        equal(int(egi['columnspan']), 1)
        equal(self.dialog.row, 1)

    def test_create_entries(self):
        self.dialog.row = 0
        self.engine.setpat('hello')
        self.dialog.create_entries()
        self.assertIn(self.dialog.ent.get(), 'hello')

    def test_make_frame(self):
        self.dialog.row = 0
        self.dialog.top = Toplevel(self.root)
        frame, label = self.dialog.make_frame()
        self.assertEqual(label, '')
        self.assertIsInstance(frame, Frame)

        frame, label = self.dialog.make_frame('testlabel')
        self.assertEqual(label['text'], 'testlabel')
        self.assertIsInstance(frame, Frame)

    def btn_test_setup(self, meth):
        self.dialog.top = Toplevel(self.root)
        self.dialog.row = 0
        return meth()

    def test_create_option_buttons(self):
        e = self.engine
        for state in (0, 1):
            for var in (e.revar, e.casevar, e.wordvar, e.wrapvar):
                var.set(state)
            frame, options = self.btn_test_setup(
                    self.dialog.create_option_buttons)
            for spec, button in zip (options, frame.pack_slaves()):
                var, label = spec
                self.assertEqual(button['text'], label)
                self.assertEqual(var.get(), state)
                if state == 1:
                    button.deselect()
                else:
                    button.select()
                self.assertEqual(var.get(), 1 - state)

    def test_create_other_buttons(self):
        for state in (False, True):
            var = self.engine.backvar
            var.set(state)
            frame, others = self.btn_test_setup(
                self.dialog.create_other_buttons)
            buttons = frame.pack_slaves()
            for spec, button in zip(others, buttons):
                val, label = spec
                self.assertEqual(button['text'], label)
                if val == state:
                    # hit other button, then this one
                    # indexes depend on button order
                    self.assertEqual(var.get(), state)
                    buttons[val].select()
                    self.assertEqual(var.get(), 1 - state)
                    buttons[1-val].select()
                    self.assertEqual(var.get(), state)

    def test_make_button(self):
        self.dialog.top = Toplevel(self.root)
        self.dialog.buttonframe = Frame(self.dialog.top)
        btn = self.dialog.make_button('Test', self.dialog.close)
        self.assertEqual(btn['text'], 'Test')

    def test_create_command_buttons(self):
        self.dialog.create_command_buttons()
        # Look for close button command in buttonframe
        closebuttoncommand = ''
        for child in self.dialog.buttonframe.winfo_children():
            if child['text'] == 'close':
                closebuttoncommand = child['command']
        self.assertIn('close', closebuttoncommand)



if __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
