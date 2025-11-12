# clone
# git clone https://github.com/yanwoo8/ktb3-yanni-community-be.git
# cd ktb3-yanni-community-be


# env and dependencies
conda create -n webproject python=3.13
conda activate webproject
which pip
# pip install fastapi uvicorn numpy pandas tensorflow keras pillow
pip install -e .


# run server
uvicorn main:app --reload
