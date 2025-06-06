import os
import sys
import pyperclip

def get_directory_size(path):
    """フォルダのサイズ（サブフォルダ含む）を再帰的に計算"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def get_size(path):
    """ファイル or ディレクトリのサイズを取得"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        return get_directory_size(path)
    else:
        return 0

def format_size_dynamic(size_in_bytes):
    """バイトサイズを適切な単位に変換して文字列で返す"""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_in_bytes)
    for unit in units:
        if size < 1024.0 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024.0

def list_directory_with_sizes(target_path):
    """ターゲットパス直下のファイル・フォルダをリストアップし、サイズとともに返す"""
    # 1行目：最後の名前だけ
    base_name = os.path.basename(os.path.normpath(target_path))
    output_lines = [f"# {base_name}"]

    try:
        entries = os.listdir(target_path)
    except FileNotFoundError:
        print(f"Error: Path not found: {target_path}")
        sys.exit(1)
    entries.sort()

    for entry in entries:
        full_path = os.path.join(target_path, entry)
        size_bytes = get_size(full_path)
        size_formatted = format_size_dynamic(size_bytes)
        output_lines.append(f"- {entry}")
        output_lines.append(f"    - {size_formatted}")
    
    return output_lines

def get_input_path():
    """クリップボード → 実行時引数 → それでもダメならエラー"""
    clipboard_text = pyperclip.paste().strip()
    if clipboard_text and os.path.exists(clipboard_text):
        print(f"Using clipboard path: {clipboard_text}")
        return clipboard_text

    if len(sys.argv) >= 2:
        arg_path = sys.argv[1]
        if os.path.exists(arg_path):
            print(f"Using argument path: {arg_path}")
            return arg_path
        else:
            print(f"Error: Argument path does not exist: {arg_path}")
            sys.exit(1)
    
    print("Error: No valid input path found (clipboard or argument).")
    sys.exit(1)

def main():
    target_path = get_input_path()

    # 出力ファイル名生成
    base_name = os.path.basename(os.path.normpath(target_path))
    parent_dir = os.path.basename(os.path.dirname(os.path.normpath(target_path)))

    # 親ディレクトリ名を大文字化
    output_dir_name = parent_dir.upper()
    output_dir = os.path.join(os.getcwd(), output_dir_name)
    os.makedirs(output_dir, exist_ok=True)

    output_filename = f"{base_name}.md"
    output_filepath = os.path.join(output_dir, output_filename)

    # データ取得
    output_lines = list_directory_with_sizes(target_path)

    # ファイルに書き込み
    with open(output_filepath, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')

    print(f"Output written to: {output_filepath}")

if __name__ == "__main__":
    main()
