

# import os
# # to handle file or folder operations but in this case or this code i use os to get pathes or names and join 
# # and i can use (pathlib) this easier without importing all os library
# import shutil
# # to handle file or folder operations move or copy 
# # i use it because i want function (copytree) because it copy all files or floder and subfolder within folder with the same structure
# import platform
# # this library to get device name or system information and i used it to khow who get the version of the file or app or package
# # and save it it database to know who get the version
# from datetime import datetime 
# #  i use it to khnow when the user get the version of the file or app or package
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.orm import declarative_base, sessionmaker
# # sqlalchemy is a library to write and read from database using python
# # import uuid
# # # uuid is library to create unique id for each record in the database
# import json
# # json is library to read and write json files
# from time import sleep

# Base = declarative_base()

# class CopySession(Base):
#     __tablename__ = 'copy_sessions'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     # id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     current_user = Column(String, nullable=False)
#     device_name = Column(String)
#     folder_name = Column(String, nullable=False)
#     source_path = Column(String, nullable=False)
#     destination_path = Column(String, nullable=False)
#     copied_at = Column(DateTime)

# def init_db():
#     engine = create_engine("sqlite:///backup_sessions.sqlite")
#     Base.metadata.create_all(engine)
#     return sessionmaker(bind=engine)()
# # ////////////////////////////////////////////////////////////////////

# def Data_json():
#     try:
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         json_path = os.path.join(base_dir, "Data.json")
        
        
#         with open(json_path, "r") as f:
#             data = json.load(f)
#             source = data.get("source", "")
#             destination = data.get("destination", "")
#             return source, destination
#     except FileNotFoundError:
#         print("Error: Data.json file not found.")
#         return "", ""
#     except json.JSONDecodeError:
#         print("Error: Data.json is not a valid JSON file.")
#         return "", ""


# # ////////////////////////////////////////////////////////////////////

# def comp_files_are_different(file1, file2):
#     try:
#         with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
#             return f1.read() != f2.read()
#     except Exception as e:
#         print(f"Error comparing {file1} and {file2}: {e}")  
#         return True 

# # ////////////////////////////////////////////////////////////////////

# def copy_folder(source, destination):

#     # try:
#     #     shutil.copytree(source, destination, dirs_exist_ok=True)
        
#     #     # >> copyfile >> handle single file copy not folder 
#     #     # >> copytree >> handle folder copy and all subfile and subfolder with metadata > ( time , date , permission >> مش فاهمها اوي لسه )
#     #     # and dont override existing files
#     #     # >> copy2 >> copy file with metadata >( time , date , permission >> مش فاهمها اوي لسه بردو ) 
        
#     #     print(f"\n Files copied from {source} to {destination}")
#     # except Exception as e:
#     #     print(f"\n Error during copying: {e}")
    
# # //////////////////////////////////////////////////////////////////////
    
    
#     # try:
#     #     for item in os.listdir(source):
#     #         src_path = os.path.join(source, item)
#     #         dest_path = os.path.join(destination, item) 
#     #         if os.path.isdir(src_path):
#     #             # لو فولدر
#     #             if os.path.exists(dest_path):
#     #                 shutil.rmtree(dest_path)  # امسح الفولدر القديم
#     #             shutil.copytree(src_path, dest_path)
#     #         else:
#     #             # لو فايل
#     #             if os.path.exists(dest_path):
#     #                 os.remove(dest_path)  # امسح الفايل القديم
#     #             shutil.copy2(src_path, dest_path)  # انسخ الفايل بمعلوماته 
                
#     #     print(f"\nFiles copied from {source} to {destination}")
#     # except Exception as e:
#     #     print(f"\nError during copying: {e}")
    

#     # /////////////////////////////////////////////////////////////////////////
    
#     try:
#         if not os.path.exists(destination):
#             os.makedirs(destination)


#         for item in os.listdir(source):
#             print("*-"*50)
#             print(f"Processing: {item}")
#             print("*-"*50)
#             src_path = os.path.join(source, item)
#             dest_path = os.path.join(destination, item)


#             if os.path.isdir(src_path):

#                 copy_folder(src_path, dest_path)
#                 # recursive التكرار هيفضل يعيد نفسه ف كل فولدر 
#             else:

#                 if not os.path.exists(dest_path):
#                     shutil.copy2(src_path, dest_path)
#                 else:
#                     # if the file exist in the destination
#                     if comp_files_are_different(src_path, dest_path):
#                         shutil.copy2(src_path, dest_path)
#                     else:
#                         print(f"Skipped (no changes): {src_path}")

#         print("Copy successfully.\n")
#     except Exception as e:
#         print(f" ******Error copy****** {e}")




# def log_copy_session(session, source, destination, device_name):
#     folder_name = os.path.basename(os.path.normpath(source))
#     # basename
#     # يجيب آخر جزء من ال path اللي هو اسم الفولدر عشان يتخزن
    
#     # normpath 
#     #  انا عايز اجيب اسم الابلكيشن او اسم الفايل اللي هنقلو ف هجيبو من اسم الفولدر 
#     #  ف بما انو انا بديلو ال path كامل ف الفانكشن دي بتشيل كل ال \ و بتجيب اخر اسم بس عشان انا اعتمدت ان طبيقي الفولدر  يبقي بنفس الاسم
#     copied_at = datetime.now()


#     record = CopySession(
#         current_user=os.getenv("USERNAME") or "unknown_user",
#         folder_name=folder_name,
#         source_path=source,
#         destination_path=destination,
#         device_name=device_name,
#         copied_at=copied_at
#     )
#     session.add(record)
#     session.commit()

#     print(f"Logged copy session: {folder_name} at {copied_at.strftime('%Y-%m-%d %H:%M:%S')}")



# def main():

#     source, destination = Data_json()
#     print(f" Source: {source} \n Destination: {destination} \n")

#     if destination == "" or source == "" or source == destination :
#         print(" error > Destination path cannot be empty or same as source")
#         return
#     if not os.path.exists(destination):
#         os.makedirs(destination)
#         print(f"Source path not exist, created: {destination}")  
        
                 

#     device_name = platform.node()
    
  
#     db = init_db()
#     copy_folder(source, destination)
#     log_copy_session(db, source, destination, device_name)

#     db.close()
#     print("\n \n Done.")
    
# if __name__ == "__main__":

#         main()

import os
import shutil
import platform
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import json

Base = declarative_base()

class CopySession(Base):
    __tablename__ = 'copy_sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    current_user = Column(String, nullable=False)
    device_name = Column(String)
    folder_name = Column(String, nullable=False)
    source_path = Column(String, nullable=False)
    destination_path = Column(String, nullable=False)
    copied_at = Column(DateTime)

def init_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    db_path = os.path.join(base_dir, "backup_sessions.sqlite")
    
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def read_data_json():
    """
    اقرأ Data.json في كل مرة قبل تنفيذ النسخ
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "Data.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            return data.get("source", ""), data.get("destination", "")
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return "", ""

def files_are_different(file1, file2):
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() != f2.read()
    except:
        return True

def copy_folder(source, destination):
    try:
        if not os.path.exists(destination):
            os.makedirs(destination)
        for item in os.listdir(source):
            src = os.path.join(source, item)
            dst = os.path.join(destination, item)
            if os.path.isdir(src):
                copy_folder(src, dst)
            else:
                if not os.path.exists(dst) or files_are_different(src, dst):
                    shutil.copy2(src, dst)
    except Exception as e:
        print(f"Copy Error: {e}")

def log_copy_session(session, source, destination, device_name):
    record = CopySession(
        current_user=os.getenv("USERNAME") or "unknown_user",
        folder_name=os.path.basename(os.path.normpath(source)),
        source_path=source,
        destination_path=destination,
        device_name=device_name,
        copied_at=datetime.now()
    )
    session.add(record)
    session.commit()

def run_backup():
    # اقرأ JSON **في كل مرة** قبل النسخ
    source, destination = read_data_json()
    if not source or not destination or source == destination:
        return

    db = init_db()

    if not os.path.exists(destination):
        shutil.copytree(source, destination)
    else:
        copy_folder(source, destination)

    log_copy_session(db, source, destination, platform.node())
    db.close()

def main():
    run_backup()
