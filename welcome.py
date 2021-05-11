import os
p = os.path.abspath('')
p1 = os.path.abspath('')
p += r'\\dbs\\'
p1 += r'\\'

open(p + "db_main_info.txt", "w", encoding="utf8").close()
open(p + "db_main_info_backup.txt", "w", encoding="utf8").close()
open(p + "db_used_info.txt", "w", encoding="utf8").close()
open(p + "db_used_info_backup.txt", "w", encoding="utf8").close()
open(p + "db_achievements_info.txt", "w", encoding="utf8").close()
open(p + "db_achievements_info_backup.txt", "w", encoding="utf8").close()
open(p1 + ".env", "w", encoding="utf8").close()

print('done!')
