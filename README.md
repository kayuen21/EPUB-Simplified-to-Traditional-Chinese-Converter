# EPUB 簡體轉繁體轉換工具 (EPUB Simplified to Traditional Chinese Converter)

專為 Windows 設計的高效、安全、免安裝的 EPUB 簡轉繁工具。封裝為單一 `.exe` 執行檔，支援直接拖放（Drag & Drop）轉換，轉換後自動於原書所在之相同目錄輸出正統繁體中文 EPUB。

---

### 快速上手步驟

1. **選取並拖曳**：在 Windows 檔案總管中，選取你要轉換的簡體 `.epub` 檔案。
2. **拖放至程式**：將檔案拖曳並直接放置到 `epub-to-traditional.exe` 圖示上。
3. **同目錄生成**：程式將自動喚起終端機視窗並顯示轉換進度；完成後，全新的繁體 EPUB 會立即儲存於原書籍所在資料夾中！

---

## 核心功能與特色 (Key Features)

- **直接拖放 (Drag & Drop)**：
  - 支援將單本或多本 `.epub` 同時拖放至 exe 圖示進行批次處理。
  - 支援將包含 `.epub` 的整份資料夾拖入進行批次轉換。
- **正統繁體引號轉換 (Quotation Marks)**：
  - **雙引號**：將 `“` 與 `”` 自動轉換為正統繁體方角引號 **`「`** 與 **`」`**。
  - **單引號**：將 `‘` 與 `’` 自動轉換為正統繁體雙角引號 **`『`** 與 **`』`**。
  - **智慧英文撇號保護**：遇到英文縮寫與所有格（如 `don’t`、`it’s`、`we’ll`、`O’Connor`）時，嚴格保留英文原始撇號不誤轉。
  - 支援 HTML 實體轉換（如 `&ldquo;`、`&rdquo;`）。
- **全方位中繼資料與目錄轉換 (Metadata & TOC)**：
  - **書名** (`dc:title`)
  - **作者** (`dc:creator`)
  - **書籍簡介與描述** (`dc:description`)
  - **出版社與分類標籤** (`dc:publisher`, `dc:subject`)
  - **目錄與導航**：完整轉換 EPUB 2（`toc.ncx`）與 EPUB 3（`nav.xhtml`）中的所有章節名稱。
  - **閱讀器語言標籤優化**：自動將 `zh-CN` / `zh-Hans` 更新為 `zh-TW`，確保 Kindle、KOReader 等閱讀器精確調用繁體字型與排版引擎。
- **排版結構零損壞 (Zero Formatting Corruption)**：
  - 採用 Tokenizer 分詞處理，**僅轉換純文字與可顯示屬性（`title`、`alt`、`aria-label`）**。
  - 嚴格保留所有 HTML/XML 標籤、CSS 樣式類別（`class`）、元素 `id`、圖片路徑（`src`）、章節跳轉連結（`href`）。
  - 保留所有封面圖片、插圖、字型及二進位檔案。
- **嚴格符合 EPUB 規範**：
  - `mimetype` 檔案作為 ZIP 首位條目，維持無壓縮儲存 (`ZIP_STORED`)。
- **智慧檔名處理**：
  - 自動儲存於**原書所在目錄**。
  - 若原檔名含簡體字，自動轉換為繁體（例如 `解忧杂货店.epub` → `解憂雜貨店.epub`）。
  - 若原檔名無簡體字（如純英文檔名），自動加上 `(繁體)` 後綴，絕不覆蓋原檔案。
  - 若目標檔案已存在，自動加上序號避開衝突。

---

## 進階使用方式 (Advanced Usage)

### 方式 1：雙擊直接開啟
1. 雙擊執行 `epub-to-traditional.exe`。
2. 在視窗提示中貼上或拖入 `.epub` 檔案路徑，按 `Enter` 即可開始轉換。

### 方式 2：命令列執行 (CLI)
```cmd
epub-to-traditional.exe "C:\Path\To\Book.epub"
```

支援參數：
- `--mode, -m <mode>`：轉換模式
  - `s2t`：簡體到繁體（OpenCC 標準，預設）
  - `s2tw`：簡體到臺灣繁體（符合臺灣字形標準）
  - `s2twp`：簡體到臺灣繁體（含臺灣慣用詞彙轉換，如：鼠標→滑鼠、軟件→軟體）
  - `s2hk`：簡體到香港繁體（符合香港字形標準）
- `--suffix, -s <str>`：同名無簡體字時添加之後綴（預設 `(繁體)`）。
- `--no-quotes`：停用引號轉換（保留彎引號）。
- `--no-pause, -y`：批次指令碼執行，完成後不暫停直接結束。

### 配置檔 (config.ini)
可在執行檔同目錄下建立 `config.ini` 自訂預設偏好：
```ini
[converter]
mode = s2t
convert_quotes = true
suffix = (繁體)
target_lang = zh-TW
```

---

## 重新編譯指南 (Build from Source)

本專案使用 Python 與 `opencc`，透過 PyInstaller 打包為獨立執行檔。

### 環境需求
- Python 3.10+
- `opencc`
- `pyinstaller`

### 一鍵編譯指令
在專案根目錄下執行：
```cmd
build.bat
```
或使用命令列編譯：
```bash
uv run --with pyinstaller --with opencc pyinstaller --onefile --name "epub-to-traditional" --icon "icon.ico" --collect-all opencc epub_s2t.py
```
編譯成功後，產生的單一獨立檔案位於 `dist/epub-to-traditional.exe`。

---

## 開源許可 (License)

本專案基於 [MIT License](LICENSE) 開源。
