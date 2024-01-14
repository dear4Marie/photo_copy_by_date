###############################################################################
## PHOTO COPY BY META DATA
## PARAM1 : SKIP COUNT (오류시 재작업할 경우 처리된 건수 제외용)
## PARAM2 : 사진을 정리할 디렉토리
## 
###############################################################################

import os, datetime, shutil, pymysql, sys
import exiftool
import common_utils as ut
from logging.config import dictConfig
import logging

## 정리할 사진, 동영상 디렉토리
dir_path = ''

# 정리된 파일을 모을 디렉토리
go_path          = "/volume2/backup_photo/" # 복사할 디렉토리
dest_path        = ''
target_date      = ''
target_file_name = ''
ext_list         = (".JPG", ".JPEG", ".PNG", ".NEF", ".HEIC", ".3GP", ".MOV", ".MP4", ".DNG", ".TIF", ".TIFF", ".CR2", ".CRW", ".RW2")
skip_count       = 0

conn = pymysql.connect(host='db호스트명', user='db유저명', password='db비밀번호', db='db명', charset='utf8', port=db포트)


c = conn.cursor()
iCnt = 0

## 제외처리할 카운드 (오류났을때 건너띄기용)
if (sys.argv[1] != ''):
    skip_count = int(sys.argv[1])

## 정리할 사진, 동영상 디렉토리 없을 경우 파라미터로 지정
if (dir_path == ''):
    dir_path = sys.argv[2]

print("#######################################")
print(" Source Directory : " + dir_path        )
print(" Target Directory : " + go_path         )
print(" Skip Count       : %d" % skip_count    )
print("#######################################")

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(message)s',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file']
    }
})


try:
    # 디렉토리 구조 돌면서 처리
    for (root, directories, files) in os.walk(dir_path) :
        for d in directories :
            d_path = os.path.join(root, d)
            #print(d_path)

        for file in files :
            file_path = os.path.join(root, file)
            #print(file_path)

            file_size = 0

            if "@eaDir" not in file_path:
                file_dir, file_name = os.path.split(file_path)
                file_dir, file_ext  = os.path.splitext(file_path)
                file_size           = os.path.getsize(file_path)
                target_file_name    = file_name.upper()

                #print("FILE LOCATION [ %d ]: %s"  % (iCnt, file_path))
                #print("FILE     SIZE [ %d ]: %d " % (iCnt, file_size))

                if (skip_count > iCnt):
                    skip_yn = 'Y'
                    iCnt = iCnt + 1
                else:
                    skip_yn = 'N'

                if (skip_yn == 'N'):
                    sql = "SELECT idx, file_loc, file_name, copy_yn, copy_loc, reg_date, mod_date FROM photo WHERE file_loc = '%s';" % (file_path)
                    #print(sql)
                    c.execute(sql)

                    data1 = c.fetchone()

                    copy_yn = 'N'
                    copy_str = 'N'

                    #print(data1)

                    if (data1 == None):
                        copy_yn = 'N'

                    elif (data1[3] == 'Y'):
                        update_sql = "UPDATE photo SET mod_date = NOW() WHERE idx = '%s';" % data1[0]
                        #print(update_sql)
                        c.execute(update_sql)
                        conn.commit

                        copy_yn = 'Y'
                        print(file_path + " Already Done!")
                    elif (data1[3] == 'N'):
                        copy_yn = 'U'

                    target_date = ''
                    exif_str    = ''
                    hash_str    = ''
                    dest_path   = ''
                    exif_model  = ''

                    # 파일 복사 대상이면 처리
                    if (copy_yn != 'Y'):
                        # 정리할 파일 확장자 정의
                        if (file_ext.upper() in ext_list):
                            #target_date = get_exif_info(file_path)
                            target_date, exif_str, hash_str, exif_model = ut.get_exif_info(file_path)

                            #print(exif_str)

                            if (len(target_date) == 10):
                                if (len(exif_model) > 0):
                                    dest_path = go_path + "/" + exif_model + "/" + target_date[0:4] + "/" + target_date+  "/"
                                else:
                                    dest_path = go_path + "/" + target_date[0:4] + "/" + target_date+  "/"
                                
                                #print(dest_path + " : " + str(len(target_date)))
                                if (os.path.isdir(dest_path) == False):
                                    os.makedirs(dest_path)

                                # 복사할 파일이 존재할 경우
                                if (os.path.exists(dest_path + target_file_name)):

                                    target_size = os.path.getsize(dest_path + target_file_name)

                                    if (target_size == file_size):
                                        #print("### 동일한 파일이 존재하므로 SKIP!! :" + file_path)
                                        copy_str = 'S'
                                    elif (target_size > file_size):
                                        #print("### 사이즈 큰 파일이 존재하므로 존재하므로 SKIP!! :" + file_path)
                                        copy_str = 'O'
                                    else:
                                        shutil.copy2(file_path, dest_path + target_file_name)
                                        copy_str = 'Y'
                                else:
                                    shutil.copy2(file_path, dest_path + target_file_name)
                                    copy_str = 'Y'
                            else:
                                dest_path = go_path + "/ERROR/"

                                if (os.path.isdir(dest_path) == False):
                                    os.makedirs(dest_path)

                                shutil.copy2(file_path, dest_path + target_file_name)
                                copy_str = ''
                        else:
                            dest_path = go_path + "/ERROR/"

                            if (os.path.isdir(dest_path) == False):
                                os.makedirs(dest_path)

                            shutil.copy2(file_path, dest_path + target_file_name)
                            copy_str = 'N'

                        now = datetime.datetime.now()
                        nowStr = now.strftime('%Y-%m-%d %H:%M:%S')

                        param2 = (file_path, target_file_name, copy_str, dest_path + target_file_name, file_size, hash_str, exif_str.replace("'", ""))
                        insert_sql = "INSERT INTO photo (file_loc, file_name, copy_yn, copy_loc, file_size, hash, exif) VALUES ('%s', '%s', '%s', '%s', %s, '%s', '%s');" % param2
                        #print(insert_sql)
                        c.execute(insert_sql)

                    #print("FILE LOCATION : " + file_path + " / " + dest_path + " / " + str(file_size))
                    logging.debug("FILE LOCATION : " + file_path + " / " + dest_path + " / " + str(file_size))

                    iCnt = iCnt + 1

                    if (iCnt % 10) == 0:
                        conn.commit()
                        print("#######################################")
                        print(" %d : Commit!!!" % iCnt)
                        print("#######################################")

    conn.commit()

    print("#######################################")
    print(" %d : Commit!!!" % iCnt)
    print("#######################################")

except Exception as inst:
    print(insert_sql)
    logging.debug(inst)
    logging.debug("exif_str : " + exif_str)
    logging.debug("insert_sql : " + insert_sql)
finally:

    conn.close()
