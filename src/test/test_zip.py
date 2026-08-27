
"""
pytest suite for the ZIP create/extract snippet:
 
    with zipfile.ZipFile('example.zip', 'w') as zipf:
        zipf.write('file1.txt')
        zipf.write('file2.txt')
 
    with zipfile.ZipFile('example.zip', 'r') as zipf:
        zipf.extractall('extracted_files')
 
The original code is a bare script, so it's wrapped here in two small,
testable functions (create_zip / extract_zip) that do exactly what the
script did. The tests exercise those functions using pytest's tmp_path
fixture, so nothing touches the real filesystem or leaves artifacts
behind.
"""
 
import zipfile
 
import pytest
 
 
def create_zip(zip_path, file_paths):
    """Create a ZIP file containing the given files (mirrors the snippet)."""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path)
 
 
def extract_zip(zip_path, extract_dir):
    """Extract a ZIP file into extract_dir (mirrors the snippet)."""
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_dir)
 
 
@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Isolated cwd with file1.txt / file2.txt already written to disk.
 
    zipfile.write() stores paths as given, so we chdir into a temp dir
    to reproduce the script's relative-path behavior. monkeypatch.chdir
    restores the original cwd automatically at teardown.
    """
    monkeypatch.chdir(tmp_path)
 
    file1, file2 = 'file1.txt', 'file2.txt'
    (tmp_path / file1).write_text('Hello from file 1')
    (tmp_path / file2).write_text('Hello from file 2')
 
    return {
        'dir': tmp_path,
        'file1': file1,
        'file2': file2,
        'zip_name': 'example.zip',
        'extract_dir': 'extracted_files',
    }
 
 
# --- creation -----------------------------------------------------------
 
def test_zip_file_is_created(workspace):
    create_zip(workspace['zip_name'], [workspace['file1'], workspace['file2']])
    assert (workspace['dir'] / workspace['zip_name']).exists()
 
 
def test_zip_contains_expected_entries(workspace):
    create_zip(workspace['zip_name'], [workspace['file1'], workspace['file2']])
    with zipfile.ZipFile(workspace['zip_name'], 'r') as zipf:
        names = zipf.namelist()
    assert workspace['file1'] in names
    assert workspace['file2'] in names
    assert len(names) == 2
 
 
def test_zip_archive_is_valid(workspace):
    create_zip(workspace['zip_name'], [workspace['file1'], workspace['file2']])
    with zipfile.ZipFile(workspace['zip_name'], 'r') as zipf:
        # testzip() returns None if every entry's CRC checks out
        assert zipf.testzip() is None
 
 
def test_create_missing_source_file_raises(workspace):
    with pytest.raises(FileNotFoundError):
        create_zip(workspace['zip_name'], ['does_not_exist.txt'])
 
 
# --- extraction -----------------------------------------------------------
 
def test_extract_creates_target_directory(workspace):
    create_zip(workspace['zip_name'], [workspace['file1'], workspace['file2']])
    extract_zip(workspace['zip_name'], workspace['extract_dir'])
    assert (workspace['dir'] / workspace['extract_dir']).is_dir()
 
 
def test_extract_recovers_all_files(workspace):
    create_zip(workspace['zip_name'], [workspace['file1'], workspace['file2']])
    extract_zip(workspace['zip_name'], workspace['extract_dir'])
    extracted = workspace['dir'] / workspace['extract_dir']
    assert (extracted / workspace['file1']).exists()
    assert (extracted / workspace['file2']).exists()
 
 
def test_extracted_content_matches_original(workspace):
    create_zip(workspace['zip_name'], [workspace['file1'], workspace['file2']])
    extract_zip(workspace['zip_name'], workspace['extract_dir'])
    extracted = workspace['dir'] / workspace['extract_dir']
    for name in (workspace['file1'], workspace['file2']):
        original_content = (workspace['dir'] / name).read_text()
        extracted_content = (extracted / name).read_text()
        assert original_content == extracted_content
 
 
def test_extract_nonexistent_zip_raises(workspace):
    with pytest.raises(FileNotFoundError):
        extract_zip('does_not_exist.zip', workspace['extract_dir'])
 
 
def test_extract_invalid_zip_raises(workspace):
    bad_zip = 'not_really_a_zip.zip'
    (workspace['dir'] / bad_zip).write_text('this is not zip data')
    with pytest.raises(zipfile.BadZipFile):
        extract_zip(bad_zip, workspace['extract_dir'])
