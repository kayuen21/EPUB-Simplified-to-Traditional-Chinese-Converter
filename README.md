# EPUB 簡體轉繁體轉換工具 (EPUB Simplified to Traditional Chinese Converter)

### 使用步驟

1. **選取並拖曳**：在 Windows 檔案總管中，選取你要轉換的簡體 `.epub` 檔案。
2. **拖放至程式**：將檔案拖曳並直接放置到 `epub-to-traditional.exe` 圖示上。
3. **同目錄生成**：程式將自動喚起終端機視窗並顯示轉換進度；完成後，繁體 EPUB 會立即儲存於原書籍所在資料夾中。

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
  - **閱讀器語言標籤優化**：自動將 `zh-CN` / `zh-Hans` 更新為 `zh-TW`。
