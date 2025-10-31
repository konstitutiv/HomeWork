# export_manager.py
import os
import sys
import django
import json
import csv
from datetime import datetime
from django.db.models import Avg  # 添加這行

# 設置Django環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Author, Category, Book

# 設置Django環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Author, Category, Book

class DataExporter:
    def __init__(self):
        self.export_time = datetime.now()
        self.export_formats = ['json', 'csv', 'report']
    
    def export_all_data(self, base_filename=None):
        """匯出所有資料"""
        if not base_filename:
            base_filename = f"data_export_{self.export_time.strftime('%Y%m%d_%H%M%S')}"
        
        print(f"開始匯出資料到 {base_filename}...")
        
        results = {}
        
        # JSON匯出
        results['json'] = self.export_to_json(f"{base_filename}.json")
        
        # CSV匯出
        results['csv'] = self.export_to_csv(base_filename)
        
        # 建立報告
        results['report'] = self.create_export_report(base_filename)
        
        # 顯示匯出結果
        self._print_export_summary(results, base_filename)
        
        return all(results.values())
    
    def export_to_json(self, filename):
        """匯出為JSON格式"""
        try:
            export_data = {
                'metadata': {
                    'export_time': self.export_time.isoformat(),
                    'total_records': {
                        'authors': Author.objects.count(),
                        'categories': Category.objects.count(),
                        'books': Book.objects.count()
                    }
                },
                'authors': list(Author.objects.values(
                    'id', 'name', 'email', 'birth_date'
                )),
                'categories': list(Category.objects.values(
                    'id', 'name', 'description'
                )),
                'books': list(Book.objects.values(
                    'id', 'title', 'author_id', 'category_id', 
                    'publish_date', 'price', 'is_available'
                ))
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ JSON匯出完成: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ JSON匯出失敗: {e}")
            return False
    
    def export_to_csv(self, base_filename):
        """匯出為CSV格式"""
        try:
            # 作者CSV
            authors = Author.objects.all()
            with open(f'{base_filename}_authors.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '姓名', '電子郵件', '出生日期', '建立時間'])
                for author in authors:
                    writer.writerow([
                        author.id,
                        author.name,
                        author.email,
                        author.birth_date,
                        author.pk  # 你可以添加created_at欄位如果有的话
                    ])
            
            # 分類CSV
            categories = Category.objects.all()
            with open(f'{base_filename}_categories.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '分類名稱', '描述'])
                for category in categories:
                    writer.writerow([
                        category.id,
                        category.name,
                        category.description
                    ])
            
            # 書籍CSV（包含關聯資訊）
            books = Book.objects.select_related('author', 'category').all()
            with open(f'{base_filename}_books.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '書名', '作者ID', '作者', '分類ID', '分類', '出版日期', '價格', '是否可借'])
                for book in books:
                    writer.writerow([
                        book.id,
                        book.title,
                        book.author.id,
                        book.author.name,
                        book.category.id,
                        book.category.name,
                        book.publish_date,
                        float(book.price),
                        '是' if book.is_available else '否'
                    ])
            
            print(f"✅ CSV匯出完成: {base_filename}_*.csv")
            return True
            
        except Exception as e:
            print(f"❌ CSV匯出失敗: {e}")
            return False
    
    def create_export_report(self, base_filename):
        """建立詳細的匯出報告"""
        try:
            authors = Author.objects.all()
            categories = Category.objects.all()
            books = Book.objects.all()
            
            report = f"""
資料匯出詳細報告
================

基本資訊:
---------
匯出時間: {self.export_time.strftime('%Y-%m-%d %H:%M:%S')}
匯出檔案基礎名稱: {base_filename}

資料統計:
---------
作者數量: {authors.count()}
分類數量: {categories.count()}  
書籍數量: {books.count()}
總記錄數: {authors.count() + categories.count() + books.count()}

作者列表:
---------
"""
            for author in authors:
                book_count = Book.objects.filter(author=author).count()
                report += f"- {author.name} ({author.email}) - 著作: {book_count}本\n"
            
            report += f"""
分類列表:
---------
"""
            for category in categories:
                book_count = Book.objects.filter(category=category).count()
                report += f"- {category.name} - 書籍: {book_count}本\n"
                if category.description:
                    report += f"  描述: {category.description}\n"
            
            report += f"""
書籍價格統計:
------------
最高價格: {books.order_by('-price').first().price if books.exists() else 'N/A'}
最低價格: {books.order_by('price').first().price if books.exists() else 'N/A'}  
平均價格: {books.aggregate(avg_price=Avg('price'))['avg_price'] if books.exists() else 'N/A'}

匯出檔案:
---------
1. {base_filename}.json - JSON格式完整資料
2. {base_filename}_authors.csv - 作者資料表
3. {base_filename}_categories.csv - 分類資料表
4. {base_filename}_books.csv - 書籍資料表
5. {base_filename}_report.txt - 本報告檔案

注意事項:
---------
- 所有檔案使用UTF-8編碼
- CSV檔案適合用Excel開啟編輯
- JSON檔案包含完整的資料關係
- 建議定期備份重要資料
"""
            
            with open(f'{base_filename}_report.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✅ 匯出報告生成完成: {base_filename}_report.txt")
            return True
            
        except Exception as e:
            print(f"❌ 報告生成失敗: {e}")
            return False
    
    def _print_export_summary(self, results, base_filename):
        """顯示匯出摘要"""
        print("\n" + "="*50)
        print("📊 資料匯出摘要")
        print("="*50)
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        print(f"匯出時間: {self.export_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"成功項目: {success_count}/{total_count}")
        print(f"基礎檔名: {base_filename}")
        
        if success_count == total_count:
            print("🎉 所有匯出操作都成功完成！")
        else:
            print("⚠️  部分匯出操作失敗，請檢查錯誤訊息")
        
        print("\n生成的檔案:")
        print(f"  📁 {base_filename}.json")
        print(f"  📁 {base_filename}_authors.csv") 
        print(f"  📁 {base_filename}_categories.csv")
        print(f"  📁 {base_filename}_books.csv")
        print(f"  📁 {base_filename}_report.txt")
        print("="*50)

# 獨立執行的匯出功能
def export_data_standalone():
    """獨立執行資料匯出"""
    exporter = DataExporter()
    success = exporter.export_all_data()
    
    if success:
        print("\n🎉 資料匯出任務完成！")
        return 0
    else:
        print("\n❌ 資料匯出任務有錯誤！")
        return 1

if __name__ == "__main__":
    exit(export_data_standalone())