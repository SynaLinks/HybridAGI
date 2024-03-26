from hybridagi.hybridstores.filesystem.context import FileSystemContext

def test_constructor():
    ctxt = FileSystemContext()
    ctxt.initialize()

def test_initialize():
    ctxt = FileSystemContext()
    ctxt.working_directory = "/this"
    ctxt.home_directory = "/this/is/a/test"
    ctxt.previous_working_directory = "/this/is"
    ctxt.initialize()
    assert ctxt.home_directory == "/home/user"
    assert ctxt.working_directory == "/home/user"
    assert ctxt.previous_working_directory == "/home/user"

def test_eval_no_effect():
    ctxt = FileSystemContext()
    path = "/this/is/a/test"
    assert ctxt.eval_path(path) == "/this/is/a/test"

def test_eval_current():
    ctxt = FileSystemContext()
    path = "."
    assert ctxt.eval_path(path) == "/home/user"

def test_eval_current_relative():
    ctxt = FileSystemContext()
    path = "./this/is/a/test"
    assert ctxt.eval_path(path) == "/home/user/this/is/a/test"

def test_eval_parent():
    ctxt = FileSystemContext()
    path = ".."
    assert ctxt.eval_path(path) == "/home"

def test_eval_parent_relative():
    ctxt = FileSystemContext()
    path = "../this/is/a/test"
    assert ctxt.eval_path(path) == "/home/this/is/a/test"

def test_eval_home():
    ctxt = FileSystemContext()
    path = "~"
    assert ctxt.eval_path(path) == "/home/user"

def test_eval_home_relative():
    ctxt = FileSystemContext()
    path = "~/this/is/a/test"
    assert ctxt.eval_path(path) == "/home/user/this/is/a/test"

def test_eval_previous():
    ctxt = FileSystemContext()
    path = "-"
    assert ctxt.eval_path(path) == "/home/user"

def test_eval_working_root():
    ctxt = FileSystemContext()
    ctxt.working_directory = "/test"
    path = "this/is/a/test"
    assert ctxt.eval_path(path) == "/test/this/is/a/test"

def test_eval_working():
    ctxt = FileSystemContext()
    path = "this/is/a/test"
    assert ctxt.eval_path(path) == "/home/user/this/is/a/test"