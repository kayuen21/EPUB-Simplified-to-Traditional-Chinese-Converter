#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB 簡體轉繁體轉換工具 (EPUB Simplified to Traditional Chinese Converter)
支援直接將 .epub 檔案拖放至 exe 圖示進行轉換，在同目錄下生成繁體 EPUB。
支援文字轉換、中繼資料、目錄，並將 “” 轉換為「」、‘’ 轉換為『』。
"""

import sys
import os
import re
import zipfile
import time
import glob
import configparser

# Enable UTF-8 console on Windows
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')
    except Exception:
        pass
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

import opencc

# Regex tokenizers
TAG_RE = re.compile(
    r'(<!--.*?-->|<!\[CDATA\[.*?\]\]>|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<[^>]+>)',
    re.DOTALL | re.IGNORECASE
)
ATTR_RE = re.compile(
    r'(\b(?:title|alt|aria-label)\s*=\s*)([\"\'])(.*?)\2',
    re.DOTALL | re.IGNORECASE
)
OPF_META_CONTENT_RE = re.compile(
    r'(<(?:dc:[a-zA-Z0-9_-]+|meta)\b[^>]*?\bcontent\s*=\s*)([\"\'])(.*?)\2',
    re.DOTALL | re.IGNORECASE
)

# Extract book title and author from OPF for summary display
OPF_TITLE_RE = re.compile(r'<dc:title\b[^>]*>(.*?)</dc:title>', re.DOTALL | re.IGNORECASE)
OPF_CREATOR_RE = re.compile(r'<dc:creator\b[^>]*>(.*?)</dc:creator>', re.DOTALL | re.IGNORECASE)


def update_lang_attributes(tag: str, target_lang: str = 'zh-TW') -> str:
    """Updates language attributes (lang and xml:lang) to target Traditional Chinese."""
    tag = re.sub(
        r'(\blang\s*=\s*[\"\'])zh-(?:CN|Hans|CHS|cmn-Hans|Hans-CN)([\"\'])',
        rf'\g<1>{target_lang}\2',
        tag,
        flags=re.IGNORECASE
    )
    tag = re.sub(
        r'(\bxml:lang\s*=\s*[\"\'])zh-(?:CN|Hans|CHS|cmn-Hans|Hans-CN)([\"\'])',
        rf'\g<1>{target_lang}\2',
        tag,
        flags=re.IGNORECASE
    )
    return tag


def convert_quotes(text: str) -> str:
    """
    Converts quotation marks:
      “ and ” -> 「 and 」
      ‘ and ’ -> 『 and 』
    Protects English apostrophes (e.g. don't, it's).
    """
    if not text:
        return text
    # Convert HTML entities if present
    text = re.sub(r'&(?:ldquo|#8220|#x201c|#x201C);', '“', text)
    text = re.sub(r'&(?:rdquo|#8221|#x201d|#x201D);', '”', text)
    text = re.sub(r'&(?:lsquo|#8216|#x2018);', '‘', text)
    text = re.sub(r'&(?:rsquo|#8217|#x2019);', '’', text)

    # Protect English contractions / apostrophes like don't, it's, isn't, we'll
    text = re.sub(r'([a-zA-Z])’([a-zA-Z])', lambda m: m.group(1) + '\uE000' + m.group(2), text)

    # Double quotes “ ” -> 「 」
    text = text.replace('“', '「').replace('”', '」')
    # Single quotes ‘ ’ -> 『 』
    text = text.replace('‘', '『').replace('’', '』')

    # Restore English apostrophes
    text = text.replace('\uE000', '’')
    return text


def convert_text(text: str, cc: opencc.OpenCC, do_quotes: bool = True) -> str:
    """Converts simplified text to traditional, and converts quotes if enabled."""
    if not text:
        return text
    res = cc.convert(text)
    if do_quotes:
        res = convert_quotes(res)
    return res


def convert_html_content(content: str, cc: opencc.OpenCC, target_lang: str = 'zh-TW', do_quotes: bool = True) -> str:
    """Safely converts XHTML/HTML text and translatable attributes without breaking tags."""
    tokens = TAG_RE.split(content)
    out = []
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('<') and tok.endswith('>'):
            if tok.startswith('<!--') or tok.lower().startswith(('<script', '<style')):
                out.append(tok)
            else:
                tag = update_lang_attributes(tok, target_lang)
                def rep_attr(m):
                    prefix, quote, val = m.group(1), m.group(2), m.group(3)
                    return f'{prefix}{quote}{convert_text(val, cc, do_quotes)}{quote}'
                tag = ATTR_RE.sub(rep_attr, tag)
                out.append(tag)
        else:
            out.append(convert_text(tok, cc, do_quotes))
    return ''.join(out)


def convert_opf_content(content: str, cc: opencc.OpenCC, target_lang: str = 'zh-TW', do_quotes: bool = True) -> str:
    """Converts OPF package metadata while preserving manifest IDs and hrefs."""
    content = re.sub(
        r'(<dc:language\b[^>]*>)\s*zh-(?:CN|Hans|CHS|cmn-Hans|Hans-CN)\s*(</dc:language>)',
        rf'\g<1>{target_lang}\2',
        content,
        flags=re.IGNORECASE
    )
    tokens = TAG_RE.split(content)
    out = []
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('<') and tok.endswith('>'):
            if tok.startswith('<!--'):
                out.append(tok)
            else:
                tag = update_lang_attributes(tok, target_lang)
                if tag.lower().startswith(('<meta', '<dc:')):
                    def rep_content(m):
                        prefix, quote, val = m.group(1), m.group(2), m.group(3)
                        return f'{prefix}{quote}{convert_text(val, cc, do_quotes)}{quote}'
                    tag = OPF_META_CONTENT_RE.sub(rep_content, tag)
                out.append(tag)
        else:
            out.append(convert_text(tok, cc, do_quotes))
    return ''.join(out)


def convert_ncx_content(content: str, cc: opencc.OpenCC, do_quotes: bool = True) -> str:
    """Converts NCX TOC text nodes."""
    tokens = TAG_RE.split(content)
    out = []
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('<') and tok.endswith('>'):
            out.append(tok)
        else:
            out.append(convert_text(tok, cc, do_quotes))
    return ''.join(out)


def get_default_config():
    """Reads optional config.ini next to executable or script."""
    cfg = {
        'mode': 's2t',
        'suffix': '(繁體)',
        'target_lang': 'zh-TW',
        'convert_quotes': True
    }
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    ini_path = os.path.join(exe_dir, 'config.ini')
    if os.path.exists(ini_path):
        try:
            parser = configparser.ConfigParser()
            parser.read(ini_path, encoding='utf-8')
            if parser.has_section('converter'):
                if parser.has_option('converter', 'mode'):
                    cfg['mode'] = parser.get('converter', 'mode').strip()
                if parser.has_option('converter', 'suffix'):
                    cfg['suffix'] = parser.get('converter', 'suffix').strip()
                if parser.has_option('converter', 'target_lang'):
                    cfg['target_lang'] = parser.get('converter', 'target_lang').strip()
                if parser.has_option('converter', 'convert_quotes'):
                    val = parser.get('converter', 'convert_quotes').strip().lower()
                    cfg['convert_quotes'] = val in ('true', '1', 'yes', 'on')
        except Exception:
            pass
    return cfg


def determine_output_path(input_path: str, cc: opencc.OpenCC, suffix: str = '(繁體)', do_quotes: bool = True) -> str:
    """
    Determines output EPUB path in the SAME directory.
    If input filename has simplified characters, translate the filename.
    If translated filename is unchanged from input, append suffix.
    Guarantees no accidental overwrite of input file.
    """
    input_dir = os.path.dirname(os.path.abspath(input_path))
    file_name = os.path.basename(input_path)
    base_name, ext = os.path.splitext(file_name)
    
    translated_base = convert_text(base_name, cc, do_quotes)
    
    if translated_base != base_name:
        candidate_name = f"{translated_base}{ext}"
    else:
        candidate_name = f"{base_name} {suffix}{ext}"
    
    candidate_path = os.path.join(input_dir, candidate_name)
    
    # If candidate is identical to input, add suffix
    if os.path.abspath(candidate_path) == os.path.abspath(input_path):
        candidate_name = f"{base_name} {suffix}{ext}"
        candidate_path = os.path.join(input_dir, candidate_name)
    
    # If candidate already exists, find non-colliding name
    if os.path.exists(candidate_path):
        counter = 1
        stem, dot_ext = os.path.splitext(candidate_name)
        while os.path.exists(candidate_path):
            candidate_path = os.path.join(input_dir, f"{stem} ({counter}){dot_ext}")
            counter += 1

    return candidate_path


def render_progress_bar(current: int, total: int, bar_length: int = 30) -> str:
    fraction = current / max(1, total)
    filled = int(fraction * bar_length)
    bar = '█' * filled + '░' * (bar_length - filled)
    percent = int(fraction * 100)
    return f"[{bar}] {percent:3d}% ({current}/{total})"


def convert_single_epub(
    input_path: str,
    mode: str = 's2t',
    suffix: str = '(繁體)',
    target_lang: str = 'zh-TW',
    do_quotes: bool = True
) -> bool:
    if not os.path.isfile(input_path):
        print(f"\n[錯誤] 檔案不存在: {input_path}")
        return False
    
    if not input_path.lower().endswith('.epub'):
        print(f"\n[跳過] 非 EPUB 檔案: {input_path}")
        return False

    print("\n" + "=" * 65)
    print(f"正在處理: {os.path.basename(input_path)}")
    print(f"檔案位置: {os.path.abspath(input_path)}")
    print("=" * 65)

    try:
        cfg_name = f"{mode}.json" if not mode.endswith('.json') else mode
        cc = opencc.OpenCC(cfg_name)
    except Exception as e:
        print(f"[錯誤] 初始化 OpenCC ({mode}) 失敗: {e}")
        return False

    output_path = determine_output_path(input_path, cc, suffix, do_quotes)
    temp_output = output_path + f".tmp.{os.getpid()}"

    t0 = time.time()
    raw_title = "未知 (Unknown)"
    raw_creator = "未知 (Unknown)"
    trans_title = ""
    trans_creator = ""

    try:
        with zipfile.ZipFile(input_path, 'r') as in_zip:
            file_list = in_zip.namelist()
            total_files = len(file_list)
            has_mimetype = 'mimetype' in file_list
            other_files = [f for f in file_list if f != 'mimetype']

            # First pass: read metadata for preview
            for name in file_list:
                if name.lower().endswith('.opf'):
                    try:
                        opf_str = in_zip.read(name).decode('utf-8', errors='ignore')
                        m_title = OPF_TITLE_RE.search(opf_str)
                        if m_title:
                            raw_title = m_title.group(1).strip()
                            trans_title = convert_text(raw_title, cc, do_quotes)
                        m_creator = OPF_CREATOR_RE.search(opf_str)
                        if m_creator:
                            raw_creator = m_creator.group(1).strip()
                            trans_creator = convert_text(raw_creator, cc, do_quotes)
                    except Exception:
                        pass
                    break

            if trans_title:
                print(f"書名 (Title) : {raw_title}  →  {trans_title}")
            if trans_creator:
                print(f"作者 (Author): {raw_creator}  →  {trans_creator}")
            print(f"轉換模式     : {mode} (簡體 → 繁體)")
            if do_quotes:
                print("引號轉換     : “” → 「」, ‘’ → 『』")
            print(f"輸出目標     : {os.path.basename(output_path)}")
            print("-" * 65)

            with zipfile.ZipFile(temp_output, 'w') as out_zip:
                # 1. mimetype MUST be the very first entry, uncompressed
                if has_mimetype:
                    mimetype_bytes = in_zip.read('mimetype').strip()
                    if not mimetype_bytes:
                        mimetype_bytes = b'application/epub+zip'
                    out_zip.writestr('mimetype', mimetype_bytes, compress_type=zipfile.ZIP_STORED)

                # 2. Process all other files
                for idx, file_name in enumerate(other_files, start=1):
                    raw_bytes = in_zip.read(file_name)
                    lower_name = file_name.lower()

                    if lower_name.endswith(('.xhtml', '.html', '.htm')):
                        try:
                            text = raw_bytes.decode('utf-8')
                            converted = convert_html_content(text, cc, target_lang, do_quotes)
                            out_data = converted.encode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                text = raw_bytes.decode('gb18030')
                                converted = convert_html_content(text, cc, target_lang, do_quotes)
                                out_data = converted.encode('utf-8')
                            except Exception:
                                out_data = raw_bytes
                    elif lower_name.endswith('.opf'):
                        try:
                            text = raw_bytes.decode('utf-8')
                            converted = convert_opf_content(text, cc, target_lang, do_quotes)
                            out_data = converted.encode('utf-8')
                        except Exception:
                            out_data = raw_bytes
                    elif lower_name.endswith('.ncx'):
                        try:
                            text = raw_bytes.decode('utf-8')
                            converted = convert_ncx_content(text, cc, do_quotes)
                            out_data = converted.encode('utf-8')
                        except Exception:
                            out_data = raw_bytes
                    elif lower_name.endswith('.svg'):
                        try:
                            text = raw_bytes.decode('utf-8')
                            converted = convert_html_content(text, cc, target_lang, do_quotes)
                            out_data = converted.encode('utf-8')
                        except Exception:
                            out_data = raw_bytes
                    else:
                        out_data = raw_bytes

                    zinfo = in_zip.getinfo(file_name)
                    compress_type = zinfo.compress_type
                    if compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                        compress_type = zipfile.ZIP_DEFLATED

                    out_zinfo = zipfile.ZipInfo(filename=file_name, date_time=zinfo.date_time)
                    out_zinfo.compress_type = compress_type
                    out_zinfo.comment = zinfo.comment
                    out_zinfo.extra = zinfo.extra
                    out_zip.writestr(out_zinfo, out_data)

                    # Update progress line
                    if idx % 5 == 0 or idx == len(other_files):
                        p_bar = render_progress_bar(idx, len(other_files))
                        short_fn = file_name if len(file_name) < 25 else "..." + file_name[-22:]
                        sys.stdout.write(f"\r進度 {p_bar}  {short_fn:<25}")
                        sys.stdout.flush()

        print("\r" + " " * 75 + "\r", end="")

        # Safe file replace with retry for Windows file locks
        replaced = False
        for attempt in range(5):
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.replace(temp_output, output_path)
                replaced = True
                break
            except PermissionError:
                time.sleep(0.5)
            except Exception as e:
                print(f"[警告] 重命名嘗試 {attempt + 1} 失敗: {e}")
                time.sleep(0.5)

        if not replaced:
            fallback_path = output_path.replace('.epub', f'_out_{int(time.time())}.epub')
            os.rename(temp_output, fallback_path)
            output_path = fallback_path

        elapsed = time.time() - t0
        in_size_kb = os.path.getsize(input_path) / 1024
        out_size_kb = os.path.getsize(output_path) / 1024

        print(f"✔ 轉換成功！(耗時 {elapsed:.2f} 秒)")
        print(f"  原始大小: {in_size_kb:,.1f} KB")
        print(f"  轉換大小: {out_size_kb:,.1f} KB")
        print(f"  輸出路徑: {output_path}")
        return True

    except Exception as e:
        print(f"\n[錯誤] 轉換失敗: {e}")
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
            except OSError:
                pass
        return False


def safe_pause(prompt="\n按 Enter 鍵關閉視窗 (Press Enter to close)..."):
    try:
        if sys.stdin and sys.stdin.isatty():
            input(prompt)
    except (EOFError, KeyboardInterrupt, OSError):
        pass


def main():
    cfg = get_default_config()
    mode = cfg['mode']
    suffix = cfg['suffix']
    target_lang = cfg['target_lang']
    do_quotes = cfg['convert_quotes']
    no_pause = False

    raw_args = sys.argv[1:]
    files_to_process = []
    
    # Parse CLI flags
    idx = 0
    while idx < len(raw_args):
        arg = raw_args[idx]
        if arg in ('--mode', '-m') and idx + 1 < len(raw_args):
            mode = raw_args[idx + 1]
            idx += 2
        elif arg in ('--suffix', '-s') and idx + 1 < len(raw_args):
            suffix = raw_args[idx + 1]
            idx += 2
        elif arg in ('--no-pause', '-y'):
            no_pause = True
            idx += 1
        elif arg == '--no-quotes':
            do_quotes = False
            idx += 1
        elif arg == '--quotes':
            do_quotes = True
            idx += 1
        elif arg.startswith('--mode='):
            mode = arg.split('=', 1)[1]
            idx += 1
        elif arg.startswith('--suffix='):
            suffix = arg.split('=', 1)[1]
            idx += 1
        elif arg in ('--help', '-h'):
            print("=" * 65)
            print(" EPUB 簡體轉繁體轉換工具 (EPUB S2T Converter)")
            print("=" * 65)
            print("使用方式:")
            print("  1. 將一個或多個 .epub 檔案直接拖放 (Drag & Drop) 到此 exe 上。")
            print("  2. 命令列方式: epub-to-traditional.exe [選項] <檔案1.epub> [檔案2.epub ...]")
            print("\n選項:")
            print("  --mode, -m <mode>   轉換模式: s2t (預設), s2tw (臺灣), s2twp (臺灣慣用詞), s2hk (香港)")
            print("  --suffix, -s <str>  同名無簡體字時添加之後綴 (預設: (繁體))")
            print("  --no-quotes         不轉換引號（預設會自動將 “” 轉為「」、‘’ 轉為『』）")
            print("  --no-pause, -y      完成後不等待按鍵直接結束")
            if not no_pause:
                safe_pause("\n按 Enter 鍵結束...")
            return
        else:
            # File or folder argument
            cleaned = arg.strip('\"\'')
            if os.path.isdir(cleaned):
                found = glob.glob(os.path.join(cleaned, "*.epub"))
                files_to_process.extend(found)
            elif os.path.isfile(cleaned):
                files_to_process.append(cleaned)
            idx += 1

    # Interactive mode if launched without drag-and-drop arguments
    if not files_to_process:
        print("=" * 65)
        print("        EPUB 簡體轉繁體轉換工具 (EPUB S2T Converter)")
        print("=" * 65)
        print("提示：你可以直接將 .epub 檔案拖放 (Drag & Drop) 到此 exe 圖示！\n")
        print("或者在下方貼上 / 拖曳 .epub 檔案至此視窗中：")
        user_input = ""
        try:
            user_input = input("請輸入 EPUB 檔案路徑: ").strip('\"\' ')
        except (EOFError, KeyboardInterrupt, OSError):
            pass
        if user_input:
            if os.path.isdir(user_input):
                files_to_process.extend(glob.glob(os.path.join(user_input, "*.epub")))
            elif os.path.isfile(user_input):
                files_to_process.append(user_input)
            else:
                print(f"[錯誤] 找不到檔案或資料夾: {user_input}")

    if not files_to_process:
        print("\n未指定任何可轉換的 EPUB 檔案。")
        if not no_pause:
            safe_pause("\n按 Enter 鍵退出...")
        return

    success_count = 0
    fail_count = 0
    start_total = time.time()

    print(f"\n共發現 {len(files_to_process)} 個檔案待處理。開始轉換...")

    for f in files_to_process:
        ok = convert_single_epub(f, mode=mode, suffix=suffix, target_lang=target_lang, do_quotes=do_quotes)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    total_time = time.time() - start_total
    print("\n" + "=" * 65)
    print(f"全部處理完成！共耗時 {total_time:.2f} 秒")
    print(f"成功: {success_count} 本  |  失敗: {fail_count} 本")
    print("=" * 65)

    if not no_pause:
        safe_pause("\n按 Enter 鍵關閉視窗 (Press Enter to close)...")


if __name__ == '__main__':
    main()
