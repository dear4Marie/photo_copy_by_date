import os, datetime, sys
import exifread
import exiftool
import hashlib
import json

def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%Y:%m:%d')

    raise TypeError('not JSON serializable')


# exiftool 사용 함수
def get_exif_info(file_path):

    #print("FILE LOCATION : " + file_path)

    create_date    = ""
    metadata       = ""
    format_str1    = '%Y:%m:%d %H:%M:%S'
    format_str2    = '%d/%m/%Y %H:%M'
    exif_date_str = ""
    file_date_str = ""
    hash_str      = ""
    file_size     = 0
    exif_model    = ""

    #with open(file_path, 'rb') as f:
    with exiftool.ExifToolHelper() as et:
        #metadata = exifread.process_file(f)
        array = et.get_metadata(file_path)

        metadata = json.dumps(array[0])
        exif_str = json.loads(metadata)
        if len(metadata) > 0: 

            #print(metadata)

            # DB등록시 오류나는 항목 삭제
            # if 'EXIF:UserComment' in metadata:
            #     del metadata['EXIF:UserComment']
            # if 'QuickTime:CompressorName' in metadata:
            #     del metadata['QuickTime:CompressorName']
            # if 'ExifTool:Warning' in metadata:
            #     del metadata['ExifTool:Warning']
            # if 'MakerNotes:AFPointsInFocus1D'  in metadata:
            #     del metadata['MakerNotes:AFPointsInFocus1D']
            # if 'JPEGThumbnail'  in metadata:
            #     del metadata['JPEGThumbnail']

            # for tag in metadata:
            #     #print("Key: %s, value %s" % (tag, metadata[tag]))
            #     if tag['EXIF:DateTimeOriginal']: # 사진 촬영할 일자
            #         print("Key: %s, value %s" % (tag, metadata[0]))
            #         exif_date_str = str(metadata[tag])
            #     if tag['QuickTime:CreateDate']:  # 동영상 촬영 일자
            #         #print("Key: %s, value %s" % (tag, metadata[tag]))
            #         exif_date_str = str(metadata[tag])
            #     if tag['File:FileModifyDate']: # 카톡 등으로 받은 사진들
            #         #print("Key: %s, value %s" % (tag, metadata[tag]))
            #         file_date_str = str(metadata[tag])
            #     if tag['File:FileSize']:
            #         file_size = metadata[tag]
            #     if tag['EXIF:Model']:
            #         exif_model = str(metadata[tag])

            if "EXIF:DateTimeOriginal" in exif_str:                     # 사진 촬영할 일자
                #print(exif_str["EXIF:DateTimeOriginal"])
                exif_date_str = exif_str["EXIF:DateTimeOriginal"]
            if "QuickTime:CreateDate" in exif_str:                      # 동영상 촬영할 일자
                #print(exif_str["QuickTime:CreateDate"])
                exif_date_str = exif_str["QuickTime:CreateDate"]
            if "File:FileModifyDate" in exif_str:                       # 파일 수정 일자
                #print(exif_str["File:FileModifyDate"])
                file_date_str = exif_str["File:FileModifyDate"]
            if "File:FileSize" in exif_str:                             # 파일 사이즈
                #print(exif_str["File:FileSize"])
                file_size = exif_str["File:FileSize"]
            if "EXIF:Model" in exif_str:                                # 사진 촬영 기종
                #print(exif_str["EXIF:Model"])
                exif_model = exif_str["EXIF:Model"]
            if "QuickTime:Model" in exif_str:                           # 동영상 촬영할 일자
                #print(exif_str["QuickTime:Model"])
                exif_model = exif_str["QuickTime:Model"]

            if (exif_date_str == '') and (file_date_str == ''):
                print(exif_str)
            else:
                #print("exif_date_str" + exif_date_str)
                if ((exif_date_str == '') or (exif_date_str == '0000:00:00 00:00:00')) and (file_date_str != ''):
                    exif_date_str = file_date_str[0:19]

                try:
                    exif_date = datetime.datetime.strptime(exif_date_str, format_str1)
                    file_date = datetime.datetime.strptime(file_date_str[0:19], format_str1)

                    if (exif_date < file_date):
                        create_date = exif_date.strftime('%Y-%m-%d')
                    else :
                        create_date = file_date.strftime('%Y-%m-%d')
                    #print(create_date)
                except ValueError as ve:
                    exif_date = datetime.datetime.strptime(exif_date_str, format_str2)
                    file_date = datetime.datetime.strptime(file_date_str[0:19], format_str1)

                    if (exif_date < file_date):
                        create_date = exif_date.strftime('%Y-%m-%d')
                    else :
                        create_date = file_date.strftime('%Y-%m-%d')
            # Dictionary -> JSON

        # 중복제거용으로(사이즈 큰 파일을 읽으면 수행속도저하)
        if (file_size <= 1024000000):
            f = open(file_path, 'rb')
            data = f.read()
            f.close

            hash_str = hashlib.sha256(data).hexdigest()

        exif_str = json.dumps(metadata, indent="\t", default=json_default)

    return create_date, exif_str, hash_str, exif_model
출처: https://papawolf.com/category/글타래/Dev. [파파울프의 일상 웹 저장소:티스토리]
