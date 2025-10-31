# import_data.py
import os
import sys
import django
import json
import csv
from datetime import datetime, date
from django.db.models import Avg  # 添加Avg導入

# 設置Django環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Author, Category, Book

class DataImporter:
    def __init__(self):
        self.raw_data = []
        self.cleaned_data = {
            'authors': [],
            'categories': [],
            'books': []
        }
    
    def load_raw_data(self, json_file_path='sample_data.json'):
        """從JSON檔案載入原始資料"""
        import json
        
        try:
            # 嘗試從JSON檔案讀取資料
            with open(json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            # 將JSON資料轉換為原來的格式
            self.raw_data = []
            
            # 轉換作者資料
            for author in json_data.get('authors', []):
                self.raw_data.append({
                    'type': 'author',
                    'name': author['name'],
                    'email': author['email'],
                    'birth_date': author['birth_date']
                })
            
            # 轉換分類資料
            for category in json_data.get('categories', []):
                self.raw_data.append({
                    'type': 'category', 
                    'name': category['name'],
                    'description': category.get('description', '')
                })
            
            # 轉換書籍資料
            for book in json_data.get('books', []):
                self.raw_data.append({
                    'type': 'book',
                    'title': book['title'],
                    'author_name': book['author_name'],
                    'category_name': book['category_name'],
                    'publish_date': book['publish_date'],
                    'price': str(book['price'])  # 確保是字串格式
                })
            
            print(f"✅ 從 {json_file_path} 成功載入 {len(self.raw_data)} 筆原始資料")
            print(f"   - 作者: {len(json_data.get('authors', []))} 筆")
            print(f"   - 分類: {len(json_data.get('categories', []))} 筆") 
            print(f"   - 書籍: {len(json_data.get('books', []))} 筆")
            
        except FileNotFoundError:
            print(f"❌ 找不到JSON檔案: {json_file_path}")
            print("使用預設的範例資料...")
            self._load_default_data()
        except json.JSONDecodeError as e:
            print(f"❌ JSON檔案格式錯誤: {e}")
            print("使用預設的範例資料...")
            self._load_default_data()
        except Exception as e:
            print(f"❌ 讀取JSON檔案時發生錯誤: {e}")
            print("使用預設的範例資料...")
            self._load_default_data()
    
    def _load_default_data(self):
        """載入預設的範例資料（備用）"""
        self.raw_data = [
            # 基本範例資料，確保程式能運行
            {'type': 'author', 'name': '張三', 'email': 'zhangsan@email.com', 'birth_date': '1980-05-15'},
            {'type': 'author', 'name': '李四', 'email': 'lisi@email.com', 'birth_date': '1975-12-01'},
            {'type': 'category', 'name': '科技', 'description': '技術相關書籍'},
            {'type': 'book', 'title': 'Python入門', 'author_name': '張三', 'category_name': '科技', 'publish_date': '2023-01-15', 'price': '350.00'},
        ]
        print(f"載入 {len(self.raw_data)} 筆預設資料")
    
    def clean_data(self):
        """清理和格式化資料"""
        print("開始清理資料...")
        
        for item in self.raw_data:
            try:
                if item['type'] == 'author':
                    # 清理作者資料
                    cleaned_item = {
                        'name': item['name'].strip(),  # 去除前後空格
                        'email': item['email'].strip().lower(),  # 轉小寫
                        'birth_date': datetime.strptime(item['birth_date'], '%Y-%m-%d').date() if item['birth_date'] else None
                    }
                    self.cleaned_data['authors'].append(cleaned_item)
                    
                elif item['type'] == 'category':
                    # 清理分類資料
                    cleaned_item = {
                        'name': item['name'].strip(),
                        'description': item.get('description', '').strip()
                    }
                    self.cleaned_data['categories'].append(cleaned_item)
                    
                elif item['type'] == 'book':
                    # 清理書籍資料
                    cleaned_item = {
                        'title': item['title'].strip(),
                        'author_name': item['author_name'].strip(),
                        'category_name': item['category_name'].strip(),
                        'publish_date': datetime.strptime(item['publish_date'], '%Y-%m-%d').date(),
                        'price': float(item['price'])
                    }
                    self.cleaned_data['books'].append(cleaned_item)
                    
            except Exception as e:
                print(f"⚠️ 清理資料時發生錯誤 (跳過此筆): {item} - 錯誤: {e}")
                continue
        
        print(f"✅ 清理完成: {len(self.cleaned_data['authors'])} 作者, {len(self.cleaned_data['categories'])} 分類, {len(self.cleaned_data['books'])} 書籍")
    
    def import_to_django(self):
        """匯入資料到Django資料庫"""
        print("開始匯入資料到Django...")
        
        # 建立作者
        author_map = {}
        for author_data in self.cleaned_data['authors']:
            try:
                author, created = Author.objects.get_or_create(
                    name=author_data['name'],
                    defaults={
                        'email': author_data['email'],
                        'birth_date': author_data['birth_date']
                    }
                )
                author_map[author_data['name']] = author
                print(f"{'✅ 建立' if created else 'ℹ️ 找到'}作者: {author.name}")
            except Exception as e:
                print(f"❌ 建立作者失敗 {author_data['name']}: {e}")
        
        # 建立分類
        category_map = {}
        for category_data in self.cleaned_data['categories']:
            try:
                category, created = Category.objects.get_or_create(
                    name=category_data['name'],
                    defaults={'description': category_data['description']}
                )
                category_map[category_data['name']] = category
                print(f"{'✅ 建立' if created else 'ℹ️ 找到'}分類: {category.name}")
            except Exception as e:
                print(f"❌ 建立分類失敗 {category_data['name']}: {e}")
        
        # 建立書籍
        book_count = 0
        for book_data in self.cleaned_data['books']:
            try:
                author = author_map.get(book_data['author_name'])
                category = category_map.get(book_data['category_name'])
                
                if author and category:
                    book, created = Book.objects.get_or_create(
                        title=book_data['title'],
                        defaults={
                            'author': author,
                            'category': category,
                            'publish_date': book_data['publish_date'],
                            'price': book_data['price']
                        }
                    )
                    if created:
                        book_count += 1
                        print(f"✅ 建立書籍: {book.title}")
                    else:
                        print(f"ℹ️ 書籍已存在: {book.title}")
                else:
                    print(f"❌ 警告: 找不到作者 '{book_data['author_name']}' 或分類 '{book_data['category_name']}' - 書籍: {book_data['title']}")
                    
            except Exception as e:
                print(f"❌ 錯誤建立書籍 {book_data['title']}: {e}")
        
        print(f"🎉 成功建立 {book_count} 本新書籍")
    
    def export_data(self, formats=['json', 'csv', 'report']):
        """多功能資料匯出"""
        base_filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"開始匯出資料 ({', '.join(formats)})...")
        
        results = {}
        
        if 'json' in formats:
            results['json'] = self.export_to_json(f"{base_filename}.json")
        
        if 'csv' in formats:
            results['csv'] = self.export_to_csv(base_filename)
        
        if 'report' in formats:
            results['report'] = self.create_export_report(base_filename)
        
        # 顯示結果
        success_count = sum(1 for r in results.values() if r)
        print(f"\n匯出完成: {success_count}/{len(results)} 種格式成功")
        
        return success_count > 0

    def export_to_json(self, filename):
        """匯出為JSON格式"""
        try:
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
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
                writer.writerow(['ID', '姓名', '電子郵件', '出生日期'])
                for author in authors:
                    writer.writerow([
                        author.id,
                        author.name,
                        author.email,
                        author.birth_date.strftime('%Y-%m-%d') if author.birth_date else ''
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
                        book.publish_date.strftime('%Y-%m-%d'),
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
匯出時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
"""
            if books.exists():
                highest_price_book = books.order_by('-price').first()
                lowest_price_book = books.order_by('price').first()
                avg_price = books.aggregate(avg_price=Avg('price'))['avg_price']
                report += f"""最高價格: {highest_price_book.price} ({highest_price_book.title})
最低價格: {lowest_price_book.price} ({lowest_price_book.title})
平均價格: {avg_price:.2f}
"""
            else:
                report += "無書籍資料\n"
            
            report += f"""
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
    
    def check_data_in_admin(self):
        """檢查資料是否可以在管理面板查看"""
        total_authors = Author.objects.count()
        total_categories = Category.objects.count()
        total_books = Book.objects.count()
        
        print("\n=== 資料統計 ===")
        print(f"作者數量: {total_authors}")
        print(f"分類數量: {total_categories}")
        print(f"書籍數量: {total_books}")
        print(f"總記錄數: {total_authors + total_categories + total_books}")
        
        if total_books >= 20:
            print("✅ 已達到至少20筆書籍記錄的要求!")
        else:
            print("❌ 尚未達到20筆書籍記錄要求")
        
        print("\n要檢查管理面板，請執行:")
        print("1. python manage.py createsuperuser")
        print("2. python manage.py runserver")
        print("3. 瀏覽 http://localhost:8000/admin")

def main():
    """主執行函數"""
    importer = DataImporter()
    
    try:
        # a) 從JSON檔案載入原始資料
        importer.load_raw_data('sample_data.json')
        
        # b) 清理和格式化資料集
        importer.clean_data()
        
        # c) 匯入到Django資料庫
        importer.import_to_django()
        
        # c) 多功能匯出資料
        print("\n" + "="*50)
        print("開始匯出資料...")
        importer.export_data(formats=['json', 'csv', 'report'])
        
        # d) 檢查結果
        importer.check_data_in_admin()
        
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("🎉 所有操作完成！")
    return 0

if __name__ == "__main__":
    exit(main())