# Django資料匯入專案

## 功能說明
- 清理和格式化原始資料
- 匯入到Django資料庫
- 支援資料匯出
- 可在Django管理面板查看

## 執行完整流程（包含匯出）

python import_data.py

## 只執行匯出功能


python export_manager.py

執行後會產生以下檔案：

data_export_20240320_143022.json          # JSON格式資料
data_export_20240320_143022_authors.csv   # 作者CSV
data_export_20240320_143022_categories.csv # 分類CSV  
data_export_20240320_143022_books.csv     # 書籍CSV
data_export_20240320_143022_report.txt    # 匯出報告

