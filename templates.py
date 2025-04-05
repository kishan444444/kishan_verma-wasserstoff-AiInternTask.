import os
from pathlib import Path

package_name="email_assistant"

list_of_files=[
    "github/workflows/.gitkeep",
    f"src/{package_name}/__init__.py",
    
    f"src/{package_name}/Authentication/__init__.py",
    f"src/{package_name}/Authentication/auth.py",
    f"src/{package_name}/utils/__init__.py",
    f"src/{package_name}/utils/utils.py",
    f"src/{package_name}/process_email/__init__.py",
    f"src/{package_name}/process_email/process_email.py",
    f"src/{package_name}/logger.py",
    f"src/{package_name}/exception.py",
    ".env",
    "requirements.txt",
     "main.py",
    
]


# here will create a directory

for filepath in list_of_files:
    filepath=Path(filepath)
    filedir,filename=os.path.split(filepath)
    
    """ how exist_ok works:if "directory" already exists, 
    os.makedirs() will not raise an error, and it will do nothing. 
    If "my_directory" doesn't exist, it will create the directory.
    """
    if filedir != "":
        os.makedirs(filedir,exist_ok=True)
        
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath,"w") as f:
            pass
    else:
        print("file already exists")


