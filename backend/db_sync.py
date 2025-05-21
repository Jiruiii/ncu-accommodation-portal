import argparse
import json
import os
from datetime import datetime
from app import create_app
from app.utils.db_json import export_db_to_json, import_db_from_json

def get_app():
    """獲取 Flask 應用實例"""
    return create_app('development')

def create_sync_folder():
    """創建同步資料夾"""
    sync_folder = os.path.join(os.path.dirname(__file__), 'db_sync')
    os.makedirs(sync_folder, exist_ok=True)
    return sync_folder

def export_command(args):
    """匯出資料庫"""
    app = get_app()
    with app.app_context():
        sync_folder = create_sync_folder()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 使用指定的檔名或生成包含時間戳的檔名
        filename = args.filename if args.filename else f"db_export_{timestamp}.json"
        filepath = os.path.join(sync_folder, filename)
        
        # 匯出資料庫
        export_db_to_json(filepath)
        print(f"資料庫已匯出至: {filepath}")
        
        # 更新同步狀態檔
        status_file = os.path.join(sync_folder, 'sync_status.json')
        status = {
            'last_export': {
                'timestamp': timestamp,
                'filename': filename,
                'user': os.environ.get('USERNAME', 'unknown')
            }
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)

        files = [f for f in os.listdir(sync_folder) if f.endswith('.json') and f != 'sync_status.json']
        if len(files) > 15:
            # 根據文件修改時間排序
            files_with_time = [(f, os.path.getmtime(os.path.join(sync_folder, f))) for f in files]
            sorted_files = sorted(files_with_time, key=lambda x: x[1], reverse=True)
            
            # 刪除舊文件
            for old_file, _ in sorted_files[15:]:
                try:
                    os.remove(os.path.join(sync_folder, old_file))
                    print(f"已刪除舊備份: {old_file}")
                except Exception as e:
                    print(f"無法刪除舊備份 {old_file}: {str(e)}")

def import_command(args):
    """匯入資料庫"""
    app = get_app()
    with app.app_context():
        sync_folder = create_sync_folder()
        
        # 使用指定的檔名或最新的匯出檔
        if args.filename:
            filepath = os.path.join(sync_folder, args.filename)
            if not os.path.exists(filepath):
                print(f"錯誤: 找不到檔案 {filepath}")
                return
        else:
            # 查找最新的匯出檔
            status_file = os.path.join(sync_folder, 'sync_status.json')
            if os.path.exists(status_file):
                with open(status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    latest_file = status.get('last_export', {}).get('filename')
                    if latest_file:
                        filepath = os.path.join(sync_folder, latest_file)
                        if not os.path.exists(filepath):
                            print(f"錯誤: 找不到最新匯出檔 {filepath}")
                            return
                    else:
                        print("錯誤: 無法確定最新的匯出檔")
                        return
            else:
                print("錯誤: 沒有同步狀態檔，請指定要匯入的檔案")
                return
        
        # 確認匯入
        if not args.force:
            confirm = input(f"將從 {filepath} 匯入資料庫，繼續嗎? [y/N] ")
            if confirm.lower() not in ['y', 'yes']:
                print("匯入已取消")
                return
        
        # 匯入資料庫
        result = import_db_from_json(filepath, clear_existing=args.clear)
        print(f"資料庫匯入完成: {result['imported']} 筆記錄成功，{result['errors']} 筆記錄失敗")
        
        # 更新同步狀態檔
        status_file = os.path.join(sync_folder, 'sync_status.json')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
        else:
            status = {}
        
        status['last_import'] = {
            'timestamp': timestamp,
            'filename': os.path.basename(filepath),
            'user': os.environ.get('USERNAME', 'unknown')
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)

def status_command(args):
    """查看同步狀態"""
    sync_folder = create_sync_folder()
    status_file = os.path.join(sync_folder, 'sync_status.json')
    
    if not os.path.exists(status_file):
        print("尚未進行過資料庫同步")
        return
    
    with open(status_file, 'r', encoding='utf-8') as f:
        status = json.load(f)
    
    print("資料庫同步狀態:")
    if 'last_export' in status:
        export_info = status['last_export']
        print(f"最後匯出: {export_info['timestamp']} (由 {export_info['user']} 執行)")
        print(f"匯出檔案: {export_info['filename']}")
    
    if 'last_import' in status:
        import_info = status['last_import']
        print(f"最後匯入: {import_info['timestamp']} (由 {import_info['user']} 執行)")
        print(f"匯入檔案: {import_info['filename']}")
    
    # 列出所有匯出檔
    print("\n可用的匯出檔:")
    files = [f for f in os.listdir(sync_folder) if f.endswith('.json') and f != 'sync_status.json']
    for file in sorted(files, reverse=True):
        file_path = os.path.join(sync_folder, file)
        file_size = os.path.getsize(file_path) / 1024  # KB
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"- {file} ({file_size:.1f} KB, {file_time.strftime('%Y-%m-%d %H:%M:%S')})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='資料庫同步工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 匯出命令
    export_parser = subparsers.add_parser('export', help='匯出資料庫')
    export_parser.add_argument('-f', '--filename', help='指定匯出檔名')
    
    # 匯入命令
    import_parser = subparsers.add_parser('import', help='匯入資料庫')
    import_parser.add_argument('-f', '--filename', help='指定匯入檔名')
    import_parser.add_argument('--clear', action='store_true', help='清空現有資料')
    import_parser.add_argument('--force', action='store_true', help='不詢問確認')
    
    # 狀態命令
    status_parser = subparsers.add_parser('status', help='查看同步狀態')
    
    args = parser.parse_args()
    
    if args.command == 'export':
        export_command(args)
    elif args.command == 'import':
        import_command(args)
    elif args.command == 'status':
        status_command(args)
    else:
        parser.print_help()