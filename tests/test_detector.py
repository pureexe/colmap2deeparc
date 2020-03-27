import os
from deeparc.reader import detect_model, detect_database
def test_detect_model_failed_case(tmpdir):
    assert detect_model(tmpdir) == False

def test_detect_db_failed_invalid_ext(tmpdir):
    path = os.path.join(tmpdir, 'hello.txt')
    assert detect_database(path) == False

def test_detect_db_failed_file_not_exist(tmpdir):
    path = os.path.join(tmpdir, 'penguinguy_cam004_matched.db')
    assert detect_database(path) == False

def test_detect_db():
    path = 'tests/assets/penguinguy_cam004_matched.db'
    assert detect_database(path) == True