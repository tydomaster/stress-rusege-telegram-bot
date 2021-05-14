import os
from os import path
p = os.path.abspath('')
p1 = os.path.abspath('')
pl = os.path.abspath('')

p += r'\dbs\''
p1 += r'\''
pl += r'\logs\''

p = p[:-1]
p1 = p1[:-1]
pl = pl[:-1]

if path.exists("dbs") == 0:
    os.mkdir("dbs")
if path.exists("logs") == 0:
    os.mkdir("logs")

pmain = p + "db_main_info.txt"
pmainb = p + "db_main_info_backup.txt"
pused = p + "db_used_info.txt"
pusedb = p + "db_used_info_backup.txt"
pach = p + "db_achievements_info.txt"
pachb = p + "db_achievements_info_backup.txt"

if path.exists(pmain) == 0:
    open(pmain, "w", encoding="utf8").close()
if path.exists(pmainb) == 0:
    open(pmainb, "w", encoding="utf8").close()
if path.exists(pused) == 0:
    open(pused, "w", encoding="utf8").close()
if path.exists(pusedb) == 0:
    open(pusedb, "w", encoding="utf8").close()
if path.exists(pach) == 0:
    open(pach, "w", encoding="utf8").close()
if path.exists(pachb) == 0:
    open(pachb, "w", encoding="utf8").close()
if path.exists(".env") == 0:
    f = open(p1 + ".env", "w", encoding="utf8")
    f.write('BOT_TOKEN=\nMAIN_INFO='
            + pmain + '\nMAIN_INFO_BACKUP='
            + pmainb + '\nUSED_INFO='
            + pused + '\nUSED_INFO_BACKUP='
            + pusedb + '\nACHIEVEMENTS_INFO='
            + pach + '\nACHIEVEMENTS_INFO_BACKUP='
            + pachb + '\nLOGS_PATH=' + pl)

print('done!')
