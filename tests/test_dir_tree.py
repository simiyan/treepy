import os
import sys
import pytest


class DummyClip:
    def paste(self):
        return ""


sys.modules["pyperclip"] = DummyClip()


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import dir_tree as dt


def create_temp_file(path, size):
    with open(path, 'wb') as f:
        f.write(b'0' * size)


def test_ディレクトリサイズ取得(tmp_path):
    d = tmp_path / 'dir'
    d.mkdir()
    f1 = d / 'f1.txt'
    create_temp_file(f1, 10)
    sub = d / 'sub'
    sub.mkdir()
    f2 = sub / 'f2.txt'
    create_temp_file(f2, 5)

    assert dt.get_size(f1) == 10
    assert dt.get_directory_size(d) == 15
    assert dt.get_size(d) == 15


@pytest.mark.parametrize(
    "size,expected",
    [
        (0, "0.00 B"),
        (1023, "1023.00 B"),
        (1024, "1.00 KB"),
        (1024**2, "1.00 MB"),
    ],
    ids=["ゼロバイト", "KB未満", "1KBちょうど", "1MB"],
)
def test_サイズフォーマット(size, expected):
    assert dt.format_size_dynamic(size) == expected


def test_ディレクトリ一覧取得(tmp_path):
    f1 = tmp_path / 'a.txt'
    create_temp_file(f1, 3)
    f2 = tmp_path / 'b.txt'
    create_temp_file(f2, 4)

    lines = dt.list_directory_with_sizes(str(tmp_path))
    assert lines[0] == f'# {tmp_path.name}'
    # Ensure alphabetical order and size output
    expected = [
        '- a.txt',
        '    - 3.00 B',
        '- b.txt',
        '    - 4.00 B',
    ]
    assert lines[1:] == expected


def test_クリップボードからパス取得(monkeypatch):
    temp_path = '/tmp/somepath'
    monkeypatch.setattr('pyperclip.paste', lambda: temp_path)
    monkeypatch.setattr(os.path, 'exists', lambda p: p == temp_path)
    assert dt.get_input_path() == temp_path


def test_引数からパス取得(monkeypatch):
    temp_path = '/tmp/argpath'
    monkeypatch.setattr('pyperclip.paste', lambda: '')
    monkeypatch.setattr(os.path, 'exists', lambda p: p == temp_path)
    monkeypatch.setattr(sys, 'argv', ['prog', temp_path])
    assert dt.get_input_path() == temp_path
