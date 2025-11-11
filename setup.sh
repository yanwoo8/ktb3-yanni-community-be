conda create -n webproject python=3.13
conda activate webproject
which pip
pip install fastapi uvicorn numpy pandas tensorflow keras pillow
uvicorn main:app --reload