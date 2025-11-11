from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd


app = FastAPI()

df = pd.read_csv('data.csv')

class Item(BaseModel):
    name: str
    price: float


"""
@app.get("/")
async def read_root():
    return {"Hello": "KTB-AI"}
"""

@app.get("/")
async def read_root():
    return df.to_dict()




@app.get("/items/{item_id}")
def read_item(item_id: int,
              q: str,
              limit: int = 10):
    
    result_df = df[df['id'] == item_id][q].head(limit)
    #return {"item_id": item_id, "q": q}
    return {"result": result_df.to_list()}




@app.post("/items/")
async def save_item(item_id: int, item: Item):
    df.loc[len(df)] = {
        "item_id" : item_id,
        "name" : item.name,
        "price" : item.price
    }
    df.to_csv('data.csv', index=False)
    return item